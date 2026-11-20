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


@when("input", "#colour-picker")
def picker_changed(event):
    colour = event.target.value.lower()

    waypoints[0] = colour

    document.querySelector("#hex-input").value = colour

    set_hex_validity(True)


@when("change", "#hex-input")
def hex_changed(event):
    colour = event.target.value.strip()

    if is_valid_hex(colour):
        waypoints[0] = colour

        document.querySelector("#colour-picker").value = colour

        set_hex_validity(True)

    else:
        set_hex_validity(False)
