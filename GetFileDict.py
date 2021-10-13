import os
import json
import argparse

initial_path = '/gpfs/ddn/srm/cms/store/mc/RunIIAutumn18NanoAODv7/'
parser = argparse.ArgumentParser()
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])
args = parser.parse_args()
absolute_path={}
absolute_path['local'] = "/Users/valeriadamante/Desktop/Dottorato/"
absolute_path['lxplus'] = "/eos/home-v/vdamante/"
absolute_path['gridui']= "/home/users/damante/"

prefix = ("{}To{}ToHHTo2B2Tau_M-").format(args.prodMode, args.sample)
suffix = "_narrow_TuneCP5_PSWeights_13TeV-madgraph-pythia8"
masses = {
    "GluGlu":{
        #,
        "Radion":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
        "BulkGraviton":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000 ]
    },
    "VBF": {
        "Radion": [250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 3000],
        "BulkGraviton": [ 250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 600, 650, 700, 750, 850, 900, 1000, 1200, 1750, 2000]
    }
}
abs_paths=[('{}/{}{}{}').format(initial_path, prefix, mass, suffix) for mass in masses[args.prodMode][args.sample]]
#for abs_path in abs_paths:
#    print(abs_path)

files_dict = {}
for abs_path in abs_paths:
    all_files = []
    file_name = abs_path.split("_")[1]
    for i in os.listdir(abs_path):
      for j in os.listdir(('{}/{}').format(abs_path,i)):
        for k in os.listdir((('{}/{}/{}').format(abs_path,i,j))):
          for l in os.listdir(('{}/{}/{}/{}').format(abs_path,i,j,k)):
            final_string =  ('{}/{}/{}/{}/{}').format(abs_path,i,j,k,l)
            if(final_string.endswith('.root')):
                all_files.append(final_string)
            else:
                print(final_string)

    #print(all_files)
    files_dict[file_name]=all_files

#print(files_dict)

dictName = ("{}_{}.json").format(args.prodMode, args.sample)
with open(dictName, 'w') as fp:
    json.dump(files_dict, fp)

with open(dictName, 'r') as fp:
    data = json.load(fp)

#:wqprint(data['M-600'])
