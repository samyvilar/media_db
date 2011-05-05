from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, BLOB, create_engine
from sqlalchemy.orm import sessionmaker, mapper, relationship

import image_indexer.ImageIndexer as indx
import base64

class Image(object):
    def __init__(self, filename, title, description, source, edge_map, histogram, edge_map_hist):    
        self.filename       = filename
        self.title          = title
        self.description    = description
        self.source         = source
        self.edge_map       = edge_map
        self.histogram      = histogram
        self.edge_map_hist  = edge_map_hist

    def __repr__(self):
        return "<Image('%s','%s', '%s')>" % (self.filename, self.title, self.description)

class Keyword(object):
    def __init__(self, id, keyword, images, videos):
        self.id = id
        
class DB(object):
    db      = "media.db"
    session = None
    engine  = None

    def __init__(self):
        self.engine = create_engine('sqlite:///' + self.db, echo = True)
        self.session = sessionmaker(bind = self.engine)

    def create_db(self):        
        metadata = MetaData()

        keywords = Table('keywords', metadata,
                         Column('keyword', String, primary_key = True))


        images = Table('images', metadata,
                       Column('id',             Integer, primary_key = True, autoincrement = True),
                       Column('filename',       String, nullable = False),
                       Column('title',          String, nullable = True),
                       Column('description',    String, nullable = True),
                       Column('source',         String,   nullable = False),
                       Column('edge_map',       BLOB,   nullable = True),
                       Column('histogram',      BLOB,   nullable = True),                       
                       Column('keyword',        String, ForeignKey('keywords.keyword')))

        metadata.create_all(self.engine)
        mapper(Image, images)

        mapper(Keyword, keywords, properties = {'images': relationship(Image)})


    # We need to decide whether or not we are going to use base64, but all points to yes ...
    def add_image(self, filename, source, title, description):
        raise Exception("Function has yet to be fully implemented!")
    
        indexer = indx.ImageIndexer(source)
        indexer.makeGrayscale()

        hist = indexer.makeHistogram()
        edge_map = indexer.makeEdgeMap()


        image = Image()

    def search_by_keyword(self, keyword):
        raise Exception("Function has yet to be fully implemented!")
    
        keywords = keyword.strip().split(' ')


    def search_by_image(self, filename, source):
        raise Exception("Function has yet to be fully implemented!")


        
    


        
