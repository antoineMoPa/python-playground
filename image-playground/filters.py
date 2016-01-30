import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import math

# Put some pictures in images/ to test this

#img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")

img = npimg.imread("images/image-4.jpg")
img = np.asarray(img).astype(float)

img = img/np.max(img)

def show(img):
    plt.imshow(img)
    plt.show()

def vignette(img):
    h = img.shape[0]/2
    w = img.shape[1]/2
    fct = lambda i,j,k: np.sqrt(np.power(i-h,2)+np.power((j-w),2))
    dists = np.fromfunction(fct,img.shape)
    dists = 1 - dists / np.max(dists)
    img = img * dists
    return img

img = vignette(img)
show(img)
