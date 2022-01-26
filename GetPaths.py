import os
import json
import argparse
outdir_dict={}
outdir_dict['local'] = "/Users/valeriadamante/Desktop/Dottorato/public/analysis/output/"
outdir_dict['lxplus'] = "/afs/cern.ch/work/v/vdamante/public/analysis/output/"
outdir_dict['gridui']= "/home/users/damante/"

parser = argparse.ArgumentParser()

parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--year', required=False, type=int, default=2018, choices=[2016, 2017, 2018])
parser.add_argument('--iter', required=False, type=str, default='iter_0', choices=['iter_0', 'iter_1','iter_2','iter_2Ext', 'allOR', 'iter_0Baseline', 'Louis','baseline','recomLouis'])
parser.add_argument('--iter_diff', required=False, type=str, default='iter_0', choices=['iter_0', 'iter_1','iter_2','iter_2Ext', 'allOR', 'iter_0Baseline', 'Louis','baseline','recomLouis'])
parser.add_argument('--nEvts', required=False, type=int, default=-1)
parser.add_argument('--mass_points', required=False, type=str, default='0')
parser.add_argument('--verbose', required=False, type=int, default=1)
parser.add_argument('--machine', required=False,type=str, default="gridui", choices=["local", "lxplus", "gridui"])
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--mode', required=False, type=str, default="w", choices = ["w", "a"])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])

args = parser.parse_args()



