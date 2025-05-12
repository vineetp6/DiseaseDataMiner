"""
Data seeder for the Drug Discovery Platform
Populates the database with initial data for demonstration purposes
"""

import logging
import os
from datetime import datetime

from app import app, db
from models import Compound, Disease, Target, Analysis
from molecular_analysis import calculate_molecular_properties
from ml_models import predict_binding_affinity, predict_admet_properties

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Seed data for neglected diseases
DISEASES = [
    {
        "name": "Malaria",
        "category": "Parasitic",
        "description": "A mosquito-borne disease caused by Plasmodium parasites. It causes high fevers, chills, flu-like symptoms, and severe complications if untreated.",
        "prevalence": "228 million cases worldwide (2018)",
        "regions_affected": "Sub-Saharan Africa, South Asia, Southeast Asia"
    },
    {
        "name": "Tuberculosis",
        "category": "Bacterial",
        "description": "An infectious disease caused by Mycobacterium tuberculosis. It primarily affects the lungs and can be fatal if untreated.",
        "prevalence": "10 million cases worldwide (2019)",
        "regions_affected": "South-East Asia, Africa, Western Pacific"
    },
    {
        "name": "Chagas Disease",
        "category": "Parasitic",
        "description": "A tropical parasitic disease caused by Trypanosoma cruzi. It can cause heart failure and digestive system damage if untreated.",
        "prevalence": "6-7 million people infected worldwide",
        "regions_affected": "Latin America, particularly rural areas"
    },
    {
        "name": "Leishmaniasis",
        "category": "Parasitic",
        "description": "A disease caused by Leishmania parasites and spread by sandflies. It can cause skin sores, organ damage, and death if untreated.",
        "prevalence": "700,000 to 1 million new cases annually",
        "regions_affected": "Tropical and subtropical regions, particularly Brazil, East Africa, and India"
    },
    {
        "name": "Schistosomiasis",
        "category": "Parasitic",
        "description": "A disease caused by parasitic worms called schistosomes. It affects the urinary tract and intestines.",
        "prevalence": "Over 200 million people infected worldwide",
        "regions_affected": "Sub-Saharan Africa, South America, Caribbean, Middle East, Southeast Asia"
    }
]

# Seed data for biological targets
TARGETS = [
    {
        "name": "Plasmodium falciparum Dihydrofolate Reductase",
        "uniprot_id": "P13922",
        "organism": "Plasmodium falciparum",
        "function": "Essential enzyme in folate metabolism and DNA synthesis.",
        "disease_name": "Malaria",
        "sequence": "MLKPNVTLGFELWKRKIKDEFTLLFRYDSATHVPNVTLGFELWKRKIKDEFTLLFRYDNDTHMKPNVTVNERIKMAINFK"
    },
    {
        "name": "Mycobacterium tuberculosis InhA",
        "uniprot_id": "P9WGR1",
        "organism": "Mycobacterium tuberculosis",
        "function": "Enoyl-ACP reductase involved in fatty acid synthesis.",
        "disease_name": "Tuberculosis",
        "sequence": "MGLLDGKRILVSGIITDSSIAFHIARVAQEQGAQLVLTGFDRLRLIQRITDRLPAKAPLLELDVQNEEHLASLAGRVTEAIGAGNKLDGVVHSIGFMPQTGMGINPFFDAPYADVSKGIHISAYSYASMAKALLPIMNPGGSIVGMDFDPSRAMPAYNWMTVAKSALESVNRFVAREAGKYGVRSNLVAAGPIRTLAMSAIVGGALGEEAGAQIQLLEEGWDQRAPLGWNMKDATPVAKTVCALLSDWLPATTGDIIYADGGAHTQLL"
    },
    {
        "name": "Trypanosoma cruzi Cruzain",
        "uniprot_id": "P25779",
        "organism": "Trypanosoma cruzi",
        "function": "Cysteine protease essential for parasite survival and infection.",
        "disease_name": "Chagas Disease",
        "sequence": "APAAVDWRARGAVTAVKDQGQCGSCWAFSAIGNVECQWFLAGHPLTNLSEQMLVSCDKTDSGCSGGLMNNAFEWIVQENNGAVYTEDSYPYASGEGISPPCTTSGHTVGATITGHVELPQDEAQIAAWLAVNGPVAVAVDASSWMTYTGGVMTSCVSEQLDHGVLLVGYNDSAAVPYWIIKNSWTTQWGEEGYIRIAKGSNQCLVKEEASSAVVG"
    },
    {
        "name": "Leishmania major Pteridine Reductase 1",
        "uniprot_id": "Q01782",
        "organism": "Leishmania major",
        "function": "NADPH-dependent short-chain reductase involved in pterin metabolism.",
        "disease_name": "Leishmaniasis",
        "sequence": "MTTAPVAVALVTGAAKRLGRSIAEALREWGASVYATTRAEREAGGAGFGVAHYKLPPGTSPSEVEGMVLNALKLEALAPSDAPCVSLINTAAVSPQLKAALDGVRGSRVACVSSMLKGLAADSVRYFTGTIAGKLGMAPETRVYAIGEGSAQVIQSTLTAASQVRLLEEPEPEDVMGMLVNAVGDEPEVKAAAELMLDGRLCNVLGLGHASPLSPEQAEFIEKLRELGY"
    },
    {
        "name": "Schistosoma mansoni Thioredoxin Glutathione Reductase",
        "uniprot_id": "Q962Y6",
        "organism": "Schistosoma mansoni",
        "function": "Essential for parasite redox balance and antioxidant defense.",
        "disease_name": "Schistosomiasis",
        "sequence": "MALFKDKVSDYEAYTVIYFGKRAPKDKLLEAAGFQKVAVGYSRGIRVALDSGKELLYQNSWCTPRCMLDLPVYLRELLKQRPGVKIITTVTKDKGVEAEFENTVWDAIKRFDSVYIKIDDDKRLRSLLTGESTVGLFLKKNKVTYTNWAIYVSKHTPLSGVPGSIGTAFLNKLDGKTLGIYGSDHESWSLKEGILTKTFDSCYVCGFVKGVEFQDKGVLELNDSKVAYNRTGIGVTTDKGKINVTEGNLIKPQEGRSVDQIKRLRSTYNPHIFAIGDVTGKPQLTALPGVEFPLLADKYSVAVLGSGGTVALVGLGPANVGKSTIMRAIQENNEKVSGVTIYESHFTPNGQKIPALPTLAWIQGGFGVCPNYDLGLELPSDSDVNRTKEVLKKGE"
    }
]

