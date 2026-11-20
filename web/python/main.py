
from pyscript import when, document
from pyscript.ffi import is_none


# ==========================================
# Palette data
# ==========================================

waypoints = [
    "#3478b8"
]


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
    rgb = [
        int(colour[i:i + 2], 16) / 255
        for i in (1, 3, 5)
    ]

    linear_rgb = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb
    ]

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
            <div class="waypoint-item" data-index="{index}">

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

    # print("event", event)
    # print(dir(event))
    # print("event.target", event.target)
    # print(dir(event.target))
    # print("event.target.className", event.target.className)

    button = event.target.closest("[data-action]")

    # print("button", button, type(button))

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

# @when("waypoint-action", "document")
# def waypoint_action(event):
#     """Handle waypoint insertion and deletion."""

#     action = event.detail.action
#     index = int(event.detail.index)

#     if action == "insert":
#         add_waypoint(index)

#     elif action == "delete":
#         if len(waypoints) > 1:
#             waypoints.pop(index)
#             render_waypoints()


# ==========================================
# Waypoint input events
# ==========================================

@when("input", "#waypoint-list")
def waypoint_input_changed(event):
    """Handle colour picker and hexadecimal input changes."""

    target = event.target

    waypoint_item = target.closest(".waypoint-item")

    if waypoint_item is None:
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

        else:
            target.classList.add("invalid")


def update_waypoint_swatch(waypoint_item, colour):
    """Update a waypoint's colour swatch and text contrast."""

    swatch = waypoint_item.querySelector(".waypoint-number")

    text_colour = get_contrasting_text_colour(colour)

    swatch.style.backgroundColor = colour
    swatch.style.color = text_colour


# ==========================================
# Initialisation
# ==========================================

render_waypoints()
