import os
import json
import argparse
absolute_path={}
absolute_path['local'] = "/Users/valeriadamante/Desktop/Dottorato/gridui/"
absolute_path['lxplus'] = "/eos/home-v/vdamante/"
absolute_path['gridui']= "/home/users/damante/"

parser = argparse.ArgumentParser()
parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--nTriggers', required=False, type=int, default=-1)
parser.add_argument('--nEvts', required=False, type=int, default=-1)
parser.add_argument('--mass_points', required=False, type=str, default='all')
parser.add_argument('--parentDir', required=False, type=str, default='')
parser.add_argument('--verbose', required=False, type=int, default=1)
parser.add_argument('--machine', required=False,type=str, default="gridui", choices=["local", "lxplus", "gridui"])
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])
parser.add_argument('--reco', required=False, type=bool, default=False)
parser.add_argument('--Louis', required=False, type=bool, default=False)
parser.add_argument('--Test', required=False, type=bool, default=False)
parser.add_argument('--allOR', required=False, type=bool, default=False)
args = parser.parse_args()



masses = {
    "GluGlu":{
        "Radion": [250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
        "BulkGraviton":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000 ]
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
        all_masses.append(masses[args.prodMode][args.sample][int(i)])
else:
    all_masses = masses[args.prodMode][args.sample]

print(("all_masses {} ").format(all_masses ))
all_data = {}
nEvts_used = str(args.nEvts) if args.nEvts>0 else "all"
masses_used = '_'.join(str(mass) for mass in all_masses) # if args.mass_points!= 'all' else "all"

has_Louis = '' if args.Louis == False else '_Louis'
has_AllOR= '' if args.allOR == False else '_allOR'
for mass in all_masses:
    #if(args.allOR==True):
    #    continue
    #outDir = ("{}/output/{}_{}_{}/Step_0").format(os.getcwd(), args.prodMode, args.sample, args.channel)
    dictName = ("{}/{}_{}_{}_{}Triggers_{}Evts_{}Masses{}{}.json").format(args.parentDir,args.prodMode, args.sample, args.channel, args.nTriggers, nEvts_used, mass, has_Louis, has_AllOR)
    #print(dictName)
    #dictName = ("{}/{}_{}_{}_{}Triggers_{}Evts_{}Masses{}{}.json").format(outDir,args.prodMode, args.sample, args.channel, nTriggers, nEvts_used, mass, has_Louis, has_AllOR)
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




if(args.allOR == False and args.Louis == False):
    for massValue in all_data:
        prev_eff = all_data[massValue]["best_eff"][0]
        print(("{}").format(massValue))
        #print("\n\n")
        #j=0
        for path,eff,err in zip(all_data[massValue]["best_paths"], all_data[massValue]["best_eff"], all_data[massValue]["best_eff_err"]):
            #if(prev_eff>0):
                #print(("\t {} \t {} \t {} \t {}").format(str(path), str(eff).replace('.',','), str(err).replace('.',','), str(eff-prev_eff).replace('.',',')))
            #else:
            #print(("\t {} \t {} \t {}").format(str(path), str(eff).replace('.',','), str(err).replace('.',',')))
            #if(j==0):
            #    print(("baseline \t {} \t {}").format(str(eff).replace('.',','), str(err).replace('.',',')))
            #else:
            print(("\t {} \t {} \t {}").format(str(path), str(eff).replace('.',','), str(err).replace('.',',')))
            #j=j+1
        print()
elif (args.allOR==True and args.Louis == False):
    #dictName = ("{}/{}_{}_{}_{}Triggers_{}Evts_allMasses{}{}.json").format(args.parentDir,args.prodMode, args.sample, args.channel, args.nTriggers, nEvts_used, has_Louis, has_AllOR)
    #with open(dictName, 'r') as fp:
    #    all_data=json.load(fp)
    #    print(dictName)
    for massValue in all_data:
        print(("{}").format(massValue))
        #for path,eff,err in zip(all_data[massValue]["best_paths"], all_data[massValue]["best_eff"], all_data[massValue]["best_eff_err"]):
        print("\n\n\n\n\n\n\n\n")
        print(("{} \t {}").format(str(all_data[massValue]["best_eff"][0]).replace('.',','), str(all_data[massValue]["best_eff_err"][0]).replace('.',',')))
        print()
elif (args.Louis == True and args.allOR == False):
    #dictName = ("{}/{}_{}_{}_{}Triggers_{}Evts_allMasses{}{}.json").format(args.parentDir,args.prodMode, args.sample, args.channel, args.nTriggers, nEvts_used, has_Louis, has_AllOR)
    #with open(dictName, 'r') as fp:
    #    all_data=json.load(fp)
    #    print(dictName)
    for massValue in all_data:
        print(("{}").format(massValue))
        best_paths = all_data[massValue]["best_paths"][0].split(" == 1  ||  ")
        #print(len(best_paths))
        for k in range(0, len(best_paths)):
            if(k ==(len(best_paths)-1)):
                print(("{} \t {} \t {} ").format(best_paths[k], str(all_data[massValue]["best_eff"][0]).replace('.',','), str(all_data[massValue]["best_eff_err"][0]).replace('.',',')))
            else:
                print(("{}").format(best_paths[k]))
        #    print(("{} \t {}").format(str(eff).replace('.',','), str(err).replace('.',',')))
        #    print("\n\n\n\n\n\n\n\n\n\n")
        print()
else:
    print("louis and allor true is not possible")
