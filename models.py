from datetime import datetime
from app import db

class Compound(db.Model):
    """Model for chemical compounds."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    smiles = db.Column(db.String(1000), nullable=False, unique=True)
    inchi = db.Column(db.String(1000), nullable=True)
    molecular_weight = db.Column(db.Float, nullable=True)
    molecular_formula = db.Column(db.String(200), nullable=True)
    logp = db.Column(db.Float, nullable=True)
    hba = db.Column(db.Integer, nullable=True)  # Hydrogen Bond Acceptors
    hbd = db.Column(db.Integer, nullable=True)  # Hydrogen Bond Donors
    tpsa = db.Column(db.Float, nullable=True)  # Topological Polar Surface Area
    disease_target = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analyses = db.relationship('Analysis', backref='compound', lazy=True)

    def __repr__(self):
        return f"<Compound {self.name}>"

class Disease(db.Model):
    """Model for neglected diseases."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    prevalence = db.Column(db.String(100), nullable=True)
    regions_affected = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Disease {self.name}>"

class Target(db.Model):
    """Model for biological targets (proteins, enzymes, etc.)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    uniprot_id = db.Column(db.String(20), nullable=True, unique=True)
    organism = db.Column(db.String(100), nullable=True)
    function = db.Column(db.Text, nullable=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=True)
    sequence = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    disease = db.relationship('Disease', backref='targets')

    def __repr__(self):
        return f"<Target {self.name}>"

class Analysis(db.Model):
    """Model for storing analysis results."""
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=True)
    analysis_type = db.Column(db.String(50), nullable=False)  # e.g., "Docking", "ADMET", "ML Prediction"
    binding_affinity = db.Column(db.Float, nullable=True)
    toxicity_score = db.Column(db.Float, nullable=True)
    solubility_score = db.Column(db.Float, nullable=True)
    blood_brain_barrier = db.Column(db.Float, nullable=True)
    bioavailability = db.Column(db.Float, nullable=True)
    effectiveness_score = db.Column(db.Float, nullable=True)
    results_json = db.Column(db.Text, nullable=True)  # JSON string for additional results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    target = db.relationship('Target', backref='analyses')

    def __repr__(self):
        return f"<Analysis {self.analysis_type} for Compound {self.compound_id}>"
