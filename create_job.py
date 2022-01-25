#  we need to run the command time python3 triggerStudiesAnalysis.py --machine gridui  --channel tauTau --nTriggers 10 --sample Radion --prodMode GluGlu --reco True  --verbose 0 --mode w --masses_points all --

import argparse
import os
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--year', required=False, type=int, default=2018, choices=[2016, 2017, 2018])
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--iter', required=False, type=str, default='iter_0', choices=['iter_0','iter_0Baseline', 'iter_1','iter_2','iter_2Ext', 'allOR', 'Louis','baseline','recomLouis'])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])
parser.add_argument('--mass_points', required=False, type=str, default='all')
parser.add_argument('--best_path_baseline', required=False, type=str, default='') #insert path separated by comma
parser.add_argument('--nTriggers', required=False, type=int, default=-1)
parser.add_argument('--Louis', required=False, type=bool, default=False)
parser.add_argument('--allOR', required=False, type=bool, default=False)
parser.add_argument('--max-runtime', required=False, type=float, default=6, help="max runtime in hours")
parser.add_argument('--mass_ordered', required=False, type=bool, default=False)
args = parser.parse_args()
masses = {
    "GluGlu":{
        "Radion":{
            "2016":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 800, 900],
            "2017":[250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
            "2018":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],

        },
        "BulkGraviton":{
            "2016":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 750, 800],
            "2017":[250, 260, 270, 280, 350, 400, 450, 550, 600, 650, 750, 800],
            "2018":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000 ]
        },
    },
    "VBF": {
        "Radion": [250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 3000],
        "BulkGraviton": [ 250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 600, 650, 700, 750, 850, 900, 1000, 1200, 1750, 2000]
    }
}
mass_pts = len(masses[args.prodMode][args.sample][str(args.year)])
n_masses = str(mass_pts) if args.mass_points=="all" else args.mass_points
print(n_masses)



outDir = ("/afs/cern.ch/work/v/vdamante/public/analysis/output/{}_{}_{}_{}").format(args.prodMode, args.sample, args.channel, args.year)
if not os.path.exists(outDir):
    os.makedirs(outDir)

Louis = "--Louis True" if args.Louis == True else ""
allOR = "--allOR True" if args.allOR == True else ""
best_paths = ("--best_path_baseline {}").format(args.best_path_baseline) if args.best_path_baseline!= '' else ""

run_script = '''#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_100 x86_64-centos7-gcc10-opt
python3 /afs/cern.ch/work/v/vdamante/public/analysis/triggerStudiesAnalysis.py --machine lxplus --channel {0} --nTriggers {1} --sample {2} --prodMode {3} --reco True  --verbose 0 --mode w {4} --year {5} --iter {6} {7} {8} $*
'''.format(args.channel, args.nTriggers, args.sample, args.prodMode,best_paths, args.year, args.iter, Louis, allOR)

print(run_script)

script_file = os.path.join(outDir, ('run_TSA_{}.sh').format(args.iter))
with open(script_file, 'w') as f:
    f.write(run_script)
os.chmod(script_file, 0o744)

max_runtime_seconds = int(args.max_runtime * 60 * 60)
all_mass_idx = [i for i in range(0, len(masses[args.prodMode][args.sample][str(args.year)]))] if(args.mass_points=='all') else args.mass_points.split(',')

directories = ['log', 'out', 'err', 'sub']

for dir in directories:
    complete_dir = ('{}/{}').format(outDir, dir)
    if not os.path.exists(complete_dir):
        os.makedirs(complete_dir)

if(args.mass_ordered == True):
    print(all_mass_idx)
    for mass_idx in all_mass_idx:
        condor_job = '''
            executable              = {0}
            arguments               = --mass_point {1}
            log                     = {2}/log/file_{4}_Mass{1}.log
            output                  = {2}/out/file_{4}_Mass{1}.out
            error                   = {2}/err/file_{4}_Mass{1}.err
            +MaxRuntime             = {3}
            x509userproxy           = /afs/cern.ch/work/v/vdamante/public/analysis/x509up_u127699
            RequestCPUs             = 4
            queue 1
            '''.format(script_file, mass_idx, outDir, max_runtime_seconds,args.iter)
        print(masses[args.prodMode][args.sample][str(args.year)][int(mass_idx)])
        sub_file = os.path.join(outDir, ('sub/tsa_{}_Mass{}.sub').format(args.iter, masses[args.prodMode][args.sample][str(args.year)][int(mass_idx)]))
        with open(sub_file, 'w') as f:
            f.write(condor_job)
        batch_name = ('{}{}{}{}{}').format(args.prodMode,args.sample,args.year,args.channel,args.iter.replace('_',''))
        print(('condor_submit -batch-name {} {}').format(batch_name, sub_file))
        subprocess.call([('condor_submit -batch-name {} {}').format(batch_name, sub_file)],shell=True)
else:
    condor_job = '''
    executable              = {0}
    arguments               = --mass_point $(ProcId)
    log                     = {1}/log/file_$(ClusterId).$(ProcId).log
    output                  = {1}/out/file_$(ClusterId).$(ProcId).out
    error                   = {1}/err/file_$(ClusterId).$(ProcId).err
    +MaxRuntime             = {2}
    x509userproxy           = /afs/cern.ch/work/v/vdamante/public/analysis/x509up_u127699
    RequestCPUs             = 4
    queue {3}
    '''.format(script_file, outDir, max_runtime_seconds, n_masses)
    #print(condor_job)
    sub_file = os.path.join(outDir, ('sub/tsa_{}.sub').format(args.iter))
    with open(sub_file, 'w') as f:
        f.write(condor_job)
    batch_name = ('{}{}{}{}{}').format(args.prodMode,args.sample,args.year,args.channel,args.iter.replace('_',''))
    print(('condor_submit -batch-name {} {}').format(batch_name, sub_file))

    subprocess.call([('condor_submit -batch-name {} {}').format(batch_name, sub_file)],shell=True)
    #subprocess.call(['condor_submit -batch-name {} {}'.format(args.channel + args.suffix, sub_file)], shell=True)
