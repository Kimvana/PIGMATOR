
export function renderChromaticityDiagram(data) {

    const trace = {
        x: data.spectral_x,
        y: data.spectral_y,
        mode: "lines",
        type: "scatter",
        name: "Spectral locus",
        line: {
            color: "#333333",
            width: 2
        },
        hovertemplate:
            "x: %{x:.4f}<br>" +
            "y: %{y:.4f}<br>" +
            "<extra>Spectral locus</extra>"
    };

    const layout = {
        margin: {
            l: 45,
            r: 15,
            t: 15,
            b: 40
        },
        xaxis: {
            title: "CIE x",
            range: [0, 0.8],
            zeroline: false
        },
        yaxis: {
            title: "CIE y",
            range: [0, 0.9],
            zeroline: false,
            scaleanchor: "x",
            scaleratio: 1
        },
        showlegend: false
    };

    Plotly.newPlot(
        "colour-space-viewer",
        [trace],
        layout,
        {
            responsive: true
        }
    );
}

window.renderChromaticityDiagram = renderChromaticityDiagram;
