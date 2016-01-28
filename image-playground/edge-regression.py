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

edge_points = edge > 0.3

def points_to_line(points):
    points = points.astype(int)
    height = points.shape[0]
    width = points.shape[1]

    if(width % 2 == 1):
        width = width-1
        points = points[:,:width]
        
    xs = np.arange(0,width/2,1).reshape(1,width/2)
    ys = np.arange(0,height,1).reshape((height,1))

    pointsa = points[:,0:width/2]
    pointsb = points[:,width/2:width]

    num_a = np.sum(pointsa)
    num_b = np.sum(pointsb)

    x_a = 0
    y_a = 0
    m = 0
    b = 0
    
    strength = np.sum(points)
    
    if(num_a == 0 or num_b == 0):
        m = 0
    else:
        x_a = np.sum(pointsa*xs)/num_a
        x_b = np.sum(pointsb*(xs + width/2))/num_b
        y_a = np.sum(pointsa*ys)/num_a
        y_b = np.sum(pointsb*ys)/num_b
        deltay = y_b - y_a
        deltax = x_b - x_a

        if(deltay == 0):
            m = 0
        else:
            m = deltay / deltax
            b = y_a - m * x_a

    # to test this part, uncomment this
    #if(strength > 2):
    #    plt.imshow(points)
    #    xs = np.linspace(0,width)
    #    plt.ylim(0,height)
    #    plt.xlim(0,width)
    #    plt.plot(xs,np.clip(m*xs+b,0,height))
    #    plt.show()

    return m, b, strength

# separate image
width = edge_points.shape[1]
height = edge_points.shape[0]

num = 10
cell_width = width/num
cell_height = height/num

lines = np.empty([num,num,7])

for j in range(0,num):
    for i in range(0,num):
        start_x = j * cell_width
        end_x = (j+1) * cell_width
        start_y = i * cell_height
        end_y = (i+1) * cell_height
        m,b,strength = points_to_line(
            edge_points
            [
                int(start_y):int(end_y),
                int(start_x):int(end_x)
            ]
        )

        lines[i,j,0] = m
        lines[i,j,1] = b
        lines[i,j,2] = strength


strength = strength / np.max(strength)
        
fig = plt.figure()
plt.subplot(131)
plt.imshow(edge_points,cmap = cm.Greys_r)
plt.xlim(0,width)
plt.ylim(height,0)

# stackoverflow.com/questions/17990845
plt.gca().set_aspect('equal', adjustable='box')

for i in range(0,num):
    for j in range(0,num):
        line = lines[i,j]
        start_x = j * cell_width
        end_x = (j+1) * cell_width
        start_y = i * cell_height
        end_y = (i+1) * cell_height

        # min strength
        if(line[2] < 0.5):
            continue
        
        x_axis = np.linspace(0,cell_width)

        m = line[0]
        b = line[1]
        
        plt.plot(
            x_axis+start_x,
            m * x_axis + b + start_y
        )

plt.grid()

plt.subplot(132)
plt.imshow(img)

plt.subplot(133)
plt.imshow(edge_points,cmap=cm.Greys_r)

plt.show();