# Seed data for compounds
COMPOUNDS = [
    {
        "name": "Chloroquine",
        "smiles": "CCN(CC)CCCC(C)Nc1ccnc2cc(Cl)ccc12",
        "inchi": "InChI=1S/C18H26ClN3/c1-3-21(4-2)12-5-6-13-18(20-14(13)7-8-22-17-11-9-15(19)10-16(17)22)21/h9-11,14H,3-8,12H2,1-2H3",
        "disease_target": "Malaria",
        "description": "An antimalarial and amoebicidal drug used to treat and prevent malaria, including chloroquine-sensitive malaria."
    },
    {
        "name": "Isoniazid",
        "smiles": "NNC(=O)c1ccncc1",
        "inchi": "InChI=1S/C6H7N3O/c7-8-6(10)5-2-1-3-9-4-5/h1-4H,(H2,7,8,10)",
        "disease_target": "Tuberculosis",
        "description": "A first-line antituberculosis medication used in the prevention and treatment of tuberculosis."
    },
    {
        "name": "Benznidazole",
        "smiles": "O=C(Cn1nnnc1)N(C1CC1)c1ccc([N+](=O)[O-])cc1",
        "inchi": "InChI=1S/C12H12N4O3/c17-12(10-13-15-16-14-10)18-11(8-9-8)6-4-7(5-1-2-3-19-5)9-2/h1-7,11H,8-9H2",
        "disease_target": "Chagas Disease",
        "description": "An antiparasitic medication used for the treatment of Chagas disease."
    },
    {
        "name": "Miltefosine",
        "smiles": "CCCCCCCCCCCCCCCCOP(=O)([O-])OCC[N+](C)(C)C",
        "inchi": "InChI=1S/C21H46NO4P/c1-5-6-7-8-9-10-11-12-13-14-15-16-17-18-19-20-25-27(23,24)26-21-22(2,3)4/h5-21H2,1-4H3/p-1",
        "disease_target": "Leishmaniasis",
        "description": "An oral medication used to treat various types of leishmaniasis."
    },
    {
        "name": "Praziquantel",
        "smiles": "O=C1N2CC(c3ccccc3)N=C2COC1c1ccccc1",
        "inchi": "InChI=1S/C19H24N2O2/c1-2-4-14(5-3-1)19-17-12-20-16(13-15-7-9-8-10-15)18(21(16)17)11-6-23-19/h1-11,15-17,19-20H,12-14H2",
        "disease_target": "Schistosomiasis",
        "description": "An anthelmintic effective against flatworms, used to treat schistosomiasis and other parasitic worm infections."
    },
    {
        "name": "Quinine",
        "smiles": "COc1ccc2nccc(C(O)C3CC4CCN3CC4C=C)c2c1",
        "inchi": "InChI=1S/C20H24N2O2/c1-3-13-12-22-9-7-14(22)19(13)20(23)18-10-11-21-16-6-5-15(24-2)8-17(16)18/h3,5-6,8,10-11,13-14,19-20,23H,1,7,9,12H2,2H3",
        "disease_target": "Malaria",
        "description": "An antimalarial medication used to treat malaria caused by Plasmodium falciparum."
    },
    {
        "name": "Rifampicin",
        "smiles": "CC1COC2(C(O)=C(C(=O)N3C=C4C(=O)C(O)=C(C)C(OC)=C4N(C)C3=O)C(=O)C2=C(O)C3=C(O)C=C(C)C=C13)OC",
        "inchi": "InChI=1S/C43H58N4O12/c1-11-15-43(59-11)33(53)28-31(52)35(55)41-38(58)34(54)29(2)17-22(41)12-13-26-27-14-21(48-9)36(56)42(39(27)57)49(10)40(26)59-19-30(51)37(47-18-24-16-23(44-24)32(3,4)5)46-25(45)20-50-43/h12-17,19,21,24,30,37,44,51-55H,11,18,20H2,1-10H3,(H,25,45,46,50)",
        "disease_target": "Tuberculosis",
        "description": "An antibiotic used to treat tuberculosis, leprosy, and Mycobacterium avium complex."
    },
    {
        "name": "Nifurtimox",
        "smiles": "CC1=C(C=NO1)CN(C=O)S(=O)(=O)c1ccc([N+](=O)[O-])cc1",
        "inchi": "InChI=1S/C10H13N3O5S/c1-7-6-11-18-8(7)5-12(4-14)19(15,16)10-2-3-9(13(16)17)10/h2-4,6,8H,5H2,1H3",
        "disease_target": "Chagas Disease",
        "description": "An antiparasitic medication used to treat Chagas disease and African trypanosomiasis."
    },
    {
        "name": "Amphotericin B",
        "smiles": "CC1C=CC=CC=CC=CC=CC=CC=CC(CC2C(C(CC(O2)(CC(CC(C(CCC(CC(CC(=O)OC(C(C1O)C)O)O)O)O)O)O)O)O)C(=O)O)O",
        "inchi": "InChI=1S/C47H73NO17/c1-25-12-8-6-4-2-3-5-7-9-13-19-21-31(48-65-27-15-29(31)46(62)63)22-32-39(55)40(56)34(52)20-16-28(50)18-24-47(64)42(58)36(54)44-45(24,61)35(53)33(51)17-26(2)37(44)57-43(59)38(32)60-41(25)57/h2-9,12-13,25-29,32-42,44,50-56,58,61,64H,10-11,14-18,20-22,24,27,48H2,1-2H3,(H,62,63)",
        "disease_target": "Leishmaniasis",
        "description": "An antifungal medication also used to treat leishmaniasis and other protozoal infections."
    },
    {
        "name": "Oxamniquine",
        "smiles": "CCN(CC)CCOc1cc(C[C@@H]2NC(=C[C@H](O2)CO)[N+](=O)[O-])ccc1[N+](=O)[O-]",
        "inchi": "InChI=1S/C14H19N3O6/c1-2-16(3-1)10-9-23-12-7-11(8-14(5)6-15-13(14)17(18)19)4-5-12-21(22)20/h4-7,9-11,13-15H,1-3,8H2,(H-,18,19,20,22)",
        "disease_target": "Schistosomiasis",
        "description": "An antiparasitic drug used in the treatment of schistosomiasis, specifically Schistosoma mansoni infections."
    }
]

