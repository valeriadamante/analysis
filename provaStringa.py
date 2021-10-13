import csv
import ROOT
import json
import pandas
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--nTriggers', required=False, type=int, default=-1)
parser.add_argument('--nEvts', required=False, type=int, default=-1)
parser.add_argument('--masses_values', required=False, type=str, default='')
parser.add_argument('--best_path_baseline', required=False, type=str, default='') #insert path separated by comma
parser.add_argument('--verbose', required=False, type=int, default=1)
parser.add_argument('--machine', required=False,type=str, default="gridui", choices=["local", "lxplus", "gridui"])
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--mode', required=False, type=str, default="w", choices = ["w", "a"])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])
parser.add_argument('--reco', required=False, type=bool, default=False)
parser.add_argument('--Louis', required=False, type=bool, default=False)
parser.add_argument('--Test', required=False, type=bool, default=False)
parser.add_argument('--allOR', required=False, type=bool, default=False)

args = parser.parse_args()

absolute_path={}
absolute_path['local'] = "/Users/valeriadamante/Desktop/Dottorato/"
absolute_path['lxplus'] = "/eos/home-v/vdamante/"
absolute_path['gridui']= "/home/users/damante/"


masses = {
    "GluGlu":{
        "Radion":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
        "BulkGraviton":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000 ]
    },
    "VBF": {
        "Radion": [250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 3000],
        "BulkGraviton": [ 250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 600, 650, 700, 750, 850, 900, 1000, 1200, 1750, 2000]
    }
}
if(args.Test == True or args.masses_values != ''):
    masses[args.prodMode][args.sample]=[int(i) for i in args.masses_values.split(',')]
    if(args.verbose>VerbosityLevel.medium):
        print(("masses {} ").format(masses[args.prodMode][args.sample]))

# lumi trigger dict --> this dict has the effective luminosity (HLT Prescale)
lumiTrigger_dict_path  = ('{}trigger_info/TriggerLumi_2018.json').format(absolute_path[args.machine])
with open(lumiTrigger_dict_path, 'r') as f:
    lumiTrigger_dict = json.load(f)

# L1 seeds csv file and dict --> this is a CSV with the L1 seeds for each HLT path
l1Seeds_csv  = ('{}trigger_info/triggers_prompt_2018_L1seeds_319991.csv').format(absolute_path[args.machine])
l1Seeds_dict = {}




trig_types = ['prompt']
triggers = {}
for trig_type in trig_types:
    trigger_dict = ('{}/trigger_info/triggers_{}_2018.json').format(absolute_path[args.machine],trig_type)
    with open(trigger_dict, 'r') as f:
        trig_list = json.load(f)
        for trig_desc in trig_list:
            if trig_desc['dataset'] in [ 'NotFound', 'HcalNZS' ]: continue
            name = trig_desc['path']
            if name.endswith('_v'):
                name = name[:-2]
            if name in [ 'HLT_Random', 'HLT_Physics' ]: continue
            if name in triggers:
                raise RuntimeError('Duplicated trigger path = "{}"'.format(name))
            trig_desc['trig_type'] = trig_type
            triggers[name] = trig_desc

# ****** function to load file for each mass value ******
def load_file(mass):
    if(args.machine == 'gridui'):
        dictFile = ("{}_{}.json").format(args.prodMode, args.sample)
        with open(dictFile, 'r') as fp:
            data = json.load(fp)
        files = data[('M-{}').format(mass)]
    elif(args.machine == 'lxplus' or args.machine == 'local'):
        files = absolute_path[args.machine]+("/rootfiles/signalRadionTest{}.root").format(mass)
        print(files)
    #files = ('{}/rootfiles/radionSignalTest.root').format(absolute_path[args.machine])
    df = ROOT.RDataFrame('Events', files)
    return df


# find L1 Missing Paths in nano AOD
#for mass in masses[args.prodMode][args.sample]:
mass = 300
print(("evaluating for mass {}").format(mass))

#  1. Define dataframe and define columns

df = load_file(mass)
# this was for debugging

df_initial = df

columns = sorted([ str(c) for c in df.GetColumnNames() ])
hlt_columns = [c for c in columns if c.startswith('HLT') and c in triggers]

l1Prescale_dict_path  = ('{}trigger_info/L1Prescale_2018_1p7e34.json').format(absolute_path[args.machine])
with open(l1Prescale_dict_path, 'r') as f:
    l1Prescale_dict = json.load(f)

columns = df.GetColumnNames()
missing_l1_columns = [L1Col for L1Col in l1Prescale_dict if L1Col not in columns ]
print("missing l1 columns")
print(missing_l1_columns)

# now find all HLT paths containing those columns
k=0
with open(l1Seeds_csv) as f2:
    csv_reader = csv.reader(f2)
    previous_path = ''
    previous_version = 0
    for l in csv_reader:
      if(len(l)<2):
          continue
      #if(k>30):
      #     continue
      path = l[0]
      #print(path)
      pos = path.rfind('_v')
      if pos>0:
          version = path[pos:]
          path = path.replace(version, '')
          version = version.replace('_v', '')
          #print(("current path is {}, current version is {}, previous path is {}, previous version is {}").format(path, version, previous_path, previous_version))
          if(path != previous_path):
              previous_path = path
              previous_version = version
          else:
              if(version > previous_version):
                  previous_version = version
      if(l[1]=='OR'):
          l1Seeds_dict[path] = l[2].split()
      else:
          if(l[2].rfind('bit')>0):
              continue
          l1Seeds_dict[path] = []
          l1Seeds_dict[path].append(l[2])
      k+=1
