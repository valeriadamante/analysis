#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_100 x86_64-centos7-gcc10-opt
echo python3 /home/users/damante/analysis/triggerStudiesAnalysis.py --machine gridui  $*
