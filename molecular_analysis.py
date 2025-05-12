import logging
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem

def calculate_molecular_properties(smiles):
    """
    Calculate molecular properties using RDKit.
    
    Args:
        smiles (str): SMILES string of the compound
    
    Returns:
        dict: Dictionary containing calculated molecular properties
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logging.error(f"Invalid SMILES string: {smiles}")
            return {
                'error': 'Invalid SMILES string',
                'molecular_weight': None,
                'logp': None,
                'hba': None,
                'hbd': None,
                'tpsa': None,
                'qed': None,
                'num_rings': None,
                'rotatable_bonds': None
            }
        
        # Calculate properties
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hba = Descriptors.NumHAcceptors(mol)
        hbd = Descriptors.NumHDonors(mol)
        tpsa = Descriptors.TPSA(mol)
        qed = Descriptors.qed(mol)
        num_rings = Descriptors.RingCount(mol)
        rotatable_bonds = Descriptors.NumRotatableBonds(mol)
        
        # Generate molecular formula
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        
        return {
            'molecular_weight': round(mw, 2),
            'logp': round(logp, 2),
            'hba': hba,
            'hbd': hbd,
            'tpsa': round(tpsa, 2),
            'qed': round(qed, 3),
            'num_rings': num_rings,
            'rotatable_bonds': rotatable_bonds,
            'molecular_formula': formula
        }
    except Exception as e:
        logging.error(f"Error calculating molecular properties: {str(e)}")
        return {
            'error': str(e),
            'molecular_weight': None,
            'logp': None,
            'hba': None,
            'hbd': None,
            'tpsa': None,
            'qed': None,
            'num_rings': None,
            'rotatable_bonds': None
        }

def generate_2d_structure(smiles):
    """
    Generate a 2D structure SVG from a SMILES string.
    
    Args:
        smiles (str): SMILES string of the compound
    
    Returns:
        str: SVG string of the molecular structure
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logging.error(f"Invalid SMILES string for 2D structure: {smiles}")
            return ""
        
        # Generate 2D coordinates
        AllChem.Compute2DCoords(mol)
        
        # Draw molecule as SVG
        drawer = Draw.MolDraw2DSVG(300, 200)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        
        return svg
    except Exception as e:
        logging.error(f"Error generating 2D structure: {str(e)}")
        return ""

def check_lipinski_rule_of_five(smiles):
    """
    Check if compound follows Lipinski's Rule of Five.
    
    Args:
        smiles (str): SMILES string of the compound
    
    Returns:
        tuple: (bool, dict) - whether it passes and details of violations
    """
    properties = calculate_molecular_properties(smiles)
    
    # Lipinski's Rule of Five criteria
    mw_pass = properties.get('molecular_weight', 0) <= 500
    logp_pass = properties.get('logp', 0) <= 5
    hbd_pass = properties.get('hbd', 0) <= 5
    hba_pass = properties.get('hba', 0) <= 10
    
    # Count violations
    violations = sum(not x for x in [mw_pass, logp_pass, hbd_pass, hba_pass])
    
    return (violations <= 1, {
        'molecular_weight': {'value': properties.get('molecular_weight'), 'pass': mw_pass},
        'logp': {'value': properties.get('logp'), 'pass': logp_pass},
        'hbd': {'value': properties.get('hbd'), 'pass': hbd_pass},
        'hba': {'value': properties.get('hba'), 'pass': hba_pass},
        'violations': violations
    })

def generate_similar_compounds(smiles, num=5, similarity_threshold=0.7):
    """
    Generate similar compounds based on SMILES using Morgan fingerprints.
    This is a placeholder - in a real application, this would search a database 
    or use a generative model.
    
    Args:
        smiles (str): SMILES string of the reference compound
        num (int): Number of similar compounds to return
        similarity_threshold (float): Minimum similarity score (0-1)
    
    Returns:
        list: List of dictionaries with similar compounds
    """
    # This is a placeholder - would require a database of compounds to search
    # In a real app, this would search a database using fingerprint similarity
    
    return [
        {
            'smiles': smiles,
            'similarity': 1.0,
            'name': 'Reference Compound'
        }
    ]
