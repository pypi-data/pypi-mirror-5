# -*- coding: utf8 -*- 
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os


class EMSegmentTransformToNewFormatInputSpec(CommandLineInputSpec):
    inputMRMLFileName = File(desc="Active MRML scene that contains EMSegment algorithm parameters in the format before 3.6.3 - please include absolute  file name in path.", exists=True, argstr="--inputMRMLFileName %s")
    outputMRMLFileName = traits.Either(traits.Bool, File(), hash_files=False, desc="Write out the MRML scene after transformation to format 3.6.3 has been made. - has to be in the same directory as the input MRML file due to Slicer Core bug  - please include absolute  file name in path ", argstr="--outputMRMLFileName %s")
    templateFlag = traits.Bool(desc="Set to true if the transformed mrml file should be used as template file ", argstr="--templateFlag ")


class EMSegmentTransformToNewFormatOutputSpec(TraitedSpec):
    outputMRMLFileName = File(desc="Write out the MRML scene after transformation to format 3.6.3 has been made. - has to be in the same directory as the input MRML file due to Slicer Core bug  - please include absolute  file name in path ", exists=True)


class EMSegmentTransformToNewFormat(SEMLikeCommandLine):
    """title: 
  Transform MRML Files to New EMSegmenter Standard
  

category: 
  Utilities
  

description: 
  Transform MRML Files to New EMSegmenter Standard
  

"""

    input_spec = EMSegmentTransformToNewFormatInputSpec
    output_spec = EMSegmentTransformToNewFormatOutputSpec
    _cmd = "EMSegmentTransformToNewFormat "
    _outputs_filenames = {'outputMRMLFileName':'outputMRMLFileName.mrml'}
