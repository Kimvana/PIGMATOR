
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
