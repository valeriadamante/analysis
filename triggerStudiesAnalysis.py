import ROOT
import json
import argparse
import enum
import os
import csv
import math
from uncertainties import ufloat
from uncertainties.umath import *  # sin(), etc.


parser = argparse.ArgumentParser()
parser.add_argument('--channel', required=False, type=str, default="tauTau", choices=["eTau","muTau", "tauTau", "eE", "muMu", "eMu"])
parser.add_argument('--nTriggers', required=False, type=int, default=-1)
parser.add_argument('--nEvts', required=False, type=int, default=-1)
parser.add_argument('--mass_points', required=False, type=str, default='0')
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
class VerbosityLevel (enum.IntEnum):
    very_low = 0
    low = 1
    mid_low = 2
    medium = 3
    mid_high = 4
    high = 5
    very_high = 6
    super_high = 7



absolute_path={}
absolute_path['local'] = "/Users/valeriadamante/Desktop/Dottorato/"
absolute_path['lxplus'] = "/afs/cern.ch/work/v/vdamante/public/"
absolute_path['gridui']= "/home/users/damante/"
ROOT.gInterpreter.Declare(
    """
    #include <math.h>
    namespace Channel{
        enum {
            eTau = 0,
            muTau = 1,
            tauTau = 2,
            eMu = 3,
            eE =4,
            muMu = 5
        } ;
    }
    using LorentzVectorM = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>>;
    std::map<int, float> particleMasses {{11, 0.00051099894}, {12, 0.}, {13, 1.0565837}, {14,0.}, {15, 1.77686}, {16, 0.}, {22, 0.}, {111, 0.134977}, {211, 0.13957}, {311, 0.497611}, {321, 0.493677}};
    double muon_mass = particleMasses.at(13);
    double electron_mass = particleMasses.at(11);
    using vec_i = ROOT::VecOps::RVec<int>;
    using vec_s = ROOT::VecOps::RVec<size_t>;
    using vec_f = ROOT::VecOps::RVec<float>;
    using vec_b = ROOT::VecOps::RVec<bool>;
    using vec_uc = ROOT::VecOps::RVec<unsigned char>;
    struct EvtInfo{
        int channel;
        std::array<LorentzVectorM,2> leg_p4;
    };
    struct ExtendedTau {
        int Tau_charge ;
        float Tau_chargedIso	;
        unsigned char Tau_cleanmask	;
        int Tau_decayMode ;
        float Tau_dxy	;
        float Tau_dz	;
        float Tau_eta	;
        unsigned char Tau_genPartFlav	;
        int Tau_genPartIdx ;
        unsigned char Tau_idAntiEle	;
        unsigned char Tau_idAntiEle2018	;
        bool Tau_idAntiEleDeadECal	;
        unsigned char Tau_idAntiMu	;
        bool Tau_idDecayMode	;
        bool Tau_idDecayModeNewDMs	;
        unsigned char Tau_idDeepTau2017v2p1VSe	;
        unsigned char Tau_idDeepTau2017v2p1VSjet	;
        unsigned char Tau_idDeepTau2017v2p1VSmu	;
        unsigned char Tau_idMVAnewDM2017v2	;
        unsigned char Tau_idMVAoldDM	;
        unsigned char Tau_idMVAoldDM2017v1	;
        unsigned char Tau_idMVAoldDM2017v2	;
        unsigned char Tau_idMVAoldDMdR032017v2	;
        int Tau_jetIdx ;
        float Tau_leadTkDeltaEta	;
        float Tau_leadTkDeltaPhi	;
        float Tau_leadTkPtOverTauPt	;
        float Tau_mass	;
        float Tau_neutralIso	;
        float Tau_phi	;
        float Tau_photonsOutsideSignalCone	;
        float Tau_pt	;
        float Tau_puCorr	;
        float Tau_rawAntiEle	;
        float Tau_rawAntiEle2018	;
        int Tau_rawAntiEleCat ;
        int Tau_rawAntiEleCat2018 ;
        float Tau_rawDeepTau2017v2p1VSe	;
        float Tau_rawDeepTau2017v2p1VSjet	;
        float Tau_rawDeepTau2017v2p1VSmu	;
        float Tau_rawIso	;
        float Tau_rawIsodR03	;
        float Tau_rawMVAnewDM2017v2	;
        float Tau_rawMVAoldDM	;
        float Tau_rawMVAoldDM2017v1	;
        float Tau_rawMVAoldDM2017v2	;
        float Tau_rawMVAoldDMdR032017v2	;
        unsigned int nTau;
    };
    float DeltaPhi(Float_t phi1, Float_t phi2) {
        static constexpr float pi = M_PI;
        float dphi = phi1 - phi2;
        if(dphi > pi){
            dphi -= 2*pi;
        }
        else if(dphi <= -pi){
            dphi += 2*pi;
        }
        return dphi;
    }
    float DeltaEta(Float_t eta1, Float_t eta2)  {
      return (eta1-eta2);
    }
    float DeltaR(Float_t phi1,Float_t eta1,Float_t phi2,Float_t eta2) {
      float dphi = DeltaPhi(phi1, phi2);
      float deta = DeltaEta(eta1, eta2);
      return (std::sqrt(deta * deta + dphi * dphi));
    }

    bool isTauDaughter(int tau_idx, int particle_idx, const vec_i& GenPart_genPartIdxMother){
        bool isTauDaughter = false;
        int idx_mother = GenPart_genPartIdxMother[particle_idx];
        while(1){
            if(idx_mother == -1){
                return false;
            }
            else {
                if(idx_mother==tau_idx){
                    return true;
                }
                else{
                    int newParticle_index = idx_mother;
                    idx_mother = GenPart_genPartIdxMother[newParticle_index];
                }
            }
        }
    }

    LorentzVectorM GetTauP4(int tau_idx, const vec_f& pt, const vec_f& eta, const vec_f& phi, const vec_f& mass, const vec_i& GenPart_genPartIdxMother, const vec_i& GenPart_pdgId, const vec_i& GenPart_status){
        LorentzVectorM sum(0.,0.,0.,0.);
        LorentzVectorM TauP4;

        for(size_t particle_idx=0; particle_idx< GenPart_pdgId.size(); particle_idx++ ){
            if(GenPart_pdgId[particle_idx] == 12 || GenPart_pdgId[particle_idx] == 14 || GenPart_pdgId[particle_idx] == 16) continue;
            if(GenPart_status[particle_idx]!= 1 ) continue;

            bool isRelatedToTau = isTauDaughter(tau_idx, particle_idx, GenPart_genPartIdxMother);
            if(isRelatedToTau){
                LorentzVectorM current_particleP4 ;
                float p_mass ;
                if (particleMasses.find(GenPart_pdgId[particle_idx]) != particleMasses.end()){
                    p_mass=particleMasses.at(GenPart_pdgId[particle_idx]);
                }
                else{
                    p_mass = mass[particle_idx];
                }
                current_particleP4=LorentzVectorM(pt[particle_idx], eta[particle_idx], phi[particle_idx],p_mass);
                sum = sum + current_particleP4;
            }

        }
        TauP4=LorentzVectorM(sum.Pt(), sum.Eta(), sum.Phi(), sum.M());
        return TauP4;

    }


    EvtInfo IsComingFromTau(int evt, const vec_i& GenPart_pdgId, const vec_i& GenPart_genPartIdxMother, const vec_i& GenPart_statusFlags, const vec_i& GenPart_status, const vec_f& GenPart_pt, const vec_f& GenPart_eta, const vec_f& GenPart_phi, const vec_f& GenPart_mass){
        EvtInfo evt_info;
        std::set<int> e_indices;
        std::set<int> mu_indices;
        std::set<int> tau_indices;

        // start the loop to look for the indices of e, mu and taus
        for(size_t i=0; i< GenPart_pdgId.size(); i++ ){
            if(GenPart_genPartIdxMother[i]>0 && ((GenPart_statusFlags[i])&(1<<13))  ){
                if(std::abs(GenPart_pdgId[i])==15 && ( ( (GenPart_statusFlags[i])&(1<<0) || (GenPart_statusFlags[i])&(1<<5) )  ) && ((GenPart_statusFlags[i])&(1<<8)) ){
                    tau_indices.insert(i);
                }

                else if((std::abs(GenPart_pdgId[i])==13 || std::abs(GenPart_pdgId[i])==11) && ( (GenPart_statusFlags[i])&(1<<5) ) && ((GenPart_statusFlags[i])&(1<<9) || (GenPart_statusFlags[i])&(1<<10)) ) {
                    if( std::abs(GenPart_pdgId[GenPart_genPartIdxMother[i]]) != 15) {
                        std::cout << "event " << evt << " particle " << i << " is " << GenPart_pdgId[i] <<" particle mother " << GenPart_genPartIdxMother[i] << " is " << GenPart_pdgId[GenPart_genPartIdxMother[i]]  << std::endl;
                        throw std::runtime_error("particle mother is not tau");
                    }
                    if(std::abs(GenPart_pdgId[i])==11 ){
                    //std::cout << "in the event " << evt << " there is an electron in " << i << " coming from tau "<< GenPart_genPartIdxMother[i] << " whose pdg id is "<< GenPart_pdgId[GenPart_genPartIdxMother[i]] << std::endl;
                        e_indices.insert(i);
                        tau_indices.erase(GenPart_genPartIdxMother[i]);
                    }
                    if(std::abs(GenPart_pdgId[i])==13 ){
                        mu_indices.insert(i);
                        tau_indices.erase(GenPart_genPartIdxMother[i]);

                    }
                } // closes if on pdg ids for mu and e

            } // closes if on status flags and have idx mother
        } // closes for on genParticles
        /*if(evt == 73756 ){
            std::cout << "in the event " << evt << " tau_indices ==  " << tau_indices.size() << " mu_indices ==  " << mu_indices.size() << " e_indices ==  " << e_indices.size() << std::endl;
        }*/
        // tauTau
        if(e_indices.size()==0 && mu_indices.size()==0){

            /* uncomment this part to require tau with pt > 10 GeV */

            //if(tau_indices.size()!=2){
            //    for(size_t t = 0; t <tau_indices.size(); t++){
            //        int tau_idx = *std::next(tau_indices.begin(), t);
            //        if(GenPart_pt[tau_idx]<10.){
            //            tau_indices.erase(tau_idx);
            //        }
            //    }
            //} // closes if on tau_indices size

            if(tau_indices.size()!=2){
                std::cout << "in this event tauTau = " << evt << " there should be 2 taus but there are "<< tau_indices.size()<< " taus" <<std::endl;

                // loop over taus
                for(size_t t = 0; t <tau_indices.size(); t++){
                    int tau_idx = *std::next(tau_indices.begin(), t);
                    std::cout << "index = "<< tau_idx<< "\t pdgId = " << GenPart_pdgId[tau_idx] << "\t pt = " << GenPart_pt[tau_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[tau_idx]] << "\t status = " << GenPart_status[tau_idx] << std::endl;
                } // end of loop over taus

                throw std::runtime_error("it should be tautau, but tau indices is not 2 ");
            }

            int leg_p4_index = 0;

            // loop over tau_indices
            std::set<int>::iterator it_tau = tau_indices.begin();
            while (it_tau != tau_indices.end()){
                int tau_idx = *it_tau;
                evt_info.leg_p4[leg_p4_index] = GetTauP4(tau_idx,GenPart_pt,GenPart_eta, GenPart_phi, GenPart_mass, GenPart_genPartIdxMother, GenPart_pdgId, GenPart_status);
                leg_p4_index++;
                it_tau++;
            } // closes loop over tau_indices

            evt_info.channel = Channel::tauTau;

        } // closes tauTau Channel

        // muTau
        if(e_indices.size()==0 && (mu_indices.size()==1 || tau_indices.size()==1)){
            /* uncomment this part to require tau with pt > 10 GeV */

            //if(tau_indices.size()!=1){
            //    for(size_t t = 0; t <tau_indices.size(); t++){
            //        int tau_idx = *std::next(tau_indices.begin(), t);
            //        if(GenPart_pt[tau_idx]<10.){
            //            tau_indices.erase(tau_idx);
            //        }
            //    }
            //} // closes if on tau_indices size

            // case 1: when there is 1 mu and != 1 tau
            if(tau_indices.size()!=1){
                std::cout << "in this event muTau = " << evt << " there should be 1 tau but there are "<< tau_indices.size()<< " taus" <<std::endl;
                for(size_t t = 0; t <tau_indices.size(); t++){
                    int tau_idx = *std::next(tau_indices.begin(), t);
                    std::cout << "index = "<< tau_idx<< "\t pdgId = " << GenPart_pdgId[tau_idx] << "\t pt = " << GenPart_pt[tau_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[tau_idx]] << "\t status = " << GenPart_status[tau_idx] << std::endl;
                }
                throw std::runtime_error("it should be muTau, but tau indices is not 1 ");
            }

            // case 2: when there is 1 tau and != 1 mu
            if(mu_indices.size()!=1){
                std::cout << "in this event muTau = " << evt << " there should be 1 mu but there are "<< mu_indices.size()<< " mus" <<std::endl;
                for(size_t t = 0; t <mu_indices.size(); t++){
                    int mu_idx = *std::next(mu_indices.begin(), t);
                    std::cout << "index = "<< mu_idx<< "\t pdgId = " << GenPart_pdgId[mu_idx] << "\t pt = " << GenPart_pt[mu_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[mu_idx]] << "\t status = " << GenPart_status[mu_idx] << std::endl;
                }
                throw std::runtime_error("it should be muTau, but mu indices is not 1 ");
            }

            int leg_p4_index = 0;

            // loop over tau_indices
            std::set<int>::iterator it_tau = tau_indices.begin();
            while (it_tau != tau_indices.end()){
                int tau_idx = *it_tau;
                evt_info.leg_p4[leg_p4_index] = GetTauP4(tau_idx,GenPart_pt,GenPart_eta, GenPart_phi, GenPart_mass, GenPart_genPartIdxMother, GenPart_pdgId, GenPart_status);
                leg_p4_index++;
                it_tau++;
            } // closes loop over tau_indices

            // loop over mu_indices
            std::set<int>::iterator it_mu = mu_indices.begin();
            while (it_mu != mu_indices.end()){
                int mu_idx = *it_mu;
                evt_info.leg_p4[leg_p4_index] =  LorentzVectorM(GenPart_pt[mu_idx], GenPart_eta[mu_idx],GenPart_phi[mu_idx], muon_mass);
                leg_p4_index++;
                it_mu++;
            } // closes loop over mu_indices

            evt_info.channel = Channel::muTau;

        } // closes muTau Channel


        // eTau
        if(mu_indices.size()==0 && (e_indices.size()==1 || tau_indices.size()==1)){
            /* uncomment this part to require tau with pt > 10 GeV */

            //if(tau_indices.size()!=1){
            //    for(size_t t = 0; t <tau_indices.size(); t++){
            //        int tau_idx = *std::next(tau_indices.begin(), t);
            //        if(GenPart_pt[tau_idx]<10.){
            //            tau_indices.erase(tau_idx);
            //        }
            //    }
            //} // closes if on tau_indices size

            // case 1: when there is 1 e and != 1 tau
            if(tau_indices.size()!=1){
                std::cout << "in this event eTau = " << evt << " there should be 1 tau but there are "<< tau_indices.size()<< " taus" <<std::endl;
                for(size_t t = 0; t <tau_indices.size(); t++){
                    int tau_idx = *std::next(tau_indices.begin(), t);
                    std::cout << "index = "<< tau_idx<< "\t pdgId = " << GenPart_pdgId[tau_idx] << "\t pt = " << GenPart_pt[tau_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[tau_idx]] << "\t status = " << GenPart_status[tau_idx] << std::endl;
                }
                throw std::runtime_error("it should be eTau, but tau indices is not 1 ");
            }

            // case 2: when there is 1 tau and != 1 e
            if(e_indices.size()!=1){
                std::cout << "in this event eTau = " << evt << " there should be 1 e but there are "<< e_indices.size()<< " es" <<std::endl;
                for(size_t t = 0; t <e_indices.size(); t++){
                    int e_idx = *std::next(e_indices.begin(), t);
                    std::cout << "index = "<< e_idx<< "\t pdgId = " << GenPart_pdgId[e_idx] << "\t pt = " << GenPart_pt[e_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[e_idx]] << "\t status = " << GenPart_status[e_idx] << std::endl;
                }
                throw std::runtime_error("it should be eTau, but e indices is not 1 ");
            }

            int leg_p4_index = 0;

            // loop over tau_indices
            std::set<int>::iterator it_tau = tau_indices.begin();
            while (it_tau != tau_indices.end()){
                int tau_idx = *it_tau;
                evt_info.leg_p4[leg_p4_index] = GetTauP4(tau_idx,GenPart_pt,GenPart_eta, GenPart_phi, GenPart_mass, GenPart_genPartIdxMother, GenPart_pdgId, GenPart_status);
                leg_p4_index++;
                it_tau++;
            } // closes loop over tau_indices

            // loop over e_indices
            std::set<int>::iterator it_e = e_indices.begin();
            while (it_e != e_indices.end()){
                int e_idx = *it_e;
                evt_info.leg_p4[leg_p4_index] = LorentzVectorM(GenPart_pt[e_idx], GenPart_eta[e_idx],GenPart_phi[e_idx], electron_mass);
                leg_p4_index++;
                it_e++;
            } // closes loop over e_indices

            evt_info.channel = Channel::eTau;

        } // closes eTau Channel

        // muMu
        if(e_indices.size()==0 && tau_indices.size()==0){

            /* uncomment this part to require mu with pt > 10 GeV */

            //if(mu_indices.size()!=2){
            //    for(size_t t = 0; t <mu_indices.size(); t++){
            //        int mu_idx = *std::next(mu_indices.begin(), t);
            //        if(GenPart_pt[mu_idx]<10.){
            //            mu_indices.erase(mu_idx);
            //        }
            //    }
            //} // closes if on mu_indices size

            if(mu_indices.size()!=2){
                std::cout << "in this event muTau = " << evt << " there should be 2 mus but there are "<< mu_indices.size()<< " mus" <<std::endl;

                // loop over mus
                for(size_t t = 0; t <mu_indices.size(); t++){
                    int mu_idx = *std::next(mu_indices.begin(), t);
                    std::cout << "index = "<< mu_idx<< "\t pdgId = " << GenPart_pdgId[mu_idx] << "\t pt = " << GenPart_pt[mu_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[mu_idx]] << "\t status = " << GenPart_status[mu_idx] << std::endl;
                } // end of loop over mus

                throw std::runtime_error("it should be mumu, but mu indices is not 2 ");
            }

            int leg_p4_index = 0;

            // loop over mu_indices

            std::set<int>::iterator it_mu = mu_indices.begin();
            while (it_mu != mu_indices.end()){
                int mu_idx = *it_mu;
                evt_info.leg_p4[leg_p4_index] =  LorentzVectorM(GenPart_pt[mu_idx], GenPart_eta[mu_idx],GenPart_phi[mu_idx], muon_mass);
                leg_p4_index++;
                it_mu++;
            } // closes loop over mu_indices

            evt_info.channel = Channel::muMu;

        } // closes muMu Channel


        // eE
        if(mu_indices.size()==0 && tau_indices.size()==0){

            /* uncomment this part to require mu with pt > 10 GeV */

            //if(e_indices.size()!=2){
            //    for(size_t t = 0; t <e_indices.size(); t++){
            //        int e_idx = *std::next(e_indices.begin(), t);
            //        if(GenPart_pt[e_idx]<10.){
            //            e_indices.erase(e_idx);
            //        }
            //    }
            //} // closes if on e_indices size

            if(e_indices.size()!=2){
                std::cout << "in this event eTau = " << evt << " there should be 2 es but there are "<< e_indices.size()<< " es" <<std::endl;

                // loop over es
                for(size_t t = 0; t <e_indices.size(); t++){
                    int e_idx = *std::next(e_indices.begin(), t);
                    std::cout << "index = "<< e_idx<< "\t pdgId = " << GenPart_pdgId[e_idx] << "\t pt = " << GenPart_pt[e_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[e_idx]] << "\t status = " << GenPart_status[e_idx] << std::endl;
                } // end of loop over es

                throw std::runtime_error("it should be ee, but e indices is not 2 ");
            }

            int leg_p4_index = 0;

            // loop over e_indices

            std::set<int>::iterator it_e = e_indices.begin();
            while (it_e != e_indices.end()){
                int e_idx = *it_e;
                evt_info.leg_p4[leg_p4_index] = LorentzVectorM(GenPart_pt[e_idx], GenPart_eta[e_idx],GenPart_phi[e_idx], electron_mass);
                leg_p4_index++;
                it_e++;
            } // closes loop over e_indices

            evt_info.channel = Channel::eE;

        } // closes eE Channel

        // eMu
        if(tau_indices.size()==0 && (e_indices.size()==1 || mu_indices.size()==1)){
            /* uncomment this part to require tau with pt > 10 GeV */

            //if(mu_indices.size()!=1){
            //    for(size_t t = 0; t <mu_indices.size(); t++){
            //        int mu_idx = *std::next(mu_indices.begin(), t);
            //        if(GenPart_pt[mu_idx]<10.){
            //            mu_indices.erase(mu_idx);
            //        }
            //    }
            //} // closes if on mu_indices size

            // case 1: when there is 1 e and != 1 mu
            if(mu_indices.size()!=1){
                std::cout << "in this event eMu = " << evt << " there should be 1 mu but there are "<< mu_indices.size()<< " mus" <<std::endl;
                for(size_t t = 0; t <mu_indices.size(); t++){
                    int mu_idx = *std::next(mu_indices.begin(), t);
                    std::cout << "index = "<< mu_idx<< "\t pdgId = " << GenPart_pdgId[mu_idx] << "\t pt = " << GenPart_pt[mu_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[mu_idx]] << "\t status = " << GenPart_status[mu_idx] << std::endl;
                }
                throw std::runtime_error("it should be eMu, but mu indices is not 1 ");
            }

            // case 2: when there is 1 mu and != 1 e
            if(e_indices.size()!=1){
                std::cout << "in this event eTau = " << evt << " there should be 1 e but there are "<< e_indices.size()<< " es" <<std::endl;
                for(size_t t = 0; t <e_indices.size(); t++){
                    int e_idx = *std::next(e_indices.begin(), t);
                    std::cout << "index = "<< e_idx<< "\t pdgId = " << GenPart_pdgId[e_idx] << "\t pt = " << GenPart_pt[e_idx] << "\t mother = " << GenPart_pdgId[GenPart_genPartIdxMother[e_idx]] << "\t status = " << GenPart_status[e_idx] << std::endl;
                }
                throw std::runtime_error("it should be eTau, but e indices is not 1 ");
            }

            int leg_p4_index = 0;

            // loop over mu_indices
            std::set<int>::iterator it_mu = mu_indices.begin();
            while (it_mu != mu_indices.end()){
                int mu_idx = *it_mu;
                evt_info.leg_p4[leg_p4_index] =  LorentzVectorM(GenPart_pt[mu_idx], GenPart_eta[mu_idx],GenPart_phi[mu_idx], muon_mass);
                leg_p4_index++;
                it_mu++;
            } // closes loop over mu_indices

            // loop over e_indices
            std::set<int>::iterator it_e = e_indices.begin();
            while (it_e != e_indices.end()){
                int e_idx = *it_e;
                evt_info.leg_p4[leg_p4_index] = LorentzVectorM(GenPart_pt[e_idx], GenPart_eta[e_idx],GenPart_phi[e_idx], electron_mass);
                leg_p4_index++;
                it_e++;
            } // closes loop over e_indices

            evt_info.channel = Channel::eMu;

        } // closes eMu Channel

        return evt_info;

    }

    bool PassAcceptance(const EvtInfo& evt_info){
        for(size_t i =0; i<evt_info.leg_p4.size(); i++){
            if(!(evt_info.leg_p4.at(i).pt()>20 && std::abs(evt_info.leg_p4.at(i).eta())<2.3 )){
                //std::cout << "channel that does not pass acceptance == " << evt_info.channel << std::endl;
                //if(evt_info.channel == Channel::eTau){
                //    std::cout << "pt == " << evt_info.leg_p4.at(i).pt() << "eta == " << evt_info.leg_p4.at(i).eta() << std::endl;
                //}
                return false;
            }
        }
        return true;
    }


    vec_s RecoTauSelectedIndices(int event, EvtInfo& evt_info, const vec_f& Tau_dz, const vec_f& Tau_eta, const vec_f& Tau_phi, const vec_f& Tau_pt, const vec_uc& Tau_idDeepTau2017v2p1VSjet, const vec_uc&  Tau_idDeepTau2017v2p1VSmu, const vec_uc& Tau_idDeepTau2017v2p1Vse, const vec_f& Tau_rawDeepTau2017v2p1VSJet){
      if (evt_info.channel != Channel::tauTau){
          throw std::runtime_error("channel is not TauTau");
      }
      vec_s indices;
      vec_s final_indices ;

      for(size_t i=0; i< Tau_dz.size(); i++ ){
          if(std::abs(Tau_dz[i])>0.2) continue;
          if( ((Tau_idDeepTau2017v2p1VSjet[i])&(1<<3)) &&  ((Tau_idDeepTau2017v2p1VSmu[i])&(1<<2)) && ((Tau_idDeepTau2017v2p1Vse[i])&(1<<1)) ){
              if(Tau_pt[i] > 20 && std::abs(Tau_eta[i])<2.3){
                  indices.push_back(i);
              }
          }
      }
      std::vector<std::pair<size_t, size_t>> tau_pairs;
      // find taus with dR > 0.5 and compare pairs
      for(size_t i=0; i< indices.size(); i++ ){
        for(size_t j=0; j< indices.size(); j++ ){
            size_t firstTau = indices.at(i);
            size_t secondTau = indices.at(j);
            float current_dR = DeltaR(Tau_phi[firstTau], Tau_eta[firstTau],Tau_phi[secondTau], Tau_eta[secondTau]);
            //std::cout<<"current_dR = " << current_dR << std::endl;
            if(i!=j && current_dR > 0.5){
              tau_pairs.push_back(std::make_pair(firstTau, secondTau));
              }
          }
        }
        const auto Comparitor = [&](std::pair<size_t, size_t> tau_pair_1, std::pair<size_t, size_t> tau_pair_2) -> bool
        {
            if(tau_pair_1 == tau_pair_2) return false;
            for(size_t leg_id = 0; leg_id < 2; ++leg_id) {
                const size_t h1_leg_id = leg_id == 0 ? tau_pair_1.first : tau_pair_1.second;
                const size_t h2_leg_id = leg_id == 0 ? tau_pair_2.first : tau_pair_2.second;

                if(h1_leg_id != h2_leg_id) {
                    // per ora lo faccio solo per i tau ma poi va aggiustato!!
                    auto iso_tau_1 = Tau_rawDeepTau2017v2p1VSJet.at(h1_leg_id);
                    auto iso_tau_2 = Tau_rawDeepTau2017v2p1VSJet.at(h2_leg_id);
                    int iso_cmp;
                    if(iso_tau_1 == iso_tau_2){ iso_cmp= 0;}
                    else {iso_cmp =  iso_tau_1 > iso_tau_2 ? 1 : -1; }
                    if(iso_cmp != 0) return iso_cmp == 1;
                    if(Tau_pt.at(h1_leg_id) != Tau_pt.at(h2_leg_id))
                        return Tau_pt.at(h1_leg_id) > Tau_pt.at(h2_leg_id);
                }
            }
            std::cout << event << std::endl;
            throw std::runtime_error("not found a good criteria for best tau pair");
        };
        if(!tau_pairs.empty()){
            const auto best_pair = *std::min_element(tau_pairs.begin(), tau_pairs.end(), Comparitor);
            final_indices.push_back(best_pair.first);
            final_indices.push_back(best_pair.second);
        }
        return final_indices;

  }

      vec_f ReorderVSJet(const vec_i& reco_tau_indices, const vec_f& Tau_rawDeepTau2017v2p1VSjet){
        vec_f reordered_vs_jet ;
        for(auto& i : reco_tau_indices){
            reordered_vs_jet.push_back(Tau_rawDeepTau2017v2p1VSjet.at(i));
        }
        return reordered_vs_jet;
      }

      bool JetFilter(const vec_i& indices, const vec_f&  Tau_phi, const vec_f&  Tau_eta, const vec_f&  FatJet_pt, const vec_f&  FatJet_eta, const vec_f&  FatJet_phi, const vec_f& FatJet_msoftdrop, const vec_f&  Jet_eta, const vec_f&  Jet_phi, const vec_f&  Jet_pt, const vec_i&  Jet_jetId){
        int nFatJetsAdd=0;
        int nJetsAdd=0;
        for (size_t jet_idx =0 ; jet_idx < Jet_pt.size(); jet_idx++){
            if(Jet_pt.at(jet_idx)>20 && std::abs(Jet_eta.at(jet_idx)) < 2.5 && (Jet_jetId.at(jet_idx))&(1<<1)  ) {
                for(auto & tau_idx : indices ){
                    float current_dR = DeltaR(Tau_phi[tau_idx], Tau_eta[tau_idx],Jet_phi[jet_idx], Jet_eta[jet_idx]);
                    if(current_dR > 0.5 ){
                        nJetsAdd +=1;
                      }

                      //std::cout <<"current dr with jet " << jet_idx << " = " << current_dR << std::endl;
                     //std::cout<<"nJetsAdd == " <<nJetsAdd<<std::endl;
                }
            }
        }
        for (size_t fatjet_idx =0 ; fatjet_idx < FatJet_pt.size(); fatjet_idx++){
            if(FatJet_msoftdrop.at(fatjet_idx)>30 && std::abs(FatJet_eta.at(fatjet_idx)) < 2.5) {
                for(auto & tau_idx : indices ){
                    float current_dR = DeltaR(Tau_phi[tau_idx], Tau_eta[tau_idx],FatJet_phi[fatjet_idx], FatJet_eta[fatjet_idx]);
                    if(current_dR > 0.5 ){
                        nFatJetsAdd +=1;
                      }
                      //std::cout <<"current dr with fat jet " << fatjet_idx << " = " << current_dR << std::endl;
                     //std::cout<<"nFatJets == " <<nFatJetsAdd<<std::endl;
                }
            }
        }
        //std::cout << nFatJetsAdd << "\t" <<nJetsAdd << std::endl;
        if(nFatJetsAdd>=1 || nJetsAdd>=2){
            return true;
        }
        return false;
      }


      bool ElectronVeto(const vec_f& Electron_pt, const vec_f& Electron_dz, const vec_f& Electron_dxy, const vec_f& Electron_eta, const vec_b& Electron_mvaFall17V2Iso_WP90, const vec_b& Electron_mvaFall17V2noIso_WP90 , const vec_f&  Electron_pfRelIso03_all){
      int nElectrons =0 ;
        for (size_t el_idx =0 ; el_idx < Electron_pt.size(); el_idx++){
            if(Electron_pt.at(el_idx) >10 && std::abs(Electron_eta.at(el_idx)) < 2.5 && std::abs(Electron_dz.at(el_idx)) < 0.2 && std::abs(Electron_dxy.at(el_idx)) < 0.045 && ( Electron_mvaFall17V2Iso_WP90.at(el_idx) == true || ( Electron_mvaFall17V2noIso_WP90.at(el_idx) == true && Electron_pfRelIso03_all.at(el_idx)<0.3 )) ){
                nElectrons +=1 ;
            }
        }
        if(nElectrons>=1){
            return false;
        }
        return true;
      }
      bool MuonVeto(const vec_f& Muon_pt, const vec_f& Muon_dz, const vec_f& Muon_dxy, const vec_f& Muon_eta, const vec_b& Muon_tightId, const vec_b& Muon_mediumId , const vec_f&  Muon_pfRelIso04_all){
      int nMuons =0 ;
        for (size_t mu_idx =0 ; mu_idx < Muon_pt.size(); mu_idx++){
            if( Muon_pt.at(mu_idx) >10 && std::abs(Muon_eta.at(mu_idx)) < 2.4 && std::abs(Muon_dz.at(mu_idx)) < 0.2 && std::abs(Muon_dxy.at(mu_idx)) < 0.045 && ( Muon_mediumId.at(mu_idx) == true ||  Muon_tightId.at(mu_idx) == true ) && Muon_pfRelIso04_all.at(mu_idx)<0.3  ){
                nMuons +=1 ;
            }
        }
        if(nMuons>=1){
            return false;
        }
        return true;
      }


    """
)

