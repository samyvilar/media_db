# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="samyvilar"
__date__ ="$May 9, 2011 11:30:30 PM$"

import Image
import ImageFilter
import numpy
import StringIO
import os.path

class ImageProc(object):    
    edge        = None
    histogram   = None
    img         = None
    
    def __init__(self, source = None, stype = 'file'):
        if source == None:
            pass
        elif stype == 'file':
            assert os.path.isfile(source)
            self.img = Image.open(source)
        elif stype == 'string':
            assert stype == type('')
            self.img = Image.open(StringIO.StringIO(source))
        else:
            raise Exception("I was expecting a type either 'file' or 'string' not " + str(stype))

        if self.img:
            self.img = self.img.convert("L")
            self.histogram = numpy.zeros(16)
            for value in self.img.getdata():
                self.histogram[value % 16] = self.histogram[value % 16] + 1
            width, height = self.img.size
            self.edge = self.edge(list(self.img.filter(ImageFilter.GaussianBlur).getdata()), width, height)

    def edge(self, pixels, width, height):
        outimg = Image.new('L', (width, height))
        outpixels = list(outimg.getdata())
        kernel = [  -1, -1, -1,
                    -1,  8, -1,
                    -1, -1, -1  ]
        for y in xrange(1, height - 1):
            for x in xrange(1, width  - 1):
                sum = pixels[x-1+(y+1)*width]   * kernel[0] + pixels[x+(y+1)*width] * kernel[1] + pixels[x+1+(y+1)*width]   * kernel[2] + \
                      pixels[x-1+y*width]       * kernel[3] + pixels[x+y*width]     * kernel[4] + pixels[x+1+y*width]       * kernel[5] + \
                      pixels[x-1+(y-1)*width]   * kernel[6] + pixels[x+(y-1)*width] * kernel[7] + pixels[x+1+(y-1)*width]   * kernel[8]
                if sum <= 0:
                    outpixels[x+y*width] = 0
                elif sum >= 255:
                    outpixels[x+y*width] = 255
                else:
                    outpixels[x+y*width] = sum
        outimg.putdata(outpixels)
        return outimg
