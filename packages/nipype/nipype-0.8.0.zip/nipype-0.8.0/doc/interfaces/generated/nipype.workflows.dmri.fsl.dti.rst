.. AUTO-GENERATED FILE -- DO NOT EDIT!

workflows.dmri.fsl.dti
======================


.. module:: nipype.workflows.dmri.fsl.dti


.. _nipype.workflows.dmri.fsl.dti.create_bedpostx_pipeline:

:func:`create_bedpostx_pipeline`
--------------------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L121>`__



Creates a pipeline that does the same as bedpostx script from FSL -
calculates diffusion model parameters (distributions not MLE) voxelwise for
the whole volume (by splitting it slicewise).

Example
~~~~~~~

>>> nipype_bedpostx = create_bedpostx_pipeline("nipype_bedpostx")
>>> nipype_bedpostx.inputs.inputnode.dwi = 'diffusion.nii'
>>> nipype_bedpostx.inputs.inputnode.mask = 'mask.nii'
>>> nipype_bedpostx.inputs.inputnode.bvecs = 'bvecs'
>>> nipype_bedpostx.inputs.inputnode.bvals = 'bvals'
>>> nipype_bedpostx.inputs.xfibres.n_fibres = 2
>>> nipype_bedpostx.inputs.xfibres.fudge = 1
>>> nipype_bedpostx.inputs.xfibres.burn_in = 1000
>>> nipype_bedpostx.inputs.xfibres.n_jumps = 1250
>>> nipype_bedpostx.inputs.xfibres.sample_every = 25
>>> nipype_bedpostx.run() # doctest: +SKIP

Inputs::

    inputnode.dwi
    inputnode.mask

Outputs::

    outputnode.thsamples
    outputnode.phsamples
    outputnode.fsamples
    outputnode.mean_thsamples
    outputnode.mean_phsamples
    outputnode.mean_fsamples
    outputnode.dyads
    outputnode.dyads_dispersion


Graph
~~~~~

.. graphviz::

	digraph bedpostx{

	  label="bedpostx";

	  bedpostx_inputnode[label="inputnode (utility)"];

	  bedpostx_xfibres[label="xfibres (fsl)"];

	  bedpostx_outputnode[label="outputnode (utility)"];

	  bedpostx_inputnode -> bedpostx_xfibres;

	  bedpostx_inputnode -> bedpostx_xfibres;

	  subgraph cluster_bedpostx_preproc {

	      label="preproc";

	    bedpostx_preproc_inputnode[label="inputnode (utility)"];

	    bedpostx_preproc_mask_dwi[label="mask_dwi (fsl)"];

	    bedpostx_preproc_slice_mask[label="slice_mask (fsl)"];

	    bedpostx_preproc_slice_dwi[label="slice_dwi (fsl)"];

	    bedpostx_preproc_inputnode -> bedpostx_preproc_mask_dwi;

	    bedpostx_preproc_inputnode -> bedpostx_preproc_mask_dwi;

	    bedpostx_preproc_inputnode -> bedpostx_preproc_slice_mask;

	    bedpostx_preproc_mask_dwi -> bedpostx_preproc_slice_dwi;

	  }

	  subgraph cluster_bedpostx_postproc {

	      label="postproc";

	    bedpostx_postproc_inputnode[label="inputnode (utility)"];

	    bedpostx_postproc_merge_thsamples[label="merge_thsamples (fsl)"];

	    bedpostx_postproc_mean_thsamples[label="mean_thsamples (fsl)"];

	    bedpostx_postproc_merge_mean_dsamples[label="merge_mean_dsamples (fsl)"];

	    bedpostx_postproc_merge_fsamples[label="merge_fsamples (fsl)"];

	    bedpostx_postproc_merge_phsamples[label="merge_phsamples (fsl)"];

	    bedpostx_postproc_mean_phsamples[label="mean_phsamples (fsl)"];

	    bedpostx_postproc_make_dyads[label="make_dyads (fsl)"];

	    bedpostx_postproc_mean_fsamples[label="mean_fsamples (fsl)"];

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_phsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_make_dyads;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_thsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_mean_dsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_fsamples;

	    bedpostx_postproc_merge_thsamples -> bedpostx_postproc_mean_thsamples;

	    bedpostx_postproc_merge_thsamples -> bedpostx_postproc_make_dyads;

	    bedpostx_postproc_merge_fsamples -> bedpostx_postproc_mean_fsamples;

	    bedpostx_postproc_merge_phsamples -> bedpostx_postproc_mean_phsamples;

	    bedpostx_postproc_merge_phsamples -> bedpostx_postproc_make_dyads;

	  }

	  bedpostx_preproc_slice_dwi -> bedpostx_xfibres;

	  bedpostx_preproc_slice_mask -> bedpostx_xfibres;

	  bedpostx_postproc_merge_thsamples -> bedpostx_outputnode;

	  bedpostx_postproc_merge_phsamples -> bedpostx_outputnode;

	  bedpostx_postproc_merge_fsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_thsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_phsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_fsamples -> bedpostx_outputnode;

	  bedpostx_postproc_make_dyads -> bedpostx_outputnode;

	  bedpostx_postproc_make_dyads -> bedpostx_outputnode;

	  bedpostx_inputnode -> bedpostx_preproc_inputnode;

	  bedpostx_inputnode -> bedpostx_preproc_inputnode;

	  bedpostx_inputnode -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.create_dmri_preprocessing:

:func:`create_dmri_preprocessing`
---------------------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L16>`__