# ****** ALL DICTIONARIES DEFINED HERE ******

# masses to run over
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
all_masses = []
if(args.mass_points!='all'):
    for i in args.mass_points.split(','):
        #print(("mass {} is {}").format(i, masses[args.prodMode][args.sample][int(i)]))
        all_masses.append(masses[args.prodMode][args.sample][int(i)])
else:
    all_masses = masses[args.prodMode][args.sample]
if(args.verbose>VerbosityLevel.medium):
    print(("all_masses {} ").format(all_masses ))



print(('Running with following options: \n channel = {} \n machine = {} \n prodMode = {} \n sample = {}  \n nTriggers = {} \n nEvts = {} \n mass_points = {} \n best_path_baseline = {} \n verbose = {} \n reco = {} \n Louis = {} \n test = {} \n allOR = {}').format(args.channel, args.machine, args.prodMode, args.sample, args.nTriggers, args.nEvts, all_masses, args.best_path_baseline, args.verbose, args.reco, args.Louis, args.Test, args.allOR))


# lumi trigger dict --> this dict has the effective luminosity (HLT Prescale)
lumiTrigger_dict_path  = ('{}trigger_info/TriggerLumi_2018.json').format(absolute_path[args.machine])
with open(lumiTrigger_dict_path, 'r') as f:
  lumiTrigger_dict = json.load(f)

