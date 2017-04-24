import numpy as np
import math

from PIL import Image

size = 540;

# nabla (or del operator)
# in this function, we approximate nabla(u)
# by looking at the neighbor pixels
# in the y and x axis.
# To do this, we roll the matrix by increments
# of +/-1 in the x and y axis. We then find
# dx and dy by substracting the matrices
def nabla(u):
    out = np.zeros([size, size, 2])

    # roll the matrices in every needed direction
    rollxp = np.roll(u, 1, axis=0)
    rollxn = np.roll(u, -1, axis=0)
    rollyp = np.roll(u, 1, axis=1)
    rollyn = np.roll(u, -1, axis=1)
    # TODO: verify and use with 0.707 factor
    #rolld1p = np.roll(rollxp, 1, axis=1)
    #rolld1n = np.roll(rollxn, -1, axis=1)
    #rolld2p = np.roll(rollxp, 1, axis=0)
    #rolld2n = np.roll(rollxn, -1, axis=0)

    dx = -np.subtract(rollxp, rollxn)
    dy = np.subtract(rollyp, rollyn)

    out[:,:,0] += dx[:,:,0]
    out[:,:,1] += dy[:,:,1]
    
    return out

# Pacman clamp: makes sure
# a number is between 0 and max
# The method is analogous to the way
# pacman returns to the left side
# when it goes through the border of
# the screen at the right side
def pacman_clamp(num, max):
    ret = num

    if(ret < 0):
        ret += max
    elif(ret > max):
        ret -= max

    ret = ret % max
    
    if(math.isnan(ret)):
        ret = np.random.uniform(0, max)
        
    return ret

# Number of particles we will use
partnum=13000
# Particles array
# (x,y) coordinates, repeat for 'partnum' times
parts = np.random.uniform(size=(partnum, 2)) * size

#u = np.random.uniform(size=(size, size, 2)) - 0.5
# Flow field
u = np.zeros((size, size, 2))
# divergence of the flow
du = np.zeros([size, size, 2])
# environment map
env = np.zeros([size, size])

# We don't use this for now
w = np.zeros([size, size, 2])
g = np.zeros([size, size, 2])

# Distance between 2 points
def distance(x1, y1, x2, y2):
    d = math.sqrt(math.pow(x2 - x1, 2.0) + math.pow(y2 - y1 ,2.0))
    return d

# Create environment
for i in range(0, size):
    for j in range(0, size):
        d = distance(i, j, size/2, size/2)
        if(d < size*0.45):
            env[i,j] = 1
        if(distance(i,j,size/2,size/3) < 20):
            env[i,j] = 0    

# Creates a rotating flow at xx, yy
# direction is either 1 of -1
# (clockwise vs counterclockwise)
def swirl(xx, yy, direction):
    for i in range(0,size):
        for j in range(0,size):
            x = i / size - 0.5 - xx
            y = j / size - 0.5 - yy
            
            d = distance(x, y, 0.0, 0.0)

            if(d < 0.4 or direction < 8):
                u[i,j,0] += direction * -y
                u[i,j,1] += direction * x
                
            #if(x < 0.05 and x > -0.05):
            #    u[i,j,1] += 0.4

# Add some initial flow
swirl(0.0, 0.0, 7.0)

# If we wanted to set flow for some pixels
#for i in range(200,210):
#    for j in range(200,300):
#        u[i,j,1] = 1

# This matrix will contain the image's data
# (note the type: uint8)
im = np.array(np.zeros([size, size, 3]), dtype=np.uint8)

# Number of frames we will render
image_qty=1200

for img_num in range(0, image_qty):
    # Number of sub steps
    subframes = 40

    # Perfom sub frame computation
    # (which calculates 'du', and updates 'u' accordingly)
    for sub_it in range(0, subframes):
        # Viscosity
        v=0.4
        # Compute du
        nu = nabla(u)
        nnu = nabla(nu)
        du = v * nnu - u * nu
        du *= 0.002
        # Add to u
        u += du
        u[:,:,0] *= env
        u[:,:,1] *= env

    # Draw particles
    # and update their position according to flow
    for i in range(0, len(parts)):
        # Clamp (manage borders)
        parts[i,0] = pacman_clamp(parts[i,0], size)
        parts[i,1] = pacman_clamp(parts[i,1], size)
            
        x = math.floor(parts[i,0])
        y = math.floor(parts[i,1])

        # Draw point at current position
        im[x,y,:] += 1.0
        
        # Update position
        parts[i,0] = (parts[i,0] + u[x,y,0])
        parts[i,1] = (parts[i,1] + u[x,y,1])

    im[:,:,0] *= env
    im[:,:,1] *= env
    im[:,:,2] *= env
    im[:,:,:] *= 255
    # Uncomment to view flow encoded in green and blue
    #im[:,:,1] += (u[:,:,0] * 20.0 + 20.0).clip(0,255).astype('uint8')
    #im[:,:,2] += (u[:,:,1] * 20.0 + 20.0).clip(0,255).astype('uint8')
        
    img = Image.fromarray(im, 'RGB')
    im *= 0.0

    # Save image
    img.save('%04d.png' % img_num)
    # Print progress
    print("done %d of %d" % (img_num, image_qty))
