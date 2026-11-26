
function getThemeColour(variable) {

    const element = document.createElement("span");

    element.style.color = `var(${variable})`;
    document.body.appendChild(element);

    const colour = getComputedStyle(element).color;

    element.remove();

    return colour;
}


export function updateChromaticityTheme() {

    const textColour = getThemeColour("--text");
    const mutedColour = getThemeColour("--muted");

    const graph = document.getElementById("colour-space-viewer");

    if (!graph || !graph._fullLayout) {
        return;
    }

    Plotly.relayout(
        graph,
        {
            "font.color": textColour,

            "xaxis.tickfont.color": textColour,
            "xaxis.linecolor": mutedColour,
            "xaxis.tickcolor": mutedColour,

            "yaxis.tickfont.color": textColour,
            "yaxis.linecolor": mutedColour,
            "yaxis.tickcolor": mutedColour,

            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)"
        }
    );
}


window.updateChromaticityTheme = updateChromaticityTheme;


export function renderChromaticityDiagram(data) {

    const styles = getComputedStyle(document.documentElement);

    const textColour = getThemeColour("--text");
    const mutedColour = getThemeColour("--muted");

    const background = data.background;

    // Coloured chromaticity background.
    const backgroundTrace = {
        type: "image",
        z: background.rgb,
        colormodel: "rgba",

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

    const gamutTrace = {
        x: [0.6400, 0.3000, 0.1500, 0.6400],
        y: [0.3300, 0.6000, 0.0600, 0.3300],

        mode: "lines",
        type: "scatter",
        name: "sRGB gamut",

        line: {
            color: "#222222",
            width: 1,
            dash: "solid"
        },

        hovertemplate:
            "x: %{x:.4f}<br>" +
            "y: %{y:.4f}<br>" +
            "<extra>sRGB gamut</extra>"
    };

    const whitePointTrace = {
        x: [0.3127],
        y: [0.3290],

        mode: "markers",
        type: "scatter",
        name: "D65 white point",

        marker: {
            size: 9,
            color: "white",
            line: {
                color: "#222222",
                width: 1
            },
            symbol: "circle"
        },

        hovertemplate:
            "x: %{x:.4f}<br>" +
            "y: %{y:.4f}<br>" +
            "<extra>D65 white point</extra>"
    };

    const interpolationTrace = {
        x: data.interpolation_x,
        y: data.interpolation_y,

        mode: "lines",
        type: "scatter",
        name: "Interpolation path",

        connectgaps: false,

        line: {
            color: "#222222",
            width: 1.5,
            dash: "dash"
        },

        hovertemplate:
            "x: %{x:.4f}<br>" +
            "y: %{y:.4f}<br>" +
            "<extra>Interpolation path</extra>"
    };

    const waypointTrace = {
        x: data.waypoint_x,
        y: data.waypoint_y,

        mode: "markers",
        type: "scatter",
        name: "Waypoints",

        marker: {
            size: 11,
            color: data.waypoint_colours,
            opacity: 1,
            line: {
                color: "#222222",
                width: 1.2
            },
            symbol: "circle"
        },

        customdata: data.waypoint_colours,

        hovertemplate:
            "x: %{x:.4f}<br>" +
            "y: %{y:.4f}<br>" +
            "Colour: %{customdata}<br>" +
            "<extra>Waypoint</extra>"
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
            zeroline: false,
            color: textColour,
            linecolor: mutedColour,
            tickcolor: mutedColour,
            gridcolor: "rgba(0,0,0,0)"
        },

        yaxis: {
            title: "CIE y",
            range: [0, 0.9],
            zeroline: false,
            scaleanchor: "x",
            scaleratio: 1,
            color: textColour,
            linecolor: mutedColour,
            tickcolor: mutedColour,
            gridcolor: "rgba(0,0,0,0)"
        },

        showlegend: false,

        // Transparent backgrounds.
        plot_bgcolor: "rgba(0,0,0,0)",
        paper_bgcolor: "rgba(0,0,0,0)",

        // Text and axis styling.
        font: {
            color: textColour
        },

        annotations: [
            {
                x: 0.35,
                y: 0.6000,
                xref: "x",
                yref: "y",
                text: "sRGB",
                showarrow: false,
                font: {
                    size: 11,
                    color: "#222222"
                }
            },
            {
                x: 0.3127,
                y: 0.3290,
                xref: "x",
                yref: "y",
                text: "D65",
                showarrow: false,
                xshift: 13,
                yshift: 10,
                font: {
                    size: 11,
                    color: "#222222"
                }
            }
        ],
    };

    Plotly.newPlot(
        "colour-space-viewer",
        [
            backgroundTrace,
            spectralTrace,
            gamutTrace,
            whitePointTrace,
            interpolationTrace,
            waypointTrace
        ],
        layout,
        {
            responsive: true
        }
    );
}

export function updateChromaticityWaypoints(data) {

    // Update waypoint markers.
    Plotly.restyle(
        "colour-space-viewer",
        {
            x: [data.waypoint_x],
            y: [data.waypoint_y],
            "marker.color": [data.waypoint_colours],
            customdata: [data.waypoint_colours]
        },
        [5]
    );

    // Update interpolation path.
    Plotly.restyle(
        "colour-space-viewer",
        {
            x: [data.interpolation_x],
            y: [data.interpolation_y]
        },
        [4]
    );
}

window.renderChromaticityDiagram = renderChromaticityDiagram;
window.updateChromaticityWaypoints = updateChromaticityWaypoints;
