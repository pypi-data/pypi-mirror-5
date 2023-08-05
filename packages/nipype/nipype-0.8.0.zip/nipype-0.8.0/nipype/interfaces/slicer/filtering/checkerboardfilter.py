# -*- coding: utf8 -*- 
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os


class CheckerBoardFilterInputSpec(CommandLineInputSpec):
    checkerPattern = InputMultiPath(traits.Int, desc="The pattern of input 1 and input 2 in the output image. The user can specify the number of checkers in each dimension. A checkerPattern of 2,2,1 means that images will alternate in every other checker in the first two dimensions. The same pattern will be used in the 3rd dimension.", sep=",", argstr="--checkerPattern %s")
    inputVolume1 = File(position=-3, desc="First Input volume", exists=True, argstr="%s")
    inputVolume2 = File(position=-2, desc="Second Input volume", exists=True, argstr="%s")
    outputVolume = traits.Either(traits.Bool, File(), position=-1, hash_files=False, desc="Output filtered", argstr="%s")


class CheckerBoardFilterOutputSpec(TraitedSpec):
    outputVolume = File(position=-1, desc="Output filtered", exists=True)


class CheckerBoardFilter(SEMLikeCommandLine):
    """title: CheckerBoard Filter

category: Filtering

description: Create a checkerboard volume of two volumes. The output volume will show the two inputs alternating according to the user supplied checkerPattern. This filter is often used to compare the results of image registration. Note that the second input is resampled to the same origin, spacing and direction before it is composed with the first input. The scalar type of the output volume will be the same as the input image scalar type.

version: 0.1.0.$Revision: 19608 $(alpha)

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/CheckerBoard

contributor: Bill Lorensen (GE)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

"""

    input_spec = CheckerBoardFilterInputSpec
    output_spec = CheckerBoardFilterOutputSpec
    _cmd = "CheckerBoardFilter "
    _outputs_filenames = {'outputVolume':'outputVolume.nii'}
