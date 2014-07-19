from sqlalchemy import Column, Integer, Unicode, UnicodeText
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///db/dogs.db')
Base = declarative_base(bind=engine)

class Dog(Base):
    __tablename__ = 'dogs'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(40))
    image = Column(UnicodeText)

    def __init__(self, name, image):
        self.name = name
        self.image = image

    def get_image_url(self):
        return '/dog/%s/image' %self.id


Base.metadata.create_all()

Session = sessionmaker(bind=engine)
db_session = Session()

