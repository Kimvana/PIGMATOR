export function renderChromaticityDiagram(data) {

    const background = data.background;

    // Coloured chromaticity background.
    const backgroundTrace = {
        type: "image",
        z: background.rgb,
        colormodel: "rgb",

        x0: background.x0,
        dx: background.dx,

        y0: background.y0,
        dy: background.dy,

        hoverinfo: "skip",
        name: "Chromaticity background"
    };

    // Spectral locus and line of purples.
    const spectralTrace = {
        x: [...data.spectral_x, data.spectral_x[0]],
        y: [...data.spectral_y, data.spectral_y[0]],

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

        showlegend: false,

        plot_bgcolor: "white",
        paper_bgcolor: "white"
    };

    Plotly.newPlot(
        "colour-space-viewer",
        [backgroundTrace, spectralTrace],
        layout,
        {
            responsive: true
        }
    );
}

window.renderChromaticityDiagram = renderChromaticityDiagram;
