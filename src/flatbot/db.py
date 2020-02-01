import aiopg.sa as sa


async def setup(app, config):
    db_config = config.db
    db = await sa.create_engine(database=db_config.name,
                                user=db_config.user,
                                password=db_config.password,
                                host=db_config.host,
                                port=db_config.port)
    app['db'] = db

    async def close_pg(app):
        app['db'].close()
        await app['db'].wait_closed()
    app.on_cleanup.append(close_pg)

    return db


# TODO: define tables with SA
meta = sa.MetaData()
user = sa.Table('user', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('login', sa.String(100), nullable=False),
    sa.Column('passwd', sa.String(100), nullable=False),
)

membership = sa.Table(
    'membership', meta,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
    sa.Column('channel_id', sa.Integer, sa.ForeignKey('channel.id'))
)

channel = sa.Table('channel', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('url', sa.String(200), nullable=False),
    sa.relationship('advertisement'),
    sa.relationship('user', secondary=membership)
)

advertisement = sa.Table('advertisement', meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('content', sa.String(500), nullable=False),
    sa.Column(sa.Integer, sa.ForeignKey('channel.id'))
)


class Storage:
    def __init__(self):
        self.results = {}

    def update(self, id, updates):
        prev = self.results.get(id, [])
        diff = [u for u in updates if u not in prev]

        if diff:
            self.results[id] = updates
        return diff
