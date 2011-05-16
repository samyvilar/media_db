from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, LargeBinary, create_engine
from sqlalchemy.orm import sessionmaker, mapper, relationship

import ImageIndexer.ImageIndexer as indx
import StringIO

import numpy

class Video(object):
    def __init__(self, source):        
        self.source         = source
        
        
class Image(object):
    def __init__(self, filename, title, description, source, edge_map, histogram, hash, width, height, mode, format):
        self.filename       = filename
        self.title          = title
        self.description    = description
        self.source         = source
        self.edge_map       = edge_map
        self.histogram      = histogram
        self.hash           = hash
        self.width          = width
        self.height         = height
        self.mode           = mode
        self.format         = format

    def __repr__(self):
        return "<Image('%s','%s', '%s')>" % (self.filename, self.title, self.description)

    def __eq__(self, other):
        assert(type(self) == type(other))
        return self.id == other.id and self.filename == other.filename


class Keyword(object):
    def __init__(self, keyword, frequency):
        self.keyword = keyword
        self.frequency = frequency

    def __eq__(self, other):
        assert(type(self) == type(other))
        return self.id == other.id and self.keyword == other.keyword
    
        
class DB(object):
    db      = "media.db"
    session = None
    engine  = None
    images  = {}  # List would have being faster but building a 2**31 even through list comprehenssion on arrandale chip still takes a while, in python


    def __init__(self, create = False):
        self.engine = create_engine('sqlite:///' + self.db, echo = False) # Set echo to true if you want to debug, either wise false, messy terminal        
        self.session = sessionmaker(bind = self.engine)()

        metadata = MetaData()
        image_keywords = Table('image_keywords', metadata,
                        Column('image_id',      Integer,        ForeignKey('images.id')),
                        Column('keyword_id',    Integer,        ForeignKey('keywords.id')))

        keywords = Table('keywords', metadata,
                       Column('id',             Integer,        primary_key = True),
                       Column('keyword',        String,         nullable = False, unique = True),
                       Column('frequency',      Integer,        nullable = False))

        videos = Table('videos', metadata,
                       Column('id',             Integer,        primary_key = True, autoincrement = True),
                       Column('source',         LargeBinary,    nullable = True))

        images = Table('images', metadata,
                       Column('id',             Integer,        primary_key = True, autoincrement = True),
                       Column('filename',       String,         nullable = False),
                       Column('title',          String,         nullable = True ),
                       Column('description',    String,         nullable = True ),
                       Column('source',         LargeBinary,    nullable = False),
                       Column('edge_map',       LargeBinary,    nullable = True ),
                       Column('histogram',      LargeBinary,    nullable = True ),
                       Column('hash',           Integer,        nullable = True ),
                       Column('width',          Integer,        nullable = True ),
                       Column('height',         Integer,        nullable = True ),
                       Column('mode',           String,         nullable = True ),
                       Column('format',         String,         nullable = True ),                       
                       Column('video',          Integer,        ForeignKey('videos.id'), nullable = True))
            
        mapper(Image,   images, properties = {'videos':relationship(Video), 'keywords': relationship(Keyword, secondary=image_keywords, backref='images')})
        mapper(Video,   videos)
        mapper(Keyword, keywords)

        if create:
            metadata.create_all(self.engine)
        else:            
            for image in self.session.query(Image).order_by(Image.hash).all():                
                self.add_image_hash(image)


    def add_image_hash(self, image):
        if self.images.has_key(image.hash):
            self.images[image.hash].append(image)
        else:
            self.images[image.hash] = []
            self.images[image.hash].append(image)


    def remove_image_hash(self, image):
        if self.images.has_key(image.hash):
            images = self.images[image.hash]
            for img in images:
                if img.id == image.id:
                    self.images[image.hash].remove(img)
                    return 1
        else:
            return 0


    def get_hist(self, values, size = 16):
        hist = [0 for x in xrange(size)]
        for value in values: hist[value % size] += 1 # 44% faster than what found in the ImageIndexer ...
        return hist


    def get_hash(self, hist, maxsize = 2**31):
        hash = 0
        for loc in xrange(len(hist)): hash += loc * hist[loc] # Simple hashing function ...
        return (hash % maxsize)


    def get_image_stats(self, source):
        indexer = indx.ImageIndexer(StringIO.StringIO(source))
        indexer.makeGrayscale()

        stats = {}
        
        stats['hist']       = self.get_hist(list(indexer.img.getdata()))
        stats['hash']       = self.get_hash(stats['hist'])
        stats['width']      = indexer.img.size[0]
        stats['height']     = indexer.img.size[1]
        stats['mode']       = indexer.img.mode
        stats['format']     = indexer.img.format

        indexer.makeEdgeMap(90) # Seems high enough to remove noise ...  we need as many zeros as possible to reduce computation on collisions ...
        stats['edge_map']   = list(indexer.edge_map.getdata())

        return stats


    def get_keywords(self, string):
        keywords = []
        temp = ''
        for ch in string:
            if '0' <= ch <= '9' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
                temp += ch
            elif temp == '':
                continue
            else:
                keywords.append(temp)
                temp = ''
        if temp != '':
            keywords.append(temp)
        return [keyword for keyword in keywords if keyword != '']


    def get_keyword(self, keyword):
        return self.session.query(Keyword).filter(Keyword.keyword == keyword).all()


    def add_keyword(self, keyword, image):        
        keyword_obj = self.get_keyword(keyword)
        if len(keyword_obj) == 0:
            temp = Keyword(keyword, 1)
            self.session.add(temp)
            self.session.commit()
            temp.images.append(image)            
            image.keywords.append(temp)            
        elif len(keyword_obj) == 1:
            if keyword_obj[0] not in image.keywords: image.keywords.append(keyword_obj[0])
            keyword_obj[0].frequency += 1
            if image not in keyword.images: keyword.images.append(image)
        else:
            raise Exception("Multiple keywords found! " + keyword_obj)
            
        self.session.commit()
            

    def add_keywords(self, image):
        keywords = self.get_keywords(image.filename)
        keywords.extend(self.get_keywords(image.title))
        keywords.extend(self.get_keywords(image.description))
        
        for keyword in keywords: self.add_keyword(keyword, image)
        
        return len(keywords)            


    def add_image(self, filename, source, title = None, description = None):
        assert filename != ''
        assert source   != ''
                
        stats = self.get_image_stats(source)

        image = Image(filename, title, description, buffer(source), buffer(numpy.asarray(stats['edge_map']).tostring()),
            buffer(numpy.asarray(stats['hist']).tostring()), stats['hash'], stats['width'], stats['height'], stats['mode'], stats['format'])
            
        self.session.add(image)        
        self.session.commit()        

        keyword_count = self.add_keywords(image)
        self.add_image_hash(image)

        return {'id':image.id, 'keyword_count':keyword_count}


    def delete_image(self, id):
        image = self.session.query(Image).filter(Image.id == int(id)).all()[0]
        self.session.delete(image)
        return image.id


    def update_image(self, id, filename, source, title = None, description = None):
        image = self.get_image(id)

        image.filename      = filename
        image.title         = title
        image.description   = description

        if image.source != source:
            stats           = self.get_image_stats(source)
            image.source    = source
            image.edge_map  = buffer(numpy.asarray(stats['edge_map']).tostring())
            image.hist      = buffer(numpy.asarray(stats['hist']).tostring())
            if image.hash != stats['hash']:
                self.remove_image_hash(image)
                image.hash      = stats['hash']                
            image.width     = stats['width']
            image.height    = stats['height']
            image.mode      = stats['mode']
            image.format    = stats['format']

        self.session.commit()
        self.add_image_hash(image)
        return self.get_image(id)


    def get_image(self, id):
        return self.session.query(Image).filter(Image.id == int(id)).all()

    def get_all_images(self):
        return self.session.query(Image).all()


    def search_by_image(self, source):
        stats  = self.get_image_stats(source)
        images = self.images[stats['hash']]
        return sorted(images, key = lambda image: numpy.sum(abs(numpy.asarray(stats['edge_map']) - numpy.fromstring(image.edge_map, dtype = 'int'))))


    def search_by_keywords(self, allkeywords):
        keywords = sorted([self.get_keyword(keyword)[0] for keyword in self.get_keywords(allkeywords) if self.get_keyword(keyword) != []],
                            key = lambda keyword: keyword.frequency, reverse = True)
        images = []
        images.extend([image for keyword in keywords for image in keyword.images if image not in images])

        return images



        


        
    


        
