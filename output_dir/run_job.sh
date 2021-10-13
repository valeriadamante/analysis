#!/bin/sh
cd "/home/users/damante/analysis/output_dir"
echo "Job started at $(date --rfc-3339=seconds)." >> run_job.log
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_100 x86_64-centos7-gcc10-opt 
/usr/bin/time --verbose /home/users/damante/analysis/test.sh --channel tauTau --nTriggers 10 --sample Radion --prodMode GluGlu --reco True --verbose 0 --best_path_baseline HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg,HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1,HLT_PFMETNoMu120_PFMHTNoMu120_IDTight --masses_values 900 &>> run_job.log
RESULT=$?
if [ $RESULT -eq 0 ] ; then
    MSG="successfully ended"
else
    MSG="failed"
fi
echo "Job $MSG at $(date --rfc-3339=seconds)." >> run_job.log
