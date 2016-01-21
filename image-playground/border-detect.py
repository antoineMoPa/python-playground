import matplotlib.image as npimg
import matplotlib.pyplot as plt
import numpy as np

img = npimg.imread("images/image-2.png")

img1 = np.roll(img,2,0)
img2 = np.roll(img,-2,0)
img3 = np.roll(img,2,1)
img4 = np.roll(img,-2,1)


img = img1 - img2 + img3 - img4
plot = plt.imshow(img)
plt.show(block=True)
