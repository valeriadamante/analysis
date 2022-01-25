import ROOT
import math
giorni_2018 = [42]
giorni_2019 = [37,31,39,39,36,45,39,36,36,36]
giorni_2020 = [46,42,37,40,39,46,38,42,38]
giorni_2021 = [43,38,41,33,38,35,32,40,29]
giorni_2022 = [23]
histo = ROOT.TH1D("","", 20, 20, 50)
for g in giorni_2019:
    p=2019/2022
    histo.Fill(g,p)
for g in giorni_2020:
    p=2020/2022
    histo.Fill(g,p)
for g in giorni_2021:
    p=2021/2022
    histo.Fill(g,p)
for g in giorni_2022:
    histo.Fill(g)
fitFunc = ROOT.TF1("cicloFunc", "gaus", 20, 50)
fitFunc.SetParameter(0, 1)
fitFunc.SetParameter(1, 28)
fitFunc.SetParameter(2, 7)
histo.Fit(fitFunc)
canvas=ROOT.TCanvas()
canvas.cd()
histo.Draw()
canvas.Update()
input()
