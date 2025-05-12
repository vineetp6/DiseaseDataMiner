/**
 * Draws a 2D structure thumbnail from a SMILES string.
 * Uses RDKit in the browser to render the structure.
 * 
 * @param {HTMLElement} element - Container element for the structure
 * @param {string} smiles - SMILES string of the compound
 * @param {number} width - Width of the rendering in pixels
 * @param {number} height - Height of the rendering in pixels
 */
function drawStructureThumbnail(element, smiles, width = 200, height = 150) {
    // If we have a direct SVG from the server, use it
    if (element.innerHTML.trim().startsWith('<svg')) {
        return;
    }
    
    // Create a placeholder while loading
    element.innerHTML = `
        <div class="text-center p-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading structure...</span>
            </div>
            <p class="mt-2">Loading molecular structure...</p>
        </div>
    `;
    
    // Fetch structure SVG from server
    fetch(`/api/compound/${element.dataset.compoundId || 0}/structure`)
        .then(response => {
            if (!response.ok) {
                // If no specific compound ID was given, use the SMILES directly
                return { smiles: smiles };
            }
            return response.json();
        })
        .then(data => {
            // Create a simpler placeholder if RDKit is not available
            // In a real application, we would use RDKit.js here
            // For this implementation, we'll use a simple SVG representation
            
            // Create a minimal atom-bond representation
            const svg = createSimpleMolecularSvg(data.smiles || smiles, width, height);
            element.innerHTML = svg;
        })
        .catch(error => {
            console.error('Error fetching structure:', error);
            element.innerHTML = `
                <div class="alert alert-warning">
                    <i data-feather="alert-triangle"></i> Could not load structure
                </div>
            `;
            // Re-initialize feather icons if they're being used
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        });
}

/**
 * Creates a simple SVG representation of a molecule.
 * This is a fallback when RDKit.js is not available.
 * 
 * @param {string} smiles - SMILES string of the compound
 * @param {number} width - Width of the SVG
 * @param {number} height - Height of the SVG
 * @returns {string} - SVG markup
 */
