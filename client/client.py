import urllib
import urllib2
import httplib, mimetypes

def post_multipart(host, selector, fields, files):
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    headers = {
        'User-Agent': 'INSERT USERAGENTNAME',
        'Content-Type': content_type
        }
    h.request('POST', selector, body, headers)
    res = h.getresponse()
    return res.status, res.reason, res.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'



class MediaDBClient(object):
    server  = 'http://localhost:8080/server'

    def isServerAlive(self):
        try:
            return urllib2.urlopen("http://localhost:8080/server",
                data = urllib.urlencode({'action':'getstatus'})).read() == "OK"
        except urllib2.URLError:
            return False

    def addImage(self, name, content):
        data = urllib.urlencode({'action':'addimage', 'name':name})
        length = len(content)
        request = urllib2.Request(url, data=png_data)

        

