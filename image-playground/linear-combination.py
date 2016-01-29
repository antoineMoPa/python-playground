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
img = 1/3*(imgr + imgg + imgb)

img /= np.max(img)

def show(image):
    plt.imshow(image,cmap=cm.Greys_r)
    plt.show()

grid_size = 80
    
part = np.empty(img.shape)

max_steps = 2
coefficients = np.empty((grid_size,grid_size,max_steps))

cell_width = img.shape[1] / grid_size
cell_height = img.shape[0] / grid_size

for a in range(0,grid_size):
    for b in range(0,grid_size):
        sub_img = img[
            a * cell_height:(a + 1) * cell_height,
            b * cell_width:(b + 1) * cell_width
        ]
        part = np.empty(sub_img.shape)
        for step in range(1,max_steps,1):
            k = step ** 2
            w = sub_img.shape[1]/k
            h = sub_img.shape[0]/k
            for j in range(0, k):
                for i in range(0, k):
                    if (i + j) % 2 == 0:
                        part[j * h:(j+1)*h,i * w:(i+1)*w] = 1
                    else:
                        part[j * h:(j+1)*h,i * w:(i+1)*w] = -1
                    coefficients[a,b,step] = np.sum(part * sub_img)
                        

final = np.zeros(img.shape)

#coefficients = coefficients / np.max(coefficients)

for a in range(0,grid_size):
    for b in range(0,grid_size):
        sub_img = img[
                a * cell_height:(a + 1) * cell_height,
                b * cell_width:(b + 1) * cell_width
            ]
        part = np.empty(sub_img.shape)
        for step in range(1,max_steps,1):
            k = step ** 30
            w = sub_img.shape[1]/k
            h = sub_img.shape[0]/k
            for j in range(0, k):
                for i in range(0, k):
                    if (i + j) % 2 == 0:
                        part[j * h:(j+1)*h,i * w:(i+1)*w] = 1
                    else:
                        part[j * h:(j+1)*h,i * w:(i+1)*w] = -1
                        
            final[
                a * cell_height:(a + 1) * cell_height,
                b * cell_width:(b + 1) * cell_width
            ] += coefficients[a,b,step] * part


show(final)
