#!/usr/bin/python

import sys
import os
import nipype.pipeline.engine as np_pe
import nipype.interfaces.fsl as np_fsl

os.environ['FSLDIR'] = '/usr/local/fsl'
os.environ['PATH'] = '%s:/usr/local/fsl/bin' % os.environ['PATH']

workflow = np_pe.Workflow(name='structural_qa')

reorient = np_pe.Node(interface=np_fsl.Reorient2Std(), name='reorient')
reorient.inputs.in_file = '/Users/ch/Desktop/ndar/python/anat.nii.gz'
bet = np_pe.Node(interface=np_fsl.BET(), name='bet')
bet.inputs.mask = True
bet.inputs.surfaces = True
workflow.connect(reorient, 'out_file', bet, 'in_file')

fast = np_pe.Node(interface=np_fsl.FAST(), name='fast')
fast.inputs.img_type = 1
workflow.connect(bet, 'out_file', fast, 'in_files')

generate_external = np_pe.Node(interface=np_fsl.ImageMaths(), 
                               name='generate_external')
generate_external.inputs.op_string = '-sub 1 -mul -1'
workflow.connect(bet, 'outskin_mask_file', generate_external, 'in_file')

generate_csf = np_pe.Node(interface=np_fsl.ImageMaths(), name='generate_csf')
generate_csf.inputs.op_string = '-thr 1 -uthr 1 -bin'
workflow.connect(fast, 'tissue_class_map', generate_csf, 'in_file')

generate_gm = np_pe.Node(interface=np_fsl.ImageMaths(), name='generate_gm')
generate_gm.inputs.op_string = '-thr 2 -uthr 2 -bin'
workflow.connect(fast, 'tissue_class_map', generate_gm, 'in_file')

generate_wm = np_pe.Node(interface=np_fsl.ImageMaths(), name='generate_wm')
generate_wm.inputs.op_string = '-thr 3 -uthr 3 -bin'
workflow.connect(fast, 'tissue_class_map', generate_wm, 'in_file')

external_stats = np_pe.Node(interface=np_fsl.ImageStats(), 
                            name='external_stats')
external_stats.inputs.op_string = '-k %s -R -r -m -s -v'
workflow.connect(reorient, 'out_file', external_stats, 'in_file')
workflow.connect(generate_external, 'out_file', external_stats, 'mask_file')

brain_stats = np_pe.Node(interface=np_fsl.ImageStats(), name='brain_stats')
brain_stats.inputs.op_string = '-k %s -R -r -m -s -v'
workflow.connect(reorient, 'out_file', brain_stats, 'in_file')
workflow.connect(bet, 'mask_file', brain_stats, 'mask_file')

csf_stats = np_pe.Node(interface=np_fsl.ImageStats(), name='csf_stats')
csf_stats.inputs.op_string = '-k %s -R -r -m -s -v'
workflow.connect(reorient, 'out_file', csf_stats, 'in_file')
workflow.connect(generate_csf, 'out_file', csf_stats, 'mask_file')

gm_stats = np_pe.Node(interface=np_fsl.ImageStats(), name='gm_stats')
gm_stats.inputs.op_string = '-k %s -R -r -m -s -v'
workflow.connect(reorient, 'out_file', gm_stats, 'in_file')
workflow.connect(generate_gm, 'out_file', gm_stats, 'mask_file')

wm_stats = np_pe.Node(interface=np_fsl.ImageStats(), name='wm_stats')
wm_stats.inputs.op_string = '-k %s -R -r -m -s -v'
workflow.connect(reorient, 'out_file', wm_stats, 'in_file')
workflow.connect(generate_wm, 'out_file', wm_stats, 'mask_file')

g = workflow.run()
for node in g.nodes():
    if node.name in ('brain_stats', 'csf_stats', 'gm_stats', 'wm_stats', 'external_stats'):
        print node.name, node.result.outputs.out_stat

sys.exit(0)

# eof