# L1 seeds csv file and dict --> this is a CSV with the L1 seeds for each HLT path
l1Seeds_csv  = ('{}trigger_info/triggers_prompt_2018_L1seeds_319991.csv').format(absolute_path[args.machine])
l1Seeds_dict = {}
k=0

# REMEMBER: we want to select only last versions of L1 seeds CSV
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
        if(args.verbose>VerbosityLevel.super_high):
            print(("path = {}").format(path))
        pos = path.rfind('_v')
        l1Seeds_for_path = []
        if pos>0:
            version = path[pos:]
            path = path.replace(version, '')
            version = version.replace('_v', '')
            if(args.verbose>VerbosityLevel.super_high):
                print(("current path is {}, current version is {}, previous path is {}, previous version is {}").format(path, version, previous_path, previous_version))
            if(path != previous_path):
                previous_path = path
                previous_version = version
            else:
                if(version > previous_version):
                    l1Seeds_for_path =[]
                    previous_version = version
                    if(l[1]=='OR'):
                        l1Seeds_for_path = l[2].split()
                    else:
                        l1Seeds_for_path.append(l[2])

        l1Seeds_dict[path] = []
        l1Seeds_dict[path] = l[2].split()
        '''
        if(l[1]=='OR'):
            l1Seeds_dict[path] = l[2].split()
        else:
            if(l[2].rfind('bit')>0):
                continue
            l1Seeds_dict[path].append(l[2])
        '''
        k+=1
    if(args.verbose>VerbosityLevel.super_high):
        print(("l1Seeds_dict {}").format(l1Seeds_dict))

