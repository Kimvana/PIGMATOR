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


def update_colour(colour):
    """Update the colour preview."""
    document.querySelector("#colour-preview").style.backgroundColor = colour


def set_hex_validity(is_valid):
    """Indicate whether the hexadecimal input is valid."""
    hex_input = document.querySelector("#hex-input")

    if is_valid:
        hex_input.classList.remove("invalid")
    else:
        hex_input.classList.add("invalid")


@when("input", "#colour-picker")
def picker_changed(event):
    colour = event.target.value

    document.querySelector("#hex-input").value = colour

    set_hex_validity(True)
    update_colour(colour)


@when("change", "#hex-input")
def hex_changed(event):
    colour = event.target.value.strip()

    if len(colour) == 7 and colour.startswith("#"):
        try:
            int(colour[1:], 16)
            document.querySelector("#colour-picker").value = colour
            set_hex_validity(True)
            update_colour(colour)

        except ValueError:
            set_hex_validity(False)

    else:
        set_hex_validity(False)
