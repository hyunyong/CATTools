/**
  \class    cat::CATGenTopProducer CATGenTopProducer.h "CATTools/CatProducer/interface/CATGenTopProducer.h"
  \brief    CAT GenTop 
*/


#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/RefToPtr.h"

#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "CATTools/DataFormats/interface/GenTop.h"
#include "CATTools/DataFormats/interface/GenJet.h"
#include "CATTools/DataFormats/interface/MCParticle.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterLazyTools.h"
#include "FWCore/Utilities/interface/isFinite.h"

using namespace edm;
using namespace std;

namespace cat {

  class CATGenTopProducer : public edm::EDProducer {
    public:
      explicit CATGenTopProducer(const edm::ParameterSet & iConfig);
      virtual ~CATGenTopProducer() { }

      virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup);
      

    private:
      edm::EDGetTokenT<edm::View<reco::GenJet> > genJetLabel_;
      edm::EDGetTokenT<edm::View<reco::GenParticle> > mcParticleLabel_;

  };

} // namespace

cat::CATGenTopProducer::CATGenTopProducer(const edm::ParameterSet & iConfig) :
    genJetLabel_(consumes<edm::View<reco::GenJet> >(iConfig.getParameter<edm::InputTag>("genJetLabel"))),
    mcParticleLabel_(consumes<edm::View<reco::GenParticle> >(iConfig.getParameter<edm::InputTag>("mcParticleLabel")))
{
    produces<std::vector<cat::GenTop> >();
}

void 
cat::CATGenTopProducer::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {

    Handle<View<reco::GenJet> > genJets;
    iEvent.getByToken(genJetLabel_, genJets);

    Handle<View<reco::GenParticle> > mcParticles;
    iEvent.getByToken(mcParticleLabel_, mcParticles);

    cat::GenTop aGenTop;
    aGenTop.building( genJets, mcParticles);

    auto_ptr<vector<cat::GenTop> >  out(new vector<cat::GenTop>());

    out->push_back(aGenTop);

    iEvent.put(out);
}

#include "FWCore/Framework/interface/MakerMacros.h"
using namespace cat;
DEFINE_FWK_MODULE(CATGenTopProducer);