#  L1 seeds prescale dict --> once we have L1 seeds for each HLT we want the L1 path prescales (among which we will take the maximum)
l1Prescale_dict_path  = ('{}trigger_info/L1Prescale_2018_1p7e34.json').format(absolute_path[args.machine])
with open(l1Prescale_dict_path, 'r') as f:
  l1Prescale_dict = json.load(f)

# HLTrigger dict --> with HLT paths we are going to take in exam. In our case only prompt
triggers = {}
#trig_types = ['prompt', 'parking', 'scouting' ]
trig_types = ['prompt']
for trig_type in trig_types:
  trigger_dict = ('{}trigger_info/triggers_{}_2018.json').format(absolute_path[args.machine],trig_type)
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



# ******* ALL FUNCTIONS HERE !! ********

# ****** function to load file for each mass value ******
def load_file(mass):
  files = []
  if(args.machine == 'gridui'):
      file_name = ("{}trigger_info/input_files/{}_{}_M-{}.txt").format(absolute_path[args.machine],args.prodMode, args.sample, mass)
      if(args.verbose > VerbosityLevel.medium):
          print(("taking files from {}").format(file_name))
      with open(file_name ) as file:
          files = file.read().splitlines()
  elif(args.machine == 'lxplus'):
      file_name = ("{}trigger_info/input_files/{}_{}_M-{}.txt").format(absolute_path[args.machine],args.prodMode, args.sample, mass)
      if(args.verbose > VerbosityLevel.medium):
          print(("taking files from {}").format(file_name))
      with open(file_name ) as file:
          files_names = file.read().splitlines()
          #print(files_names)
      for k in files_names:
          files.append(("root://xrootd-cms.infn.it//{}").format(k))
      #print(files)
  else:
      files = absolute_path[args.machine]+("/rootfiles/signalRadionTest{}.root").format(mass)
  #files = ('{}/rootfiles/radionSignalTest.root').format(absolute_path[args.machine])
  print(files)
  df = ROOT.RDataFrame('Events', files)
  return df

