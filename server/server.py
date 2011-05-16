from bottle import route, run, get, post, request, HTTPResponse
import db as database
import mimetypes
import Image
import numpy

db = database.DB()

def verify_image_id(id):
    if image_id == '':
        return {'exception':"Expecting an image id got ''"}
    
    image = db.get_image(int(id))
    if len(image) == 0  : return {'exception':"There was no image with an id: "          + id}
    if len(image) >  1  : return {'exception':"There where multiple images with an id: " + id}

    return image[0]

# GET, DELETE AND UPDATE SINGLE IMAGE ##########################################
@post('/add_image')
def add_image():     
    filename    = request.forms.get('filename', '')
    source      = request.files.get('source', '')

    if filename == '': return {'exception':'(add_image)A file name is required! received ""'}
    if source == ''  : return {'exception':'(add_image)A file source is required!'}

    source      = source.file.read()
    title       = request.forms.get('title', '')
    description = request.forms.get('description', '')

    try:
        props = db.add_image(filename, source, title, description)
        return {'message':'Successfully added image.', 'id':props.image_id, 'keyword_count':props.keyword_count}
    except Exception as ex:
        return {'exception':str(ex)}


@post('/delete_image')
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
def update_image():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image

    filename    = request.forms.get('filename', '')        
    source      = source.file.read() if source != '' else ''
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


@get('/get_image_source')
def get_image_source():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image
        
    header = {}
    mimetype, encoding = mimetypes.guess_type(image.filename)
    body = image.source
    if mimetype: header['Content-Type'] = mimetype
    if encoding: header['Content-Encoding'] = encoding
    header['Content-Disposition'] = 'attachment; filename="%s"' % image.filename
    header['Content-Length'] = len(body)

    return HTTPResponse(body, header = header)


@get('/get_image_info')
def get_image_info():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image
    
    return {'id'            :image.id,
            'filename'      :image.filename,
            'title'         :image.title,
            'description'   :image.description,
            'size'          :len(image.source),
            'width'         :image.width,
            'height'        :image.height,
            'mode'          :image.mode,
            'format'        :image.format,
            'keywords'      :[keyword.keyword for keyword in image.keywords]}


@get('/get_image_edge_source')
def get_image_edge_source():
    image_id = request.GET.get('image_id', '')

    image = verify_image_id(image_id)
    if type(image) == type({}): return image

    header = {}
    mimetype, encoding = mimetypes.guess_type(image.filename)

    img = Image.new('L', (image.width, image.height))
    img.putdata(numpy.fromstring(image.edge_data, dtype = 'int'))
    body = StringIO.StringIO()
    img.save(body, image.format)

    if mimetype: header['Content-Type'] = mimetype
    if encoding: header['Content-Encoding'] = encoding
    header['Content-Disposition']   = 'attachment; filename="%s"' % 'edge_' + image.filename
    header['Content-Length']        = len(body.getvalue())

    return HTTPResponse(body.getvalue(), header = header)


@get('/get_all_images')
def get_all_images():
    images = db.get_all_images()
    return {'images':[{'id':image, 'filename':image.filename, 'title':image.title, 'description':image.description} for image in images]}
################################################################################

@post('/search_by_image')
def search_by_image():    
    source = request.files.get('source')

    if source == ''  : return {'exception':'(add_image)A file source is required!'}

    source      = source.file.read()

    try:
        images = search_by_image(source)
        return {'images':[{'id':image.id, 'filename':image.filename, 'title':image.tile, 'description':image.description} for image in images]}
    except Exception as ex:
        return {'exception':str(ex)}


@get('/search_by_keyword')
def search_by_keyword():
    keyword = request.GET.get('request.GET.get', '')

    if keyword == '':
        return get_all_images()

    try:
        results = db.search_by_keywords(keyword)

        return {'images':results['images'], 'videos':results['videos']}
    except Exception as ex:
        return {'exception':str(ex)}


if __name__ == '__main__':    
    run(host = 'localhost', port = 8080)
    