masses = {
    "GluGlu":{
        "Radion":{
            #"2016":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 800, 900],
            "2016":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600,  800, 900],
            "2017":[250, 260, 270, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
            #"2017":[250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
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
all_masses = []
if(args.mass_points!='all'):
    for i in args.mass_points.split(','):
        #print(("mass {} is {}").format(i, masses[args.prodMode][args.sample][int(i)]))
        all_masses.append(masses[args.prodMode][args.sample][str(args.year)][int(i)])
else:
    all_masses = masses[args.prodMode][args.sample][str(args.year)]

#print(("all_masses {} ").format(all_masses ))

general_prefix =  ('{}_{}_{}').format(args.prodMode, args.sample, args.channel)
years = ['2016','2017', '2018']
channels = ['eTau', 'muTau', 'tauTau']
all_data = {}
prefix = {}
outDir_dict = {}
for ch in channels:
    prefix[ch] = {}
    for y in years:
        prefix[ch][y] = {}
        outDir_dict[y] = ('{}/{}_{}/').format(outdir_dict[args.machine], general_prefix,y)

nTriggers_dict = {'iter_0': 10, 'iter_1': 10, 'iter_2': 0, 'iter_2Ext': 0, 'Louis':10, 'nonRes': 0, 'allOR': 525}
#nTriggers_dict = {'iter_2': 0, 'iter_2Ext': 0, 'Louis':10, 'nonRes': 0, 'allOR': 525}
outDir = outDir_dict[str(args.year)]
options = ['iter_0','iter_0Baseline', 'iter_1','iter_2','iter_2Ext', 'allOR', 'Louis','baseline','recomLouis']

for opt in options:
    for ch in channels:
        for y in years:
            prefix[ch][y][opt] = ('{}With_{}/{}_').format(outDir_dict[y], opt, general_prefix) #if i == 'iter_0' or i== 'allOR' else ''


all_data = {}
all_data_iter_diff = {}
nEvts_used = str(args.nEvts) if args.nEvts>0 else "all"
masses_used = '_'.join(str(mass) for mass in all_masses) # if args.mass_points!= 'all' else "all"


for mass in all_masses:
    iter_diff_dictName = ("{}{}Evts_{}Masses.json").format(prefix[args.channel][str(args.year)][args.iter_diff], nEvts_used, mass)
    dictName = ("{}{}Evts_{}Masses.json").format(prefix[args.channel][str(args.year)][args.iter], nEvts_used, mass)
    #print(dictName, iter_diff_dictName)
    #print(dictName)
    with open(dictName, 'r') as fp:
        lines = fp.read().replace('}{\"M', ', \"M')
        #print(lines)
    with open(dictName, 'w') as fp:
        fp.write(lines)
    with open(dictName, 'r') as fp:
        data=json.load(fp)
        #print(data)
    for k in data:
        all_data[k] = data[k]
    with open(iter_diff_dictName, 'r') as fp:
        lines = fp.read().replace('}{\"M', ', \"M')
        #print(lines)
    with open(iter_diff_dictName, 'w') as fp:
        fp.write(lines)
    with open(iter_diff_dictName, 'r') as fp:
        iter_diff_data=json.load(fp)
        #print(data)
    for k in iter_diff_data:
        all_data_iter_diff[k] = iter_diff_data[k]


diff_type_array = ['pp', 'fp', 'pf', 'ff', 'b','no']

diff_type_dict = {
    "iter_0":{
        "iter_0": 'no',
        "iter_0Baseline": "b",
        "iter_1": "b",
        "iter_2": "pf",
        "iter_2Ext": "pf",
        "baseline": "pf",
        "allOR":"pf",
        "Louis":"pf",
        "recomLouis":"pf",
    },
    "iter_0Baseline":{
        "iter_0Baseline": 'no',
        "iter_0": "b",
        "iter_1": "b",
        "iter_2": "pf",
        "iter_2Ext": "pf",
        "baseline": "pf",
        "allOR":"pf",
        "Louis":"pf",
        "recomLouis":"pf",
    },
    "iter_1":{
        "iter_1": 'no',
        "iter_0": "b",
        "iter_0Baseline": "b",
        "iter_2": "pf",
        "iter_2Ext": "pf",
        "baseline": "pf",
        "allOR":"pf",
        "Louis":"pf",
        "recomLouis":"pf",
    },
    "iter_2":{
        "iter_2": 'no',
        "iter_0": "fp",
        "iter_0Baseline": "fp",
        "iter_1": "b",
        "iter_2Ext": "b",
        "baseline": "ff",
        "allOR":"ff",
        "Louis":"ff",
        "recomLouis":"ff",
    },
    "iter_2Ext":{
        "iter_2Ext": 'no',
        "iter_0": "fp",
        "iter_0Baseline": "fp",
        "iter_1": "fp",
        "iter_2": "b",
        "baseline": "pf",
        "allOR":"pf",
        "Louis":"pf",
        "recomLouis":"pf",
    },
    "baseline":{
        "baseline": 'no',
        "iter_0":"fp",
        "iter_0Baseline":"fp",
        "iter_1":"fp",
        "iter_2":"fp",
        "iter_2Ext":"fp",
        "allOR":"ff",
        "Louis":"ff",
        "recomLouis":"ff",
    },
    "allOR":{
        "allOR": 'no',
        "iter_0Baseline":"fp",
        "iter_0":"fp",
        "iter_1":"fp",
        "iter_2":"ff",
        "iter_2Ext":"ff",
        "baseline":"ff",
        "Louis":"ff",
        "recomLouis":"ff",
    },
    "Louis":{
        "baseline": 'ff',
        "iter_0Baseline":"fp",
        "iter_0":"fp",
        "iter_1":"fp",
        "iter_2":"ff",
        "iter_2Ext":"ff",
        "allOR":"ff",
        "Louis":"no",
        "recomLouis":"ff",
    },
    "recomLouis":{
        "baseline": 'ff',
        "iter_0":"fp",
        "iter_0Baseline":"fp",
        "iter_1":"fp",
        "iter_2":"ff",
        "iter_2Ext":"ff",
        "allOR":"ff",
        "Louis":"ff",
        "recomLouis":"no",
    }

}

diff_type = diff_type_dict[args.iter][args.iter_diff]
#print(("diffType is {}").format(diff_type))
if(diff_type =='fp'): # end of the current iter and point by point with the iter diff
    #for k in all_data[('M-{}').format(all_masses[0])]["best_paths"][final_idx].split(" == 1  ||  "):
        #k=k.replace(" == 1 ", " ")
        #best_paths_array.append(k)
    for massValue in all_data:
        final_idx =  ( len(all_data[massValue]["best_paths"]) -2) if (str(args.year)=='2018' and args.iter=='iter_1' and args.channel=='tauTau') else  ( len(all_data[massValue]["best_paths"]) -1)
        best_paths_iter_diff = all_data_iter_diff[massValue]["best_paths"]
        final_idx_iterdiff =(len(best_paths_iter_diff)-2) if (str(args.year)=='2018' and args.iter_diff=='iter_1' and args.channel=='tauTau') else  (len(best_paths_iter_diff)-1)
        #best_paths = (','.join(best_paths_array))
        print(("{}").format(massValue))
        #if(final_idx_iterdiff<5 ):
        #    print("\n\n\n\n\n\n\n\n")
        for iterdiff_idx in range(0, len(best_paths_iter_diff)):
            if(str(args.year)=='2018' and args.iter_diff=='iter_1' and args.channel=='tauTau'):
                if(iterdiff_idx==10): break
            number = all_data_iter_diff[massValue]["best_eff"][iterdiff_idx]-all_data[massValue]["best_eff"][final_idx]
            number_str = str(number).replace('.',',')
            if(iterdiff_idx == final_idx_iterdiff ):
                print(("{} \t {}").format(str(all_data[massValue]["best_eff"][final_idx]).replace('.',','),  number_str))
            else:
                print(("\t \t {}").format( number_str ))
        print()
elif( diff_type=='pf' ):
    for massValue in all_data:
        best_paths_iter_diff=all_data_iter_diff[massValue]["best_paths"]
        final_idx_iterdiff =(len(best_paths_iter_diff)-2) if (str(args.year)=='2018' and args.iter_diff=='iter_1' and args.channel=='tauTau') else  (len(best_paths_iter_diff)-1)
        best_paths = all_data[massValue]["best_paths"]
        print(("{}").format(massValue))
        for iter_idx in range(0, len(best_paths)):
            if(str(args.year)=='2018' and args.iter=='iter_1' and args.channel=='tauTau'):
                if(iter_idx==10): break
            number = all_data_iter_diff[massValue]["best_eff"][final_idx_iterdiff]-all_data[massValue]["best_eff"][iter_idx]
            number_str = str(number).replace('.',',')
            final_idx =  ( len(all_data[massValue]["best_paths"]) -2) if (str(args.year)=='2018' and args.iter=='iter_1' and args.channel=='tauTau') else  ( len(all_data[massValue]["best_paths"]) -1)
            if(iter_idx == final_idx ):
                print(("{}  \t {}").format(str(all_data[massValue]["best_eff"][final_idx]).replace('.',','), number_str))
            else:
                print(("\t \t {}").format( number_str ))
        print()
elif( diff_type=='ff' ):
    for massValue in all_data:
        best_paths_iter_diff=all_data_iter_diff[massValue]["best_paths"]
        final_idx_iterdiff =(len(best_paths_iter_diff)-2) if (str(args.year)=='2018' and args.iter_diff=='iter_1' and args.channel=='tauTau') else  (len(best_paths_iter_diff)-1)
        final_idx =  ( len(all_data[massValue]["best_paths"]) -2) if (str(args.year)=='2018' and args.iter=='iter_1' and args.channel=='tauTau') else  ( len(all_data[massValue]["best_paths"]) -1)
        #print(final_idx, final_idx_iterdiff)
        best_paths = all_data[massValue]["best_paths"]
        print(("{}").format(massValue))
        spaces_idx = final_idx if final_idx>5 else 9
        #for i in range(0,spaces_idx):
        #    print()
        number = all_data_iter_diff[massValue]["best_eff"][final_idx_iterdiff]-all_data[massValue]["best_eff"][final_idx]
        number_str = str(number).replace('.',',')
        print(("{} \t {}").format(str(all_data[massValue]["best_eff"][final_idx]).replace('.',','), number_str))

        print()
else:
    for massValue in all_data:
        prev_eff = all_data[massValue]["best_eff"][0]
        final_idx_iterdiff = ( len(all_data_iter_diff[massValue]["best_paths"]) -2) if (str(args.year)=='2018' and args.iter_diff=='iter_1' and args.channel=='tauTau') else  ( len(all_data_iter_diff[massValue]["best_paths"]) -1)
        print(("{}").format(massValue))
        #if(args.iter=='iter_2Ext'):
        #    print("\n\n\n\n\n\n\n")
        for path,eff in zip(all_data[massValue]["best_paths"], all_data[massValue]["best_eff"]):
            k=all_data[massValue]["best_paths"].index(path)
            if(str(args.year)=='2018' and (args.iter=='iter_1' or args.iter_diff=='iter_1') and args.channel=='tauTau'):
                if(k==10): break
            difference_pf = eff-all_data_iter_diff[massValue]["best_eff"][final_idx_iterdiff]
            difference_pf_str = str(difference_pf).replace('.',',')
            #print(k)
            difference_pp = eff-all_data_iter_diff[massValue]["best_eff"][k]
            difference_pp_str = str(difference_pp).replace('.',',')
            #if(prev_eff>0):
                #print(("\t {} \t {} \t {}").format(str(path), str(eff).replace('.',','),  str(eff-prev_eff).replace('.',',')))
            #else:
            if(diff_type=='no'):
                if(len(all_data[massValue]["best_paths"])<5 or final_idx_iterdiff < 5):
                    print("\n\n\n\n\n\n\n")
                path2 = path
                path = 'baseline' if " == 1" in path2 else path2
                print(("\t {} \t {} \t {} ").format(str(path), str(eff).replace('.',',')))
            else:
                #if(len(all_data[massValue]["best_paths"])<5 and final_idx_iterdiff < 5):
                #    print("\n\n\n\n\n\n\n")
                if(k==0):
                    print(("\t baseline \t {} \t {} \t {}").format(str(eff).replace('.',',') difference_pp_str, difference_pf_str))
                else:
                    print(("\t {} \t {} \t {} \t {}").format(str(path), str(eff).replace('.',',')  difference_pp_str, difference_pf_str))
        print()
