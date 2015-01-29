# dep: (python2)
# apt-get install python2.6-dev python-pip
# pip-2.6 install pyevtk

import numpy as np
from mayavi import mlab

#mlab.options.offscreen = True
voxel = np.load("voxel.npy")
mlab.pipeline.volume(mlab.pipeline.scalar_field(voxel))
mlab.savefig("scene.png")
mlab.show_pipeline()
#imageToVTK("./image",cellData={"density":voxel})
