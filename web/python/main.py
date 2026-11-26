
from pyscript import when, document
from pyscript.ffi import is_none

import json
import js

from interpolation import interpolate_palette
import vision
import conversions as conv
import assetloader as al


# ==========================================
# Palette data
# ==========================================

waypoints = [
    "#3478b8"
]

interpolation_method = "srgb"

chromaticity_initialized = False


# ==========================================
# Colour calculations
# ==========================================

def is_valid_hex(colour):
    """Check whether a colour is a valid six-digit hex value."""

    if len(colour) != 7 or not colour.startswith("#"):
        return False

    try:
        int(colour[1:], 16)
        return True
    except ValueError:
        return False


def get_contrasting_text_colour(colour):
    """Return black or white, depending on colour luminance."""

    # Convert sRGB values to linear RGB.
    linear_rgb = conv.srgb_to_linear(conv.hex_to_srgb(colour))

    # Calculate relative luminance.
    luminance = (
        0.2126 * linear_rgb[0]
        + 0.7152 * linear_rgb[1]
        + 0.0722 * linear_rgb[2]
    )

    # Select whichever text colour gives better contrast.
    black_contrast = (luminance + 0.05) / 0.05
    white_contrast = 1.05 / (luminance + 0.05)

    if black_contrast >= white_contrast:
        return "#000000"

    return "#ffffff"


# ==========================================
# Waypoint rendering
# ==========================================

def render_waypoints():
    """Rebuild the waypoint list from the Python data."""

    waypoint_list = document.querySelector("#waypoint-list")

    html = ""

    for index, colour in enumerate(waypoints):

        number = index + 1
        text_colour = get_contrasting_text_colour(colour)

        html += f"""
            <div class="waypoint-item" data-index="{index}" draggable="true">

                <span class="drag-handle"
                    title="Drag to reorder">
                    ⠿
                </span>

                <span class="waypoint-number"
                      style="background-color: {colour};
                             color: {text_colour};">
                    {number}
                </span>

                <label class="colour-picker-control"
                       title="Choose waypoint colour">

                    <svg viewBox="0 0 24 24"
                         class="colour-picker-icon"
                         aria-hidden="true">

                        <path d="M14.5 6.5L17.5 9.5
                                 M13 8L5 16
                                 L4 20
                                 L8 19
                                 L16 11"/>

                        <path d="M14.5 6.5L16 5
                                 C17.5 3.5 19 3.5 20 4.5
                                 C21 5.5 21 7 19.5 8.5
                                 L18 10"/>

                        <circle cx="6.5" cy="17.5" r="1"
                                fill="currentColor"
                                stroke="none"/>

                    </svg>

                    <input
                        type="color"
                        class="waypoint-colour-picker"
                        value="{colour}"
                        aria-label="Waypoint {number} colour"
                    >

                </label>

                <input
                    type="text"
                    class="waypoint-hex-input"
                    value="{colour}"
                    maxlength="7"
                    spellcheck="false"
                    aria-label="Waypoint {number} hexadecimal colour"
                >

                <button
                    type="button"
                    class="delete-waypoint"
                    data-action="delete"
                    data-index="{index}"
                    title="Delete waypoint"
                >
                    ×
                </button>

            </div>
        """

        # Add an insertion button between waypoints.
        if index < len(waypoints) - 1:
            html += f"""
                <div class="waypoint-insertion">

                    <button
                        type="button"
                        class="insert-waypoint"
                        data-action="insert"
                        data-index="{index + 1}"
                        title="Insert waypoint here"
                    >
                        +
                    </button>

                </div>
            """

    waypoint_list.innerHTML = html

    # The last remaining waypoint cannot be deleted.
    delete_buttons = waypoint_list.querySelectorAll(
        ".delete-waypoint"
    )

    if len(waypoints) == 1:
        delete_buttons[0].disabled = True

    render_updates()


# ==========================================
# Add waypoints
# ==========================================

def add_waypoint(index):
    """Insert a new waypoint at the specified position."""

    index = max(0, min(index, len(waypoints)))

    waypoints.insert(index, "#808080")

    render_waypoints()


@when("click", "#add-waypoint-top")
def add_waypoint_top(event):
    """Add a waypoint at the beginning."""

    add_waypoint(0)


@when("click", "#add-waypoint-bottom")
def add_waypoint_bottom(event):
    """Add a waypoint at the end."""

    add_waypoint(len(waypoints))


# ==========================================
# Waypoint button events
# ==========================================

