import numpy as np
import scipy.constants as cnt
from abc import abstractmethod
from collections.abc import MutableMapping

from pyticra.units import convert


class GridBase(MutableMapping, object):
    """
    Notes
    -----
    When properly defined in inherited functions, this class should behave like
    a dictionary.

    As this class inherits from MutableMapping, any class inherting from
    AirconicsBase must also define the abstract methods of Mutable mapping,
    i.e. __setitem__, __getitem__, __len__, __iter__, __delitem__
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self, *args, **kwargs):
        pass


class GraspGrid (GridBase):

    def __init__(self, filename, meta={}, freq=100 * 10**9, unit="mm", *args, **kwargs):
        # Set the components dictionary (default empty)
        self._meta = meta
        self.filename = filename
        self.fp = open(filename, "r")
        self.id = filename.split("/")[-1].split(".")[-2]
        self.split_header()
        self.freq = freq
        self.wave = cnt.c / self.freq
        self.knum = 2 * np.pi / self.wave
        self.z_0 = np.sqrt(cnt.mu_0 / cnt.epsilon_0)
        self.unit = unit
        self.initialize()

        for name, data in meta.items():
            self.__setitem__(name, data)

        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __getitem__(self, name):
        return self._meta[name]

    def __setitem__(self, name, data):
        self._meta[name] = data

    def __delitem__(self, name):
        del self._meta[name]

    def __iter__(self):
        return iter(self._meta)

    def __len__(self):
        return len(self._meta)

    def __str__(self):
        output = str(self.keys())
        return output

    def split_header(self, contxt="++++"):
        self._meta['header'] = []
        self._meta['header'].append(self.fp.readline().rstrip('\n'))
        while self._meta['header'][-1] != contxt:
            self._meta['header'].append(self.fp.readline().rstrip('\n'))

    def initialize(self):
        """
        Grid Type
            Spherical Far  (F1, F2)
            Spherical Near (F1, F2, F3)
            Planer    (F1, F2, F3)
            Surface   (F1, F2, F3)            

        line 3; NSET, ICOMP, NCOMP, IGRID
        ICOMP =  1 "linear"          (Linear  ; E_rho,E_phi)
        ICOMP =  2 "circular"        (Circular; rhc,lhc)
        ICOMP =  3 "theta_phi"       (Linear  ; x,y)
        ICOMP =  4 "major_minor"     (Major Minor; pol-elipse)
        ICOMP =  5 "linear_xpd"      (XPD; E_rho/E_phi, E_phi/E_rho)
        ICOMP =  6 "circular_xpd"    (XPD; rhc/lhc, lhc/rhc)
        ICOMP =  7 "theta_phi_xpd"   (XPD; E_x/E_x, E_y/E_x)
        ICOMP =  8 "major_minor_xpd" (XPD; major/minor, minor/major)
        ICOMP =  9 "power"           (Power; |E|, sqrt(rhc/lhc))
        ICOMP = 11 "poyting"         (Poynting)
        """
        self._meta['KTYPE'] = int(self.fp.readline().split()[0])
        if self._meta['KTYPE'] != 1:
            raise ValueError("Not implemented.")
        nset, icomp, ncomp, igrid = [int(s)
                                     for s in self.fp.readline().split()]
        self._meta['NSET'] = nset
        self._meta['ICOMP'] = icomp
        self._meta['NCOMP'] = ncomp
        self._meta['IGRID'] = igrid
        for i in range(self._meta['NSET']):
            self._meta['IX'], self._meta['IY'] = [
                int(s) for s in self.fp.readline().split()]
        self._meta['XS'], self._meta['YS'], self._meta['XE'], self._meta['YE'] = [float(
            s) * convert(unit_in=self.unit, unit_out="mm") for s in self.fp.readline().split()]
        self._meta['NX'], self._meta['NY'], self._meta['KLIMIT'] = [
            int(s) for s in self.fp.readline().split()]
        if self._meta['KLIMIT'] != 0:
            raise ValueError("Not implemented.")
        self._meta['PX'] = np.linspace(
            self._meta['XS'], self._meta['XE'], self._meta['NX'])
        self._meta['PY'] = np.linspace(
            self._meta['YS'], self._meta['YE'], self._meta['NY'])
        self._meta['MESH'] = np.meshgrid(self._meta['PX'], self._meta['PY'])
        self._meta['DX'] = (self._meta['XE'] -
                            self._meta['XS']) / (self._meta['NX'] - 1)
        self._meta['DY'] = (self._meta['YE'] -
                            self._meta['YS']) / (self._meta['NY'] - 1)
        self._meta['XCEN'] = self._meta['DX'] * self._meta['IX']
        self._meta['YCEN'] = self._meta['DY'] * self._meta['IY']

    def get_data(self, name, indx):
        num = len(self._meta['header'])
        num += self._meta['NSET'] + 4
        row = self._meta['NX'] * self._meta['NY']
        n0 = num + indx * (row + 2)
        n1 = n0 + row
        rows = range(n0, n1)
        data = get_grd(self.filename, rows)
        if self.id == "cur":
            coef = 1 / self.knum * (np.sqrt(self.z_0 / 2))
            # coef = 1.0
            self._meta[name] = get_cur(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "e":
            coef = 1 / (self.knum * np.sqrt(2 * self.z_0))
            # coef = 1.0
            self._meta[name] = get_e(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "h":
            coef = 1 / (self.knum) * np.sqrt(self.z_0 / 2)
            # coef = 1.0
            self._meta[name] = get_h(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "pw":
            coef = 1.0
            self._meta[name] = get_pw(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        else:
            coef = 1.0
            self._meta[name] = get_e(self._meta, data) / \
                (convert("m", self.unit)**2)
        print(self.filename, n0, n1)


class GraspGridMulti (GridBase):

    def __init__(self, filename, meta={}, freqs=[100.0], unit="mm", *args, **kwargs):
        # Set the components dictionary (default empty)
        self._meta = meta
        self.filename = filename
        self.fp = open(filename, "r")
        self.id = filename.split("/")[-1].split(".")[-2]
        self.unit = unit
        self.freqs = freqs
        self.freqs_txt = [f"{f:.1f}GHz" for f in freqs]
        for freq in self.freqs_txt:
            if freq not in self._meta.keys():
                self._meta[freq] = {}
        self.split_header()
        self.initialize()

        for name, data in meta.items():
            self.__setitem__(name, data)

        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __getitem__(self, name):
        return self._meta[name]

    def __setitem__(self, name, data):
        self._meta[name] = data

    def __delitem__(self, name):
        del self._meta[name]

    def __iter__(self):
        return iter(self._meta)

    def __len__(self):
        return len(self._meta)

    def __str__(self):
        output = str(self.keys())
        return output

    def split_header(self, contxt="++++"):
        self._meta['header'] = []
        self._meta['header'].append(self.fp.readline().rstrip('\n'))
        while self._meta['header'][-1] != contxt:
            self._meta['header'].append(self.fp.readline().rstrip('\n'))

    def initialize(self):
        """
        NSET   -  Number of field sets or beams.
        ICOMP  -  Control parameter of field components.
        NCOMP  -  Number of components.
        IGRID  -  Control parameter of field grid type

        Grid Type
            Spherical Far  (F1, F2)
            Spherical Near (F1, F2, F3)
            Planer    (F1, F2, F3)
            Surface   (F1, F2, F3)            

        line 3; NSET, ICOMP, NCOMP, IGRID
        ICOMP =  1 "linear"          (Linear  ; E_rho,E_phi)
        ICOMP =  2 "circular"        (Circular; rhc,lhc)
        ICOMP =  3 "theta_phi"       (Linear  ; x,y)
        ICOMP =  4 "major_minor"     (Major Minor; pol-elipse)
        ICOMP =  5 "linear_xpd"      (XPD; E_rho/E_phi, E_phi/E_rho)
        ICOMP =  6 "circular_xpd"    (XPD; rhc/lhc, lhc/rhc)
        ICOMP =  7 "theta_phi_xpd"   (XPD; E_x/E_x, E_y/E_x)
        ICOMP =  8 "major_minor_xpd" (XPD; major/minor, minor/major)
        ICOMP =  9 "power"           (Power; |E|, sqrt(rhc/lhc))
        ICOMP = 11 "poyting"         (Poynting)
        """
        self._meta['KTYPE'] = int(self.fp.readline().split()[0])
        if self._meta['KTYPE'] != 1:
            raise ValueError("Not implemented.")
        nset, icomp, ncomp, igrid = [int(s)
                                     for s in self.fp.readline().split()]
        self._meta['NSET'] = nset
        self._meta['ICOMP'] = icomp
        self._meta['NCOMP'] = ncomp
        self._meta['IGRID'] = igrid
        for i in range(self._meta['NSET']):
            ixy = self.fp.readline().split()
            self._meta['IX'], self._meta['IY'] = [int(s) for s in ixy]
        xy = self.fp.readline().split()
        self._meta['XS'] = float(xy[0]) * convert(self.unit, "mm")
        self._meta['YS'] = float(xy[1]) * convert(self.unit, "mm")
        self._meta['XE'] = float(xy[2]) * convert(self.unit, "mm")
        self._meta['YE'] = float(xy[3]) * convert(self.unit, "mm")
        nxy = self.fp.readline().split()
        self._meta['NX'] = int(nxy[0])
        self._meta['NY'] = int(nxy[1])
        self._meta['KLIMIT'] = int(nxy[2])
        if self._meta['KLIMIT'] != 0:
            raise ValueError("Not implemented.")
        self._meta['PX'] = np.linspace(self._meta['XS'],
                                       self._meta['XE'],
                                       self._meta['NX'])
        self._meta['PY'] = np.linspace(self._meta['YS'],
                                       self._meta['YE'],
                                       self._meta['NY'])
        self._meta['MESH'] = np.meshgrid(self._meta['PX'], self._meta['PY'])
        self._meta['DX'] = (self._meta['XE'] -
                            self._meta['XS']) / (self._meta['NX'] - 1)
        self._meta['DY'] = (self._meta['YE'] -
                            self._meta['YS']) / (self._meta['NY'] - 1)
        self._meta['XCEN'] = self._meta['DX'] * self._meta['IX']
        self._meta['YCEN'] = self._meta['DY'] * self._meta['IY']

    def get_data(self, name="e", indx=0):
        num = len(self._meta['header'])
        num += self._meta['NSET'] + 4
        row = self._meta['NX'] * self._meta['NY']
        n0 = num + indx * (row + 2)
        n1 = n0 + row
        rows = range(n0, n1)
        data = get_grd(self.filename, rows)
        freq = self.freqs[indx] * convert("GHz", "Hz")
        wave = wave = cnt.c / freq
        knum = 2 * np.pi / wave
        z_0 = np.sqrt(cnt.mu_0 / cnt.epsilon_0)
        freq_txt = self.freqs_txt[indx]
        if self.id == "cur":
            coef = 1 / knum * (np.sqrt(z_0 / 2))
            self._meta[freq_txt][name] = get_cur(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "e":
            coef = 1 / (knum * np.sqrt(2 * z_0))
            self._meta[freq_txt][name] = get_e(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "h":
            coef = 1 / (knum) * np.sqrt(z_0 / 2)
            self._meta[freq_txt][name] = get_h(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        elif self.id == "pw":
            coef = 1.0
            self._meta[freq_txt][name] = get_pw(
                self._meta, data, coef=1 / coef) / (convert("m", self.unit)**2)
        else:
            coef = 1.0
            self._meta[freq_txt][name] = get_e(
                self._meta, data) / (convert("m", self.unit)**2)
        print(self.filename, n0, n1)


class TicraSpilOver(GridBase):

    def __init__(self, filename, meta={}, freqs=[100.0], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the components dictionary (default empty)
        self._meta = meta
        self.filename = filename
        self.fp = open(filename, "r")
        self.freqs = freqs
        self.freqs_txt = [f"{f:.1f}GHz" for f in freqs]
        for freq in self.freqs_txt:
            if freq not in self._meta.keys():
                self._meta[freq] = {}
        self.split_header()
        self.initialize()

        for name, data in meta.items():
            self.__setitem__(name, data)

        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __getitem__(self, name):
        return self._meta[name]

    def __setitem__(self, name, data):
        self._meta[name] = data

    def __delitem__(self, name):
        del self._meta[name]

    def __iter__(self):
        return iter(self._meta)

    def __len__(self):
        return len(self._meta)

    def __str__(self):
        output = str(self.keys())
        return output

    def split_header(self, contxt="++++"):
        self._meta['header'] = []
        self._meta['header'].append(self.fp.readline().rstrip('\n'))
        while self._meta['header'][-1] != contxt:
            self._meta['header'].append(self.fp.readline().rstrip('\n'))

    def initialize(self):
        key_list = self.fp.readline().split(",")
        file_end = True
        beam_indx = 0
        while file_end:
            file_line = self.fp.readline()
            if not file_line:
                file_end = False
            else:
                line_text = file_line.split(",")
                beam_name = line_text[1]
                beam_freq = float(line_text[2])
                beam_powr = float(line_text[3])
                beam_spil = float(line_text[4])
                meta = {}
                meta["BeamName"] = beam_name
                meta["BeamFreq"] = beam_freq
                meta["RelativePowerHitting"] = beam_powr
                meta["Spill-Over"] = beam_spil
                self._meta[self.freqs_txt[beam_indx]] = meta
                beam_indx += 1


def call_func(name, *arg, **args):
    return globals()[name](*arg, **args)


def string_to_float(string):
    try:
        return float(string)
    except ValueError:
        if '-' in string[1:]:
            return float('E-'.join(string.rsplit('-', 1)))
        else:
            return float('E+'.join(string.rsplit('+', 1)))


def get_grd(filename, rows):
    fp = open(filename, "r").readlines()
    x = []
    for i in rows:
        vals = fp[i].split()
        item = [string_to_float(val) for val in vals]
        x.append(item)
    return np.array(x)


def get_cur(meta, data, coef=1.0):
    func = np.empty((meta['NCOMP'], meta['NY'], meta['NX']), dtype=complex)
    for comp in range(meta['NCOMP']):
        col = data[:, 2 * comp] + 1j * data[:, 2 * comp + 1]
        func[comp] = col.reshape(meta['NY'], meta['NX'], order='C') * coef
    return func


def get_pw(meta, data, coef=1.0):
    func = np.empty((meta['NCOMP'], meta['NY'], meta['NX']))
    func[0] = data[:, 0].reshape(meta['NY'], meta['NX'], order='C') * coef
    func[1] = data[:, 2].reshape(meta['NY'], meta['NX'], order='C') * coef
    if meta['NCOMP'] == 3:
        func[2] = (data[:, 4] + 1j * data[:, 5]).reshape(meta['NY'],
                                                         meta['NX'], order='C') * coef
    return func


def get_eh(meta, data, coef=1.0):
    func = np.empty((meta['NCOMP'], meta['NY'], meta['NX']), dtype=complex)
    for i in range(meta['NCOMP']):
        i0, i1 = i * 2, i * 2 + 1
        func[i] = (data[:, i0] + 1j * data[:, i1]
                   ).reshape(meta['NY'], meta['NX'], order='C') * coef
    return func


def get_e(meta, data, coef=1.0):
    return get_eh(meta, data, coef=coef)


def get_h(meta, data, coef=1.0):
    return get_eh(meta, data, coef=coef)
