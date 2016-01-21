import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")

imgr = img[:,:,0]
imgg = img[:,:,1]
imgb = img[:,:,2]

img = 1/3*(imgr + imgg + imgb)

roll = 1
img1 = np.roll(img,roll,0) # right
img2 = np.roll(img,-roll,0) # left
img3 = np.roll(img,roll,1) # top
img4 = np.roll(img,-roll,1) # bottom

img5 = np.roll(img1,roll,1) # right top
img6 = np.roll(img1,-roll,1) # right bottom
img7 = np.roll(img2,roll,1) # left top
img8 = np.roll(img2,-roll,1) # left bottom

img = np.abs(
    img1 - img2 +
    img3 - img4 +
    img8 - img5 +
    img6 - img7
)

fig = plt.figure()
plot = plt.imshow(img,cmap = cm.Greys_r)
plt.show(block=True)
