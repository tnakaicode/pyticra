import numpy as np
import scipy.constants as cnt
from scipy import constants

"""
This class converts between GRASP units and SI units.
"""

SI = {
    'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.,
    'GHz': 10**9, 'MHz': 10**6, 'kHz': 10**3, 'Hz': 1.0,
    'MeW': 10**6, 'kW': 10**3, 'W': 1.0, 'mW': 10**(-3), "uW": 10**(-6)
}


def convert_SI(val_unit, unit_in="cm", unit_out="mm"):
    val = float(val_unit.split(unit_in)[0])
    return val * SI[unit_in] / SI[unit_out]


def convert(unit_in="cm", unit_out="mm"):
    return SI[unit_in] / SI[unit_out]


def convert_wave(val, unit_in="GHz", unit_out="mm"):
    if unit_in in ["GHz", "MHz", "kHz", "Hz"]:
        freq = convert_SI(val, unit_in, "Hz")
        wave = cnt.c / freq * convert("m", unit_out)
        freq *= convert("Hz", unit_in)
    elif unit_in in ["mm", "cm", "m", "km"]:
        wave = convert_SI(val, unit_in, "m")
        freq = cnt.c / wave * convert("Hz", unit_out)
        wave *= convert("m", unit_in)
    return freq, wave


def power_unit(val, unit_in="mW", unit_out="dBm"):
    if unit_in in ["uW", "mW", "W", "kW", "MeW"]:
        return 10 * np.log10(val * convert(unit_in, "mW"))
    elif unit_in == "dBm":
        return 10**(val / 10) * convert("mW", unit_out)
    else:
        return val


class Units(object):

    # Permittivity of free space [?]
    epsilon_0 = constants.epsilon_0
    # Permeability of free space [?]
    mu_0 = constants.mu_0
    # Impedance of free space [ohm].
    Z_0 = np.sqrt(mu_0 / epsilon_0)
    # Speed of light [m s^-1].
    c = constants.c

    @classmethod
    def E_to_SI(cls, E_GRASP, k):
        return k * np.sqrt(2 * cls.Z_0) * E_GRASP

    @classmethod
    def E_to_GRASP(cls, E_SI, k):
        return 1 / (k * np.sqrt(2 * cls.Z_0)) * E_SI

    @classmethod
    def H_to_SI(cls, H_GRASP, k):
        return k * np.sqrt(2 / cls.Z_0) * H_GRASP

    @classmethod
    def H_to_GRASP(cls, H_SI, k):
        return 1 / k * np.sqrt(cls.Z_0 / 2) * H_SI


if __name__ == "__main__":
    print(power_unit(1.0, "mW", "dBm"))
    print(power_unit(1.0, "W", "dBm"))
    print(power_unit(1.0, "uW", "dBm"))
    print(power_unit(13, "mW", "dBm"))
    print(power_unit(0, "dBm", "mW"))
    print(power_unit(30, "dBm", "W"))
    print(power_unit(-30, "dBm", "mW"))
    print(power_unit(3, "dBm", "mW"))
