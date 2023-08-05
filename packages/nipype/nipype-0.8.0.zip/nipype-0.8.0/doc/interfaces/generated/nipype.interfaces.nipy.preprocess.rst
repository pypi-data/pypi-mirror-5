.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.nipy.preprocess
==========================


.. _nipype.interfaces.nipy.preprocess.ComputeMask:


.. index:: ComputeMask

ComputeMask
-----------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/nipy/preprocess.py#L48>`__

Inputs::

        [Mandatory]
        mean_volume: (an existing file name)
                mean EPI image, used to compute the threshold for the mask

        [Optional]
        M: (a float)
                upper fraction of the histogram to be discarded
        cc: (a boolean)
                Keep only the largest connected component
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        m: (a float)
                lower fraction of the histogram to be discarded
        reference_volume: (an existing file name)
                reference volume used to compute the mask. If none is give, the mean volume is used.

Outputs::

        brain_mask: (an existing file name)

.. _nipype.interfaces.nipy.preprocess.FmriRealign4d:


.. index:: FmriRealign4d

FmriRealign4d
-------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/nipy/preprocess.py#L120>`__

Simultaneous motion and slice timing correction algorithm

This interface wraps nipy's FmriRealign4d algorithm [1]_.

Examples
~~~~~~~~
>>> from nipype.interfaces.nipy.preprocess import FmriRealign4d
>>> realigner = FmriRealign4d()
>>> realigner.inputs.in_file = ['functional.nii']
>>> realigner.inputs.tr = 2
>>> realigner.inputs.slice_order = range(0,67)
>>> res = realigner.run() # doctest: +SKIP

References
~~~~~~~~~~
.. [1] Roche A. A four-dimensional registration algorithm with        application to joint correction of motion and slice timing        in fMRI. IEEE Trans Med Imaging. 2011 Aug;30(8):1546-54. DOI_.

.. _DOI: http://dx.doi.org/10.1109/TMI.2011.2131152

Inputs::

        [Mandatory]
        in_file
                File to realign
        tr: (a float)
                TR in seconds

        [Optional]
        between_loops: (an integer, nipype default value: [5])
                loops used to                                                           realign
                different                                                           runs
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        loops: (an integer, nipype default value: [5])
                loops within each run
        slice_order: (a list of items which are an integer)
                0 based slice order. This would be equivalent to enteringnp.argsort(spm_slice_order) for
                this field. This effectsinterleaved acquisition. This field will be deprecated infuture
                Nipy releases and be replaced by actual sliceacquisition times.
                requires: time_interp
        speedup: (an integer, nipype default value: [5])
                successive image                                   sub-sampling factors
                for acceleration
        start: (a float, nipype default value: 0.0)
                time offset into TR to align slices to
        time_interp: (True)
                Assume smooth changes across time e.g.,                     fmri series. If you don't
                want slice timing                      correction set this to undefined
                requires: slice_order
        tr_slices: (a float)
                TR slices
                requires: time_interp

Outputs::

        out_file: (an existing file name)
                Realigned files
        par_file: (an existing file name)
                Motion parameter files

.. _nipype.interfaces.nipy.preprocess.Trim:


.. index:: Trim

Trim
----

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/nipy/preprocess.py#L219>`__

Simple interface to trim a few volumes from a 4d fmri nifti file

Examples
~~~~~~~~
>>> from nipype.interfaces.nipy.preprocess import Trim
>>> trim = Trim()
>>> trim.inputs.in_file = 'functional.nii'
>>> trim.inputs.begin_index = 3 # remove 3 first volumes
>>> res = trim.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                EPI image to trim

        [Optional]
        begin_index: (an integer, nipype default value: 0)
                first volume
        end_index: (an integer, nipype default value: 0)
                last volume indexed as in python (and 0 for last)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name)
                output filename
        suffix: (a string, nipype default value: _trim)
                suffix for out_file to use if no out_file provided

Outputs::

        out_file: (an existing file name)