@when("click", "#waypoint-list")
def waypoint_button_clicked(event):
    """Handle insertion and deletion buttons."""

    button = event.target.closest("[data-action]")

    if is_none(button):
        return

    action = button.dataset.action
    index = int(button.dataset.index)

    if action == "insert":
        add_waypoint(index)

    elif action == "delete":

        if len(waypoints) > 1:
            waypoints.pop(index)
            render_waypoints()


# ==========================================
# Waypoint input events
# ==========================================

@when("change", "#waypoint-list")
def waypoint_input_changed(event):
    """Handle colour picker and hexadecimal input changes."""

    target = event.target

    waypoint_item = target.closest(".waypoint-item")

    if is_none(waypoint_item):
        return

    index = int(waypoint_item.dataset.index)

    if target.classList.contains("waypoint-colour-picker"):

        colour = target.value.lower()

        waypoints[index] = colour

        hex_input = waypoint_item.querySelector(
            ".waypoint-hex-input"
        )

        hex_input.value = colour
        hex_input.classList.remove("invalid")

        update_waypoint_swatch(waypoint_item, colour)
        render_updates()

    elif target.classList.contains("waypoint-hex-input"):

        colour = target.value.strip().lower()

        if is_valid_hex(colour):

            waypoints[index] = colour

            picker = waypoint_item.querySelector(
                ".waypoint-colour-picker"
            )

            picker.value = colour

            target.classList.remove("invalid")

            update_waypoint_swatch(waypoint_item, colour)
            render_updates()

        else:
            target.classList.add("invalid")


def update_waypoint_swatch(waypoint_item, colour):
    """Update a waypoint's colour swatch and text contrast."""

    swatch = waypoint_item.querySelector(".waypoint-number")

    text_colour = get_contrasting_text_colour(colour)

    swatch.style.backgroundColor = colour
    swatch.style.color = text_colour


# ==========================================
# Drag and drop
# ==========================================

dragged_index = None


@when("dragstart", "#waypoint-list")
def waypoint_drag_start(event):
    """Record which waypoint is being dragged."""

    global dragged_index

    item = event.target.closest(".waypoint-item")

    if is_none(item):
        return

    dragged_index = int(item.dataset.index)

    item.classList.add("dragging")

    event.dataTransfer.effectAllowed = "move"
    event.dataTransfer.setData("text/plain", str(dragged_index))


@when("dragover", "#waypoint-list")
def waypoint_drag_over(event):
    """Allow dropping inside the waypoint list."""

    event.preventDefault()

    target = event.target.closest(".waypoint-item")

    if is_none(target):
        return

    # Remove previous indicators.
    items = document.querySelectorAll(".waypoint-item")

    for item in items:
        item.classList.remove("drag-over")
        item.classList.remove("drag-over-above")
        item.classList.remove("drag-over-below")

    # Determine whether the pointer is in the upper or lower half.
    rect = target.getBoundingClientRect()

    pointer_y = event.clientY
    midpoint = rect.top + rect.height / 2

    target.classList.add("drag-over")

    if pointer_y < midpoint:
        target.classList.add("drag-over-above")
    else:
        target.classList.add("drag-over-below")

    event.dataTransfer.dropEffect = "move"


@when("drop", "#waypoint-list")
def waypoint_drop(event):
    """Move the dragged waypoint to its new position."""

    global dragged_index

    event.preventDefault()

    if dragged_index is None:
        return

    target = event.target.closest(".waypoint-item")

    if is_none(target):
        dragged_index = None
        render_waypoints()
        return

    target_index = int(target.dataset.index)

    rect = target.getBoundingClientRect()
    midpoint = rect.top + rect.height / 2

    # Determine insertion position.
    insert_after = event.clientY >= midpoint

    if insert_after:
        target_index += 1

    colour = waypoints.pop(dragged_index)

    # Account for removal shifting subsequent indices.
    if target_index > dragged_index:
        target_index -= 1

    waypoints.insert(target_index, colour)

    dragged_index = None

    render_waypoints()


@when("dragend", "#waypoint-list")
def waypoint_drag_end(event):
    """Clean up drag styling."""

    global dragged_index

    dragged_index = None

    items = document.querySelectorAll(".waypoint-item")

    for item in items:
        item.classList.remove("dragging")
        item.classList.remove("drag-over")
        item.classList.remove("drag-over-above")
        item.classList.remove("drag-over-below")


# ==========================================
# Chromaticity diagram
# ==========================================