# ****** function to check numbers of dataframe and channel selection ******
def check_numbers(df):
  num_tot_evts = df.Count().GetValue()
  num_tot_evts_separated  = 0
  for i in range(0, 6):
      nevts_channel = df.Filter(('evt_info.channel == {}').format(i)).Count().GetValue()
      print(("channel == {} \t n_evts_channel = {} ").format(i,  channel))
      num_tot_evts_separated += nevts_channel
  print(("num initial = {} \t after sum = {}").format(num_tot_evts, num_tot_evts_separated))

# ****** function for ordering ******
def take_second(elem):
  return elem[1]

# have a c++ routine that do proper OR between all selected pathes. like this we don’t need to define filter steps adding one path at the time
# e.g. for each path define path_weight column, which would account for both HLT and L1 prescale then event_weight = max(all_path_weights)
# and efficiency numerator is sum of event_weight

# you already have a code to compute L1 prescale weight for the given path, right? so path_weight would be a simple multiplications of L1_prescale * HLT_prescale and then loop where we add active HLT paths one by one can be dropped

# path_weight = HLT_path_accepted * HLT_path_prescale * max(L1_seed1_accept * L1_seed1_prescale, …)
# where HLT_path_prescale_factor = HLT_path_effective_lumi / lumi_2018
# L1_seedN_prescale_factor = (1 / L1_seedN_prescale_from_menu) / max_i (1 / L1_seedi_prescale_from_menu), excluding prescale=0 cases