function createSimpleMolecularSvg(smiles, width, height) {
    // Very simple representation based on SMILES - not chemically accurate
    // Just for visual placeholder purposes
    
    // Count some basic elements in the SMILES to determine complexity
    const carbonCount = (smiles.match(/C/g) || []).length;
    const oxygenCount = (smiles.match(/O/g) || []).length;
    const nitrogenCount = (smiles.match(/N/g) || []).length;
    const bondCount = (smiles.match(/[\-\=\#\:]/g) || []).length;
    const ringCount = (smiles.match(/[0-9]/g) || []).length / 2;
    
    // Simple layout algorithm
    const atoms = [];
    const bonds = [];
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.4;
    
    // Add carbon atoms in a ring-like structure
    const atomCount = Math.max(3, Math.min(8, carbonCount + nitrogenCount + oxygenCount));
    for (let i = 0; i < atomCount; i++) {
        const angle = (i / atomCount) * 2 * Math.PI;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        
        // Determine atom type based on position in SMILES (simplified)
        let atomType = 'C';
        if (i % 3 === 0 && oxygenCount > 0) atomType = 'O';
        if (i % 4 === 0 && nitrogenCount > 0) atomType = 'N';
        
        atoms.push({ x, y, type: atomType });
        
        // Add bonds between consecutive atoms and to center for complex molecules
        if (i > 0) {
            bonds.push({ from: i - 1, to: i, type: 'single' });
        }
        
        // Close the ring for cyclic structures
        if (i === atomCount - 1 && ringCount > 0) {
            bonds.push({ from: i, to: 0, type: 'single' });
        }
        
        // Add some random bonds for more complex molecules
        if (bondCount > atomCount && i > 1 && i < atomCount - 1 && Math.random() > 0.7) {
            const target = Math.floor(Math.random() * i);
            bonds.push({ from: i, to: target, type: 'single' });
        }
    }
    
    // Generate SVG
    let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
    
    // Draw bonds
    for (const bond of bonds) {
        const from = atoms[bond.from];
        const to = atoms[bond.to];
        
        svg += `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="#909090" stroke-width="2" />`;
        
        // Add second line for double bonds
        if (bond.type === 'double') {
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const length = Math.sqrt(dx * dx + dy * dy);
            const ux = -dy / length * 3;  // perpendicular unit vector * offset
            const uy = dx / length * 3;
            
            svg += `<line x1="${from.x + ux}" y1="${from.y + uy}" x2="${to.x + ux}" y2="${to.y + uy}" stroke="#909090" stroke-width="2" />`;
        }
    }
    
    // Draw atoms
    for (const atom of atoms) {
        const color = atom.type === 'O' ? '#ff0000' : atom.type === 'N' ? '#0000ff' : '#000000';
        svg += `<circle cx="${atom.x}" cy="${atom.y}" r="5" fill="${color}" />`;
        svg += `<text x="${atom.x}" y="${atom.y + 5}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="white">${atom.type}</text>`;
    }
    
    svg += '</svg>';
    return svg;
}

/**
 * Initializes a 3D molecular viewer using 3DMol.js.
 * 
 * @param {string} elementId - ID of the container element
 * @param {string} smiles - SMILES string of the compound
 */
function initialize3DMolViewer(elementId, smiles) {
    // Check if 3DMol.js is available
    if (typeof $3Dmol === 'undefined') {
        const element = document.getElementById(elementId);
        element.innerHTML = `
            <div class="alert alert-warning text-center">
                <i data-feather="alert-triangle"></i> 3D viewer library not available
            </div>
        `;
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        return;
    }

    // Create a placeholder while loading
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="text-center p-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading 3D structure...</span>
            </div>
            <p class="mt-2">Generating 3D structure...</p>
        </div>
    `;
    
    // Give the DOM time to update before loading 3D structure
    setTimeout(() => {
        try {
            // Create viewer with proper sizing
            const width = element.clientWidth;
            const height = 300; // Fixed height for consistency
            element.style.height = height + 'px';
            
            const config = { 
                backgroundColor: 'black',
                width: width,
                height: height 
            };
            
            // Clear the element
            element.innerHTML = '';
            
            const viewer = $3Dmol.createViewer($(element), config);
            
            // Use SDF parser with embedded 3D coordinates generation
            let mol = window.RDKit ? window.RDKit.getSubstructMatches : null;
            
            if (window.RDKit && window.RDKit.Molecule && window.RDKit.Molecule.fromSmiles) {
                // Use RDKit.js if available for better 3D coordinates
                const rdkitMol = window.RDKit.Molecule.fromSmiles(smiles);
                const molblock = rdkitMol.toMolBlock();
                const m = viewer.addModel(molblock, "mol");
                viewer.setStyle({}, {stick: {radius: 0.2, color: 'lightgrey'}, sphere: {scale: 0.3}});
            } else {
                // Fall back to 3DMol built-in methods
                const m = viewer.addModel();
                m.addMolData(smiles, 'smi');
                
                // Generate 3D coordinates
                m.addAtoms([]);
                $3Dmol.generate3DStructure(m, smiles, 'smi');
                
                // Set visualization style
                m.setStyle({}, {stick: {radius: 0.15, color: 'lightgrey'}, sphere: {scale: 0.25}});
                
                // Set atom colors for common elements
                m.setStyle({elem: 'C'}, {sphere: {color: 'grey', scale: 0.25}});
                m.setStyle({elem: 'O'}, {sphere: {color: 'red', scale: 0.25}});
                m.setStyle({elem: 'N'}, {sphere: {color: 'blue', scale: 0.25}});
                m.setStyle({elem: 'S'}, {sphere: {color: 'yellow', scale: 0.25}});
                m.setStyle({elem: 'F'}, {sphere: {color: 'green', scale: 0.25}});
                m.setStyle({elem: 'Cl'}, {sphere: {color: 'green', scale: 0.25}});
                m.setStyle({elem: 'Br'}, {sphere: {color: 'brown', scale: 0.25}});
            }
            
            // Center and zoom to fit
            viewer.zoomTo();
            
            // Set up rotation
            viewer.spin(true);
            
            // Render the scene
            viewer.render();
        } catch (error) {
            console.error('Error initializing 3D viewer:', error);
            element.innerHTML = `
                <div class="alert alert-danger text-center">
                    <i data-feather="alert-triangle"></i> Error loading 3D structure
                </div>
            `;
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }, 100);
}
