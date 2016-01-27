import matplotlib.image as npimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Put some pictures in images/ to test this

img = npimg.imread("images/image-1.jpg")
#img = npimg.imread("images/image-2.png")
#img = npimg.imread("images/image-3.jpg")

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
        0.25 * (image8 - image5 +
        image6 - image7)
    )
    return image_edge

def grow(image):
    image1 = np.roll(image,1,0)
    image2 = np.roll(image,-1,0)
    image3 = np.roll(image,1,1)
    image4 = np.roll(image,-1,1)
    
    image = image + image1 + image2 + image3 + image4
    return image

def normalize(image):
    image /= np.max(image)
    return image

def show(image):
    plt.imshow(image,cmap = cm.Greys_r)
    plt.show(block=True)

# We can also use only the
# R,g or b channel (imgr,imgg,imgb)
edge = edgedetect(imggrey)
edge = normalize(edge)

edge = grow(edge)

# We can also use only the
# R,g or b channel (imgr,imgg,imgb)
edge = edgedetect(imggrey)

edge_points = edge > 0.8


def points_to_line(points):
    height = points.shape[0]
    width = points.shape[1]
    
    edge_y_sum = np.sum(points,axis=1)
    
    # Create 2 groups to find 2 points
    # to perform simple linear regression
    group1, group2 = np.split(edge_y_sum,2)
    
    half = len(group1)
    
    # Average x
    x_1 = half/2
    x_2 = 1.5 * half
    
    # Average y
    y_1 = np.sum(group1)/half
    y_2 = np.sum(group2)/half
    
    delta_y = (y_2 - y_1)
    delta_x = (x_2 - x_1)
    
    m = delta_y / delta_x
    
    # y = mx + b -> b = y - mx
    b = y_1 - m * x_1
    
    line = m * np.linspace(0,100,10) + b
        
    return m, b

fig = plt.figure()
plt.subplot(211)

plt.xlim(0,edge.shape[1])
plt.ylim(0,edge.shape[0])

m,b = points_to_line(edge_points)
    
# stackoverflow.com/questions/17990845
plt.gca().set_aspect('equal', adjustable='box')
x_axis = np.linspace(0,edge.shape[1])
plt.plot(x_axis, m * x_axis + b)

plt.subplot(212)
plt.imshow(img)

plt.show();
