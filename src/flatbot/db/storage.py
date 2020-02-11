import aiopg.sa as aiosa
import sqlalchemy as sa
from psycopg2.errors import UniqueViolation

from flatbot.db.model import Advertisement, Site


meta = sa.MetaData()
users = sa.Table(
    'users', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('login', sa.String(100), unique=True, nullable=False),
    sa.Column('passwd', sa.String(100), nullable=False),
)

tracks = sa.Table(
    'tracks', meta,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('site_id', sa.Integer, sa.ForeignKey('site.id')),
    sa.PrimaryKeyConstraint('user_id', 'site_id', name='tracks_pk')
)

sites = sa.Table(
    'site', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('url', sa.String(200), unique=True, nullable=False),
)

advertisements = sa.Table(
    'advertisement', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('url', sa.String(200), unique=True, nullable=False),
    sa.Column('content', sa.String(500), nullable=False),
    sa.Column('site_id', sa.Integer, sa.ForeignKey('site.id'))
)

# I can't seem to find a clean SA way to CREATE IF NOT EXISTS (!) async.
# Hello SQL, my old friend.
user_query = ('CREATE TABLE IF NOT EXISTS users('
              'id SERIAL PRIMARY KEY, '
              'login VARCHAR (100) UNIQUE NOT NULL, '
              'passwd VARCHAR (500) NOT NULL);')

site_query = ('CREATE TABLE IF NOT EXISTS site('
              'id SERIAL PRIMARY KEY, '
              'url VARCHAR (200) UNIQUE NOT NULL);')

advertisement_query = ('CREATE TABLE IF NOT EXISTS advertisement('
                       'id SERIAL PRIMARY KEY, '
                       'url VARCHAR (200) UNIQUE NOT NULL, '
                       'content VARCHAR (500) NOT NULL, '
                       'site_id SERIAL NOT NULL REFERENCES site(id) ON DELETE CASCADE);')

tracks_query = ('CREATE TABLE IF NOT EXISTS tracks('
                'user_id SERIAL REFERENCES users(id) ON DELETE CASCADE, '
                'site_id SERIAL REFERENCES site(id) ON DELETE CASCADE, '
                'CONSTRAINT tracks_pk PRIMARY KEY (user_id, site_id));')


class DBError(Exception):
    pass


class InvalidOpError(DBError):
    pass


class Storage:
    def __init__(self, db):
        self.db = db

    async def close(self):
        self.db.close()
        await self.db.wait_closed()

    async def registered(self, login):
        async with self.db.acquire() as conn:
            s_query = users.count().where(users.c.login == login)
            user_res = await conn.scalar(s_query)
            if user_res:
                return True
            return False

    async def get_hash(self, login):
        async with self.db.acquire() as conn:
            s_query = users.select().where(users.c.login == login)
            user_res = await conn.execute(s_query)
            if user_res:
                user = await user_res.fetchone()
                if user:
                    return user['passwd']
            return None

    async def get_site(self, url):
        async with self.db.acquire() as conn:
            site_query = sites.select().where(sites.c.url == url)
            site_res = await conn.execute(site_query)

            if not site_res:
                return None

            site = await site_res.fetchone()
            ads_query = advertisements.select().where(advertisements.c.site_id == site.id)
            ads_res = await conn.execute(ads_query)
            ads = await ads_res.fetchall()

            domain_ads = {Advertisement(a.url, a.content) for a in ads}
            domain_site = Site(site.url, domain_ads)

            return domain_site

    async def get_active_urls(self):
        async with self.db.acquire() as conn:
            site_query = sa.select([sites.c.url]).select_from(sites.join(tracks))
            site_res = await conn.execute(site_query)

            if not site_res:
                return None

            return [s[0] for s in await site_res.fetchall()]

    async def create_site(self, url):
        async with self.db.acquire() as conn:
            try:
                await conn.execute(sites.insert().values(url=url))
            except UniqueViolation:
                pass

    async def update_site(self, url, site):
        async with self.db.acquire() as conn:
            site_query = sites.select().where(sites.c.url == url)
            site_res = await conn.execute(site_query)

            if not site_res:
                res = await conn.execute(sites.insert().values(url=url))
                for ad in site.ads:
                    await conn.execute(advertisements.insert().values(
                        url=ad.url, content=ad.content, site_id=res.inserted_primary_key
                    ))
            else:
                prev_site = await site_res.fetchone()
                await conn.execute(
                    advertisements.delete().where(advertisements.c.site_id == prev_site.id)
                )
                for ad in site.ads:
                    await conn.execute(advertisements.insert().values(
                        url=ad.url, content=ad.content, site_id=prev_site.id
                    ))

    async def remove_site(self, url):
        # TODO: unused for now? just use scripts?
        async with self.db.acquire() as conn:
            await conn.execute(sites.delete().where(sites.c.url == url))

    async def add_track(self, url, login):
        async with self.db.acquire() as conn:
            # TODO: fewer DB requests?
            site_res = await conn.execute(sites.select().where(sites.c.url == url))
            if not site_res:
                raise InvalidOpError()

            site = await site_res.fetchone()
            user_res = await conn.execute(users.select().where(users.c.login == login))
            user = await user_res.fetchone()

            insert_query = tracks.insert().values(site_id=site.id, user_id=user.id)
            await conn.execute(insert_query)

    async def remove_track(self, url, login):
        async with self.db.acquire() as conn:
            query = sites.join(tracks).join(users).select().where(
                sa.and_(
                    users.c.login == login,
                    sites.c.url == url
                )
            )
            track_res = await conn.execute(query)
            if not track_res:
                raise InvalidOpError()

            track = await track_res.fetchone()
            del_query = tracks.delete().where(
                sa.and_(
                    tracks.c.site_id == track['site_id'],
                    tracks.c.user_id == track['user_id']
                )
            )
            await conn.execute(del_query)

    async def is_tracked(self, url):
        async with self.db.acquire() as conn:
            query = sites.join(tracks).select().where(sites.c.url == url)
            tracks_res = await conn.execute(query)
            return bool(tracks_res)


async def get_engine(config):
    db_config = config.db
    engine = await aiosa.create_engine(database=db_config['name'],
                                       user=db_config['user'],
                                       password=db_config['password'],
                                       host=db_config['host'],
                                       port=db_config['port'])
    return engine


async def cleanup_storage(app):
    await app['storage'].close()


def setup_db(app, config):
    async def _setup(app):
        engine = await get_engine(config)
        app['storage'] = Storage(engine)

        # Create tables.
        async with engine.acquire() as conn:
            await conn.execute(user_query)
            await conn.execute(site_query)
            await conn.execute(advertisement_query)
            await conn.execute(tracks_query)

    app.on_startup.append(_setup)
    app.on_cleanup.append(cleanup_storage)
