__author__ = "Daniel Garfield"
__date__="$May 11, 2011 7:25:00PM$"

#this utilizes the Image class of PIL version 1.1.7, for list of dependencies see README
import Image
import ImageFilter #must not use ImageFilter.FIND_EDGES. must re-invent wheel. grrrr.
import math

#note to self: this should probably just be inheriting from the Image object and adding a couple of methods to it, maybe rewrite later
class ImageIndexer(object):
    "open images from file and produce histogram and edgemap index for the image"
    def __init__(self, filename):
        self.img = Image.open(filename)
        self.filename = filename

    def getImgInfo(self):
        print "format = %s, size = %s, mode = %s" %(self.img.format, self.img.size, self.img.mode)

    def makeGrayscale(self):
        if self.img.mode != "L":
            self.img = self.img.convert("L")

    def makeHistogram(self):
        "returns a 16 bin histogram of the image"
        hist = {}
        vals_vector = list(self.img.getdata())
        for value in vals_vector:
            key = value%16
            if key not in hist:
                hist[key] = 1
            else:
                hist[key] += 1
        return hist

    def makeEdgeMap(self, thresh):
        "creates an edge map with double threshold filtering. edges are at minimum stronger then thresh_low"
        #first denoise image with Gaussian filter then Sharpen to avoid fat edges
        temp_img = self.img.filter(ImageFilter.GaussianBlur)
        temp_img = self.img.filter(ImageFilter.SHARPEN)
        temp_img_data = list(temp_img.getdata())
        width = temp_img.size[0]
        height = temp_img.size[1]
        edge_map = Image.new(temp_img.mode, temp_img.size)
        edge_map_data = [0]*(width*height) #initialized to 0's, values will be altered as we go
        #second step is to detect strongest edges using the [-1,-1,-1,-1,8,-1,-1,-1,-1] kernel
        for rownum in range(1, height-1):
            for i in range(1, width-1):
                cur_mask = self.get_mask(temp_img_data, width, rownum, i)
                if self.is_edgepoint(cur_mask, thresh): 
                    edge_map_data[rownum*width + i] = cur_mask[4]
                else:
                    edge_map_data[rownum*width + i] = 0
        #finish up
        edge_map.putdata(edge_map_data)
        self.edge_map = edge_map
        #edge_map.save("edgemap_of_"+self.filename, self.img.format)
        

   
    def get_mask(self, img_data, width, rownum, i):
        "returns a flat 3x3 mask centered on pixel i"
        mask = [0]*9
        mask[0] = img_data[(rownum*width-1) + (i-1)]
        mask[1] = img_data[(rownum*width-1) + i]
        mask[2] = img_data[(rownum*width-1) + (i+1)]
        mask[3] = img_data[(rownum*width) + (i-1)]
        mask[4] = img_data[(rownum*width) + i]
        mask[5] = img_data[(rownum*width) + (i+1)]
        mask[6] = img_data[(rownum*width+1) + (i-1)]
        mask[7] = img_data[(rownum*width+1) + i]
        mask[8] = img_data[(rownum*width+1) + (i+1)]
        return mask

    def is_edgepoint(self, cur_mask, threshold):
        "returns true if the central point of the mask is sufficiently brighter then its surroundings"
        convolution = [-1, -1, -1, -1, 8, -1, -1, -1, -1]
        sum = 0
        for i in range(9):
            sum +=  convolution[i]*cur_mask[i]
        if sum > threshold:
            return True
        else:
            return False
    
