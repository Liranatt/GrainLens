UHCS_PX_PER_UM_DEFAULT = 6.5  # placeholder; update from Linoy's calibration


def px_to_um2(area_px: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return area_px / (px_per_um ** 2)


def px_to_um(length_px: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return length_px / px_per_um


def um_to_px(length_um: float, px_per_um: float = UHCS_PX_PER_UM_DEFAULT) -> float:
    return length_um * px_per_um
