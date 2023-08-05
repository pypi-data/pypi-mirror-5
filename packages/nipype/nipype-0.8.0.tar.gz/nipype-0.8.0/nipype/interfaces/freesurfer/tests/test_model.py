# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from nipype.testing import (assert_equal, assert_false, assert_true,
                            assert_raises, skipif)
import nipype.interfaces.freesurfer as freesurfer


def test_binarize():
    input_map = dict(abs = dict(argstr='--abs',),
                     args = dict(argstr='%s',),
                     bin_col_num = dict(argstr='--bincol',),
                     bin_val = dict(argstr='--binval %d',),
                     bin_val_not = dict(argstr='--binvalnot %d',),
                     binary_file = dict(argstr='--o %s',),
                     count_file = dict(argstr='--count %s',),
                     dilate = dict(argstr='--dilate %d',),
                     environ = dict(),
                     erode = dict(argstr='--erode  %d',),
                     erode2d = dict(argstr='--erode2d %d',),
                     frame_no = dict(argstr='--frame %s',),
                     in_file = dict(copyfile=False, mandatory=True, argstr='--i %s'),
                     invert = dict(argstr='--inv',),
                     mask_file = dict(argstr='--mask maskvol',),
                     mask_thresh = dict(argstr='--mask-thresh %f',),
                     match = dict(argstr='--match %d...',),
                     max = dict(argstr='--max %f',),
                     merge_file = dict(argstr='--merge %s',),
                     min = dict(argstr='--min %f',),
                     out_type = dict(argstr='',),
                     rmax = dict(argstr='--rmax %f',),
                     rmin = dict(argstr='--rmin %f',),
                     subjects_dir = dict(),
                     ventricles = dict(argstr='--ventricles',),
                     wm = dict(argstr='--wm',),
                     wm_ven_csf = dict(argstr='--wm+vcsf',),
                     zero_edges = dict(argstr='--zero-edges',),
                     zero_slice_edge = dict(argstr='--zero-slice-edges',),
                     )
    instance = freesurfer.Binarize()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_concatenate():
    input_map = dict(add_val = dict(argstr='--add %f',),
                     args = dict(argstr='%s',),
                     combine = dict(argstr='--combine',),
                     concatenated_file = dict(argstr='--o %s',),
                     environ = dict(),
                     gmean = dict(argstr='--gmean %d',),
                     in_files = dict(mandatory=True, argstr='--i %s...',),
                     keep_dtype = dict(argstr='--keep-datatype',),
                     mask_file = dict(argstr='--mask %s',),
                     max_bonfcor = dict(argstr='--max-bonfcor',),
                     max_index = dict(argstr='--max-index',),
                     mean_div_n = dict(argstr='--mean-div-n',),
                     multiply_by = dict(argstr='--mul %f',),
                     multiply_matrix_file = dict(argstr='--mtx %s',),
                     paired_stats = dict(argstr='--paired-%s',),
                     sign = dict(argstr='--%s',),
                     sort = dict(argstr='--sort',),
                     stats = dict(argstr='--%s',),
                     subjects_dir = dict(),
                     vote = dict(argstr='--vote',),
                     )
    instance = freesurfer.Concatenate()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_glmfit():
    input_map = dict(allow_ill_cond = dict(argstr='--illcond',),
                     allow_repeated_subjects = dict(argstr='--allowsubjrep',),
                     args = dict(argstr='%s',),
                     calc_AR1 = dict(argstr='--tar1',),
                     check_opts = dict(argstr='--checkopts',),
                     compute_log_y = dict(argstr='--logy',),
                     contrast = dict(argstr='--C %s...',),
                     cortex = dict(xor=['label_file'], argstr='--cortex',),
                     debug = dict(argstr='--debug',),
                     design = dict(xor=('fsgd', 'design', 'one_sample'), argstr='--X %s',),
                     diag = dict(),
                     diag_cluster = dict(argstr='--diag-cluster',),
                     environ = dict(),
                     fixed_fx_dof = dict(xor=['fixed_fx_dof_file'], argstr='--ffxdof %d',),
                     fixed_fx_dof_file = dict(xor=['fixed_fx_dof'], argstr='--ffxdofdat %d',),
                     fixed_fx_var = dict(argstr='--yffxvar %s',),
                     force_perm = dict(argstr='--perm-force',),
                     fsgd = dict(argstr='--fsgd %s %s', xor=('fsgd', 'design', 'one_sample'),),
                     fwhm = dict(argstr='--fwhm %f',),
                     glm_dir = dict(argstr='--glmdir %s',),
                     in_file = dict(copyfile=False, argstr='--y %s', mandatory=True,),
                     invert_mask = dict(argstr='--mask-inv',),
                     label_file = dict(xor=['cortex'], argstr='--label %s',),
                     mask_file = dict(argstr='--mask %s',),
                     no_contrast_sok = dict(argstr='--no-contrasts-ok',),
                     no_est_fwhm = dict(argstr='--no-est-fwhm',),
                     no_mask_smooth = dict(argstr='--no-mask-smooth',),
                     no_prune = dict(xor=['prunethresh'], argstr='--no-prune',),
                     one_sample = dict(xor=('one_sample', 'fsgd', 'design', 'contrast'), argstr='--osgm',),
                     pca = dict(argstr='--pca',),
                     per_voxel_reg = dict(argstr='--pvr %s...',),
                     profile = dict(argstr='--profile %d',),
                     prune = dict(argstr='--prune',),
                     prune_thresh = dict(xor=['noprune'], argstr='--prune_thr %f',),
                     resynth_test = dict(argstr='--resynthtest %d',),
                     save_cond = dict(argstr='--save-cond',),
                     save_estimate = dict(argstr='--yhat-save',),
                     save_res_corr_mtx = dict(argstr='--eres-scm',),
                     save_residual = dict(argstr='--eres-save',),
                     seed = dict(argstr='--seed %d',),
                     self_reg = dict(argstr='--selfreg %d %d %d',),
                     sim_done_file = dict(argstr='--sim-done %s',),
                     sim_sign = dict(argstr='--sim-sign %s',),
                     simulation = dict(argstr='--sim %s %d %f %s',),
                     subjects_dir = dict(),
                     surf = dict(argstr="--surf %s %s %s"),
                     synth = dict(argstr='--synth',),
                     uniform = dict(argstr='--uniform %f %f',),
                     var_fwhm = dict(argstr='--var-fwhm %f',),
                     vox_dump = dict(argstr='--voxdump %d %d %d',),
                     weight_file = dict(xor=['weighted_ls'],),
                     weight_inv = dict(xor=['weighted_ls'], argstr='--w-inv',),
                     weight_sqrt = dict(xor=['weighted_ls'], argstr='--w-sqrt',),
                     weighted_ls = dict(xor=('weight_file', 'weight_inv', 'weight_sqrt'), argstr='--wls %s',),
                     )
    instance = freesurfer.GLMFit()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_label2vol():
    input_map = dict(annot_file = dict(copyfile=False, mandatory=True,
                                       xor=('label_file', 'annot_file', 'seg_file', 'aparc_aseg'),
                                       requires=('subject_id', 'hemi'), argstr='--annot %s',),
                     aparc_aseg = dict(xor=('label_file', 'annot_file', 'seg_file', 'aparc_aseg'),
                                       argstr='--aparc+aseg', mandatory=True,),
                     args = dict(argstr='%s',),
                     environ = dict(),
                     fill_thresh = dict(argstr='--fillthresh %.f',),
                     hemi = dict(argstr='--hemi %s',),
                     identity = dict(xor=('reg_file', 'reg_header', 'identity'), argstr='--identity',),
                     invert_mtx = dict(argstr='--invertmtx',),
                     label_file = dict(copyfile=False, xor=('label_file', 'annot_file', 'seg_file', 'aparc_aseg'),
                                       argstr='--label %s...', mandatory=True,),
                     label_hit_file = dict(argstr='--hits %s',),
                     label_voxel_volume = dict(argstr='--labvoxvol %f',),
                     map_label_stat = dict(argstr='--label-stat %s',),
                     native_vox2ras = dict(argstr='--native-vox2ras',),
                     proj = dict(argstr='--proj %s %f %f %f',),
                     reg_file = dict(xor=('reg_file', 'reg_header', 'identity'), argstr='--reg %s',),
                     reg_header = dict(xor=('reg_file', 'reg_header', 'identity'), argstr='--regheader %s',),
                     seg_file = dict(copyfile=False, mandatory=True,
                                     xor=('label_file', 'annot_file', 'seg_file', 'aparc_aseg'),
                                     argstr='--seg %s',),
                     subject_id = dict(argstr='--subject %s',),
                     subjects_dir = dict(),
                     surface = dict(argstr='--surf %s',),
                     template_file = dict(mandatory=True, argstr='--temp %s',),
                     vol_label_file = dict(argstr='--o %s',),
                     )
    instance = freesurfer.Label2Vol()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_mrispreproc():
    input_map = dict(args = dict(argstr='%s',),
                     environ = dict(),
                     fsgd_file = dict(xor=('subjects', 'fsgd_file', 'subject_file'), argstr='--fsgd %s',),
                     fwhm = dict(xor=['num_iters'], argstr='--fwhm %f',),
                     fwhm_source = dict(xor=['num_iters_source'], argstr='--fwhm-src %f',),
                     hemi = dict(argstr='--hemi %s', mandatory=True,),
                     num_iters = dict(xor=['fwhm'], argstr='--niters %d',),
                     num_iters_source = dict(xor=['fwhm_source'], argstr='--niterssrc %d',),
                     out_file = dict(argstr='--out %s',),
                     proj_frac = dict(argstr='--projfrac %s',),
                     smooth_cortex_only = dict(argstr='--smooth-cortex-only',),
                     source_format = dict(argstr='--srcfmt %s',),
                     subject_file = dict(xor=('subjects', 'fsgd_file', 'subject_file'), argstr='--f %s',),
                     subjects = dict(xor=('subjects', 'fsgd_file', 'subject_file'), argstr='--s %s...',),
                     subjects_dir = dict(),
                     surf_area = dict(xor=('surf_measure', 'surf_measure_file', 'surf_area'), argstr='--area %s',),
                     surf_dir = dict(argstr='--surfdir %s',),
                     surf_measure = dict(xor=('surf_measure', 'surf_measure_file', 'surf_area'), argstr='--meas %s',),
                     surf_measure_file = dict(xor=('surf_measure', 'surf_measure_file', 'surf_area'), argstr='--is %s...',),
                     target = dict(mandatory=True, argstr='--target %s',),
                     vol_measure_file = dict(argstr='--iv %s %s...',),
                     )
    instance = freesurfer.MRISPreproc()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_onesamplettest():
    input_map = dict(allow_ill_cond = dict(argstr='--illcond',),
                     allow_repeated_subjects = dict(argstr='--allowsubjrep',),
                     args = dict(argstr='%s',),
                     calc_AR1 = dict(argstr='--tar1',),
                     check_opts = dict(argstr='--checkopts',),
                     compute_log_y = dict(argstr='--logy',),
                     contrast = dict(argstr='--C %s...',),
                     cortex = dict(xor=['label_file'], argstr='--cortex',),
                     debug = dict(argstr='--debug',),
                     design = dict(xor=('fsgd', 'design', 'one_sample'), argstr='--X %s',),
                     diag = dict(),
                     diag_cluster = dict(argstr='--diag-cluster',),
                     environ = dict(),
                     fixed_fx_dof = dict(xor=['fixed_fx_dof_file'], argstr='--ffxdof %d',),
                     fixed_fx_dof_file = dict(xor=['fixed_fx_dof'], argstr='--ffxdofdat %d',),
                     fixed_fx_var = dict(argstr='--yffxvar %s',),
                     force_perm = dict(argstr='--perm-force',),
                     fsgd = dict(argstr='--fsgd %s %s', xor=('fsgd', 'design', 'one_sample'),),
                     fwhm = dict(argstr='--fwhm %f',),
                     glm_dir = dict(argstr='--glmdir %s',),
                     in_file = dict(copyfile=False, argstr='--y %s', mandatory=True,),
                     invert_mask = dict(argstr='--mask-inv',),
                     label_file = dict(xor=['cortex'], argstr='--label %s',),
                     mask_file = dict(argstr='--mask %s',),
                     no_contrast_sok = dict(argstr='--no-contrasts-ok',),
                     no_est_fwhm = dict(argstr='--no-est-fwhm',),
                     no_mask_smooth = dict(argstr='--no-mask-smooth',),
                     no_prune = dict(xor=['prunethresh'], argstr='--no-prune',),
                     one_sample = dict(xor=('one_sample', 'fsgd', 'design', 'contrast'), argstr='--osgm',),
                     pca = dict(argstr='--pca',),
                     per_voxel_reg = dict(argstr='--pvr %s...',),
                     profile = dict(argstr='--profile %d',),
                     prune = dict(argstr='--prune',),
                     prune_thresh = dict(xor=['noprune'], argstr='--prune_thr %f',),
                     resynth_test = dict(argstr='--resynthtest %d',),
                     save_cond = dict(argstr='--save-cond',),
                     save_estimate = dict(argstr='--yhat-save',),
                     save_res_corr_mtx = dict(argstr='--eres-scm',),
                     save_residual = dict(argstr='--eres-save',),
                     seed = dict(argstr='--seed %d',),
                     self_reg = dict(argstr='--selfreg %d %d %d',),
                     sim_done_file = dict(argstr='--sim-done %s',),
                     sim_sign = dict(argstr='--sim-sign %s',),
                     simulation = dict(argstr='--sim %s %d %f %s',),
                     subjects_dir = dict(),
                     surf = dict(),
                     synth = dict(argstr='--synth',),
                     uniform = dict(argstr='--uniform %f %f',),
                     var_fwhm = dict(argstr='--var-fwhm %f',),
                     vox_dump = dict(argstr='--voxdump %d %d %d',),
                     weight_file = dict(xor=['weighted_ls'],),
                     weight_inv = dict(xor=['weighted_ls'], argstr='--w-inv',),
                     weight_sqrt = dict(xor=['weighted_ls'], argstr='--w-sqrt',),
                     weighted_ls = dict(xor=('weight_file', 'weight_inv', 'weight_sqrt'), argstr='--wls %s',),
                     )
    instance = freesurfer.OneSampleTTest()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_segstats():
    input_map = dict(annot = dict(mandatory=True, argstr='--annot %s %s %s',
                                  xor=('segmentation_file', 'annot', 'surf_label'),),
                     args = dict(argstr='%s',),
                     avgwf_file = dict(argstr='--avgwfvol %s',),
                     avgwf_txt_file = dict(argstr='--avgwf %s',),
                     brain_vol = dict(),
                     calc_power = dict(argstr='--%s',),
                     calc_snr = dict(argstr='--snr',),
                     color_table_file = dict(xor=('color_table_file', 'default_color_table', 'gca_color_table'),
                                             argstr='--ctab %s',),
                     cortex_vol_from_surf = dict(argstr='--surf-ctx-vol',),
                     default_color_table = dict(xor=('color_table_file', 'default_color_table', 'gca_color_table'),
                                                argstr='--ctab-default',),
                     environ = dict(),
                     etiv = dict(argstr='--etiv',),
                     etiv_only = dict(),
                     exclude_ctx_gm_wm = dict(argstr='--excl-ctxgmwm',),
                     exclude_id = dict(argstr='--excludeid %d',),
                     frame = dict(argstr='--frame %d',),
                     gca_color_table = dict(xor=('color_table_file', 'default_color_table', 'gca_color_table'),
                                            argstr='--ctab-gca %s',),
                     in_file = dict(argstr='--i %s',),
                     mask_erode = dict(argstr='--maskerode %d',),
                     mask_file = dict(argstr='--mask %s',),
                     mask_frame = dict(requires=['mask_file'],),
                     mask_invert = dict(argstr='--maskinvert',),
                     mask_sign = dict(),
                     mask_thresh = dict(argstr='--maskthresh %f',),
                     multiply = dict(argstr='--mul %f',),
                     non_empty_only = dict(argstr='--nonempty',),
                     partial_volume_file = dict(argstr='--pv %f',),
                     segment_id = dict(argstr='--id %s...',),
                     segmentation_file = dict(xor=('segmentation_file', 'annot', 'surf_label'),
                                              argstr='--seg %s', mandatory=True,),
                     sf_avg_file = dict(argstr='--sfavg %s',),
                     subjects_dir = dict(),
                     summary_file = dict(argstr='--sum %s',),
                     surf_label = dict(mandatory=True, argstr='--slabel %s %s %s',
                                       xor=('segmentation_file', 'annot', 'surf_label'),),
                     vox = dict(argstr='--vox %s',),
                     wm_vol_from_surf = dict(argstr='--surf-wm-vol',),
                     )
    instance = freesurfer.SegStats()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key], metakey), value

def test_MS_LDA():
    input_map = dict(args = dict(argstr='%s',),
                     conform = dict(argstr='-conform',),
                     environ = dict(usedefault=True,),
                     ignore_exception = dict(usedefault=True,),
                     images = dict(copyfile=False,mandatory=True,argstr='%s',),
                     label_file = dict(argstr='-label %s',),
                     lda_labels = dict(mandatory=True,sep=' ',argstr='-lda %s',),
                     mask_file = dict(argstr='-mask %s',),
                     output_synth = dict(mandatory=True,argstr='-synth %s',),
                     shift = dict(argstr='-shift %d',),
                     subjects_dir = dict(),
                     use_weights = dict(argstr='-W',),
                     weight_file = dict(mandatory=True,argstr='-weight %s',),
                     )
    instance = freesurfer.MS_LDA()
    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(instance.inputs.traits()[key],
                                        metakey), value
