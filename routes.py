import json
from flask import render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy import or_
from app import app, db
from models import Compound, Disease, Target, Analysis
from molecular_analysis import calculate_molecular_properties, generate_2d_structure
from ml_models import predict_binding_affinity, predict_admet_properties

@app.route('/')
def index():
    """Home page with dashboard and introduction."""
    compound_count = Compound.query.count()
    disease_count = Disease.query.count()
    target_count = Target.query.count()
    analysis_count = Analysis.query.count()
    
    # Get recent compounds for display
    recent_compounds = Compound.query.order_by(Compound.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                          compound_count=compound_count,
                          disease_count=disease_count,
                          target_count=target_count,
                          analysis_count=analysis_count,
                          recent_compounds=recent_compounds)

@app.route('/search')
def search():
    """Search compounds and display results."""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limit per_page to reasonable values
    if per_page < 10:
        per_page = 10
    elif per_page > 100:
        per_page = 100
    
    # If search query provided
    if query:
        # Search in multiple fields
        compounds = Compound.query.filter(
            or_(
                Compound.name.ilike(f'%{query}%'),
                Compound.smiles.ilike(f'%{query}%'),
                Compound.molecular_formula.ilike(f'%{query}%'),
                Compound.disease_target.ilike(f'%{query}%')
            )
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        # Display all compounds if no search term
        compounds = Compound.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('search.html', 
                          compounds=compounds,
                          query=query)

@app.route('/compound/<int:id>')
def compound_details(id):
    """Display detailed information about a compound."""
    compound = Compound.query.get_or_404(id)
    analyses = Analysis.query.filter_by(compound_id=id).all()
    
    # Generate 2D structure SVG if not provided
    structure_svg = generate_2d_structure(compound.smiles)
    
    return render_template('compound_details.html',
                          compound=compound,
                          analyses=analyses,
                          structure_svg=structure_svg)

@app.route('/analyze/<int:id>', methods=['GET', 'POST'])
def analyze_compound(id):
    """Perform and display analysis for a compound."""
    compound = Compound.query.get_or_404(id)
    
    if request.method == 'POST':
        # Get analysis parameters
        analysis_type = request.form.get('analysis_type')
        target_id = request.form.get('target_id', type=int, default=None)
        
        # Run the appropriate analysis
        results = {}
        
        if analysis_type == 'properties':
            # Calculate molecular properties
            properties = calculate_molecular_properties(compound.smiles)
            
            # Update compound with calculated properties
            compound.molecular_weight = properties.get('molecular_weight')
            compound.logp = properties.get('logp')
            compound.hba = properties.get('hba')
            compound.hbd = properties.get('hbd')
            compound.tpsa = properties.get('tpsa')
            db.session.commit()
            
            results = properties
            
        elif analysis_type == 'binding':
            if not target_id:
                flash('Target must be selected for binding analysis', 'error')
                targets = Target.query.all()
                return render_template('analysis.html', compound=compound, targets=targets)
            
            # Predict binding affinity
            target = Target.query.get_or_404(target_id)
            binding_score = predict_binding_affinity(compound.smiles, target.uniprot_id)
            
            # Save analysis results
            analysis = Analysis(
                compound_id=id,
                target_id=target_id,
                analysis_type='Binding Prediction',
                binding_affinity=binding_score,
                results_json=json.dumps({'binding_score': binding_score})
            )
            db.session.add(analysis)
            db.session.commit()
            
            results = {'binding_score': binding_score}
            
        elif analysis_type == 'admet':
            # Predict ADMET properties
            admet = predict_admet_properties(compound.smiles)
            
            # Save analysis results
            analysis = Analysis(
                compound_id=id,
                analysis_type='ADMET Prediction',
                toxicity_score=admet.get('toxicity'),
                solubility_score=admet.get('solubility'),
                blood_brain_barrier=admet.get('blood_brain_barrier'),
                bioavailability=admet.get('bioavailability'),
                results_json=json.dumps(admet)
            )
            db.session.add(analysis)
            db.session.commit()
            
            results = admet
        
        flash(f'{analysis_type.capitalize()} analysis completed successfully', 'success')
        return render_template('analysis.html', 
                             compound=compound, 
                             results=results, 
                             analysis_type=analysis_type,
                             targets=Target.query.all())
    
    # GET request - show analysis options
    targets = Target.query.all()
    return render_template('analysis.html', compound=compound, targets=targets)

@app.route('/api/compound/<int:id>/structure')
def get_compound_structure(id):
    """API endpoint to get compound structure data."""
    compound = Compound.query.get_or_404(id)
    return jsonify({
        'smiles': compound.smiles,
        'name': compound.name,
        'inchi': compound.inchi,
    })

@app.route('/api/compounds')
def api_compounds():
    """API endpoint to get filtered compounds."""
    # Get filter parameters
    disease = request.args.get('disease', '')
    property_min = request.args.get('property_min', type=float)
    property_max = request.args.get('property_max', type=float)
    property_name = request.args.get('property', '')
    
    # Start with base query
    query = Compound.query
    
    # Apply filters
    if disease:
        query = query.filter(Compound.disease_target.ilike(f'%{disease}%'))
    
    if property_name and (property_min is not None or property_max is not None):
        if property_name == 'mw':
            if property_min is not None:
                query = query.filter(Compound.molecular_weight >= property_min)
            if property_max is not None:
                query = query.filter(Compound.molecular_weight <= property_max)
        elif property_name == 'logp':
            if property_min is not None:
                query = query.filter(Compound.logp >= property_min)
            if property_max is not None:
                query = query.filter(Compound.logp <= property_max)
    
    # Get results
    compounds = query.limit(100).all()
    
    # Format response
    results = []
    for compound in compounds:
        results.append({
            'id': compound.id,
            'name': compound.name,
            'smiles': compound.smiles,
            'molecular_weight': compound.molecular_weight,
            'logp': compound.logp,
            'hba': compound.hba,
            'hbd': compound.hbd,
            'disease_target': compound.disease_target
        })
    
    return jsonify(results)

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template('404.html'), 404

@app.route('/target_identification', methods=['GET', 'POST'])
def target_identification():
    """Target identification and validation interface."""
    targets = Target.query.all()
    diseases = Disease.query.all()
    
    if request.method == 'POST':
        disease_id = request.form.get('disease_id', type=int)
        target_criteria = request.form.get('target_criteria', '')
        
        query = Target.query
        
        if disease_id:
            query = query.filter_by(disease_id=disease_id)
        
        if target_criteria:
            query = query.filter(Target.name.ilike(f'%{target_criteria}%') | 
                                Target.function.ilike(f'%{target_criteria}%') |
                                Target.organism.ilike(f'%{target_criteria}%'))
        
        potential_targets = query.all()
        
        # Find compounds tested against these targets
        target_ids = [t.id for t in potential_targets]
        target_compound_analyses = {}
        
        if target_ids:
            analyses = Analysis.query.filter(
                Analysis.target_id.in_(target_ids), 
                Analysis.analysis_type == 'Binding Prediction'
            ).order_by(Analysis.binding_affinity.desc()).all()
            
            for analysis in analyses:
                if analysis.target_id not in target_compound_analyses:
                    target_compound_analyses[analysis.target_id] = []
                
                if len(target_compound_analyses[analysis.target_id]) < 3:  # Limit to top 3
                    compound = Compound.query.get(analysis.compound_id)
                    if compound:
                        target_compound_analyses[analysis.target_id].append({
                            'compound': compound,
                            'binding_score': analysis.binding_affinity
                        })
        
        return render_template('target_identification.html', 
                              diseases=diseases,
                              targets=targets,
                              potential_targets=potential_targets,
                              target_compound_analyses=target_compound_analyses,
                              selected_disease=disease_id,
                              target_criteria=target_criteria)
                              
    return render_template('target_identification.html', 
                          diseases=diseases,
                          targets=targets)

@app.route('/compound_screening', methods=['GET', 'POST'])
def compound_screening():
    """Compound screening and ranking interface."""
    diseases = Disease.query.all()
    compounds = []
    selected_disease = None
    
    if request.method == 'POST':
        disease_id = request.form.get('disease_id', type=int)
        property_filter = request.form.get('property_filter', '')
        
        if disease_id:
            selected_disease = Disease.query.get_or_404(disease_id)
            disease_targets = Target.query.filter_by(disease_id=disease_id).all()
            target_ids = [t.id for t in disease_targets]
            
            # Find compounds tested against these targets
            if target_ids:
                # Get all analyses for these targets
                analyses = Analysis.query.filter(
                    Analysis.target_id.in_(target_ids),
                    Analysis.analysis_type == 'Binding Prediction'
                ).order_by(Analysis.binding_affinity.desc()).all()
                
                # Get unique compounds with their best binding score
                compound_scores = {}
                for analysis in analyses:
                    if analysis.compound_id not in compound_scores or analysis.binding_affinity > compound_scores[analysis.compound_id]['score']:
                        compound = Compound.query.get(analysis.compound_id)
                        if compound:
                            compound_scores[analysis.compound_id] = {
                                'compound': compound,
                                'score': analysis.binding_affinity,
                                'target': Target.query.get(analysis.target_id)
                            }
                
                # Apply additional property filters
                if property_filter:
                    filtered_scores = {}
                    if property_filter == 'lipinski':
                        # Filter by Lipinski's Rule of Five
                        for compound_id, data in compound_scores.items():
                            compound = data['compound']
                            if (compound.molecular_weight <= 500 and 
                                compound.logp <= 5 and 
                                compound.hbd <= 5 and 
                                compound.hba <= 10):
                                filtered_scores[compound_id] = data
                        compound_scores = filtered_scores
                    elif property_filter == 'low_toxicity':
                        # Filter by toxicity
                        for compound_id, data in compound_scores.items():
                            admet_analysis = Analysis.query.filter_by(
                                compound_id=compound_id,
                                analysis_type='ADMET Prediction'
                            ).first()
                            if admet_analysis and admet_analysis.toxicity_score and admet_analysis.toxicity_score < 0.4:
                                filtered_scores[compound_id] = data
                        compound_scores = filtered_scores
                
                # Convert to list and sort by score
                compounds = list(compound_scores.values())
                compounds.sort(key=lambda x: x['score'], reverse=True)
        
        return render_template('compound_screening.html',
                              diseases=diseases,
                              compounds=compounds,
                              selected_disease=selected_disease,
                              property_filter=property_filter)
    
    return render_template('compound_screening.html',
                          diseases=diseases,
                          compounds=compounds)

@app.route('/dashboard')
def dashboard():
    """Interactive dashboard and visualization."""
    # Get statistics for dashboard
    compound_count = Compound.query.count()
    disease_count = Disease.query.count()
    target_count = Target.query.count()
    analysis_count = Analysis.query.count()
    
    # Disease distribution
    disease_compounds = db.session.query(
        Compound.disease_target, 
        db.func.count(Compound.id)
    ).group_by(Compound.disease_target).all()
    
    # Make sure to handle None values in disease_target
    disease_compounds = [(disease if disease else "Unknown", count) for disease, count in disease_compounds]
    
    # Get property distributions
    mw_ranges = [
        {'min': 0, 'max': 250, 'label': '<250'},
        {'min': 250, 'max': 500, 'label': '250-500'},
        {'min': 500, 'max': 750, 'label': '500-750'},
        {'min': 750, 'max': 10000, 'label': '>750'}
    ]
    
    mw_distribution = []
    for range_data in mw_ranges:
        count = Compound.query.filter(
            Compound.molecular_weight >= range_data['min'],
            Compound.molecular_weight < range_data['max']
        ).count()
        mw_distribution.append({
            'label': range_data['label'],
            'count': count
        })
    
    # Get recent analyses
    recent_analyses = Analysis.query.order_by(Analysis.created_at.desc()).limit(5).all()
    
    # Format analysis data for display
    formatted_analyses = []
    for analysis in recent_analyses:
        compound = Compound.query.get(analysis.compound_id)
        if compound:
            formatted_analyses.append({
                'id': analysis.id,
                'type': analysis.analysis_type,
                'compound_name': compound.name,
                'compound_id': compound.id,
                'date': analysis.created_at.strftime('%Y-%m-%d'),
                'binding_score': analysis.binding_affinity if analysis.binding_affinity else None,
                'target_name': Target.query.get(analysis.target_id).name if analysis.target_id else None
            })
    
    return render_template('dashboard.html',
                          compound_count=compound_count,
                          disease_count=disease_count,
                          target_count=target_count,
                          analysis_count=analysis_count,
                          disease_compounds=disease_compounds,
                          mw_distribution=mw_distribution,
                          recent_analyses=formatted_analyses)

@app.errorhandler(500)
def server_error(e):
    """Custom 500 page."""
    return render_template('500.html'), 500
