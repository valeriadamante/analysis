#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_100 x86_64-centos7-gcc10-opt
python3 /afs/cern.ch/work/v/vdamante/public/analysis/triggerStudiesAnalysis.py --machine lxplus --channel tauTau --nTriggers 9 --sample Radion --prodMode GluGlu --reco True  --verbose 0 --mode w  --year 2016 --iter iter_0Baseline   $*
