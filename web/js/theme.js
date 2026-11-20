
const root = document.documentElement;

const themeSelector = document.querySelector(".theme-selector");
const themeButton = document.querySelector("#theme-menu-button");
const themeMenu = document.querySelector("#theme-menu");

const themeOptions = themeMenu.querySelectorAll("[data-theme]");

const themeIcons = {
    light: document.querySelector(".icon-light"),
    dark: document.querySelector(".icon-dark"),
    system: document.querySelector(".icon-system")
};


// Apply the selected theme.
function applyTheme(preference) {

    root.dataset.theme = preference;

    // Show the icon corresponding to the selected preference.
    Object.entries(themeIcons).forEach(([theme, icon]) => {
        if (theme === preference) {
            icon.removeAttribute("hidden");
        } else {
            icon.setAttribute("hidden", "");
        }
    });

    // Update the accessible button description.
    themeButton.setAttribute(
        "aria-label",
        `Colour theme: ${preference}`
    );

    // Highlight the selected menu option.
    themeOptions.forEach((option) => {
        const isActive = option.dataset.theme === preference;

        option.classList.toggle("active", isActive);
        option.setAttribute("aria-checked", isActive);
    });
}


// Open or close the dropdown.
function setMenuOpen(isOpen) {

    themeMenu.hidden = !isOpen;

    themeButton.setAttribute(
        "aria-expanded",
        String(isOpen)
    );
}


// Toggle dropdown when clicking the main button.
themeButton.addEventListener("click", () => {
    setMenuOpen(themeMenu.hidden);
});


// Select a theme.
themeOptions.forEach((option) => {

    option.addEventListener("click", () => {

        applyTheme(option.dataset.theme);
        setMenuOpen(false);

    });

});


// Close when clicking outside the selector.
document.addEventListener("click", (event) => {

    if (!themeSelector.contains(event.target)) {
        setMenuOpen(false);
    }

});


// Close with Escape.
document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {
        setMenuOpen(false);
        themeButton.focus();
    }

});


// Start by following the operating system.
applyTheme("system");
