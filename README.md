# python-playground

Here are scripts that simulate stuff and/or produce nice images. The goal is not to design interfaces so the UI/UX is bad and I like it like this.

# Contents

## pseudo-Physics

Physics without equations.

* a wave simulator
* particles with different properties

## Math

* Mandelbrot set explorer
* Julia set explorer
* weird 3d volumetric export of the Julia set

# Setup

You need these packages:

    python3 python3-pip python-imaging python3-tk tk8.5-dev tcl8.5-dev python3-scipy python3-cairo-dev

If you use debian (including ubuntu and stuff like that), just do this:

    sudo apt-get install python3 python-imaging python3-pip python3-tk tk8.5-dev tcl8.5-dev python3-scipy python3-cairo-dev

You also need to install some python packages:
  
    sudo pip-3.2 install Pillow PyEVTK

For some 3d things, like the 3d Julia set thing, maybe you will want to download mayavi2

    sudo apt-get install mayavi2

# Running code

    python3 the-script-name.py