def generate_chromaticity_data():
    """Generate data for the CIE 1931 chromaticity diagram."""

    wavelengths, spectral_xy = al.load_spectral_locus()

    # Convert spectral locus coordinates into separate arrays.
    spectral_x = [point[0] for point in spectral_xy]
    spectral_y = [point[1] for point in spectral_xy]

    # Convert waypoint colours to chromaticity coordinates.
    waypoint_xy = []

    for colour in waypoints:
        rgb = conv.hex_to_srgb(colour)
        xyz = conv.srgb_to_xyz(rgb)
        xy = conv.xyz_to_xy(xyz)

        waypoint_xy.append(xy)

    background = generate_chromaticity_background()

    return {
        "spectral_x": spectral_x,
        "spectral_y": spectral_y,
        "wavelengths": list(wavelengths),
        "waypoint_x": [point[0] for point in waypoint_xy],
        "waypoint_y": [point[1] for point in waypoint_xy],
        "waypoint_colours": list(waypoints),
        "background": background,
    }


def generate_chromaticity_background(width=320, height=360):
    """Generate an RGBA image of the CIE 1931 chromaticity diagram."""

    wavelengths, spectral_xy = al.load_spectral_locus()

    # Close the polygon using the line of purples.
    polygon = list(spectral_xy) + [spectral_xy[0]]

    # Standard XYZ (D65) to linear sRGB matrix.
    xyz_to_linear_rgb = (
        (3.2404542, -1.5371385, -0.4985314),
        (-0.9692660, 1.8760108, 0.0415560),
        (0.0556434, -0.2040259, 1.0572252),
    )

    x_min, x_max = 0.0, 0.8
    y_min, y_max = 0.0, 0.9

    dx = (x_max - x_min) / (width - 1)
    dy = (y_max - y_min) / (height - 1)

    # Neutral background outside the chromaticity boundary.
    background = []

    for iy in range(height):

        # Rows are generated from top to bottom.
        y = y_max - iy * dy

        row = []

        # Find intersections between this scanline and polygon edges.
        intersections = []

        for i in range(len(polygon) - 1):

            x1, y1 = polygon[i]
            x2, y2 = polygon[i + 1]

            if (y1 <= y < y2) or (y2 <= y < y1):

                x_intersection = (
                    x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                )

                intersections.append(x_intersection)

        intersections.sort()

        # Generate RGB values for each pixel.
        for ix in range(width):

            x = x_min + ix * dx

            # Check whether this pixel lies inside the polygon.
            inside = any(
                intersections[j] <= x <= intersections[j + 1]
                for j in range(0, len(intersections) - 1, 2)
            )

            if not inside or y <= 0:

                # Fully transparent pixel outside the chromaticity boundary.
                row.append([0, 0, 0, 0])
                continue

            # Convert xyY to XYZ, assuming Y = 1.
            X = x / y
            Y = 1.0
            Z = (1.0 - x - y) / y

            xyz = (X, Y, Z)

            # Convert XYZ to linear sRGB.
            # Convert XYZ to linear sRGB.
            linear_rgb = tuple(
                sum(
                    xyz_to_linear_rgb[i][j] * xyz[j]
                    for j in range(3)
                )
                for i in range(3)
            )

            # Remove negative RGB components.
            linear_rgb = tuple(
                max(0.0, channel)
                for channel in linear_rgb
            )

            # Normalise the largest channel to 1.
            maximum = max(linear_rgb)

            if maximum > 0:
                linear_rgb = tuple(
                    channel / maximum
                    for channel in linear_rgb
                )

            # Convert normalised linear RGB to sRGB.
            rgb = conv.linear_to_srgb(linear_rgb)

            # Convert to 8-bit RGB.
            pixel = [
                round(channel * 255)
                for channel in rgb
            ]

            row.append(pixel + [255])

        background.append(row)

    return {
        "rgb": background,
        "width": width,
        "height": height,
        "x0": x_min,
        "dx": dx,
        "y0": y_max,
        "dy": -dy,
    }


def render_chromaticity_diagram(samples=None):
    """Initialise or update the chromaticity diagram."""

    global chromaticity_initialized

    if samples is None:
        samples = interpolate_palette(
            waypoints,
            method=interpolation_method
        )

    if not chromaticity_initialized:

        data = generate_chromaticity_data()

        dynamic_data = generate_chromaticity_waypoint_data(samples)
        data.update(dynamic_data)

        js_data = js.JSON.parse(json.dumps(data))

        js.window.renderChromaticityDiagram(js_data)

        chromaticity_initialized = True

    else:

        data = generate_chromaticity_waypoint_data(samples)

        js_data = js.JSON.parse(json.dumps(data))

        js.window.updateChromaticityWaypoints(js_data)


