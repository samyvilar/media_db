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

    def makeEdgeMap(self, thresh_low, thresh_high):
        "returns an edge map found by Canny edge detection"
        #first denoise image with Gaussian filter and then crop image to appropriate size for 3x3 mask processing
        temp_img = self.img.filter(ImageFilter.BLUR) 
        temp_img = self.crop_img(temp_img, 3)
        temp_img_data = list(temp_img.getdata())
        width = temp_img.size[0]
        height = temp_img.size[1]
        edge_map = Image.new(temp_img.mode, temp_img.size)
        edge_map_data = [0]*(width*height) #initialized to 0's, values will be altered as we go
        #second step is to apply non-maximum suppression using a flat 3x3 mask
        for rownum in range(1, height, 3):
            for i in range(1, width, 3):
                cur_mask = self.get_mask(temp_img_data, width, rownum, i)
                grad_x = self.get_x_gradient(cur_mask)
                grad_y = self.get_y_gradient(cur_mask)
                edge_strength = int(math.sqrt(grad_x*grad_x + grad_y*grad_y))
                if edge_strength > 255:
                    edge_strength = 255
                edge_direction_angle = math.degrees(math.atan2(grad_y, grad_x))
                #initial filtering pass rejects very weak edges only (will fill the mask with 0's), 
                #if strength is above threshold fill edge values only with maximum value in cur_mask and suppress all other pixels to 0
                if edge_strength < thresh_low:
                    edge_mask = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                else:
                    edge_mask = self.generate_edge_mask(cur_mask, edge_direction_angle)
                #admittedly, this is fuckin hideous. will probably refactor much of this later to avoid such ugliness
                edge_map_data[(rownum*width-1) + (i-1)] = edge_mask[0]
                edge_map_data[(rownum*width-1) + i] = edge_mask[1]
                edge_map_data[(rownum*width-1) + (i+1)] = edge_mask[2]
                edge_map_data[(rownum*width) + (i-1)] = edge_mask[3]
                edge_map_data[(rownum*width) + i] = edge_mask[4]
                edge_map_data[(rownum*width) + (i+1)] = edge_mask[5]
                edge_map_data[(rownum*width+1) + (i-1)] = edge_mask[6]
                edge_map_data[(rownum*width+1) + i] = edge_mask[7]
                edge_map_data[(rownum*width+1) + (i+1)] = edge_mask[8]


        #third step is double threshold hysteresis
        #hysteresis(low, high, abra_cadabra, pixie_dust)
        #finish up
        edge_map.putdata(edge_map_data)
        edge_map.save("edgemap_of_"+self.filename, self.img.format)
        return "ok"

    def crop_img(self, img, n):
        "crops an image so that its width and height are multiples of n, note: this causes a small amount of data loss as the cropped image is slightly smaller"
        width = img.size[0]
        height = img.size[1]
        new_width = width - width%n
        new_height = height - height%n
        cropped_img = Image.new(img.mode, (new_width, new_height))
        cropped_img = img.crop((0, 0, new_width, new_height))
        return cropped_img

    def get_mask(self, img_data, width, rownum, i):
        "returns a 3x3 mask centered on pixel i"
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

    def get_x_gradient(self, mask):
        "gets the scalar gradient with respect to X direction of the 3x3 mask using the Sobel Operator"
        grad_matrix = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
        sum = 0
        for i in range(9):
            sum += mask[i]*grad_matrix[i]
        return sum

    def get_y_gradient(self, mask):
        "gets the scalar gradient with respect to Y direction of the 3x3 mask using the Sobel Operator"
        grad_matrix = [1, 2, 1, 0, 0, 0, -1, -2, -1]
        sum = 0
        for i in range(9):
            sum += mask[i]*grad_matrix[i]
        return sum

    def get_angle_mask(self, angle):
        "gets the flat 3x3 edge mask that corresponds to the given angle"
        #there are 4 possible masks that can be given here, based on angle
        #they are: up<->down, left<->right, top-left<->bottom-right, top-right<->bottom-left
        if (-22.5 < angle <= 22.5) or (157.5 < angle <= 180) or (-157.5 >= angle >= -180):
            angle_mask = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        if (22.5 < angle <= 67.5) or (-112.5 >= angle > -157.5):
            angle_mask = [0, 0, 1, 0, 1, 0, 1, 0, 0]
        if (67.5 < angle <= 112.5) or (-67.5 >= angle > -112.5):
            angle_mask = [0, 1, 0, 0, 1, 0, 0, 1, 0]
        if (112.5 < angle <= 157.5) or (-22.5 >= angle > -67.5):
            angle_mask = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        return angle_mask

    def get_max(self, lst):
        "returns the value of the largest element in the list, note, must be iterable object with > defined"
        max = 0
        for i in range(len(lst)):
            if lst[i] > max:
                max = lst[i]
        return max

    def generate_edge_mask(self, cur_mask, angle):
        "returns the flat 3x3 mask with the appropriate angle selected and non-maximum suppression applied"
        max = self.get_max(cur_mask)
        edge_mask = self.get_angle_mask(angle)
        for i in range(len(edge_mask)):
            edge_mask[i] = edge_mask[i]*max
        return edge_mask
         


        







