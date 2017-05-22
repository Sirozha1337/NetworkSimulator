from sqlalchemy import *

db = create_engine('sqlite:///tutorial.db')

db.echo = False  # Try changing this to True and see what happens

metadata = MetaData(db)

users = Table('user', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(40), unique=True),
    Column('password', String(40)),
    Column('authenticated', Boolean, default=False),
)
users.create()

i = users.insert()
i.execute(username='admin', password='secret')
i.execute(username='user', password='password')

#users = Table('users', metadata, autoload=True)

s = users.select()
rs = s.execute()

row = rs.fetchone()
print 'Id:', row[0]
print 'username:', row['username']
print 'Password:', row['password']

