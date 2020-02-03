import asyncio
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
    sa.Column('site_id', sa.Integer, sa.ForeignKey('site.id'))
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

    async def add_track(self, site, user):
        pass

    async def remove_track(self, site, user):
        pass


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
