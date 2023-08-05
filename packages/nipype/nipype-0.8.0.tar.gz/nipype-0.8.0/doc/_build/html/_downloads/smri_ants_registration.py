#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
==================================
sMRI: Using ANTS for registration
==================================

In this simple tutorial we will use the Registration interface from ANTS to
coregister two T1 volumes.

1. Tell python where to find the appropriate functions.
"""

import os
import urllib2
from nipype.interfaces.ants import Registration

"""
2. Download T1 volumes into home directory
"""

homeDir=os.getenv("HOME")
requestedPath=os.path.join(homeDir,'nipypeTestPath')
mydatadir=os.path.realpath(requestedPath)
if not os.path.exists(mydatadir):
    os.makedirs(mydatadir)
print mydatadir

MyFileURLs=[
           ('http://slicer.kitware.com/midas3/download?bitstream=13121','01_T1_half.nii.gz'),
           ('http://slicer.kitware.com/midas3/download?bitstream=13122','02_T1_half.nii.gz'),
           ]
for tt in MyFileURLs:
    myURL=tt[0]
    localFilename=os.path.join(mydatadir,tt[1])
    if not os.path.exists(localFilename):
        remotefile = urllib2.urlopen(myURL)

        localFile = open(localFilename, 'wb')
        localFile.write(remotefile.read())
        localFile.close()
        print("Downloaded file: {0}".format(localFilename))
    else:
        print("File previously downloaded {0}".format(localFilename))

input_images=[
os.path.join(mydatadir,'01_T1_half.nii.gz'),
os.path.join(mydatadir,'02_T1_half.nii.gz'),
]

"""
3. Define the parameters of the registration
"""

reg = Registration()
reg.inputs.fixed_image =  input_images[0]
reg.inputs.moving_image = input_images[1]
reg.inputs.output_transform_prefix = 'thisTransform'
reg.inputs.output_warped_image = 'INTERNAL_WARPED.nii.gz'

reg.inputs.transforms = ['Translation', 'Rigid', 'Affine', 'SyN']
reg.inputs.transform_parameters = [(0.1,), (0.1,), (0.1,), (0.3, 3.0, 0.0)]
reg.inputs.number_of_iterations = [[10000, 0, 0], [10000, 0, 0], [10000, 0, 0], [10, 0, 0]]
reg.inputs.dimension = 3
reg.inputs.write_composite_transform = True
reg.inputs.collapse_output_transforms = True
reg.inputs.metric = ['Mattes']*4
reg.inputs.metric_weight = [1]*4 # Default (value ignored currently by ANTs)
reg.inputs.radius_or_number_of_bins = [32]*4
reg.inputs.sampling_strategy = ['Regular']*3 + [None]
reg.inputs.sampling_percentage = [0.1]*3 + [None]
reg.inputs.convergence_threshold = [1.e-8]*4
reg.inputs.convergence_window_size = [20]*4
reg.inputs.smoothing_sigmas = [[4,2,1]]*3 + [[2,1,0]]
reg.inputs.sigma_units = ['vox']*4
reg.inputs.shrink_factors = [[6,4,2]]*3 + [[4,2,1]]
reg.inputs.use_estimate_learning_rate_once = [True, True, True, True]
reg.inputs.use_histogram_matching = [False]*3 + [True] # This is the default
reg.inputs.initial_moving_transform_com = True
reg.inputs.output_warped_image = True
reg.cmdline


"""
3. Run the registration
"""

reg.run()
