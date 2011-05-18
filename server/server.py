import bottle
from bottle import route, run, get, post, request, HTTPResponse, template, static_file
import db as database
import mimetypes
import Image
import numpy
import time
import StringIO

db = database.DB()
bottle.debug(True)

@route('/js/:path#.+#')
def server_static(path):
    return static_file(path, root='./js/')
    

def verify_image_id(id):
    if id == '':  return {'exception':"Expecting an image id got ''"}
    
    image = db.get_image(int(id))
    if len(image) == 0  : return {'exception':"There was no image with an id: "          + id}
    if len(image) >  1  : return {'exception':"There where multiple images with an id: " + id}

    return image[0]

def verify_video_id(id):
    if id == '': return {'exception':"Expecting a video id got ''"}

    video = db.get_video(int(id))

    if len(video) == 0 : return {'exception':"There was no video with an id: " + id}
    if len(video) >  1 : return {'exception':"There where multiple videos with an id " + id}

    return video[0]

def get_file_name_source(request):
    return (request.files.get('source', '').filename, request.files.get('source', '').file.read()) if request.files.get('source', '') != '' else ('','')

def verify_filename_source(filename, source):
    if filename == '': return {'exception':'(add_image)A file name is required! received ""'}
    if source   == '': return {'exception':'(add_image)A file source is required!'}
    return True
    

# GET, DELETE AND UPDATE SINGLE IMAGE ##########################################
@post('/add_image')
def add_image():
    filename, source = get_file_name_source(request)

    status = verify_filename_source(filename, source)
    if type(status) == type({}):
        return status
        
    title       = request.forms.get('title', '')
    description = request.forms.get('description', '')

    try:
        props = db.add_image(filename, source, title, description)
        return {'message':'Successfully added image.', 'id':props.image_id, 'keyword_count':props.keyword_count}
    except Exception as ex:
        return {'exception':str(ex)}


@get('/delete_image')
def delete_image():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image

    try:
        db.delete_image(image_id)
        return {'message':'Successfully delete image.', 'id':image.id}
    except Exception as ex:
        return {'exception':str(ex)}


@post('/update_image')
def update_image(): # This is method hasn't being fully thought out ...
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image
    

    filename, source = get_file_name_source(request)

    title       = request.forms.get('title', '')
    description = request.forms.get('description', '')

    try:
        newimg = db.update_image(image_id, filename, source, title, description)
        if newimg.tilte == title and newimg.filename == filename and newimg.description == description:
            return {'message':"Successfully updated image.", 'id':newimg.id}
        else:
            return {'message':"The image wasn't updated properly.", 'id':image.id}
    except Exception as ex:
        return {'exception':str(ex)}

def get_header(object):
    header = {}

    mimetype, encoding = mimetypes.guess_type(object.filename)
    
    if mimetype: header['Content-Type'] = mimetype
    if encoding: header['Content-Encoding'] = encoding
    header['Content-Disposition'] = 'attachment; filename="%s"' % object.filename
    header['Content-Length'] = len(object.source)

    return header
    

@get('/get_image_source')
def get_image_source():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image            
    
    body    = image.source
    header  = get_header(image)
    
    return HTTPResponse(body, header = header)
    

def get_video_dict(video):
    return {'id'            :video.id,
            'filename'      :video.filename,
            'length'        :video.length,
            'width'         :video.width,
            'height'        :video.height,
            'fps'           :video.fps,
            'format'        :video.format,
            'codec'         :video.codec,
            'images'        :[image.id for image in video.images]}

def get_image_dict(image):
    return {'id'            :image.id,
            'filename'      :image.filename,
            'title'         :image.title,
            'description'   :image.description,
            'size'          :len(image.source),
            'width'         :image.width,
            'height'        :image.height,
            'mode'          :image.mode,
            'format'        :image.format,
            'keywords'      :[keyword.keyword for keyword in image.keywords],
            'video'         :image.video[0].id if len(image.video) > 0 else None}

