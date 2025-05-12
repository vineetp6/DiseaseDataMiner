/**
 * Creates a radar chart for ADMET properties visualization.
 * 
 * @param {string} elementId - ID of the container element
 * @param {Object} data - ADMET properties data
 */
function createAdmetRadarChart(elementId, data) {
    // Check if D3.js is available
    if (typeof d3 === 'undefined') {
        const element = document.getElementById(elementId);
        element.innerHTML = `
            <div class="alert alert-warning text-center">
                <i data-feather="alert-triangle"></i> D3.js visualization library not available
            </div>
        `;
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        return;
    }
    
    // Prepare the data
    const properties = [
        { name: "Absorption", value: data.absorption || 0, axis: "Absorption" },
        { name: "Solubility", value: data.solubility || 0, axis: "Solubility" },
        { name: "BBB Permeability", value: data.blood_brain_barrier || 0, axis: "BBB" },
        { name: "Bioavailability", value: data.bioavailability || 0, axis: "Bioavailability" },
        { name: "Low Toxicity", value: 1 - (data.toxicity || 0), axis: "Safety" }  // Invert toxicity
    ];
    
    // Set up dimensions
    const element = document.getElementById(elementId);
    const margin = {top: 50, right: 50, bottom: 50, left: 50};
    const width = element.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    const radius = Math.min(width, height) / 2;
    
    // Clear any previous chart
    element.innerHTML = '';
    
    // Create SVG
    const svg = d3.select(`#${elementId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left + width/2}, ${margin.top + height/2})`);
    
    // Define scales
    const angleScale = d3.scaleLinear()
        .domain([0, properties.length])
        .range([0, 2 * Math.PI]);
    
    const radiusScale = d3.scaleLinear()
        .domain([0, 1])
        .range([0, radius]);
    
    // Draw circles
    const circleData = [0.2, 0.4, 0.6, 0.8, 1];
    
    svg.selectAll(".circle")
        .data(circleData)
        .enter()
        .append("circle")
        .attr("cx", 0)
        .attr("cy", 0)
        .attr("r", d => radiusScale(d))
        .attr("fill", "none")
        .attr("stroke", "#666")
        .attr("stroke-dasharray", "2,2")
        .attr("stroke-width", 1);
    
    // Add circle labels (percentages)
    svg.selectAll(".circle-label")
        .data(circleData)
        .enter()
        .append("text")
        .attr("x", 0)
        .attr("y", d => -radiusScale(d) - 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "8px")
        .attr("fill", "#888")
        .text(d => `${d * 100}%`);
    
    // Draw axes
    const axes = svg.selectAll(".axis")
        .data(properties)
        .enter()
        .append("g")
        .attr("class", "axis");
    
    axes.append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", (d, i) => radius * Math.cos(angleScale(i) - Math.PI/2))
        .attr("y2", (d, i) => radius * Math.sin(angleScale(i) - Math.PI/2))
        .attr("stroke", "#666")
        .attr("stroke-width", 1);
    
    // Add axis labels
    axes.append("text")
        .attr("x", (d, i) => (radius + 10) * Math.cos(angleScale(i) - Math.PI/2))
        .attr("y", (d, i) => (radius + 10) * Math.sin(angleScale(i) - Math.PI/2))
        .attr("text-anchor", (d, i) => {
            const angle = angleScale(i);
            if (Math.abs(angle - Math.PI) < 0.1 || Math.abs(angle - 0) < 0.1) return "middle";
            return angle > Math.PI ? "end" : "start";
        })
        .attr("dominant-baseline", (d, i) => {
            const angle = angleScale(i) - Math.PI/2;
            if (Math.abs(angle - Math.PI/2) < 0.1 || Math.abs(angle + Math.PI/2) < 0.1) return "middle";
            return angle > 0 && angle < Math.PI ? "hanging" : "auto";
        })
        .attr("font-size", "10px")
        .attr("fill", "#eee")
        .text(d => d.axis);
    
    // Generate path data
    const pathData = properties.map((d, i) => {
        const angle = angleScale(i) - Math.PI/2;
        return [
            radiusScale(d.value) * Math.cos(angle),
            radiusScale(d.value) * Math.sin(angle)
        ];
    });
    
    // Draw path and points
    const lineGenerator = d3.lineRadial()
        .angle((d, i) => angleScale(i) - Math.PI/2)
        .radius(d => radiusScale(d.value));
    
    // Draw radar area
    svg.append("path")
        .datum(properties)
        .attr("d", lineGenerator)
        .attr("fill", "rgba(0, 123, 255, 0.3)")
        .attr("stroke", "#007bff")
        .attr("stroke-width", 2);
    
    // Add data points
    svg.selectAll(".point")
        .data(properties)
        .enter()
        .append("circle")
        .attr("cx", (d, i) => radiusScale(d.value) * Math.cos(angleScale(i) - Math.PI/2))
        .attr("cy", (d, i) => radiusScale(d.value) * Math.sin(angleScale(i) - Math.PI/2))
        .attr("r", 5)
        .attr("fill", "#007bff");
    
    // Add title
    svg.append("text")
        .attr("x", 0)
        .attr("y", -radius - 20)
        .attr("text-anchor", "middle")
        .attr("font-size", "14px")
        .attr("font-weight", "bold")
        .attr("fill", "#eee")
        .text("ADMET Properties");
    
    // Add data value labels
    svg.selectAll(".value-label")
        .data(properties)
        .enter()
        .append("text")
        .attr("x", (d, i) => (radiusScale(d.value) + 10) * Math.cos(angleScale(i) - Math.PI/2))
        .attr("y", (d, i) => (radiusScale(d.value) + 10) * Math.sin(angleScale(i) - Math.PI/2))
        .attr("text-anchor", "middle")
        .attr("font-size", "9px")
        .attr("fill", "#fff")
        .text(d => `${Math.round(d.value * 100)}%`);
}