def seed_diseases():
    """Seed the database with neglected diseases data"""
    logger.info("Seeding diseases...")
    for disease_data in DISEASES:
        # Check if disease already exists
        existing = Disease.query.filter_by(name=disease_data['name']).first()
        if existing:
            logger.info(f"Disease '{disease_data['name']}' already exists. Skipping.")
            continue
            
        disease = Disease(
            name=disease_data['name'],
            category=disease_data['category'],
            description=disease_data['description'],
            prevalence=disease_data['prevalence'],
            regions_affected=disease_data['regions_affected'],
            created_at=datetime.utcnow()
        )
        db.session.add(disease)
    
    db.session.commit()
    logger.info(f"Added {len(DISEASES)} diseases to the database.")

def seed_targets():
    """Seed the database with biological targets data"""
    logger.info("Seeding biological targets...")
    for target_data in TARGETS:
        # Check if target already exists
        existing = Target.query.filter_by(name=target_data['name']).first()
        if existing:
            logger.info(f"Target '{target_data['name']}' already exists. Skipping.")
            continue
            
        # Get the disease ID
        disease = Disease.query.filter_by(name=target_data['disease_name']).first()
        if not disease:
            logger.warning(f"Disease '{target_data['disease_name']}' not found. Skipping target '{target_data['name']}'.")
            continue
            
        target = Target(
            name=target_data['name'],
            uniprot_id=target_data['uniprot_id'],
            organism=target_data['organism'],
            function=target_data['function'],
            disease_id=disease.id,
            sequence=target_data['sequence'],
            created_at=datetime.utcnow()
        )
        db.session.add(target)
    
    db.session.commit()
    logger.info(f"Added {len(TARGETS)} targets to the database.")