print(l1Seeds_dict)
'''
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

HLT_columns_L1_missing_columns = {}
for hltCol in l1Seeds_dict:
    if(hltCol not in hlt_columns): continue
    HLT_columns_L1_missing_columns[hltCol] = []
    for l1missingCol in missing_l1_columns:
        if(l1missingCol in l1Seeds_dict[hltCol]):
            HLT_columns_L1_missing_columns[hltCol].append(l1missingCol)
    if(len(HLT_columns_L1_missing_columns[hltCol])==0):
        HLT_columns_L1_missing_columns = removekey(HLT_columns_L1_missing_columns, hltCol)
print("hlt path with missing columns")
print(HLT_columns_L1_missing_columns)
#with open('/Users/valeriadamante/Desktop/Dottorato/trigger_info/L1Prescale_2018_1p7e34.json', 'w') as fp:


pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df = pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df.head()
df_new = df.loc[1:, [1,5]]
df_new.head()
df_new.to_json(r'/Users/valeriadamante/Desktop/Dottorato/trigger_info/L1Prescale_2018_1p7e34.json')
for i in df:
	print(i)
df.to_json(r'prova.json')
exit()
import pandas
df = pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df_new = df.loc[2:, [1,3]]
df_new.head()
df_new.to_json(r'prova.json')
exit()
import pandas
df = pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df_new.to_json(r'/Users/valeriadamante/Desktop/Dottorato/trigger_info/L1Prescale_2018_1p7e34.json')
df_new.head()
df_new = df.loc[2:, [1,3]]
dict = {}
for row in df_new.rows:
	print(row)
for index, row in df.iterrows():
    print(row['c1'], row['c2'])
for index, row in df.iterrows():
	print(row)
	print(row[1])
for index, row in df.iterrows():
	print(row[1])
for index, row in df_new.iterrows():
	print(row[1])
for index, row in df_new.iterrows():
	dict(row[1])=row[3]
for index, row in df_new.iterrows():
	dict[row[1]]=row[5]
print(dict)
import json
with open('data.json', 'w') as fp:
    json.dump(dict, fp)
exit()

import pandas
import json
pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df = pandas.read_excel('/Users/valeriadamante/Desktop/Dottorato/trigger_info/PrescaleTable-1_L1Menu_Collisions2018_v2_1_0.xlsx', index_col=None, header=None, engine='openpyxl')
df.head()
df_new = df.loc[1:, [1,5]]
df_new.head()
dict ={}
for index, row in df_new.iterrows():
dict[row[1]]=row[5]

print(dict)
with open('/Users/valeriadamante/Desktop/Dottorato/trigger_info/L1Prescale_2018_1p7e34.json', 'w') as fp:
json.dump(dict, fp)

l1Seeds_csv  = "/Users/valeriadamante/Desktop/Dottorato/trigger_info/triggers_prompt_2018_L1seeds_325022.csv"
trig_types = ['prompt']
triggers = {}
for trig_type in trig_types:
trigger_dict = ('/Users/valeriadamante/Desktop/Dottorato/trigger_info/triggers_{}_2018.json').format(trig_type)
with open(trigger_dict, 'r') as f:
    trig_list = json.load(f)
    for trig_desc in trig_list:
        if trig_desc['dataset'] in [ 'NotFound', 'HcalNZS' ]: continue
        name = trig_desc['path']
        if name.endswith('_v'):
            name = name[:-2]
        if name in [ 'HLT_Random', 'HLT_Physics' ]: continue
        if name in triggers:
            raise RuntimeError('Duplicated trigger path = "{}"'.format(name))
        trig_desc['trig_type'] = trig_type
        triggers[name] = trig_desc
l1Seeds_dict = {}
k=0

with open(l1Seeds_csv) as f:
csv_reader = csv.reader(f)
previous_path = ''
previous_version = 0
for l in csv_reader:
  if(len(l)<2):
      continue
  #if(k>30):
  #     continue
  path = l[0]
  #print(path)
  pos = path.rfind('_v')
  if pos>0:
      version = path[pos:]
      path = path.replace(version, '')
      version = version.replace('_v', '')
      #print(("current path is {}, current version is {}, previous path is {}, previous version is {}").format(path, version, previous_path, previous_version))
      if(path != previous_path):
          previous_path = path
          previous_version = version
      else:
          if(version > previous_version):
              previous_version = version
  if(l[1]=='OR'):
      l1Seeds_dict[path] = l[2].split()
  else:
      if(l[2].rfind('bit')>0):
          continue
      l1Seeds_dict[path] = []
      l1Seeds_dict[path].append(l[2])
  k+=1


file = '/Users/valeriadamante/Desktop/Dottorato/rootfiles/radionSignalTest.root'
df_initial = ROOT.RDataFrame('Events', file)
df = df_initial
columns = sorted([ str(c) for c in df.GetColumnNames() ])
hlt_columns = [c for c in columns if c.startswith('HLT') and c in triggers]
for col in hlt_columns:
if(l1Seeds_dict.get(col)==None):
    print(("column not found {}").format(col))

'''