/**
 * Creates a visualization for binding affinity.
 * 
 * @param {string} elementId - ID of the container element
 * @param {number} bindingScore - Binding affinity score (0-1)
 */
function createBindingVisualization(elementId, bindingScore) {
    // Check if D3.js is available
    if (typeof d3 === 'undefined') {
        const element = document.getElementById(elementId);
        element.innerHTML = `
            <div class="alert alert-warning text-center">
                <i data-feather="alert-triangle"></i> D3.js visualization library not available
            </div>
        `;
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        return;
    }
    
    // Set up dimensions
    const element = document.getElementById(elementId);
    const width = element.clientWidth;
    const height = 200;
    
    // Clear any previous chart
    element.innerHTML = '';
    
    // Create SVG
    const svg = d3.select(`#${elementId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Create a visual representation of binding
    // We'll use a lock-and-key visualization
    
    // Define colors
    const colorScale = d3.scaleLinear()
        .domain([0, 0.4, 0.7, 1])
        .range(["#dc3545", "#ffc107", "#28a745", "#28a745"]);
    
    const bindingColor = colorScale(bindingScore);
    
    // Create binding visualization group
    const g = svg.append("g")
        .attr("transform", `translate(${width/2}, ${height/2})`);
    
    // Draw protein (target) shape
    const proteinGroup = g.append("g");
    
    // Create a receptor pocket shape
    proteinGroup.append("rect")
        .attr("x", -60)
        .attr("y", -40)
        .attr("width", 120)
        .attr("height", 80)
        .attr("rx", 15)
        .attr("ry", 15)
        .attr("fill", "#555")
        .attr("stroke", "#888")
        .attr("stroke-width", 2);
    
    // Add a binding pocket
    const pocketWidth = 50;
    proteinGroup.append("rect")
        .attr("x", -pocketWidth/2)
        .attr("y", -30)
        .attr("width", pocketWidth)
        .attr("height", 60)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("fill", "#333");
    
    // Draw compound shape (key)
    const compoundWidth = pocketWidth * (0.65 + bindingScore * 0.3); // Adjust fit based on binding score
    const compoundGroup = g.append("g");
    
    // Define the "key" shape
    compoundGroup.append("rect")
        .attr("x", -compoundWidth/2)
        .attr("y", -25)
        .attr("width", compoundWidth)
        .attr("height", 50)
        .attr("rx", 8)
        .attr("ry", 8)
        .attr("fill", bindingColor)
        .attr("stroke", "#fff")
        .attr("stroke-width", 1);
    
    // Add some atom-like circles to the compound
    const atoms = [
        { cx: -compoundWidth/3, cy: 0, r: 8 },
        { cx: 0, cy: -10, r: 6 },
        { cx: compoundWidth/3, cy: 5, r: 7 }
    ];
    
    compoundGroup.selectAll(".atom")
        .data(atoms)
        .enter()
        .append("circle")
        .attr("cx", d => d.cx)
        .attr("cy", d => d.cy)
        .attr("r", d => d.r)
        .attr("fill", d3.color(bindingColor).darker(0.5));
    
    // Create a binding indicator
    const bindingIndicator = svg.append("g")
        .attr("transform", `translate(${width/2}, ${height - 30})`);
    
    // Add binding score label
    bindingIndicator.append("text")
        .attr("x", 0)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .attr("font-size", "14px")
        .attr("fill", "#eee")
        .text(`Binding Score: ${Math.round(bindingScore * 100)}%`);
    
    // Add fit indicator
    bindingIndicator.append("text")
        .attr("x", 0)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .attr("fill", bindingColor)
        .text(() => {
            if (bindingScore >= 0.7) return "Strong binding";
            if (bindingScore >= 0.4) return "Moderate binding";
            return "Weak binding";
        });
}

/**
 * Creates a bar chart visualization.
 * 
 * @param {string} elementId - ID of the container element
 * @param {Array} data - Array of data objects with name and value properties
 * @param {Object} options - Chart options
 */
function createBarChart(elementId, data, options = {}) {
    // Check if D3.js is available
    if (typeof d3 === 'undefined') {
        const element = document.getElementById(elementId);
        element.innerHTML = `
            <div class="alert alert-warning text-center">
                <i data-feather="alert-triangle"></i> D3.js visualization library not available
            </div>
        `;
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        return;
    }
    
    // Default options
    const defaults = {
        margin: { top: 30, right: 30, bottom: 60, left: 60 },
        width: 400,
        height: 300,
        color: "#007bff",
        title: "Bar Chart",
        xAxisLabel: "",
        yAxisLabel: ""
    };
    
    // Merge options
    const opts = {...defaults, ...options};
    
    // Get container dimensions
    const element = document.getElementById(elementId);
    opts.width = options.width || element.clientWidth;
    
    // Calculate inner dimensions
    const width = opts.width - opts.margin.left - opts.margin.right;
    const height = opts.height - opts.margin.top - opts.margin.bottom;
    
    // Clear any previous chart
    element.innerHTML = '';
    
    // Create SVG
    const svg = d3.select(`#${elementId}`)
        .append("svg")
        .attr("width", opts.width)
        .attr("height", opts.height);
    
    // Create chart group
    const g = svg.append("g")
        .attr("transform", `translate(${opts.margin.left}, ${opts.margin.top})`);
    
    // Create scales
    const x = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([0, width])
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value) * 1.1]) // Add 10% padding
        .range([height, 0]);
    
    // Create axes
    const xAxis = g.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em");
    
    const yAxis = g.append("g")
        .call(d3.axisLeft(y));
    
    // Add bars
    g.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.name))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.value))
        .attr("fill", opts.color);
    
    // Add title
    svg.append("text")
        .attr("x", opts.width / 2)
        .attr("y", opts.margin.top / 2)
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .attr("fill", "#eee")
        .text(opts.title);
    
    // Add x-axis label
    if (opts.xAxisLabel) {
        svg.append("text")
            .attr("x", opts.width / 2)
            .attr("y", opts.height - 5)
            .attr("text-anchor", "middle")
            .attr("font-size", "12px")
            .attr("fill", "#eee")
            .text(opts.xAxisLabel);
    }
    
    // Add y-axis label
    if (opts.yAxisLabel) {
        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", -(opts.height / 2))
            .attr("y", 15)
            .attr("text-anchor", "middle")
            .attr("font-size", "12px")
            .attr("fill", "#eee")
            .text(opts.yAxisLabel);
    }
    
    // Add data values on top of bars
    g.selectAll(".bar-label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d.name) + x.bandwidth() / 2)
        .attr("y", d => y(d.value) - 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "#eee")
        .text(d => d.value.toFixed(2));
}