def seed_compounds():
    """Seed the database with compound data"""
    logger.info("Seeding compounds...")
    compounds_added = 0
    for compound_data in COMPOUNDS:
        # Check if compound already exists
        existing = Compound.query.filter_by(smiles=compound_data['smiles']).first()
        if existing:
            logger.info(f"Compound '{compound_data['name']}' already exists. Skipping.")
            continue
            
        # Calculate molecular properties
        properties = calculate_molecular_properties(compound_data['smiles'])
        
        compound = Compound(
            name=compound_data['name'],
            smiles=compound_data['smiles'],
            inchi=compound_data['inchi'],
            molecular_weight=properties.get('molecular_weight'),
            molecular_formula=properties.get('molecular_formula'),
            logp=properties.get('logp'),
            hba=properties.get('hba'),
            hbd=properties.get('hbd'),
            tpsa=properties.get('tpsa'),
            disease_target=compound_data['disease_target'],
            description=compound_data['description'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(compound)
        compounds_added += 1
    
    db.session.commit()
    logger.info(f"Added {compounds_added} compounds to the database.")
    return compounds_added

def seed_analyses():
    """Seed the database with analysis data"""
    logger.info("Seeding analyses...")
    analyses_added = 0
    
    # Get all compounds
    compounds = Compound.query.all()
    
    for compound in compounds:
        # Get targets related to the compound's disease target
        disease = Disease.query.filter_by(name=compound.disease_target).first()
        if not disease:
            logger.warning(f"Disease '{compound.disease_target}' not found for compound '{compound.name}'. Skipping analyses.")
            continue
            
        targets = Target.query.filter_by(disease_id=disease.id).all()
        
        # Skip if no targets found
        if not targets:
            logger.warning(f"No targets found for disease '{compound.disease_target}'. Skipping analyses for compound '{compound.name}'.")
            continue
            
        # Generate ADMET prediction
        admet = predict_admet_properties(compound.smiles)
        
        # Convert values to ensure they're Python types, not numpy types
        admet_dict = {
            'absorption': float(admet.get('absorption', 0)),
            'toxicity': float(admet.get('toxicity', 0)),
            'blood_brain_barrier': float(admet.get('blood_brain_barrier', 0)),
            'solubility': float(admet.get('solubility', 0)),
            'bioavailability': float(admet.get('bioavailability', 0))
        }
        
        # Create ADMET analysis
        admet_analysis = Analysis(
            compound_id=compound.id,
            analysis_type='ADMET Prediction',
            toxicity_score=admet_dict['toxicity'],
            solubility_score=admet_dict['solubility'],
            blood_brain_barrier=admet_dict['blood_brain_barrier'],
            bioavailability=admet_dict['bioavailability'],
            results_json=str(admet_dict),
            created_at=datetime.utcnow()
        )
        db.session.add(admet_analysis)
        analyses_added += 1
        
        # Create binding prediction for the first target
        target = targets[0]
        binding_score = float(predict_binding_affinity(compound.smiles, target.uniprot_id))
        
        binding_analysis = Analysis(
            compound_id=compound.id,
            target_id=target.id,
            analysis_type='Binding Prediction',
            binding_affinity=binding_score,
            results_json=str({'binding_score': binding_score}),
            created_at=datetime.utcnow()
        )
        db.session.add(binding_analysis)
        analyses_added += 1
    
    db.session.commit()
    logger.info(f"Added {analyses_added} analyses to the database.")

def main():
    """Main function to seed the database"""
    with app.app_context():
        logger.info("Starting database seeding...")
        seed_diseases()
        seed_targets()
        compounds_added = seed_compounds()
        
        # Only add analyses if compounds were added
        if compounds_added > 0:
            seed_analyses()
            
        logger.info("Database seeding completed successfully.")

if __name__ == "__main__":
    main()
