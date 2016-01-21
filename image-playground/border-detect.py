import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

#img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")
img = npimg.imread("images/image-3.jpg")

imgr = img[:,:,0]
imgg = img[:,:,1]
imgb = img[:,:,2]

imggrey = 1/3*(imgr + imgg + imgb)

def borderdetect(input_img):
    image = np.copy(input_img)
    roll = 1
    # We move the image 1px in every direction
    # and keep a copy
    image1 = np.roll(image,roll,0) # right
    image2 = np.roll(image,-roll,0) # left
    image3 = np.roll(image,roll,1) # top
    image4 = np.roll(image,-roll,1) # bottom
    
    image5 = np.roll(image1,roll,1) # right top
    image6 = np.roll(image1,-roll,1) # right bottom
    image7 = np.roll(image2,roll,1) # left top
    image8 = np.roll(image2,-roll,1) # left bottom
    
    image_border = np.abs(
        image1 - image2 +
        image3 - image4 +
        image8 - image5 +
        image6 - image7
    )
    return image_border


border = borderdetect(imggrey)
border = border
display = np.copy(img)

display[:,:,:] *= 0.5

border_weight = 1

display[:,:,0] += border_weight * border
display[:,:,1] += border_weight * border
display[:,:,2] += border_weight * border

fig = plt.figure()
plt.subplot(311)
plt.imshow(img)
plt.subplot(312)
plt.imshow(display)
plt.subplot(313)
plt.imshow(border,cmap = cm.Greys_r)
plt.show(block=True)
