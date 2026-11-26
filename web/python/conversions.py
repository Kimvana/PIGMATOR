

import colorsys


# ==========================================
# sRGB conversion
# ==========================================

def hex_to_srgb(colour):
    """Convert a hexadecimal colour to encoded sRGB values."""

    return tuple(
        int(colour[i:i + 2], 16) / 255
        for i in (1, 3, 5)
    )


def srgb_to_hex(rgb):
    """Convert encoded sRGB values to a hexadecimal colour."""

    # Clip values to the sRGB display gamut.
    rgb = tuple(
        max(0.0, min(1.0, channel))
        for channel in rgb
    )

    return "#" + "".join(
        f"{round(channel * 255):02x}"
        for channel in rgb
    )


def srgb_to_linear(rgb):
    """Convert gamma-encoded sRGB to linear RGB."""

    return tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb
    )


def linear_to_srgb(rgb):
    """Convert linear RGB to gamma-encoded sRGB."""

    return tuple(
        12.92 * channel
        if channel <= 0.0031308
        else 1.055 * (channel ** (1 / 2.4)) - 0.055
        for channel in rgb
    )


# ==========================================
# HSV/L conversion
# ==========================================

def srgb_to_hsv(rgb):
    r, g, b = rgb
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_srgb(hsv):
    h, s, v = hsv
    return colorsys.hsv_to_rgb(h, s, v)


def srgb_to_hsl(rgb):
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)


def hsl_to_srgb(hsl):
    h, s, l = hsl
    return colorsys.hls_to_rgb(h, l, s)


# ==========================================
# OKLab conversion
# ==========================================

def linear_rgb_to_oklab(rgb):
    """Convert linear RGB to OKLab."""

    r, g, b = rgb

    l = (
        0.4122214708 * r
        + 0.5363325363 * g
        + 0.0514459929 * b
    )

    m = (
        0.2119034982 * r
        + 0.6806995451 * g
        + 0.1073969566 * b
    )

    s = (
        0.0883024619 * r
        + 0.2817188376 * g
        + 0.6299787005 * b
    )

    l_ = l ** (1 / 3)
    m_ = m ** (1 / 3)
    s_ = s ** (1 / 3)

    L = (
        0.2104542553 * l_
        + 0.7936177850 * m_
        - 0.0040720468 * s_
    )

    a = (
        1.9779984951 * l_
        - 2.4285922050 * m_
        + 0.4505937099 * s_
    )

    b = (
        0.0259040371 * l_
        + 0.7827717662 * m_
        - 0.8086757660 * s_
    )

    return L, a, b


def oklab_to_linear_rgb(lab):
    """Convert OKLab to linear RGB."""

    L, a, b = lab

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    r = (
        4.0767416621 * l
        - 3.3077115913 * m
        + 0.2309699292 * s
    )

    g = (
        -1.2684380046 * l
        + 2.6097574011 * m
        - 0.3413193965 * s
    )

    b = (
        -0.0041960863 * l
        - 0.7034186147 * m
        + 1.7076147010 * s
    )

    return r, g, b


def srgb_to_oklab(rgb):
    """Convert encoded sRGB to OKLab."""

    linear_rgb = srgb_to_linear(rgb)

    return linear_rgb_to_oklab(linear_rgb)


def oklab_to_srgb(lab):
    """Convert OKLab to encoded sRGB."""

    linear_rgb = oklab_to_linear_rgb(lab)

    return linear_to_srgb(linear_rgb)


# ==========================================
# XYZ conversion
# ==========================================

def srgb_to_xyz(rgb):
    """Convert gamma-encoded sRGB to CIE XYZ (D65).

    XYZ values are normalised so that the reference white has Y = 1.
    """

    linear_rgb = srgb_to_linear(rgb)

    matrix = (
        (0.4124564, 0.3575761, 0.1804375),
        (0.2126729, 0.7151522, 0.0721750),
        (0.0193339, 0.1191920, 0.9503041),
    )

    return tuple(
        sum(row[i] * linear_rgb[i] for i in range(3))
        for row in matrix
    )


def xyz_to_xy(xyz):
    """Convert CIE XYZ to CIE 1931 xy chromaticity coordinates."""

    X, Y, Z = xyz
    total = X + Y + Z

    if total == 0:
        return None

    x = X / total
    y = Y / total

    return x, y