# ****** Functions that finds number of events that pass a certain path, applying L1 prescale ******

not_found_paths =[] # needed to exclude not existing paths in L1 dict
not_found_hlt_paths =[] # needed to exclude not existing paths in L1 dict
def getWeight(df_channel, best_paths):
    weight_def = "std::vector<double> path_weight;"
    weight_def += " std::vector<double> w;"
    for col in best_paths:
        if(not col[0] in l1Seeds_dict):
            if(args.verbose>VerbosityLevel.mid_low):
                print(("{} is not in l1seeds_dict").format(col[0]))
            continue
        l1_seeds= l1Seeds_dict[col[0]]
        # Step 1. Define max(l1_path_acc * L1_prescale) excluding prescale == 0
        if(args.verbose>VerbosityLevel.very_high):
            print(("l1Seeds for {} are {} " ).format(col[0], l1_seeds))
        l1zeroSeeds = [] # needed to exclude seeds with prescale == 0
        # loop to find seeds with prescale 0
        for l1_path in l1_seeds:
            if(args.verbose>VerbosityLevel.very_high):
                print(("{} : {}").format(l1_path, l1Prescale_dict[l1_path]))
            if(not l1_path in l1Prescale_dict.keys()): # if does not exist
                path_with_zero = l1_path
                if(not l1_path in not_found_paths):
                    not_found_paths.append(path_with_zero)
                l1zeroSeeds.append(path_with_zero)
                continue
            if(l1Prescale_dict[l1_path]==0 ):
                path_with_zero = l1_path
                if(args.verbose>VerbosityLevel.very_high):
                    print(("{} sta in l1ZeroSeed").format(path_with_zero))
                l1zeroSeeds.append(path_with_zero)
        for l1_path in l1zeroSeeds:
            l1_seeds.remove(l1_path)
        if(args.verbose>VerbosityLevel.high):
            print(("I removed ALL zeros!! \n not found paths = {}").format(not_found_paths))
        if(len(l1_seeds)==0):
            if(args.verbose>VerbosityLevel.mid_low):
                print("all l1 seeds are 0")
            if(args.allOR == True):
                continue
            else:
                return 0
        if(args.verbose>VerbosityLevel.high):
            print(("l1_seeds {}").format(l1_seeds))
            for l1_path in l1_seeds:
                print(("l1 prescales for {} \n {}").format(l1_path, l1Prescale_dict[l1_path]))
            print(("l1zeroSeeds {}").format(l1zeroSeeds))
        current_min = max([1/l1Prescale_dict[l1_path] for l1_path in l1_seeds])
        #current_min = min([l1Prescale_dict[l1_path] for l1_path in l1_seeds])
        #if(current_min == 0):
        #    print("current min is zero !!")
        for l1_path in l1_seeds:
            if(l1Prescale_dict[l1_path]>0):
                weight_def += "w.push_back({} * {}); ".format(l1_path, current_min / l1Prescale_dict[l1_path])
        #weight_def += "};"
        #print(weight_def)
        weight_def += ("path_weight.push_back((*std::max_element(w.begin(), w.end()))*{}*{}); w.clear();").format(col[0],col[1])

    weight_def += " auto final_w = *std::max_element(path_weight.begin(), path_weight.end()); if(final_w >1 ) throw std::runtime_error(\"peso>1\");return final_w;"
    if(args.verbose>VerbosityLevel.high):
        print(weight_def)
    #filter_str = ''
    filter_str = ' || '.join([ '( {} == 1 )'.format(p[0]) for p in best_paths ])
    if(args.verbose>VerbosityLevel.mid_low):
        print(filter_str)
    #n_evt = df_channel.Define("weight", weight_def).Sum("weight")
    n_evt = df_channel.Filter(filter_str).Define("weight", weight_def).Sum("weight")
    if(args.verbose>VerbosityLevel.high):
        print(("weight def = {}").format(weight_def))
    return n_evt


# ********************************
if(args.verbose>VerbosityLevel.low):
    print(("REMEMBER: finding best trigger efficiencies for {} {} {}").format(args.prodMode, args.sample, args.channel))