def generate_chromaticity_waypoint_data(samples=None):
    """Generate dynamic waypoint and interpolation coordinates."""

    waypoint_xy = []

    for colour in waypoints:
        rgb = conv.hex_to_srgb(colour)
        xyz = conv.srgb_to_xyz(rgb)
        xy = conv.xyz_to_xy(xyz)

        waypoint_xy.append(xy)

    data = {
        "waypoint_x": [point[0] for point in waypoint_xy],
        "waypoint_y": [point[1] for point in waypoint_xy],
        "waypoint_colours": list(waypoints),
    }

    # Convert interpolated samples to chromaticity coordinates.
    if samples is not None:

        interpolation_xy = []

        for position, colour in samples:
            rgb = conv.hex_to_srgb(colour)
            xyz = conv.srgb_to_xyz(rgb)
            xy = conv.xyz_to_xy(xyz)

            interpolation_xy.append(xy)

        data["interpolation_x"] = [
            point[0] if point is not None else None
            for point in interpolation_xy
        ]

        data["interpolation_y"] = [
            point[1] if point is not None else None
            for point in interpolation_xy
        ]

    return data


# ==========================================
# Palette preview
# ==========================================

def render_palette_representation(
    samples,
    waypoint_colours,
    gradient_id,
    markers_id,
    swatches_id
):
    """Render one palette representation."""

    gradient = document.querySelector(f"#{gradient_id}")
    markers = document.querySelector(f"#{markers_id}")
    swatches = document.querySelector(f"#{swatches_id}")

    # Construct CSS gradient stops.
    gradient_stops = [
        f"{colour} {position:.4f}%"
        for position, colour in samples
    ]

    gradient.style.background = (
        "linear-gradient(to right, "
        + ", ".join(gradient_stops)
        + ")"
    )

    # Construct waypoint markers and swatches.
    marker_html = ""
    swatch_html = ""

    for index, colour in enumerate(waypoint_colours):

        position = (
            index / (len(waypoint_colours) - 1) * 100
            if len(waypoint_colours) > 1
            else 0
        )

        marker_html += f"""
            <div
                class="palette-waypoint-marker"
                style="left: {position}%"
            ></div>
        """

        swatch_html += f"""
            <div
                class="palette-waypoint-swatch"
                style="
                    left: {position}%;
                    background-color: {colour};
                "
                title="Waypoint {index + 1}: {colour}"
            ></div>
        """

    markers.innerHTML = marker_html
    swatches.innerHTML = swatch_html


def render_palette_preview_base(model, samples):
    funcs = {
        "grayscale": vision.to_grayscale,
        "protanopia": vision.simulate_protanopia,
        "deuteranopia": vision.simulate_deuteranopia,
        "tritanopia": vision.simulate_tritanopia,
    }
    samples = [
        (position, funcs[model](colour))
        for position, colour in samples
    ]

    adj_waypoints = [funcs[model](colour) for colour in waypoints]

    render_palette_representation(
        samples,
        adj_waypoints,
        f"{model}-gradient",
        f"{model}-waypoint-markers",
        f"{model}-waypoint-swatches",
    )


def render_palette_preview():
    """Render all palette representations."""

    # Generate the interpolated palette only once.
    samples = interpolate_palette(
        waypoints,
        method=interpolation_method
    )

    # Normal-vision representation.
    render_palette_representation(
        samples,
        waypoints,
        "palette-gradient",
        "palette-waypoint-markers",
        "palette-waypoint-swatches"
    )

    # Grayscale representation.
    render_palette_preview_base("grayscale", samples)

    # Protanopia representation.
    render_palette_preview_base("protanopia", samples)

    # Deuteranopia representation
    render_palette_preview_base("deuteranopia", samples)

    # Tritanopia representation.
    render_palette_preview_base("tritanopia", samples)

    return


# ==========================================
# Interpolation method selection
# ==========================================

@when("change", "#interpolation-method")
def interpolation_method_changed(event):
    """Handle changes to the selected interpolation method."""

    global interpolation_method

    interpolation_method = event.target.value

    render_updates()


# ==========================================
# Renderer updates
# ==========================================

def render_updates():
    samples = render_palette_preview()
    render_chromaticity_diagram(samples)


# ==========================================
# Initialisation
# ==========================================

render_waypoints()
render_chromaticity_diagram()
