import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import math

# Put some pictures in images/ to test this

#img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")
img = np.asarray(npimg.imread("images/image-4.jpg"))
img = img.astype(float)

img = img/np.max(img)

# Get each channel
#imgr = img[:,:,0]
#imgg = img[:,:,1]
#imgb = img[:,:,2]

# grayscale
#img = 1/3*(imgr + imgg + imgb)

def show(image):
    plt.imshow(image,cmap=cm.Greys)
    plt.show()

image = img

width = image.shape[1]
height = image.shape[0]

def primitives(w,h):
    primitives = np.array([
        np.fromfunction(
            lambda i,j: ((i-h/2)**2+(j-w/2)**2)**(1/2) < w/2,
            (w,h)
        ),
        np.fromfunction(
            lambda i,j: i+j,
            (w,h)
        ),
        np.fromfunction(
            lambda i,j: h-i+w-j,
            (w,h)
        ),
        np.fromfunction(
            lambda i,j: i+w-j,
            (w,h)
        ),
        np.fromfunction(
            lambda i,j: h-i+j,
            (w,h)
        ),
        np.fromfunction(
            lambda i,j: ((i-h/2)**2+(j-w/2)**2)**(1/2),
            (w,h)
        )
    ])
    
    return primitives

primitives = primitives(400,400)

#for i in range(0,height):
    
show(primitives[0])
    
#show(image)