Creates a workflow that chains the necessary pipelines to
correct for motion, eddy currents, and, if selected, susceptibility
artifacts in EPI dMRI sequences.

.. warning::

IMPORTANT NOTICE: this workflow rotates the b-vectors, so please be adviced
that not all the dicom converters ensure the consistency between the resulting
nifti orientation and the b matrix table (e.g. dcm2nii checks it).


Example
~~~~~~~

>>> nipype_dmri_preprocess = create_dmri_preprocessing("nipype_dmri_prep")
>>> nipype_dmri_preprocess.inputs.inputnode.in_file = 'diffusion.nii'
>>> nipype_dmri_preprocess.inputs.inputnode.in_bvec = 'diffusion.bvec'
>>> nipype_dmri_preprocess.inputs.inputnode.ref_num = 0
>>> nipype_dmri_preprocess.inputs.inputnode.fieldmap_mag = 'magnitude.nii'
>>> nipype_dmri_preprocess.inputs.inputnode.fieldmap_pha = 'phase.nii'
>>> nipype_dmri_preprocess.inputs.inputnode.te_diff = 2.46
>>> nipype_dmri_preprocess.inputs.inputnode.epi_echospacing = 0.77
>>> nipype_dmri_preprocess.inputs.inputnode.epi_rev_encoding = False
>>> nipype_dmri_preprocess.inputs.inputnode.pi_accel_factor = True
>>> nipype_dmri_preprocess.run() # doctest: +SKIP


Inputs::

    inputnode.in_file - The diffusion data
    inputnode.in_bvec - The b-matrix file, in FSL format and consistent with the in_file orientation
    inputnode.ref_num - The reference volume (a b=0 volume in dMRI)
    inputnode.fieldmap_mag - The magnitude of the fieldmap
    inputnode.fieldmap_pha - The phase difference of the fieldmap
    inputnode.te_diff - TE increment used (in msec.) on the fieldmap acquisition (generally 2.46ms for 3T scanners)
    inputnode.epi_echospacing - The EPI EchoSpacing parameter (in msec.)
    inputnode.epi_rev_encoding - True if reverse encoding was used (generally False)
    inputnode.pi_accel_factor - Parallel imaging factor (aka GRAPPA acceleration factor)
    inputnode.vsm_sigma - Sigma (in mm.) of the gaussian kernel used for in-slice smoothing of the deformation field (voxel shift map, vsm)


Outputs::

    outputnode.dmri_corrected
    outputnode.bvec_rotated


Optional arguments::
    use_fieldmap - True if there are fieldmap files that should be used (default True)
    fieldmap_registration - True if registration to fieldmap should be performed (default False)


Graph
~~~~~

