
"""
Colour interpolation functions for PIGMATOR.

Supported interpolation methods:
- sRGB
- linRGB
- HSV
- HSL
- OKLab

All interpolation calculations are independent of the browser interface.
"""

import conversions as conv


# ==========================================
# Interpolation
# ==========================================

def interpolate_values(start, end, t):
    """Linearly interpolate between two sets of coordinates."""

    return tuple(
        a + (b - a) * t
        for a, b in zip(start, end)
    )


def interpolate_hue(h1, h2, t):
    """
    Interpolate between two hue angles using the shortest path.

    Hue is expressed in the interval [0, 1).
    """

    # Calculate the shortest signed angular difference.
    difference = (h2 - h1 + 0.5) % 1.0 - 0.5

    # Interpolate and wrap the result into [0, 1).
    return (h1 + t * difference) % 1.0


def interpolate_palette(
    waypoints,
    method="srgb",
    samples_per_segment=24
):
    """
    Interpolate a palette between consecutive waypoints.

    Parameters
    ----------
    waypoints : list
        List of hexadecimal waypoint colours.

    method : str
        Interpolation method: 'srgb', 'linrgb', 'hsv', 'hsl' or 'oklab'.

    samples_per_segment : int
        Number of interpolation intervals per segment.

    Returns
    -------
    list
        List of (position, hexadecimal colour) pairs.

        Position is expressed as a percentage from 0 to 100.
    """

    if not waypoints:
        return []

    if method not in ("srgb", "oklab", "linrgb", "hsv", "hsl"):
        raise ValueError(f"Unsupported interpolation method: {method}")

    if samples_per_segment < 1:
        raise ValueError("samples_per_segment must be at least 1")

    if len(waypoints) == 1:
        return [(0.0, waypoints[0].lower())]

    # Convert all waypoints into the selected interpolation space.
    if method == "srgb":

        converted = [
            conv.hex_to_srgb(colour)
            for colour in waypoints
        ]

    elif method == "linrgb":
        converted = [
            conv.srgb_to_linear(conv.hex_to_srgb(colour))
            for colour in waypoints
        ]

    elif method == "hsv":
        converted = [
            conv.srgb_to_hsv(conv.hex_to_srgb(colour))
            for colour in waypoints
        ]

    elif method == "hsl":
        converted = [
            conv.srgb_to_hsl(conv.hex_to_srgb(colour))
            for colour in waypoints
        ]

    else:

        converted = [
            conv.srgb_to_oklab(conv.hex_to_srgb(colour))
            for colour in waypoints
        ]

    result = []

    number_of_segments = len(waypoints) - 1

    for segment in range(number_of_segments):

        start = converted[segment]
        end = converted[segment + 1]

        for sample in range(samples_per_segment + 1):

            # Avoid duplicating shared waypoint samples.
            if segment > 0 and sample == 0:
                continue

            t = sample / samples_per_segment

            # Interpolate in the selected colour space.
            if method in ("hsv", "hsl"):
                hue = interpolate_hue(start[0], end[0], t)
                other_channels = interpolate_values(
                    start[1:],
                    end[1:],
                    t
                )
                interpolated = (hue, *other_channels)

            else:
                interpolated = interpolate_values(start, end, t)

            # Convert back to encoded sRGB.
            if method == "srgb":

                rgb = interpolated

            elif method == "linrgb":
                rgb = conv.linear_to_srgb(interpolated)

            elif method == "hsv":
                rgb = conv.hsv_to_srgb(interpolated)

            elif method == "hsl":
                rgb = conv.hsl_to_srgb(interpolated)

            else:

                rgb = conv.oklab_to_srgb(interpolated)

            colour = conv.srgb_to_hex(rgb)

            # All segments have equal parameter spacing.
            position = (
                (segment + t)
                / number_of_segments
                * 100
            )

            result.append((position, colour))

    return result
