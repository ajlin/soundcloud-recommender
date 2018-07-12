from sqlalchemy.types import JSON, String, Integer, Boolean, Float, BigInteger
from sqlalchemy import Table,Column,ForeignKey,ForeignKeyConstraint,UniqueConstraint,CheckConstraint,MetaData,create_engine
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy.ext.declarative import declarative_base

pg_server = dict(
    ip = '34.220.110.231',
    port = '5432',
    user = 'postgres',
    key = '3GXwojABHaEUDQ?jcr',
    sql = 'postgres',
    db = 'postgres'
    )

dburi = "{sql}://{user}:{key}@{ip}:{port}/{db}".format(**pg_server)

#create a metadata instance
myengine = create_engine(dburi,pool_size=15)
mymetadata = MetaData(myengine)

Base = declarative_base(metadata = mymetadata)
make_session = sessionmaker(bind=myengine)


class User(Base):
    __tablename__ = 'users'

    id=Column(type_=BigInteger,primary_key=True)
    kind=Column(type_=String)
    username=Column(type_=String)
    last_modified=Column(type_=String)
    permalink_url=Column(type_=String)
    country=Column(type_=String)
    first_name=Column(type_=String)
    last_name=Column(type_=String)
    full_name=Column(type_=String)
    description=Column(type_=String)
    city=Column(type_=String)
    track_count=Column(type_=Integer)
    playlist_count=Column(type_=Integer)
    plan=Column(type_=String)
    public_favorites_count=Column(type_=Integer)
    followers_count=Column(type_=Integer)
    followings_count=Column(type_=Integer)
    uri=Column(type_=String)

    #favs = relationship("Fav", back_populates="favs")

    is_user=Column(Boolean, default=True)
    CheckConstraint('is_user = True', name='is_user')

    __table_args__ = (UniqueConstraint(id, is_user),{})

    def __repr__(self):
        return "<Users(id='%d', username='%s', full_name='%s')>"\
                        % (self.id, self.username, self.full_name)

class Track(Base):
    __tablename__ = 'tracks'

    id=Column(type_=BigInteger,primary_key=True)
    comment_count=Column(type_=Integer)
    commentable=Column(type_=Boolean)
    created_at=Column(type_=String)
    description=Column(type_=String)
    downloadable=Column(type_=Boolean)
    duration=Column(type_=BigInteger)
    favoritings_count=Column(type_=Integer)
    genre=Column(type_=String)
    kind=Column(type_=String)
    last_modified=Column(type_=String)
    permalink_url=Column(type_=String)
    playback_count=Column(type_=Integer)
    streamable=Column(type_=Boolean)
    tag_list=Column(type_=String)
    title=Column(type_=String)
    track_type=Column(type_=String)
    uri=Column(type_=String)
    user_id=Column(type_=BigInteger)

    is_user=Column(Boolean, default=False)
    CheckConstraint('is_user = False', name='is_user')

    __table_args__ = (UniqueConstraint(id, is_user),{})

    def __repr__(self):
        return "<Tracks(id='%d', title='%s', user_id='%s')>"\
                        % (self.id, self.title, self.user_id)

class Fav(Base):
    __tablename__ = 'favs'
    track_id = Column(BigInteger,\
                primary_key=True,nullable=False)
    user_id = Column(BigInteger,\
                primary_key=True,nullable=False)

    #track = relationship("Track", back_populates="favs")
    #user = relationship("User",back_populates="favs")

    def __repr__(self):
        return "<Favs(email_address='%s')>" % self.email_address

#User.favs = relationship("Fav", order_by=User.id, back_populates="user")

#Track.favs = relationship("Fav", order_by=User.id, back_populates="track")

class Com(Base):
    __tablename__ = 'coms'

    track_id = Column(BigInteger,\
                primary_key=True,nullable=False)

    user_id = Column(BigInteger,\
                primary_key=True,nullable=False)


    #track = relationship("Track", back_populates="coms")
    #user = relationship("User",back_populates="coms")

    def __repr__(self):
        return "<Favs(email_address='%s')>" % self.email_address

#User.coms = relationship("Com", order_by=Com.track_id, back_populates="user")

#Track.coms = relationship("Com", order_by=Com.user_id, back_populates="track")


class Manifest(Base):
    __tablename__ = 'manifest'

    ref_id = Column(BigInteger,primary_key=True)
    is_user = Column(Boolean,primary_key=True)
    users = Column(type_=String)
    tracks = Column(type_=String)
    favs = Column(type_=String)
    coms = Column(type_=String)


tables = dict(
    users = User,
    tracks = Track,
    manifest = Manifest,
    favs = Fav,
    coms = Com
    )
"""
    ### one day i'll try and get this multi relational thing to work ###
    __table_args__ = (
        ForeignKeyConstraint(
            [is_user, ref_id],
            [User.is_user, User.id]),
        ForeignKeyConstraint(
            [is_user, ref_id],
            [Track.is_user,Track.id]),
        {})
"""
