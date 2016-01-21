import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Put some pictures in images/ to test this

#img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")
img = npimg.imread("images/image-3.jpg")

# Get each channel
imgr = img[:,:,0]
imgg = img[:,:,1]
imgb = img[:,:,2]

# grayscale
imggrey = 1/3*(imgr + imgg + imgb)


def edgedetect(input_img):
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

    # Subtract opposed translations
    image_edge = np.abs(
        image1 - image2 +
        image3 - image4 +
        image8 - image5 +
        image6 - image7
    )
    return image_edge

# We can also use only the
# R,g or b channel (imgr,imgg,imgb)
edge = edgedetect(imggrey)

# We'll keep the original image
# and create one with edges over it
display = np.copy(img)

# Make this image less contrasted
# so we can see the edges
display[:,:,:] *= 0.5
display[:,:,:] += 0.5

# Add the edges to the image
display[:,:,0] += edge
display[:,:,1] += edge
display[:,:,2] += edge

fig = plt.figure()

# Image
plt.subplot(311)
plt.imshow(img)

# Image with edges
plt.subplot(312)
plt.imshow(display)

# Only edges
plt.subplot(313)
plt.imshow(edge,cmap = cm.Greys_r)
plt.show(block=True)
