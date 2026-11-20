# from pyscript import when, document


# def process_text(text):
#     """A tiny example of Python application logic."""
#     return text.upper()


# @when("click", "#run-button")
# def run_application():
#     user_text = document.querySelector("#user-input").value

#     result = process_text(user_text)

#     output = document.querySelector("#output")
#     output.innerText = result


from pyscript import when, document


waypoints = [
    "#3478b8"
]


def set_hex_validity(is_valid):
    """Indicate whether the hexadecimal input is valid."""
    hex_input = document.querySelector("#hex-input")

    if is_valid:
        hex_input.classList.remove("invalid")
    else:
        hex_input.classList.add("invalid")


def is_valid_hex(colour):
    """Check whether a colour is a valid six-digit hex value."""

    if len(colour) != 7 or not colour.startswith("#"):
        return False

    try:
        int(colour[1:], 16)
        return True
    except ValueError:
        return False


def update_waypoint_number(colour):
    """Update waypoint swatch colour and number contrast."""

    swatch = document.querySelector(".waypoint-number")

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

    text_colour = (
        "#000000"
        if black_contrast >= white_contrast
        else "#ffffff"
    )

    swatch.style.backgroundColor = colour
    swatch.style.color = text_colour


@when("input", "#colour-picker")
def picker_changed(event):
    colour = event.target.value.lower()

    waypoints[0] = colour

    document.querySelector("#hex-input").value = colour

    set_hex_validity(True)
    update_waypoint_number(colour)


@when("change", "#hex-input")
def hex_changed(event):
    colour = event.target.value.strip()

    if is_valid_hex(colour):
        waypoints[0] = colour

        document.querySelector("#colour-picker").value = colour

        set_hex_validity(True)
        update_waypoint_number(colour)

    else:
        set_hex_validity(False)


update_waypoint_number(waypoints[0])