# ****** Find best paths ********
best_paths_dict = {}
for mass in all_masses:
    #for mass in masses[args.prodMode][args.sample]:
    print(("evaluating for mass {}").format(mass))

    #  1. Define dataframe and define columns

    df = load_file(mass)
    # this was for debugging
    #print("nEvts ={}).format(df.count().GetValue()))
    df_initial = df

    columns = sorted([ str(c) for c in df.GetColumnNames() ])
    hlt_columns = [c for c in columns if c.startswith('HLT') and c in triggers]
    # 2. filter for gentaus, acceptance and channel

    df = df.Define('evt_info', 'IsComingFromTau(event,GenPart_pdgId,GenPart_genPartIdxMother,GenPart_statusFlags,GenPart_status,GenPart_pt,GenPart_eta,GenPart_phi,GenPart_mass)')

    #print(("before any cut there are {} events").format(df.Count().GetValue()))

    df = df.Filter('PassAcceptance(evt_info)')
    print(("filtering for channel {}").format(args.channel))
    df_channel = df.Filter(('evt_info.channel == Channel::{}').format(args.channel))
    print(("filtered for channel {}").format(args.channel))
    #print(("after channel cut there are {} events").format(df_channel.Count().GetValue()))

    # 3. require for reco cuts eventually

    if(args.reco == True):
        if(args.verbose>VerbosityLevel.very_low):
            print("applying reco requirements")
        # this was for debugging
        #df_channel = df_initial.Filter("nGenVisTau >= 2")
        #df_channel = df_initial#.Filter("nGenVisTau >= 2")
        df_channel = df_channel.Define('reco_tau_indices', 'RecoTauSelectedIndices(event, evt_info, Tau_dz, Tau_eta, Tau_phi, Tau_pt,Tau_idDeepTau2017v2p1VSjet,  Tau_idDeepTau2017v2p1VSmu, Tau_idDeepTau2017v2p1VSe, Tau_rawDeepTau2017v2p1VSjet)').Filter('reco_tau_indices.size()==2')
        #print(("after 2 reco tau indices cut there are {} events").format(df_channel.Count().GetValue()))
        df_channel = df_channel.Define('reorderedVsJet', 'ReorderVSJet(reco_tau_indices, Tau_rawDeepTau2017v2p1VSjet)')
        df_channel = df_channel.Filter(' JetFilter( reco_tau_indices,  Tau_phi,  Tau_eta,  FatJet_pt,  FatJet_eta,  FatJet_phi, FatJet_msoftdrop,  Jet_eta,  Jet_phi, Jet_pt,  Jet_jetId)')
        #print(("after jet cut there are {} events").format(df_channel.Count().GetValue()))
        df_channel = df_channel.Filter(' MuonVeto(Muon_pt, Muon_dz, Muon_dxy, Muon_eta, Muon_tightId, Muon_mediumId ,  Muon_pfRelIso04_all)')
        #print(("after mu veto cut there are {} events").format(df_channel.Count().GetValue()))
        df_channel = df_channel.Filter(' ElectronVeto(Electron_pt, Electron_dz, Electron_dxy, Electron_eta, Electron_mvaFall17V2Iso_WP90, Electron_mvaFall17V2noIso_WP90 ,  Electron_pfRelIso03_all) ')
        #print(("after ele veto cut there are {} events").format(df_channel.Count().GetValue()))        #df_channel.Display({'reco_tau_indices', 'event', 'reorderedVsJet'}).Print()
        #df_channel.Display({'event'}).Print()
    else:
        if(args.verbose>VerbosityLevel.very_low):
            print("no reco cuts are done")
    if(args.verbose>VerbosityLevel.super_high):
        check_numbers(df)

    # 4. ask for a specific number of events
    if(args.nEvts>0):
        df_channel = df_channel.Range(args.nEvts)

    # ***** After preparing the dataframe, let's start! *******

    # 1. define n_orig
    N_orig = df_channel.Count()

    # 2. define baseline paths - in general case they will be given externally, in Louis case they will be paths used by Louis and in allOR case they will be ALL paths
    best_paths_baseline = []

    if(args.best_path_baseline!=''):
        best_paths_baseline = args.best_path_baseline.split(',')

    if(args.Louis == True):
        best_paths_baseline = ['HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1',  'HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1', 'HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1',  'HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1_1pr', 'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight', 'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60', 'HLT_MediumChargedIsoPFTau50_Trk30_eta2p1_1pr_MET100', 'HLT_MediumChargedIsoPFTau50_Trk30_eta2p1_1pr_MET110', 'HLT_MediumChargedIsoPFTau50_Trk30_eta2p1_1pr_MET130','HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg']

        if(args.verbose>VerbosityLevel.very_low):
            print("evaluating Louis HLT triggers")

    if(args.allOR == True):
        best_paths_baseline = hlt_columns
    # print for debugging purposes
    if(args.verbose > VerbosityLevel.mid_low and args.allOR == False) :
        print(('best_paths_baseline = {}').format(best_paths_baseline))

    # 3. define nTriggers and other useful quantities
    nTriggers = 0
    if(args.nTriggers < 0 or args.Louis == True or args.allOR == True):
        nTriggers = len(best_paths_baseline)
        if(args.verbose>VerbosityLevel.low):
            print(("nTriggers == {}").format(nTriggers))
    else:
        nTriggers = args.nTriggers

    best_path_string = [] # quantity necessary to write final dictionary
    best_paths = []
    best_eff = []
    best_eff_hr = []
    best_eff_err = []


    # start iteration over all paths for general case
    n_paths = len(best_paths_baseline)
    best_paths.extend(best_paths_baseline)
    if (best_paths_baseline):
        current_paths = [ ]
        path_perf = []
        current_paths.extend(best_paths)
        current_paths = [ (p, (lumiTrigger_dict[p]["eff_lumi"]/59.97)) for p in current_paths]
        #n_evt = getWeight(df_channel, best_paths)
        for n in range(len(current_paths)):
            if len(current_paths)==0:
                continue
            if(l1Seeds_dict.get(current_paths[n][0])==None):
                if(args.verbose>VerbosityLevel.mid_low) : print(("column not found {}").format(current_paths[n][0]))
                continue
            n_evt = getWeight(df_channel, current_paths)
            if n_evt ==0 :
                continue
            path_perf.append((current_paths[n][0], n_evt))
            filter_str = ' || '.join([ ' {} == 1 '.format(p[0]) for p in current_paths[:n+1] ])
            #print(filter_str)
            #print(path_perf)
        path_perf_withEff = [(filter_str, p[1].GetValue()/N_orig.GetValue(), math.sqrt(p[1].GetValue())/N_orig.GetValue()) for p in path_perf]
        #path_perf_withEff = sorted(path_perf_withEff2, key=take_second, reverse=True)
        #print(path_perf_withEff)
        #best_paths.append(path_perf_withEff[0][0])
        best_path_string.append(path_perf_withEff[0][0])
        best_eff.append(path_perf_withEff[0][1])
        best_eff_err.append(path_perf_withEff[0][2])
        best_eff_hr.append(ufloat(eval("%.0e"%(path_perf_withEff[0][1])),  eval("%.0e"%(path_perf_withEff[0][2])) ))
        #print("\n")
        if(args.verbose>VerbosityLevel.mid_low):
            print(("filter_str \t {}").format(filter_str))
            print(("path_perf_withEff \t {}").format(path_perf_withEff))
            print(("type path_perf_withEff {}").format(type(path_perf_withEff)))
            print(("len path_perf_withEff {}").format(len(path_perf_withEff)))
        if(args.verbose>VerbosityLevel.very_low):
            print(("\n filter_str \t {}").format(filter_str))
            #print(("best path at iteration {} is \t {}").format(n_paths, path_perf_withEff[0][0]))
            print(("efficiency  \t {}").format(path_perf_withEff[0][1]))
            print(("efficiency error \t {}").format(path_perf_withEff[0][2]))
            print("\n")
        if(args.verbose>VerbosityLevel.mid_low):
            print(("path_perf_withEff 0 \t {}").format(path_perf_withEff[1][0]))
            print(("path_perf_withEff 1 \t {}").format(path_perf_withEff[1][1]))
            print(("path_perf_withEff 2 \t {}").format(path_perf_withEff[1][2]))


    while(n_paths <nTriggers):
        path_perf_withEff = []
        path_perf = []
        current_paths = [ ]
        print(n_paths, best_paths)
        for new_path in hlt_columns:
            if(args.verbose>VerbosityLevel.high):
                print(("new path = {}").format(new_path))
            if new_path in best_paths:
                continue
            if new_path in best_paths_baseline:
                continue
            current_paths = [ new_path ]
            #current_paths.extend(best_paths_baseline)
            current_paths.extend(best_paths)
            # [ C, A, B ]
            current_paths = [ (p, (lumiTrigger_dict[p]["eff_lumi"]/59.97)) for p in current_paths]
            # [ (C, wC), (A, wA), (B, wB) ]
            current_paths = sorted(current_paths, key=take_second, reverse=True)
            if(args.verbose>VerbosityLevel.high):
                print(("current paths \n {} ").format(current_paths))
            for n in range(len(current_paths)):
                if len(current_paths)==0:
                    continue
                if(l1Seeds_dict.get(current_paths[n][0])==None):
                    if(args.verbose>VerbosityLevel.mid_low) : print(("column not found {}").format(current_paths[n][0]))
                    continue
                n_evt = getWeight(df_channel, current_paths)
                if n_evt ==0 or current_paths[n][0] in best_paths:
                    continue
                path_perf.append((current_paths[n][0], n_evt))
                filter_str = ' || '.join([ ' {} == 1 '.format(p[0]) for p in current_paths[:n+1] ])
                #print(filter_str)
        path_perf_withEff2 = [(p[0], p[1].GetValue()/N_orig.GetValue(), math.sqrt(p[1].GetValue())/N_orig.GetValue()) for p in path_perf]
        path_perf_withEff = sorted(path_perf_withEff2, key=take_second, reverse=True)
        #print(path_perf_withEff)
        best_paths.append(path_perf_withEff[0][0])
        best_path_string.append(path_perf_withEff[0][0])
        best_eff.append(path_perf_withEff[0][1])
        best_eff_err.append(path_perf_withEff[0][2])
        best_eff_hr.append(ufloat(eval("%.0e"%(path_perf_withEff[0][1])),  eval("%.0e"%(path_perf_withEff[0][2])) ))
        #print("\n")
        n_paths+=1
        if(args.verbose>VerbosityLevel.mid_low):
            print(("filter_str \t {}").format(filter_str))
            print(("path_perf_withEff \t {}").format(path_perf_withEff))
            print(("type path_perf_withEff {}").format(type(path_perf_withEff)))
            print(("len path_perf_withEff {}").format(len(path_perf_withEff)))
        if(args.verbose>VerbosityLevel.very_low):
            print(("\n filter_str \t {}").format(filter_str))
            #print(("best path at iteration {} is \t {}").format(n_paths, path_perf_withEff[0][0]))
            print(("efficiency  \t {}").format(path_perf_withEff[0][1]))
            print(("efficiency error \t {}").format(path_perf_withEff[0][2]))
            print("\n")
        if(args.verbose>VerbosityLevel.mid_low):
            print(("path_perf_withEff 0 \t {}").format(path_perf_withEff[1][0]))
            print(("path_perf_withEff 1 \t {}").format(path_perf_withEff[1][1]))
            print(("path_perf_withEff 2 \t {}").format(path_perf_withEff[1][2]))


    if(args.Louis or args.allOR):
        path_perf_withEff = []
        path_perf = []
        # [ C, A, B ]
        current_paths = [ (p, (lumiTrigger_dict[p]["eff_lumi"]/59.97)) for p in best_paths_baseline]
        # [ (C, wC), (A, wA), (B, wB) ]
        current_paths = sorted(current_paths, key=take_second, reverse=True)
        if(args.verbose>VerbosityLevel.super_high):
            print(("current paths \n {} ").format(current_paths))
        n_evt = getWeight(df_channel, current_paths)
        #if n_evt ==0:
        #    continue
        filter_str = ' || '.join([ ' {} == 1 '.format(p[0]) for p in current_paths ])
        #print(filter_str)
        path_perf.append((filter_str, n_evt))
              #print(filter_str)

        path_perf_withEff = [filter_str, n_evt.GetValue()/N_orig.GetValue(), math.sqrt(n_evt.GetValue())/N_orig.GetValue()]
        #path_perf_withEff = sorted(path_perf_withEff2, key=take_second, reverse=True)
        #print()
        best_paths.append(path_perf_withEff[0])
        best_path_string.append(path_perf_withEff[0])
        best_eff.append(path_perf_withEff[1])
        #print(best_eff)
        best_eff_err.append(path_perf_withEff[2])
        best_eff_hr.append(ufloat(eval("%.0e"%(path_perf_withEff[1])),  eval("%.0e"%(path_perf_withEff[2])) ))

    # print stuff for debugging purposes
    if(args.verbose > VerbosityLevel.mid_low):
        print(("nTriggers = {} \t len best_paths = {}").format(nTriggers,len(best_paths)))
        print(("best_paths \n {}").format(best_paths))
        print(("best_eff \n {}").format(best_eff))
        print(("best_eff_error \n {}").format(best_eff_err))
        print(("best_eff_error_hr \n {}").format(best_eff_hr))
        #print("\n")
        print(("n runs = {}").format(df_initial.GetNRuns()))
    best_paths_dict[('M-{}').format(mass)]={}
    best_paths_dict[('M-{}').format(mass)]['best_paths']=best_path_string
    best_paths_dict[('M-{}').format(mass)]['best_eff']=best_eff
    best_paths_dict[('M-{}').format(mass)]['best_eff_err']=best_eff_err
    #print(("best_paths_dict \n {}").format(best_paths_dict))

