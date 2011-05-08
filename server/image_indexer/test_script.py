import ImageIndexer

im = ImageIndexer.ImageIndexer("bridge.jpeg")
print "loaded test image with attributes: \n"
im.getImgInfo()
print "converting to grayscale, new attributes: \n"
im.makeGrayscale()
print im.getImgInfo()
print "making edgemap"
im.makeEdgeMap(50, 100)
