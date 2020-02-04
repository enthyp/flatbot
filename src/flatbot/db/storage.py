import aiopg.sa as aiosa
import sqlalchemy as sa

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

    # TODO: users for auth module!

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

            domain_ads = [Advertisement(a.url, a.content) for a in ads]
            domain_site = Site(site.url, domain_ads)

            return domain_site

    async def get_sites(self):
        async with self.db.acquire() as conn:
            site_query = sites.select()
            site_res = await conn.execute(site_query)

            if not site_res:
                return None

            return [s['url'] for s in await site_res.fetchall()]

    async def create_site(self, url):
        async with self.db.acquire() as conn:
            await conn.execute(sites.insert().values(url=url))

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
        async with self.db.acquire() as conn:
            await conn.execute(sites.delete().where(sites.c.url == url))

    async def add_track(self, url, login):
        async with self.db.acquire() as conn:
            # TODO: fewer DB requests?
            site_res = await conn.execute(sites.select().where(sites.c.url == url))
            if not site_res:
                raise InvalidOpError()

            user_res = await conn.execute(users.select().where(users.c.login == login))
            site = await site_res.fetchone()
            user = await user_res.fetchone()
            await tracks.insert().values(site_id=site.id, user_id=user.id)

    async def remove_track(self, url, login):
        async with self.db.acquire() as conn:
            query = sites.join(tracks).join(users).select(tracks.c.id).where(
                sa.and_(
                    users.c.login == login,
                    sites.c.url == url
                )
            )
            track_res = await conn.execute(query)
            if not track_res:
                raise InvalidOpError()

            track = await track_res.fetchone()
            await conn.execute(tracks.delete().where(tracks.c.id == track[0]))

    async def is_tracked(self, url):
        async with self.db.acquire() as conn:
            query = sites.join(tracks).select().where(sites.c.url == url)
            tracks_res = await conn.execute(query)
            return bool(tracks_res)


async def get_storage(config):
    db_config = config.db
    db = await aiosa.create_engine(database=db_config['name'],
                                   user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'])
    return Storage(db)


async def setup(app, config):
    app['storage'] = await get_storage(config)
    app.on_cleanup.append(app['storage'].close)