nEvts_used = str(args.nEvts) if args.nEvts>0 else "all"
masses_used = '_'.join(str(mass) for mass in all_masses)  if args.mass_points!= 'all' else "all"
has_Louis = '' if args.Louis == False else '_Louis'
has_AllOR= '' if args.allOR == False else '_allOR'
outDir = ("{}/output/{}_{}_{}/").format(os.getcwd(), args.prodMode, args.sample, args.channel)
if not os.path.isdir(outDir):
    os.makedirs(outDir)
if(has_Louis or has_AllOR):
    outDir = ("{}/output/{}_{}_{}/With{}{}/").format(os.getcwd(), args.prodMode, args.sample, args.channel, has_Louis, has_AllOR)
else:
    outDir = ("{}/output/{}_{}_{}/With_{}_paths/").format(os.getcwd(), args.prodMode, args.sample, args.channel, len(best_paths_baseline))
if not os.path.isdir(outDir):
    os.makedirs(outDir)
dictName = ("{}/{}_{}_{}_{}Triggers_{}Evts_{}Masses{}{}.json").format(outDir,args.prodMode, args.sample, args.channel, nTriggers, nEvts_used, masses_used, has_Louis, has_AllOR)
print(("dict name = {}").format(dictName))
mode  = args.mode
with open(dictName, mode) as finalFile:
  json.dump(best_paths_dict, finalFile, ensure_ascii=False, indent=4)
