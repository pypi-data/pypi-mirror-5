.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.spm.utils
====================


.. _nipype.interfaces.spm.utils.Analyze2nii:


.. index:: Analyze2nii

Analyze2nii
-----------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/spm/utils.py#L19>`__

Inputs::

        [Mandatory]
        analyze_file: (an existing file name)

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        nifti_file: (an existing file name)
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

.. _nipype.interfaces.spm.utils.ApplyInverseDeformation:


.. index:: ApplyInverseDeformation

ApplyInverseDeformation
-----------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/spm/utils.py#L250>`__

Uses spm to apply inverse deformation stored in a .mat file or a
deformation field to a given file

Examples
~~~~~~~~

>>> import nipype.interfaces.spm.utils as spmu
>>> inv = spmu.ApplyInverseDeformation()
>>> inv.inputs.in_files = 'functional.nii'
>>> inv.inputs.deformation = 'struct_to_func.mat'
>>> inv.inputs.target = 'structural.nii'
>>> inv.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                Files on which deformation is applied

        [Optional]
        bounding_box: (a list of from 6 to 6 items which are a float)
                6-element list (opt)
        deformation: (an existing file name)
                SN SPM deformation file
                mutually_exclusive: deformation_field
        deformation_field: (an existing file name)
                SN SPM deformation file
                mutually_exclusive: deformation
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interpolation: (an integer >= 0)
                degree of b-spline used for interpolation
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        target: (an existing file name)
                File defining target space
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        voxel_sizes: (a list of from 3 to 3 items which are a float)
                3-element list (opt)

Outputs::

        out_files: (an existing file name)
                Transformed files

.. _nipype.interfaces.spm.utils.ApplyTransform:


.. index:: ApplyTransform

ApplyTransform
--------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/spm/utils.py#L130>`__

Uses spm to apply transform stored in a .mat file to given file

Examples
~~~~~~~~

>>> import nipype.interfaces.spm.utils as spmu
>>> applymat = spmu.ApplyTransform(matlab_cmd='matlab-spm8')
>>> applymat.inputs.in_file = 'functional.nii'
>>> applymat.inputs.mat = 'func_to_struct.mat'
>>> applymat.run() # doctest: +SKIP

.. warning::

   CHANGES YOUR INPUT FILE (applies transform by updating the header)
   except when used with nipype caching or workflow.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                file to apply transform to, (only updates header)
        mat: (an existing file name)
                file holding transform to apply

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        out_file: (an existing file name)
                File with updated header

.. _nipype.interfaces.spm.utils.CalcCoregAffine:


.. index:: CalcCoregAffine

CalcCoregAffine
---------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/spm/utils.py#L53>`__

Uses SPM (spm_coreg) to calculate the transform mapping
moving to target. Saves Transform in mat (matlab binary file)
Also saves inverse transform

Examples
~~~~~~~~

>>> import nipype.interfaces.spm.utils as spmu
>>> coreg = spmu.CalcCoregAffine(matlab_cmd='matlab-spm8')
>>> coreg.inputs.target = 'structural.nii'
>>> coreg.inputs.moving = 'functional.nii'
>>> coreg.inputs.mat = 'func_to_struct.mat'
>>> coreg.run() # doctest: +SKIP

.. note::

 * the output file mat is saves as a matlab binary file
 * calculating the transforms does NOT change either input image
   it does not **move** the moving image, only calculates the transform
   that can be used to move it

Inputs::

        [Mandatory]
        moving: (an existing file name)
                volume transform can be applied to register with target
        target: (an existing file name)
                target for generating affine transform

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        invmat: (a file name)
                Filename used to store inverse affine matrix
        mat: (a file name)
                Filename used to store affine matrix
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        invmat: (a file name)
                Matlab file holding inverse transform
        mat: (an existing file name)
                Matlab file holding transform

.. _nipype.interfaces.spm.utils.Reslice:


.. index:: Reslice

Reslice
-------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/spm/utils.py#L182>`__

uses  spm_reslice to resample in_file into space of space_defining

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                file to apply transform to, (only updates header)
        space_defining: (an existing file name)
                Volume defining space to slice in_file into

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: (0 <= an integer <= 7, nipype default value: 0)
                degree of b-spline used for interpolation0 is nearest neighbor (default)
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        out_file: (a file name)
                Optional file to save resliced volume
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        out_file: (an existing file name)
                resliced volume
