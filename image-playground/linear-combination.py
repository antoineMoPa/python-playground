import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Put some pictures in images/ to test this

#img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")
img = npimg.imread("images/image-4.jpg")

# Get each channel
imgr = img[:,:,0]
imgg = img[:,:,1]
imgb = img[:,:,2]

# grayscale
image = 1/3*(imgr + imgg + imgb)

image /= np.max(image)

k = 4

def show(image):
    plt.imshow(image,cmap=cm.Greys_r)
    plt.show()

part = np.empty(img.shape)

w = img.shape[1]/k
h = img.shape[0]/k

coefficients = np.empty((5))

for k in range(2,4):
    part = np.empty(img.shape)
    for j in range(0, k):
        for i in range(0, k):
            if (i + j) % 2 == 0:
                part[j * h:(j+1)*h,i * w:(i+1)*w] = -1
            else:
                part[j * h:(j+1)*h,i * w:(i+1)*w] = -1

    coefficients[k] = np.sum(part * img)
    show(part * img)

