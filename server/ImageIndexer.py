__author__ = "Daniel Garfield"

#this utilizes the Image class of PIL version 1.1.7, for list of dependencies see README
import Image
import ImageFilter
import math

class ImageIndexer(object):
    "open images from file and produce histogram and edgemap index for the image"
    def __init__(self, filename):        
        self.img = Image.open(filename)
        self.width = self.img.size[0]
        self.height = self.img.size[1]
        self.filename = filename

    def getImgInfo(self):
        print "format = %s, size = %s, mode = %s" %(self.img.format, self.img.size, self.img.mode)

    def makeGrayscale(self):
        if self.img.mode != "L":
            self.img = self.img.convert("L")
   
    def saveBands(self):
        "splits the RGB image into 3 images, 1 per band, saves splits images to cwd"
        if self.img.mode !="RGB":
            return
        data = self.img.getdata()
        r_data = [(0, 0, 0)]*(self.width*self.height)
        g_data = [(0, 0, 0)]*(self.width*self.height)
        b_data = [(0, 0, 0)]*(self.width*self.height)
        for i, value in enumerate(data):
            r_data[i] = (value[0], 0, 0)
            g_data[i] = (0, value[1], 0)
            b_data[i] = (0, 0, value[2])
        r_img = Image.new("RGB", self.img.size)
        r_img.putdata(r_data)
        r_img.save("red_band_of_"+self.filename, self.img.format)
        g_img = Image.new("RGB", self.img.size)
        g_img.putdata(g_data)
        g_img.save("green_band_of_"+self.filename, self.img.format)
        b_img = Image.new("RGB", self.img.size)
        b_img.putdata(b_data)
        b_img.save("blue_band_of_"+self.filename, self.img.format)
        return "ok"

    
    def makeHistogram(self, type="dict"):
        "returns a 16 bin histogram of the image, grayscale images return a single band hist, RGB returns a 3 band hist, by default returns a py dict, can also return a flat list if type parameter is set to list"
        vals_vector = list(self.img.getdata())
        if type=="list": #in list mode the object returned is a list of len 16 where each index of the list is one of the 16 bins. for grayscale images each bin contains a single int, for color images each bin contains a tuple (r, g, b). list mode may have higher performance then dict mode.
            if self.img.mode=="L":
                hist = [0]*16
                for value in vals_vector:
                    key = value/16
                    hist[key] += 1
                return hist
            if self.img.mode=="RGB":
                hist = [(0, 0, 0)]*16
                for value in vals_vector:
                    key_r = value[0]/16
                    key_g = value[1]/16
                    key_b = value[2]/16
                    tmp = hist[key_r]
                    tmp = (tmp[0]+1, tmp[1], tmp[2]) 
                    hist[key_r] = tmp
                    tmp = hist[key_g]
                    tmp = (tmp[0], tmp[1]+1, tmp[2])
                    hist[key_r] = tmp
                    tmp = hist[key_b]
                    tmp = (tmp[0], tmp[1], tmp[2]+1)
                    hist[key_b] = tmp
                return hist
            else:
                return "something broke in makeHistogram"
        else:  #in the default mode the object returned is a dictionary with 16 keys (0...15) as the bins. for grayscale images only one dictionary is returned. for color images a tuple of dictionaries is returned (hist_r, hist_g, hist_b)
            if self.img.mode =="L":
                hist = {}
                for value in vals_vector:
                    key = value/16
                    try:
                        hist[key] += 1
                    except KeyError:
                        hist[key] = 1
                return hist
            elif self.img.mode =="RGB":
                hist_r = {}
                hist_g = {}
                hist_b = {}
                for value in vals_vector:
                    key_r = value[0]/16
                    key_g = value[1]/16
                    key_b = value[2]/16
                    try:
                        hist_r[key_r] += 1
                        hist_g[key_g] += 1
                        hist_b[key_b] += 1
                    except KeyError:
                        hist_r[key_r] = 1
                        hist_g[key_g] = 1
                        hist_b[key_b] = 1
                return (hist_r, hist_g, hist_b)
            else:
                return "something broke in makeHistogram"

    def makeEdgeMap(self, thresh):
        "creates an edge map with single threshold filtering. edges are at minimum stronger then thresh"
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

        #edge_map.putdata(edge_map_data)
        #edge_map.save("edgemap_of_"+self.filename, self.img.format)

        edge_map.putdata(edge_map_data)
        self.edge_map = edge_map
        
        return "ok"

   
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
    
