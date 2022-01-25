import os
import json
import ROOT
import argparse
import math
outdir_dict={}
outdir_dict['local'] = "/Users/valeriadamante/Desktop/Dottorato/public/analysis/output/"
outdir_dict['lxplus'] = "/afs/cern.ch/work/v/vdamante/public/analysis/output/"
outdir_dict['gridui']= "/home/users/damante/"
ROOT.gStyle.SetPaintTextFormat(".2f")

parser = argparse.ArgumentParser()

parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--year', required=False, type=int, default=2018, choices=[2016, 2017, 2018])
parser.add_argument('--nEvts', required=False, type=int, default=-1)
parser.add_argument('--mass_points', required=False, type=str, default='0')
parser.add_argument('--verbose', required=False, type=int, default=1)
parser.add_argument('--machine', required=False,type=str, default="gridui", choices=["local", "lxplus", "gridui"])
parser.add_argument('--prodMode', required=False, type=str, default="GluGlu", choices = ["GluGlu", "VBF"])
parser.add_argument('--mode', required=False, type=str, default="w", choices = ["w", "a"])
parser.add_argument('--sample', required=False, type=str, default="Radion", choices = ["Radion", "BulkGraviton"])

args = parser.parse_args()
def getError(eff, num, den, sigma_num, sigma_den):
    error = eff * math.sqrt((sigma_num/num)*(sigma_num/num)+(sigma_den/den)*(sigma_den/den))
    return error

def getErrorDiff(sigma_1, sigma_2):
    error =  math.sqrt(sigma_1*sigma_1 + sigma_2*sigma_2)
    return error