@get('/get_image_info')
def get_image_info():
    id = request.GET.get('image_id', '')

    image = verify_image_id(id)
    if type(image) == type({}): return image
    
    return get_image_dict(image)


@get('/get_image_edge_source')
def get_image_edge_source():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image

    header = {}
    mimetype, encoding = mimetypes.guess_type(image.filename)

    img = Image.new('L', (image.width, image.height))
    img.putdata(numpy.fromstring(image.edge_map, dtype = 'int'))
    body = StringIO.StringIO()
    img.save(body, image.format)

    if mimetype: header['Content-Type'] = mimetype
    if encoding: header['Content-Encoding'] = encoding
    header['Content-Disposition']   = 'attachment; filename="%s"' % 'edge_' + image.filename
    header['Content-Length']        = len(body.getvalue())

    return HTTPResponse(body.getvalue(), header = header)


@get('/get_image_thumbnail_source')
def get_image_thumbnail_source():
    image_id = request.GET.get('image_id', '')
    size     = request.GET.get('size', 128)

    image = verify_image_id(image_id)
    if type(image) == type({}): return image

    thumbnail = Image.open(StringIO.StringIO(image.source))
    thumbnail.thumbnail((size, size), Image.ANTIALIAS)

    body = StringIO.StringIO()
    print image.format
    thumbnail.save(body, image.format if image.format != '' else 'JPEG')

    header = get_header(image)
    header['Content-Length'] = len(body.getvalue())

    return HTTPResponse(body.getvalue(), header = header)


@get('/get_all_images')
def get_all_images():
    images = db.get_all_images()
    return {'images':[get_image_dict(image) for image in images]}

@get('/get_all_videos')
def get_all_videos():
    videos = db.get_all_videos()
    return {'videos':[get_video_dict(video) for video in videos]}
################################################################################

@post('/search_by_image')
def search_by_image():    
    source = request.files.get('source', '')

    if source == ''  : return {'exception':'(add_image)A file source is required!'}

    source      = source.file.read()

    try:
        images = search_by_image(source)
        return {'images':[get_image_dict(image) for image in images]}
    except Exception as ex:
        return {'exception':str(ex)}


@get('/search_by_keyword')
def search_by_keyword():
    keyword = request.GET.get('keyword', '')

    if keyword == '': return dict(get_all_images().items() + get_all_images().items())

    try:
        results = db.search_by_keywords(keyword)

        return {'images':[get_image_dict(image) for image in results['images']], 'videos':[get_video_dict(video) for video in results['videos']]}
    except Exception as ex:
        return {'exception':str(ex)}

@post('/add_video')
def add_video():
    filename, source = get_file_name_source(request)

    status = verify_filename_source(filename, source)
    if type(status) == type({}):
        return status
    
    title       = request.forms.get('title', '')
    description = request.forms.get('description', '')

    try:
        props = db.add_video(filename, source, title, description)
        return {'message':'Successfully added image', 'id':props.video_id}
    except Exception as ex:
        return {'exception':str(ex)}

@get('/delete_video')
def delete_video():
    video_id = request.GET.get('video_id')

    video = verify_video_id(video_id)
    if type(video) == type({}): return video

    try:
        id = db.delete_video(video)
        return {'message':'Sucessfully deleted video', 'id':id}
    except Exception as ex:
        return {'exception':str(ex)}

@get('/get_video_source')
def get_video_source():
    video_id = request.GET.get('video_id', '')
    
    video = verify_video_id(video_id)
    if type(video) == type({}) : return video

    header = get_header(video)
    body = video.source

    return HTTPResponse(body.getvalue(), header = header)

    

@get('/')
def main():
    images = db.get_all_images()
    videos = db.get_all_videos()

    return template('client', context = {'images':images, 'videos':videos})
    


@get('/status')
def status():
    return {'status':'online', 'servertime':time.time()}

if __name__ == '__main__':    
    run(host = 'localhost', port = 8080)
    