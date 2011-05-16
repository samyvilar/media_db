__author__="Daniel Garfield"

import ImageIndexer
import subprocess
import os

class VideoIndexer(object):
    "class used for indexing videos by breaking a video into distinct scenes and making thumbnails of those scenes"
    def __init__(self, filename):
        self.filename = filename
        self.vidinfo = self.getVidInfo()
        self.length = self.getLength()

    def getLength(self):
        "returns the length (in seconds) of a video"
        for field in self.vidinfo:
            if "LENGTH" in field:
                length = field.split("=")[1]
        return length

    def getVidInfo(self):
        "calls the midentify.sh script to generate a list of video attributes"
        proc_args = ["./midentify.sh", self.filename]
        proc = subprocess.Popen(proc_args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = proc.communicate()
        vidinfo = result[0].split("\n")
        return vidinfo

    def getFrame(self, time):
        "calls ffmpeg to generate a jpeg frame capture, then initialize an ImageIndexer on that frame and return it"
        #example command: ffmpeg -ss 1000 -i input.avi -vframes 1 output.jpeg
        file_title = self.filename.split(".")[0]
        cwd = os.getcwd()
        output_path = cwd+"/"+file_title+"_frames/"+file_title+"_time="+str(time)+".jpeg"
        try:
            #first of all, try to open the image to see if it already exists
            img = ImageIndexer.ImageIndexer(output_path)
            return img
        except IOError:
            #could not open image, so it doesn't exist and we need to create it
            try:
                #create directory if doesn't exist
                os.mkdir(cwd+"/"+file_title+"_frames")
            except OSError:
                pass
            #now make the frame
            proc_args = ["ffmpeg", "-ss", str(time), "-i", self.filename, "-vframes", "1", "-y", output_path]
            subprocess.check_call(proc_args, stderr=subprocess.PIPE)
            img = ImageIndexer.ImageIndexer(output_path)
            return img

    def makeThumbnails(self, start_time, stop_time, number_of_thumbnails):
        "makes thumbnails, evenly spaced between the time points given, inclusive of the endpoints, min thumbs is 3"
        if number_of_thumbnails < 3:
            thumbcount = 3
        else:
            thumbcount = number_of_thumbnails
        interval = abs(float(stop_time) - float(start_time))/float(thumbcount-1)
        for i in range(thumbcount):
            time = start_time + i*interval
            im = self.getFrame(time)
        return "ok"
 
    def dif_hist(self, img1, img2):
        "computes the difference between img1 and img2 using the 1 norm, normalized between 0 and 100. uses PIL histogram for speed"
        if img1.img.size != img2.img.size:
            return "error in dif_hist2, img1.img.size != img2.img.size"
        if img1.img.mode != img2.img.mode:
            return "error in dif_hist2, img1.img.mode != img2.img.mode"
        if img1.img.mode == "L":
            max_sum = 2*img1.height*img1.width
        elif img1.img.mode == "RGB":
            max_sum = 3*2*img1.height*img1.width
        hist1 = img1.img.histogram()
        hist2 = img2.img.histogram()
        if len(hist1) != len(hist2):
            return "error in dif_hist2, len(hist1) != len(hist2)"
        sum = 0
        for i in range(len(hist1)):
            sum += abs(hist1[i] - hist2[i])
        normalized_sum = (float(sum)/float(max_sum))*100
        return normalized_sum
    
    def sceneSearch(self, thresh):
        "returns a list of the  approximate start time of scenes based on a threshold (normalized between 0 and 100, takes floating point args), note: as a side effect this function generates a fairly substantial amount of frame capture jpegs from the video clip"
        #this is a bottom up implementation using loops
        scene_change_times = []
        window_size = 1.0
        window_start = 0.0
        window_end = window_start + window_size
        while(window_end < float(self.length) ):
            start_frame = self.getFrame(window_start)
            end_frame = self.getFrame(window_end)
            dif = self.dif_hist(start_frame, end_frame)
            if dif < thresh: #window is in same scene, double window size and check again in next loop
                window_size = window_size*2.0
                window_end = window_start + window_size
            else: #window found a scene boundary, record start of window and move window forward and reset for next loop
                scene_change_times.append(window_start)
                window_start = window_end
                window_size = 1.0
                window_end = window_start + window_size
        return scene_change_times

            
