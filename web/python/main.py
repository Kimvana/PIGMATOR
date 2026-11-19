from pyscript import when, document


def process_text(text):
    """A tiny example of Python application logic."""
    return text.upper()


@when("click", "#run-button")
def run_application():
    user_text = document.querySelector("#user-input").value

    result = process_text(user_text)

    output = document.querySelector("#output")
    output.innerText = result
