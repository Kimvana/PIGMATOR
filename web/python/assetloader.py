import csv


def load_spectral_locus():
    """Load CIE 1931 2-degree spectral locus data.

    Returns:
        wavelengths: tuple of wavelengths in nm
        xy: tuple of (x, y) chromaticity coordinates
    """

    data_path = "CIE_cc_1931_2deg.csv"

    wavelengths = []
    xy = []

    with open(data_path, newline="") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            wavelength, x, y, z = map(float, row)

            wavelengths.append(wavelength)
            xy.append((x, y))

    return tuple(wavelengths), tuple(xy)
