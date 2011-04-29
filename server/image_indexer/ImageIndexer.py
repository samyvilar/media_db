#this utilizes the Image class of PIL version 1.1.7, for list of dependencies see README
import Image

#note to self: this should probably just be inheriting from the Image object and adding a couple of methods to it, maybe rewrite later
class ImageIndexer(object):
    "open images from file and produce histogram and edgemap index for the image"
    def __init__(self, filename):
        self.img = Image.open(filename)
    def getImgInfo(self):
        print "format = %s, size = %s, mode = %s" %(self.img.format, self.img.size, self.img.mode)
    def makeGrayscale(self):
        if self.img.mode != "L":
            self.img = self.img.convert("L")
    def makeHistogram(self):
        hist = {}
        vals_vector = list(self.img.getdata())
        for value in vals_vector:
            key = value%16
            if key not in hist:
                hist[key] = 1
            else:
                hist[key] += 1
        return hist