masses = {
    "GluGlu":{
        "Radion":{
            "2016":[250, 260, 270, 280, 300, 320, 340, 350, 400, 450, 500, 550, 600,  800, 900],
            #"2017":[250, 260, 270, 280, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
            "2017":[250, 260, 270, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1250, 1500, 1750, 2000, 2500, 3000],
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

#nTriggers_dict = {'iter_0': 10, 'iter_1': 10, 'iter_2': 0, 'iter_2Ext': 0, 'Louis':10, 'allOR': 525}
#nTriggers_dict = {'iter_2': 0, 'iter_2Ext': 0, 'Louis':10, 'baseline': 0, 'allOR': 525}
outDir = outDir_dict[str(args.year)]
#options = ['iter_0','iter_0Baseline', 'iter_1','iter_2','iter_2Ext', 'allOR','baseline']
options = ['iter_1','iter_2','iter_2Ext', 'allOR','baseline']
if(args.channel=='tauTau' and args.year!=2016):
    options.extend(['recomLouis'])
    #options.extend(['Louis', 'recomLouis'])


for opt in options:
    for ch in channels:
        for y in years:
            prefix[ch][y][opt] = ('{}With_{}/{}_').format(outDir_dict[y], opt, general_prefix) #if i == 'iter_0' or i== 'allOR' else ''


all_data = {}
for opt in options:
    all_data[opt]={}

nEvts_used = str(args.nEvts) if args.nEvts>0 else "all"
masses_used = '_'.join(str(mass) for mass in all_masses) # if args.mass_points!= 'all' else "all"



for mass in all_masses:
    for opt in options:
        dictName = ("{}{}Evts_{}Masses.json").format(prefix[args.channel][str(args.year)][opt], nEvts_used, mass,)
        #print(dictName)
        with open(dictName, 'r') as fp:
            lines = fp.read().replace('}{\"M', ', \"M')
        with open(dictName, 'w') as fp:
            fp.write(lines)
        with open(dictName, 'r') as fp:
            data=json.load(fp)
            #if(opt == 'Louis'):
                #print(data)
        for k in data:
            all_data[opt][str(mass)] = data[k]

for opt in all_data:
    for mass in all_masses:
        for idx in range(0,len(all_data[opt][str(mass)]["best_paths"])):
            name = all_data[opt][str(mass)]["best_paths"][idx]
            if '== 1' in name:
                all_data[opt][str(mass)]["best_paths"][idx]=('baseline_{}').format(opt)

#import json
#print(json.dumps(all_data, indent=4))



types = ['efficiency', 'increase']
names={}
for ch in channels:
    names[ch] = {}
    for y in years:
        names[ch][y]={}
        names[ch][y]['histTitle']= ['Trigger efficiency', 'Differences w.r.t. baseline']
        names[ch][y]['xAxisTitle']='m_{X} (GeV/c^{2})'
        names[ch][y]['yAxisTitle']=['#epsilon', '#epsilon - #epsilon_{b}']
        names[ch][y]['x_min']=all_masses[0]-100
        names[ch][y]['x_max']=all_masses[(len(all_masses)-1)]+100
        names[ch][y]['y_min']=[0.1, -0.1]
        names[ch][y]['y_max']=[1, 0.8]
        names[ch][y]['outFile']=[('plots/{}/eff_{}_{}').format(args.year, args.channel, args.year),('plots/{}/diff_{}_{}').format(args.year, args.channel, args.year)]
        names[ch][y]['position_legend']=[0.11,0.11,0.2 ,0.2, 0.42,0.8,0.5 ,0.89]

names['eTau']['2016']['y_min'][0] = 0
names['eTau']['2016']['y_max'][0] = 1.75
names['eTau']['2016']['y_min'][1] = -0.5
names['eTau']['2016']['y_max'][1] = 1

names['muTau']['2016']['y_min'][0] = 0.3
names['muTau']['2016']['y_max'][0] = 1.5
names['muTau']['2016']['y_min'][1] = -0.4
names['muTau']['2016']['y_max'][1] = 0.55


names['tauTau']['2016']['y_min'][0] = 0.
names['tauTau']['2016']['y_max'][0] = 1.01
names['tauTau']['2016']['y_min'][1] = -0.05
names['tauTau']['2016']['y_max'][1] = 0.8

names['eTau']['2016']['position_legend']=[0.55,0.7,0.7,0.89, 0.6,0.7,0.75 ,0.89]
names['muTau']['2016']['position_legend']=[0.55,0.7,0.7 ,0.89, 0.6,0.7,0.75 ,0.89]
names['tauTau']['2016']['position_legend']=[0.55,0.7,0.7 ,0.89, 0.6,0.7,0.75 ,0.89]



names['eTau']['2017']['y_min'][0] = 0.
names['eTau']['2017']['y_max'][0] = 1.22
names['eTau']['2017']['y_min'][1] = -0.05
names['eTau']['2017']['y_max'][1] = 0.6
names['eTau']['2017']['position_legend']=[0.12,0.18,0.35,0.35, 0.12,0.72,0.35 ,0.89]

names['muTau']['2017']['y_min'][0] = 0.
names['muTau']['2017']['y_max'][0] = 1.22
names['muTau']['2017']['y_min'][1] = -0.05
names['muTau']['2017']['y_max'][1] = 1
names['muTau']['2017']['position_legend']=[0.12,0.18,0.35,0.35, 0.12,0.72,0.35 ,0.89]


names['tauTau']['2017']['y_min'][0] = 0.2
names['tauTau']['2017']['y_max'][0] = 1.
names['tauTau']['2017']['y_min'][1] = -0.01
names['tauTau']['2017']['y_max'][1] = 0.65
names['tauTau']['2017']['position_legend']=[0.12,0.25,0.33,0.48, 0.12,0.62,0.35 ,0.89]


names['eTau']['2018']['y_min'][0] = 0.5
names['eTau']['2018']['y_max'][0] = 1.25
names['eTau']['2018']['y_min'][1] = -0.15
names['eTau']['2018']['y_max'][1] = 0.45
names['eTau']['2018']['position_legend']=[0.27,0.72,0.6,0.89, 0.18,0.72,0.3 ,0.89]

names['muTau']['2018']['y_min'][0] = 0.23
names['muTau']['2018']['y_max'][0] = 1.12
names['muTau']['2018']['y_min'][1] = -0.1
names['muTau']['2018']['y_max'][1] = 0.8
names['muTau']['2018']['position_legend']=[0.12,0.18,0.35,0.35, 0.12,0.72,0.35 ,0.89]


names['tauTau']['2018']['y_min'][0] = 0.2
names['tauTau']['2018']['y_max'][0] = 1.04
names['tauTau']['2018']['y_min'][1] = -0.01
names['tauTau']['2018']['y_max'][1] = 0.73
names['tauTau']['2018']['position_legend']=[0.12,0.2,0.33,0.4, 0.12,0.62,0.35 ,0.89]

colors = [ROOT.kViolet + 6,  ROOT.kGreen - 6 ,  ROOT.kAzure +6 , ROOT.kRed -7 , ROOT.kMagenta, ROOT.kBlack]
opt_titles = ['baseline', 'iter_1', 'iter_2', 'iter_2Ext']
if(args.channel=='tauTau' and args.year!=2016):
    #opt_titles.extend([ 'LLR', 'LLR + Baseline'])
    opt_titles.extend([ 'LLR + Baseline'])


#####################################
########## Efficiency Plot ##########
#####################################

all_efficiencies_baseline = []
all_efficiencies_iter_1 = []
all_efficiencies_iter_2 = []
all_efficiencies_iter_2Ext = []
all_efficiencies_allOR = []
all_efficiencies_baseline = []
all_efficiencies_Louis = []
all_efficiencies_recomLouis = []

all_efficiencies_errors_iter_1 = []
all_efficiencies_errors_iter_2 = []
all_efficiencies_errors_iter_2Ext = []
all_efficiencies_errors_allOR = []
all_efficiencies_errors_baseline = []
all_efficiencies_errors_Louis = []
all_efficiencies_errors_recomLouis = []

for mass in all_masses:
    all_efficiencies_baseline.append(all_data['baseline'][str(mass)]['best_eff'][0])
    all_efficiencies_iter_1.append(all_data['iter_1'][str(mass)]['best_eff'][0])
    all_efficiencies_iter_2.append(all_data['iter_2'][str(mass)]['best_eff'][0])
    all_efficiencies_iter_2Ext.append(all_data['iter_2Ext'][str(mass)]['best_eff'][0])
    all_efficiencies_allOR.append(all_data['allOR'][str(mass)]['best_eff'][0])
    all_efficiencies_errors_baseline.append(all_data['baseline'][str(mass)]['best_eff_err'][0])
    all_efficiencies_errors_iter_1.append(all_data['iter_1'][str(mass)]['best_eff_err'][0])
    all_efficiencies_errors_iter_2.append(all_data['iter_2'][str(mass)]['best_eff_err'][0])
    all_efficiencies_errors_iter_2Ext.append(all_data['iter_2Ext'][str(mass)]['best_eff_err'][0])
    all_efficiencies_errors_allOR.append(all_data['allOR'][str(mass)]['best_eff_err'][0])
    if(args.channel=='tauTau' and args.year!=2016):
        all_efficiencies_recomLouis.append(all_data['recomLouis'][str(mass)]['best_eff'][0])
        #all_efficiencies_Louis.append(all_data['Louis'][str(mass)]['best_eff'][0])
        all_efficiencies_errors_recomLouis.append(all_data['recomLouis'][str(mass)]['best_eff_err'][0])
        #all_efficiencies_errors_Louis.append(all_data['Louis'][str(mass)]['best_eff_err'][0])

all_efficiencies_baseline_norm = [i / j for i, j in zip(all_efficiencies_baseline, all_efficiencies_allOR)]

graphs_efficiencies = []
for o in range(0, len(opt_titles)):
    graphs_efficiencies.append(ROOT.TGraphErrors(len(all_masses)))

for k in range(0, len(all_masses)):
    for o in range(0, len(opt_titles)):
        graphs_efficiencies[o].SetPointX(k, all_masses[k])

    graphs_efficiencies[0].SetPointY(k, all_efficiencies_baseline[k])
    #graphs_efficiencies[0].SetPointY(k, all_efficiencies_baseline[k]/all_efficiencies_allOR[k])
    err_baseline = getError(all_efficiencies_baseline[k]/all_efficiencies_allOR[k], all_efficiencies_baseline[k], all_efficiencies_allOR[k],all_efficiencies_errors_baseline[k], all_efficiencies_errors_allOR[k])
    graphs_efficiencies[0].SetPointError(k,0, all_efficiencies_errors_baseline[k])
    #print(('efficiency baseline for mass {} is {} ').format(all_masses[k],all_efficiencies_baseline[k]/all_efficiencies_allOR[k]))

    graphs_efficiencies[1].SetPointY(k, all_efficiencies_iter_1[k])
    #graphs_efficiencies[1].SetPointY(k, all_efficiencies_iter_1[k]/all_efficiencies_allOR[k])
    err_iter_1 = getError(all_efficiencies_iter_1[k]/all_efficiencies_allOR[k], all_efficiencies_iter_1[k], all_efficiencies_allOR[k],all_efficiencies_errors_iter_1[k], all_efficiencies_errors_allOR[k])
    graphs_efficiencies[1].SetPointError(k,0, all_efficiencies_errors_iter_1[k])
    #print(('efficiency iter 1 for mass {} is {} ').format(all_masses[k],all_efficiencies_iter_1[k]/all_efficiencies_allOR[k]))


    graphs_efficiencies[2].SetPointY(k, all_efficiencies_iter_2[k])
    #graphs_efficiencies[2].SetPointY(k, all_efficiencies_iter_2[k]/all_efficiencies_allOR[k])
    err_iter_2 = getError(all_efficiencies_iter_2[k]/all_efficiencies_allOR[k], all_efficiencies_iter_2[k], all_efficiencies_allOR[k],all_efficiencies_errors_iter_2[k], all_efficiencies_errors_allOR[k])
    graphs_efficiencies[2].SetPointError(k,0, all_efficiencies_errors_iter_2[k])
    #print(('efficiency iter 2 for mass {} is {} ').format(all_masses[k],all_efficiencies_iter_2[k]/all_efficiencies_allOR[k]))


    graphs_efficiencies[3].SetPointY(k, all_efficiencies_iter_2Ext[k])
    #graphs_efficiencies[3].SetPointY(k, all_efficiencies_iter_2Ext[k]/all_efficiencies_allOR[k])
    err_iter_2Ext = getError(all_efficiencies_iter_2Ext[k]/all_efficiencies_allOR[k], all_efficiencies_iter_2Ext[k], all_efficiencies_allOR[k],all_efficiencies_errors_iter_2Ext[k], all_efficiencies_errors_allOR[k])
    graphs_efficiencies[3].SetPointError(k,0, all_efficiencies_errors_iter_2Ext[k])
    #print(('efficiency iter 2 ext for mass {} is {} ').format(all_masses[k],all_efficiencies_iter_2Ext[k]/all_efficiencies_allOR[k]))


    #if(len(graphs_efficiencies)>4):
    #    graphs_efficiencies[4].SetPointY(k, all_efficiencies_recomLouis[k]/all_efficiencies_allOR[k])
    #    err_recomLouis = getError(all_efficiencies_recomLouis[k]/all_efficiencies_allOR[k], all_efficiencies_recomLouis[k], all_efficiencies_allOR[k],all_efficiencies_errors_recomLouis[k], all_efficiencies_errors_allOR[k])
    #    graphs_efficiencies[4].SetPointError(k,0, err_recomLouis)
        #graphs_efficiencies[5].SetPointY(k, all_efficiencies_Louis[k]/all_efficiencies_allOR[k])
        #err_Louis = getError(all_efficiencies_Louis[k]/all_efficiencies_allOR[k], all_efficiencies_Louis[k], all_efficiencies_allOR[k],all_efficiencies_errors_Louis[k], all_efficiencies_errors_allOR[k])
        #graphs_efficiencies[5].SetPointError(k,0, err_Louis)


canvas_efficiencies=ROOT.TCanvas()
canvas_efficiencies.cd()
legend_efficiencies = ROOT.TLegend(names[args.channel][str(args.year)]['position_legend'][0], names[args.channel][str(args.year)]['position_legend'][1], names[args.channel][str(args.year)]['position_legend'][2], names[args.channel][str(args.year)]['position_legend'][3])
legend_efficiencies.SetBorderSize(0)
canvas_efficiencies.SetLogx()
for g in range(0, len(graphs_efficiencies)):
    graphs_efficiencies[g].SetMarkerColor(colors[g])
    graphs_efficiencies[g].SetLineColor(colors[g])
    graphs_efficiencies[g].SetMarkerStyle( 8 )
    graphs_efficiencies[g].SetMarkerSize( 0.4 )
    graphs_efficiencies[g].SetTitle(("{} {} {} ;{};{}").format(names[args.channel][str(args.year)]["histTitle"][0], args.channel, args.year,names[args.channel][str(args.year)]["xAxisTitle"],names[args.channel][str(args.year)]["yAxisTitle"][0]))
    graphs_efficiencies[g].GetXaxis().SetRangeUser(names[args.channel][str(args.year)]['x_min'],names[args.channel][str(args.year)]['x_max'])
    graphs_efficiencies[g].GetXaxis().SetMoreLogLabels()
    graphs_efficiencies[g].GetYaxis().SetRangeUser(names[args.channel][str(args.year)]['y_min'][0],names[args.channel][str(args.year)]['y_max'][0])
    graphs_efficiencies[g].GetXaxis().SetLabelSize(0.03)
    graphs_efficiencies[g].GetXaxis().SetTitleSize(0.03)
    graphs_efficiencies[g].GetXaxis().SetTitleOffset(1.2)
    graphs_efficiencies[g].GetXaxis().SetNoExponent(1)
    legend_efficiencies.AddEntry(graphs_efficiencies[g], opt_titles[g], "p")
    if g==0:
        graphs_efficiencies[g].Draw("GAPL")
    else:
        graphs_efficiencies[g].Draw("GPLSAME")




legend_efficiencies.Draw("SAME")
canvas_efficiencies.Update()
#canvas_efficiencies.Update()
canvas_efficiencies.Print(("{}.pdf").format(names[args.channel][str(args.year)]["outFile"][0]),"pdf")
#x = input()




#### increase in Efficiency Plot #####
all_increases_iter_1 = []
all_increases_iter_2 = []
all_increases_iter_2Ext = []
all_increases_Louis = []
all_increases_recomLouis = []

all_increases_errors_iter_1 = []
all_increases_errors_iter_2 = []
all_increases_errors_iter_2Ext = []
all_increases_errors_Louis = []
all_increases_errors_recomLouis = []
for mass in all_masses:
    all_increases_iter_1.append(all_data['iter_1'][str(mass)]['best_eff'][0]-all_data['baseline'][str(mass)]['best_eff'][0])
    all_increases_iter_2.append(all_data['iter_2'][str(mass)]['best_eff'][0]-all_data['baseline'][str(mass)]['best_eff'][0])
    all_increases_iter_2Ext.append(all_data['iter_2Ext'][str(mass)]['best_eff'][0]-all_data['baseline'][str(mass)]['best_eff'][0])


    all_increases_errors_iter_1.append(getErrorDiff(all_data['iter_1'][str(mass)]['best_eff_err'][0], all_data['baseline'][str(mass)]['best_eff_err'][0]))
    all_increases_errors_iter_2.append(getErrorDiff(all_data['iter_2'][str(mass)]['best_eff_err'][0], all_data['baseline'][str(mass)]['best_eff_err'][0]))
    all_increases_errors_iter_2Ext.append(getErrorDiff(all_data['iter_2Ext'][str(mass)]['best_eff_err'][0], all_data['baseline'][str(mass)]['best_eff_err'][0]))

    if(args.channel=='tauTau' and args.year!=2016):
        #all_increases_Louis.append(all_data['Louis'][str(mass)]['best_eff'][0]-all_data['baseline'][str(mass)]['best_eff'][0])
        #all_increases_errors_Louis.append(math.sqrt(all_data['Louis'][str(mass)]['best_eff_err'][0]*all_data['Louis'][str(mass)]['best_eff_err'][0] + all_data['baseline'][str(mass)]['best_eff_err'][0]*all_data['baseline'][str(mass)]['best_eff_err'][0]))
        all_increases_recomLouis.append(all_data['recomLouis'][str(mass)]['best_eff'][0]-all_data['baseline'][str(mass)]['best_eff'][0])
        all_increases_errors_recomLouis.append(math.sqrt(all_data['recomLouis'][str(mass)]['best_eff_err'][0]*all_data['recomLouis'][str(mass)]['best_eff_err'][0] + all_data['baseline'][str(mass)]['best_eff_err'][0]*all_data['baseline'][str(mass)]['best_eff_err'][0]))

colors = [  ROOT.kGreen - 6 ,  ROOT.kAzure +6 , ROOT.kRed -7 , ROOT.kMagenta, ROOT.kBlack]
opt_titles = [ 'iter_1', 'iter_2', 'iter_2Ext']
if(args.channel=='tauTau' and args.year!=2016):
    #opt_titles.extend([ 'LLR', 'LLR + Baseline'])
    opt_titles.extend([ 'LLR + Baseline'])

graphs_increases = []
for o in range(0, len(opt_titles)):
    graphs_increases.append(ROOT.TGraphErrors(len(all_masses)))

for k in range(0, len(all_masses)):
    for o in range(0, len(opt_titles)):
        graphs_increases[o].SetPointX(k, all_masses[k])
    graphs_increases[0].SetPointY(k, all_increases_iter_1[k])
    graphs_increases[0].SetPointError(k,0, all_increases_errors_iter_1[k])
    graphs_increases[1].SetPointY(k, all_increases_iter_2[k])
    graphs_increases[1].SetPointError(k,0, all_increases_errors_iter_2[k])
    graphs_increases[2].SetPointY(k, all_increases_iter_2Ext[k])
    graphs_increases[2].SetPointError(k,0, all_increases_errors_iter_2Ext[k])

    if(len(graphs_increases)>3):
        graphs_increases[3].SetPointY(k, all_increases_recomLouis[k])
        graphs_increases[3].SetPointError(k,0, all_increases_errors_recomLouis[k])
        #graphs_increases[4].SetPointY(k, all_increases_Louis[k])
        #graphs_increases[4].SetPointError(k,0, all_increases_errors_Louis[k])


canvas_increases=ROOT.TCanvas()
canvas_increases.cd()
legend_increases = ROOT.TLegend(names[args.channel][str(args.year)]['position_legend'][4], names[args.channel][str(args.year)]['position_legend'][5], names[args.channel][str(args.year)]['position_legend'][6], names[args.channel][str(args.year)]['position_legend'][7])
legend_increases.SetBorderSize(0)
canvas_increases.SetLogx()
for g in range(0, len(graphs_increases)):
    graphs_increases[g].SetMarkerColor(colors[g])
    graphs_increases[g].SetLineColor(colors[g])
    graphs_increases[g].SetMarkerStyle( 8 )
    graphs_increases[g].SetMarkerSize( 0.4 )
    graphs_increases[g].SetTitle(("{} {} {} ;{};{}").format(names[args.channel][str(args.year)]["histTitle"][1], args.channel, args.year,names[args.channel][str(args.year)]["xAxisTitle"],names[args.channel][str(args.year)]["yAxisTitle"][1]))
    graphs_increases[g].GetXaxis().SetRangeUser(names[args.channel][str(args.year)]['x_min'],names[args.channel][str(args.year)]['x_max'])
    graphs_increases[g].GetXaxis().SetMoreLogLabels()
    graphs_increases[g].GetYaxis().SetRangeUser(names[args.channel][str(args.year)]['y_min'][1],names[args.channel][str(args.year)]['y_max'][1])
    graphs_increases[g].GetXaxis().SetLabelSize(0.03)
    graphs_increases[g].GetXaxis().SetTitleSize(0.03)
    graphs_increases[g].GetXaxis().SetTitleOffset(1.2)
    graphs_increases[g].GetXaxis().SetNoExponent(1)
    legend_increases.AddEntry(graphs_increases[g], opt_titles[g], "p")
    if g==0:
        graphs_increases[g].Draw("GAPL")
    else:
        graphs_increases[g].Draw("GPLSAME")




legend_increases.Draw("SAME")
canvas_increases.Update()
#canvas_increases.Update()
canvas_increases.Print(("{}.pdf").format(names[args.channel][str(args.year)]["outFile"][1]),"pdf")
#x = input()
