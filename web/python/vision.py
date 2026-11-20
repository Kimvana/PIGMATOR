
import conversions as conv


def to_grayscale(colour):
    """
    Convert an sRGB hexadecimal colour to luminance-based grayscale.

    The calculation uses linear-light sRGB relative luminance.
    The result is returned as an sRGB hexadecimal colour.
    """

    # Decode hexadecimal sRGB into the range [0, 1].
    linear_rgb = conv.srgb_to_linear(conv.hex_to_srgb(colour))

    # Calculate relative luminance.
    luminance = (
        0.2126 * linear_rgb[0]
        + 0.7152 * linear_rgb[1]
        + 0.0722 * linear_rgb[2]
    )

    return conv.srgb_to_hex(conv.linear_to_srgb([luminance] * 3))


def _apply_vision_matrix(colour, matrix):
    """
    Apply a colour vision transformation matrix to an sRGB colour.

    The transformation operates on linear-light RGB.
    Out-of-gamut results are clipped for sRGB display.
    """

    # Convert encoded sRGB to linear RGB.
    rgb = conv.srgb_to_linear(conv.hex_to_srgb(colour))

    # Apply the 3x3 transformation matrix.
    transformed = [
        sum(matrix[row][col] * rgb[col] for col in range(3))
        for row in range(3)
    ]

    # Clip to the linear sRGB gamut.
    transformed = [
        min(1.0, max(0.0, channel))
        for channel in transformed
    ]

    # Convert back to hexadecimal sRGB.
    return conv.srgb_to_hex(conv.linear_to_srgb(transformed))


def simulate_protanopia(colour):
    """
    Simulate complete protanopia using Machado et al. (2009).
    https://doi.org/10.1109/TVCG.2009.113

    Severity: 1.0 (complete dichromacy).
    """

    protanopia_matrix = [
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998]
    ]

    return _apply_vision_matrix(colour, protanopia_matrix)


def simulate_deuteranopia(colour):
    """
    Simulate complete deuteranopia using Machado et al. (2009).
    https://doi.org/10.1109/TVCG.2009.113

    Severity: 1.0 (complete dichromacy).
    """

    deuteranopia_matrix = [
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881]
    ]

    return _apply_vision_matrix(colour, deuteranopia_matrix)


def simulate_tritanopia(colour):
    """
    Simulate complete tritanopia using Machado et al. (2009).
    https://doi.org/10.1109/TVCG.2009.113

    Severity: 1.0 (complete dichromacy).
    """

    tritanopia_matrix = [
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900]
    ]

    return _apply_vision_matrix(colour, tritanopia_matrix)
