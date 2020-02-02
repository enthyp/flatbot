import aiopg.sa as aio_sa
import sqlalchemy as sa


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
    sa.Column('content', sa.String(500), nullable=False),
    sa.Column('site_id', sa.Integer, sa.ForeignKey('site.id'))
)


class Storage:
    def __init__(self, db_engine):
        self.db = db_engine

    async def close(self):
        self.db.close()
        await self.db.wait_closed()

    # TODO: users for auth module!
    def get_site(self, url):
        pass

    def update_site(self, site, url):
        pass

    def add_track(self, site, user):
        pass

    def remove_track(self, site, user):
        pass


async def setup(app, config):
    db_config = config.db
    db = await aio_sa.create_engine(database=db_config['name'],
                                    user=db_config['user'],
                                    password=db_config['password'],
                                    host=db_config['host'],
                                    port=db_config['port'])
    storage = Storage(db)
    app['storage'] = storage
    app.on_cleanup.append(storage.close)