.. graphviz::

	digraph dMRI_preprocessing{

	  label="dMRI_preprocessing";

	  dMRI_preprocessing_inputnode[label="inputnode (utility)"];

	  dMRI_preprocessing_outputnode[label="outputnode (utility)"];

	  subgraph cluster_dMRI_preprocessing_motion_correct {

	      label="motion_correct";

	    dMRI_preprocessing_motion_correct_inputnode[label="inputnode (utility)"];

	    dMRI_preprocessing_motion_correct_split[label="split (fsl)"];

	    dMRI_preprocessing_motion_correct_pick_ref[label="pick_ref (utility)"];

	    dMRI_preprocessing_motion_correct_coregistration[label="coregistration (fsl)"];

	    dMRI_preprocessing_motion_correct_rotate_b_matrix[label="rotate_b_matrix (utility)"];

	    dMRI_preprocessing_motion_correct_merge[label="merge (fsl)"];

	    dMRI_preprocessing_motion_correct_outputnode[label="outputnode (utility)"];

	    dMRI_preprocessing_motion_correct_inputnode -> dMRI_preprocessing_motion_correct_rotate_b_matrix;

	    dMRI_preprocessing_motion_correct_inputnode -> dMRI_preprocessing_motion_correct_split;

	    dMRI_preprocessing_motion_correct_inputnode -> dMRI_preprocessing_motion_correct_pick_ref;

	    dMRI_preprocessing_motion_correct_split -> dMRI_preprocessing_motion_correct_pick_ref;

	    dMRI_preprocessing_motion_correct_split -> dMRI_preprocessing_motion_correct_coregistration;

	    dMRI_preprocessing_motion_correct_pick_ref -> dMRI_preprocessing_motion_correct_coregistration;

	    dMRI_preprocessing_motion_correct_coregistration -> dMRI_preprocessing_motion_correct_rotate_b_matrix;

	    dMRI_preprocessing_motion_correct_coregistration -> dMRI_preprocessing_motion_correct_merge;

	    dMRI_preprocessing_motion_correct_rotate_b_matrix -> dMRI_preprocessing_motion_correct_outputnode;

	    dMRI_preprocessing_motion_correct_merge -> dMRI_preprocessing_motion_correct_outputnode;

	  }

	  subgraph cluster_dMRI_preprocessing_eddy_correct {

	      label="eddy_correct";

	    dMRI_preprocessing_eddy_correct_inputnode[label="inputnode (utility)"];

	    dMRI_preprocessing_eddy_correct_split[label="split (fsl)"];

	    dMRI_preprocessing_eddy_correct_pick_ref[label="pick_ref (utility)"];

	    dMRI_preprocessing_eddy_correct_coregistration[label="coregistration (fsl)"];

	    dMRI_preprocessing_eddy_correct_merge[label="merge (fsl)"];

	    dMRI_preprocessing_eddy_correct_outputnode[label="outputnode (utility)"];

	    dMRI_preprocessing_eddy_correct_inputnode -> dMRI_preprocessing_eddy_correct_split;

	    dMRI_preprocessing_eddy_correct_inputnode -> dMRI_preprocessing_eddy_correct_pick_ref;

	    dMRI_preprocessing_eddy_correct_split -> dMRI_preprocessing_eddy_correct_coregistration;

	    dMRI_preprocessing_eddy_correct_split -> dMRI_preprocessing_eddy_correct_pick_ref;

	    dMRI_preprocessing_eddy_correct_pick_ref -> dMRI_preprocessing_eddy_correct_coregistration;

	    dMRI_preprocessing_eddy_correct_coregistration -> dMRI_preprocessing_eddy_correct_merge;

	    dMRI_preprocessing_eddy_correct_merge -> dMRI_preprocessing_eddy_correct_outputnode;

	  }

	  subgraph cluster_dMRI_preprocessing_susceptibility_correct {

	      label="susceptibility_correct";

	    dMRI_preprocessing_susceptibility_correct_inputnode[label="inputnode (utility)"];

	    dMRI_preprocessing_susceptibility_correct_dwi_split[label="dwi_split (utility)"];

	    dMRI_preprocessing_susceptibility_correct_select_magnitude[label="select_magnitude (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_normalize_phasediff[label="normalize_phasediff (utility)"];

	    dMRI_preprocessing_susceptibility_correct_dwell_time[label="dwell_time (utility)"];

	    dMRI_preprocessing_susceptibility_correct_mask_magnitude[label="mask_magnitude (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_mask_dilate[label="mask_dilate (utility)"];

	    dMRI_preprocessing_susceptibility_correct_phase_unwrap[label="phase_unwrap (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_fill_phasediff[label="fill_phasediff (utility)"];

	    dMRI_preprocessing_susceptibility_correct_generate_vsm[label="generate_vsm (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_vsm_mean_shift[label="vsm_mean_shift (utility)"];

	    dMRI_preprocessing_susceptibility_correct_dwi_fugue[label="dwi_fugue (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_dwi_merge[label="dwi_merge (fsl)"];

	    dMRI_preprocessing_susceptibility_correct_outputnode[label="outputnode (utility)"];

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_normalize_phasediff;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_dwi_split;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_dwell_time;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_dwell_time;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_dwell_time;

	    dMRI_preprocessing_susceptibility_correct_inputnode -> dMRI_preprocessing_susceptibility_correct_select_magnitude;

	    dMRI_preprocessing_susceptibility_correct_dwi_split -> dMRI_preprocessing_susceptibility_correct_dwi_fugue;

	    dMRI_preprocessing_susceptibility_correct_select_magnitude -> dMRI_preprocessing_susceptibility_correct_mask_magnitude;

	    dMRI_preprocessing_susceptibility_correct_select_magnitude -> dMRI_preprocessing_susceptibility_correct_phase_unwrap;

	    dMRI_preprocessing_susceptibility_correct_normalize_phasediff -> dMRI_preprocessing_susceptibility_correct_phase_unwrap;

	    dMRI_preprocessing_susceptibility_correct_dwell_time -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_mask_magnitude -> dMRI_preprocessing_susceptibility_correct_mask_dilate;

	    dMRI_preprocessing_susceptibility_correct_mask_dilate -> dMRI_preprocessing_susceptibility_correct_phase_unwrap;

	    dMRI_preprocessing_susceptibility_correct_mask_dilate -> dMRI_preprocessing_susceptibility_correct_dwi_fugue;

	    dMRI_preprocessing_susceptibility_correct_mask_dilate -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_mask_dilate -> dMRI_preprocessing_susceptibility_correct_vsm_mean_shift;

	    dMRI_preprocessing_susceptibility_correct_phase_unwrap -> dMRI_preprocessing_susceptibility_correct_fill_phasediff;

	    dMRI_preprocessing_susceptibility_correct_fill_phasediff -> dMRI_preprocessing_susceptibility_correct_generate_vsm;

	    dMRI_preprocessing_susceptibility_correct_generate_vsm -> dMRI_preprocessing_susceptibility_correct_vsm_mean_shift;

	    dMRI_preprocessing_susceptibility_correct_generate_vsm -> dMRI_preprocessing_susceptibility_correct_vsm_mean_shift;

	    dMRI_preprocessing_susceptibility_correct_vsm_mean_shift -> dMRI_preprocessing_susceptibility_correct_dwi_fugue;

	    dMRI_preprocessing_susceptibility_correct_dwi_fugue -> dMRI_preprocessing_susceptibility_correct_dwi_merge;

	    dMRI_preprocessing_susceptibility_correct_dwi_merge -> dMRI_preprocessing_susceptibility_correct_outputnode;

	  }

	  dMRI_preprocessing_eddy_correct_outputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_susceptibility_correct_outputnode -> dMRI_preprocessing_outputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_susceptibility_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_motion_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_motion_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_motion_correct_inputnode;

	  dMRI_preprocessing_inputnode -> dMRI_preprocessing_eddy_correct_inputnode;

	  dMRI_preprocessing_motion_correct_outputnode -> dMRI_preprocessing_outputnode;

	  dMRI_preprocessing_motion_correct_outputnode -> dMRI_preprocessing_eddy_correct_inputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.create_eddy_correct_pipeline:

:func:`create_eddy_correct_pipeline`
------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L357>`__



Creates a pipeline that replaces eddy_correct script in FSL. It takes a
series of diffusion weighted images and linearly co-registers them to one
reference image. No rotation of the B-matrix is performed, so this pipeline
should be executed after the motion correction pipeline.

Example
~~~~~~~

>>> nipype_eddycorrect = create_eddy_correct_pipeline("nipype_eddycorrect")
>>> nipype_eddycorrect.inputs.inputnode.in_file = 'diffusion.nii'
>>> nipype_eddycorrect.inputs.inputnode.ref_num = 0
>>> nipype_eddycorrect.run() # doctest: +SKIP

Inputs::

    inputnode.in_file
    inputnode.ref_num

Outputs::

    outputnode.eddy_corrected


Graph
~~~~~

.. graphviz::

	digraph eddy_correct{

	  label="eddy_correct";

	  eddy_correct_inputnode[label="inputnode (utility)"];

	  eddy_correct_split[label="split (fsl)"];

	  eddy_correct_pick_ref[label="pick_ref (utility)"];

	  eddy_correct_coregistration[label="coregistration (fsl)"];

	  eddy_correct_merge[label="merge (fsl)"];

	  eddy_correct_outputnode[label="outputnode (utility)"];

	  eddy_correct_inputnode -> eddy_correct_split;

	  eddy_correct_inputnode -> eddy_correct_pick_ref;

	  eddy_correct_split -> eddy_correct_pick_ref;

	  eddy_correct_split -> eddy_correct_coregistration;

	  eddy_correct_pick_ref -> eddy_correct_coregistration;

	  eddy_correct_coregistration -> eddy_correct_merge;

	  eddy_correct_merge -> eddy_correct_outputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.create_motion_correct_pipeline:

:func:`create_motion_correct_pipeline`
--------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L294>`__



Creates a pipeline that corrects for motion artifact in dMRI sequences.
It takes a series of diffusion weighted images and rigidly corregisters
them to one reference image. Finally, the b-matrix is rotated accordingly
(Leemans et al. 2009 - http://www.ncbi.nlm.nih.gov/pubmed/19319973),
making use of the rotation matrix obtained by FLIRT.

.. warning::

IMPORTANT NOTICE: this workflow rotates the b-vectors, so please be adviced
that not all the dicom converters ensure the consistency between the resulting
nifti orientation and the b matrix table (e.g. dcm2nii checks it).


Example
~~~~~~~

>>> nipype_motioncorrect = create_motion_correct_pipeline("nipype_motioncorrect")
>>> nipype_motioncorrect.inputs.inputnode.in_file = 'diffusion.nii'
>>> nipype_motioncorrect.inputs.inputnode.in_bvec = 'diffusion.bvec'
>>> nipype_motioncorrect.inputs.inputnode.ref_num = 0
>>> nipype_motioncorrect.run() # doctest: +SKIP

Inputs::

    inputnode.in_file
    inputnode.ref_num
    inputnode.in_bvec

Outputs::

    outputnode.motion_corrected
    outputnode.out_bvec


Graph
~~~~~

.. graphviz::

	digraph motion_correct{

	  label="motion_correct";

	  motion_correct_inputnode[label="inputnode (utility)"];

	  motion_correct_split[label="split (fsl)"];

	  motion_correct_pick_ref[label="pick_ref (utility)"];

	  motion_correct_coregistration[label="coregistration (fsl)"];

	  motion_correct_rotate_b_matrix[label="rotate_b_matrix (utility)"];

	  motion_correct_merge[label="merge (fsl)"];

	  motion_correct_outputnode[label="outputnode (utility)"];

	  motion_correct_inputnode -> motion_correct_rotate_b_matrix;

	  motion_correct_inputnode -> motion_correct_split;

	  motion_correct_inputnode -> motion_correct_pick_ref;

	  motion_correct_split -> motion_correct_pick_ref;

	  motion_correct_split -> motion_correct_coregistration;

	  motion_correct_pick_ref -> motion_correct_coregistration;

	  motion_correct_coregistration -> motion_correct_rotate_b_matrix;

	  motion_correct_coregistration -> motion_correct_merge;

	  motion_correct_rotate_b_matrix -> motion_correct_outputnode;

	  motion_correct_merge -> motion_correct_outputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.create_susceptibility_correct_pipeline:

:func:`create_susceptibility_correct_pipeline`
----------------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L403>`__



Replaces the epidewarp.fsl script (http://www.nmr.mgh.harvard.edu/~greve/fbirn/b0/epidewarp.fsl)
for susceptibility distortion correction of dMRI & fMRI acquired with EPI sequences and the fieldmap
information (Jezzard et al., 1995) using FSL's FUGUE. The registration to the (warped) fieldmap
(strictly following the original script) is available using fieldmap_registration=True.

Example
~~~~~~~

>>> nipype_epicorrect = create_susceptibility_correct_pipeline("nipype_epicorrect", fieldmap_registration=False)
>>> nipype_epicorrect.inputs.inputnode.in_file = 'diffusion.nii'
>>> nipype_epicorrect.inputs.inputnode.fieldmap_mag = 'magnitude.nii'
>>> nipype_epicorrect.inputs.inputnode.fieldmap_pha = 'phase.nii'
>>> nipype_epicorrect.inputs.inputnode.te_diff = 2.46
>>> nipype_epicorrect.inputs.inputnode.epi_echospacing = 0.77
>>> nipype_epicorrect.inputs.inputnode.epi_rev_encoding = False
>>> nipype_epicorrect.inputs.inputnode.ref_num = 0
>>> nipype_epicorrect.inputs.inputnode.pi_accel_factor = 1.0
>>> nipype_epicorrect.run() # doctest: +SKIP

Inputs::

    inputnode.in_file - The volume acquired with EPI sequence
    inputnode.fieldmap_mag - The magnitude of the fieldmap
    inputnode.fieldmap_pha - The phase difference of the fieldmap
    inputnode.te_diff - Time difference between TE in ms.
    inputnode.epi_echospacing - The echo spacing (aka dwell time) in the EPI sequence
    inputnode.epi_ph_encoding_dir - The phase encoding direction in EPI acquisition (default y)
    inputnode.epi_rev_encoding - True if it is acquired with reverse encoding
    inputnode.pi_accel_factor - Acceleration factor used for EPI parallel imaging (GRAPPA)
    inputnode.vsm_sigma - Sigma value of the gaussian smoothing filter applied to the vsm (voxel shift map)
    inputnode.ref_num - The reference volume (B=0 in dMRI or a central frame in fMRI)


Outputs::

    outputnode.epi_corrected


Optional arguments::

    fieldmap_registration - True if registration to fieldmap should be done (default False)


Graph
~~~~~

.. graphviz::

	digraph susceptibility_correct{

	  label="susceptibility_correct";

	  susceptibility_correct_inputnode[label="inputnode (utility)"];

	  susceptibility_correct_dwi_split[label="dwi_split (utility)"];

	  susceptibility_correct_dwell_time[label="dwell_time (utility)"];

	  susceptibility_correct_select_magnitude[label="select_magnitude (fsl)"];

	  susceptibility_correct_mask_magnitude[label="mask_magnitude (fsl)"];

	  susceptibility_correct_mask_dilate[label="mask_dilate (utility)"];

	  susceptibility_correct_normalize_phasediff[label="normalize_phasediff (utility)"];

	  susceptibility_correct_phase_unwrap[label="phase_unwrap (fsl)"];

	  susceptibility_correct_fill_phasediff[label="fill_phasediff (utility)"];

	  susceptibility_correct_generate_vsm[label="generate_vsm (fsl)"];

	  susceptibility_correct_vsm_mean_shift[label="vsm_mean_shift (utility)"];

	  susceptibility_correct_dwi_fugue[label="dwi_fugue (fsl)"];

	  susceptibility_correct_dwi_merge[label="dwi_merge (fsl)"];

	  susceptibility_correct_outputnode[label="outputnode (utility)"];

	  susceptibility_correct_inputnode -> susceptibility_correct_dwi_split;

	  susceptibility_correct_inputnode -> susceptibility_correct_dwell_time;

	  susceptibility_correct_inputnode -> susceptibility_correct_dwell_time;

	  susceptibility_correct_inputnode -> susceptibility_correct_dwell_time;

	  susceptibility_correct_inputnode -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_inputnode -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_inputnode -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_inputnode -> susceptibility_correct_select_magnitude;

	  susceptibility_correct_inputnode -> susceptibility_correct_normalize_phasediff;

	  susceptibility_correct_dwi_split -> susceptibility_correct_dwi_fugue;

	  susceptibility_correct_dwell_time -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_select_magnitude -> susceptibility_correct_mask_magnitude;

	  susceptibility_correct_select_magnitude -> susceptibility_correct_phase_unwrap;

	  susceptibility_correct_mask_magnitude -> susceptibility_correct_mask_dilate;

	  susceptibility_correct_mask_dilate -> susceptibility_correct_dwi_fugue;

	  susceptibility_correct_mask_dilate -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_mask_dilate -> susceptibility_correct_phase_unwrap;

	  susceptibility_correct_mask_dilate -> susceptibility_correct_vsm_mean_shift;

	  susceptibility_correct_normalize_phasediff -> susceptibility_correct_phase_unwrap;

	  susceptibility_correct_phase_unwrap -> susceptibility_correct_fill_phasediff;

	  susceptibility_correct_fill_phasediff -> susceptibility_correct_generate_vsm;

	  susceptibility_correct_generate_vsm -> susceptibility_correct_vsm_mean_shift;

	  susceptibility_correct_generate_vsm -> susceptibility_correct_vsm_mean_shift;

	  susceptibility_correct_vsm_mean_shift -> susceptibility_correct_dwi_fugue;

	  susceptibility_correct_dwi_fugue -> susceptibility_correct_dwi_merge;

	  susceptibility_correct_dwi_merge -> susceptibility_correct_outputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.transpose:

:func:`transpose`
-----------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/workflows/dmri/fsl/dti.py#L9>`__





