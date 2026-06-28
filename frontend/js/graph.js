function renderGraph(data) {
    const svg = d3.select("#graphArea")
        .append("svg")
        .attr("width", "100%")
        .attr("height", 500);

    const nodes = data.nodes || [];
    const links = data.links || [];

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).distance(120))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(600, 250));

    const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke", "#aaa");

    const node = svg.append("g")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", 10)
        .attr("fill", "#0078ff");

    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });
}
