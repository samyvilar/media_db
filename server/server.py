from bottle import route, run, get, post, request
import db as database


db = database.DB()

@post('/add_image')
def add_image():    
    filename    = request.forms.get('filename', '')
    source      = request.files.get('source', '')

    if filename == '':
        return {'exception':'A file name is required! received ""'}
    if source == '':
        return {'exception':'A source is required!'}

    source      = source.file.read()
    title       = request.forms.get('title', '')
    description = request.forms.get('description', '')

    try:
        db.add_image(filename, source, title, description)
    except Exception as ex:
        return {'exception':str(ex)}
    

@get('/search_by_keyword')
def search_by_keyword():
    keyword = request.GET.get('request.GET.get')

    try:
        results = db.search_by_keyword(keyword)

        return {'images':results['images'], 'videos':results['videos']}
    except Exception as ex:
        return {'exception':str(ex)}

@post('/search_by_image')
def search_by_image():
    filename = request.forms.get('filename', '')
    source = request.file.get('source')

    try:
        images = search_by_image(filename, source)
        return {'images':images}
    
if __name__ == '__main__':    
    run(host = 'localhost', port = 8080)
    