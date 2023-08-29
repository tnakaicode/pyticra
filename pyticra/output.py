"""
This module contains classes that parse the output of GRASP simulations.

To do:
Implement Cut to read .cut files.
Hack .cur files.
"""
from __future__ import division

import numpy as np

# These two functions handle numbers that have three-digit exponents,
# which GRASP writes as, e.g., 0.123456789-100 for 1.23456789E-99
# To do: match GRASP format.
# Each number uses
# 1 blank space
# 1 minus sign or blank
# 12 characters for the mantissa:
# 0.xxxxxxxxxx
# 4 characters for the exponent:
# E+xx, E-xx, +xxx, or -xxx


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


def float_to_string(number):
    if number == 0 or abs(np.log10(abs(number))) < 100:
        return ' {: 0.10E}'.format(number)
    else:
        return ' {: 0.10E}'.format(number).replace('E', '')


def load_cut(filename):
    """
    Read and parse data from the GRASP .cut file. The variables in
    capital letters match those in the GRASP-10 manual.
    """
    with open(filename, 'r') as f:
        meta = {}
        meta['header'] = f.readline().rstrip('\n').strip()
        V_INI, V_INC, V_NUM, C, ICOMP, ICUT, NCOMP = f.readline().split()
        meta['V_INI'] = float(V_INI)
        meta['V_INC'] = float(V_INC)
        meta['V_NUM'] = int(V_NUM)
        meta['C'] = float(C)
        meta['ICOMP'] = int(ICOMP)
        meta['ICUT'] = int(ICUT)
        meta['NCOMP'] = int(NCOMP)

        conv = dict([(column, string_to_float)
                     for column in range(2 * meta['NCOMP'])])
        data = np.loadtxt(f, dtype=float, converters=conv)
    cut = np.array([data[:, 2 * column] +
                    1j * data[:, 2 * column + 1]
                    for column in range(meta['NCOMP'])])
    return meta, cut


def save_cut(filename, meta, cut):
    pass


def get_grd(filename, rows):
    fp = open(filename, "r").readlines()
    x = []
    for i in rows:
        vals = fp[i].split()
        item = [string_to_float(val) for val in vals]
        x.append(item)
    return np.array(x)


def get_cur(meta, data):
    func = np.empty((meta['NCOMP'], meta['NY'], meta['NX']), dtype=complex)
    for comp in range(meta['NCOMP']):
        col = data[:, 2 * comp] + 1j * data[:, 2 * comp + 1]
        func[comp] = col.reshape(meta['NY'], meta['NX'], order='C')
    return func


def get_pw(meta, data):
    func = np.empty((meta['NCOMP'], meta['NY'], meta['NX']), dtype=complex)
    func[0] = data[:, 0].reshape(meta['NY'], meta['NX'], order='C')
    func[1] = (data[:, 2] + 1j * data[:, 3]
               ).reshape(meta['NY'], meta['NX'], order='C')
    func[2] = (data[:, 4] + 1j * data[:, 5]
               ).reshape(meta['NY'], meta['NX'], order='C')
    return func


def load_grd(filename, number=0, name="name", meta={}):
    """
    Read and parse data from the GRASP .grd file. The variables in
    capital letters match those in the GRASP-10 manual.
    """
    f = open(filename, "r")
    meta['header'] = []
    meta['header'].append(f.readline().rstrip('\n'))
    while meta['header'][-1] != '++++':
        meta['header'].append(f.readline().rstrip('\n'))
    meta['KTYPE'] = int(f.readline().split()[0])
    if meta['KTYPE'] != 1:
        raise ValueError("Not implemented.")
    meta['NSET'], meta['ICOMP'], meta['NCOMP'], meta['IGRID'] = [
        int(s) for s in f.readline().split()]
    for i in range(meta['NSET']):
        meta['IX'], meta['IY'] = [int(s) for s in f.readline().split()]
    meta['XS'], meta['YS'], meta['XE'], meta['YE'] = [
        float(s) for s in f.readline().split()]
    meta['NX'], meta['NY'], meta['KLIMIT'] = [
        int(s) for s in f.readline().split()]
    if meta['KLIMIT'] != 0:
        raise ValueError("Not implemented.")
    meta['PX'] = np.linspace(meta['XS'], meta['XE'], meta['NX'])
    meta['PY'] = np.linspace(meta['YS'], meta['YE'], meta['NY'])
    meta['MESH'] = np.meshgrid(meta['PX'], meta['PY'])
    meta['DX'] = (meta['XE'] - meta['XS']) / (meta['NX'] - 1)
    meta['DY'] = (meta['YE'] - meta['YS']) / (meta['NY'] - 1)
    meta['XCEN'] = meta['DX'] * meta['IX']
    meta['YCEN'] = meta['DY'] * meta['IY']
    idx = filename.split("/")[-1].split(".")[-2]

    num = len(meta['header'])
    num += meta['NSET'] + 4
    dat_num = meta['NX'] * meta['NY']
    n0, n1 = num + number * (dat_num + 2), num + \
        (number + 1) * (dat_num) + number * 2
    rows = range(n0, n1)
    data = get_grd(filename, rows)
    meta[name] = call_func("get_" + idx, meta, data)
    num = n1 + 2
    print(filename, n0, n1)
    return meta


def save_grd(filename, meta, names=["name"], comment=[]):
    """
    Write the data in this Grid to a new .grd file. Will not overwrite.
    """
    points = meta['NX'] * meta['NY']
    components = meta['NCOMP']
    f = open(filename, "w")
    for line in meta['header'] + comment:
        f.write('{}\n'.format(line))
    f.write('{:2d}\n'.format(meta['KTYPE']))
    f.write('{:12d}{:12d}{:12d}{:12d}\n'.format(
        len(names), meta['ICOMP'], meta['NCOMP'], meta['IGRID']))
    for i in range(len(names)):
        f.write('{:12d}{:12d}\n'.format(meta['IX'], meta['IY']))
    for i, name in enumerate(names):
        f.write(' {: 0.10E} {: 0.10E} {: 0.10E} {: 0.10E}\n'.format(
            meta['XS'], meta['YS'], meta['XE'], meta['YE']))
        f.write('{:12d}{:12d}{:12d}\n'.format(
            meta['NX'], meta['NY'], meta['KLIMIT']))
        data = np.empty((points, 2 * components))
        for component in range(components):
            i0, i1 = 2 * component, 2 * component + 1
            data[:, i0] = meta[name][component].reshape(points, order='F').real
            data[:, i1] = meta[name][component].reshape(points, order='F').imag
        for p in range(points):
            f.write(''.join([float_to_string(number)
                             for number in data[p, :]]) + '\n')


def save_grasp_grd(meta, filename, name="E", dir_name="./", comment=[]):
    n_xy = meta['NX'] * meta['NY']
    nx, ny = meta["NX"], meta["NY"]
    xs, ys = meta["XS"], meta["YS"]
    xe, ye = meta["XE"], meta["YE"]
    comp = meta[name].shape[0]
    fp = open(dir_name + filename, "w")
    fp.write('{}\n'.format(meta["NAME"]))
    for line in comment:
        fp.write('{}\n'.format(line))
    fp.write('++++\n')
    fp.write(f'{1:2d}\n')
    fp.write(f'{1:12d}{3:12d}{3:12d}{3:12d}\n')
    fp.write(f'{0:12d}{0:12d}\n')
    fp.write(f' {xs: 0.10E} {ys: 0.10E} {xe: 0.10E} {ye: 0.10E}\n')
    fp.write(f'{nx:12d}{ny:12d}{0:12d}\n')
    data = np.empty((n_xy, 2 * comp))
    for idx in range(comp):
        i0, i1 = 2 * idx, 2 * idx + 1
        data[:, i0] = meta[name][idx].reshape(n_xy, order='C').real
        data[:, i1] = meta[name][idx].reshape(n_xy, order='C').imag
    for p in range(n_xy):
        fp.write(''.join([float_to_string(val) for val in data[p, :]]) + '\n')


def save_grasp_grd_multi(meta, filename, freqs=["100.0GHz"], name="e", dir_name="./", comment=[]):
    """Save *grd file

    Args:
        meta (dict): meta   - NX,NY
                            - XS,XE, YS,YE
                            - "100.0GHz" - e = e[0], e[1], e[2]
                                         - h = h[0], h[1], h[2]
                                         - SpillOver = 0.9
                                         ...
                            - "101.0GHz" - e = e[0], e[1], e[2]
        filename (str): filename (not contain directroy name)
        freqs (list, optional): Saved freqs name. Defaults to ["100.0GHz"].
        name (str, optional): Saved component's name. Defaults to "e".
        dir_name (str, optional): Defaults to "./".
        comment (list, optional): Defaults to [].
    """
    nx, ny = meta["NX"], meta["NY"]
    xs, ys = meta["XS"], meta["YS"]
    xe, ye = meta["XE"], meta["YE"]
    n_xy = nx * ny

    fp = open(dir_name + filename, "w")
    fp.write('{}\n'.format(filename))
    for line in comment + freqs:
        fp.write('{}\n'.format(line))
    fp.write('++++\n')
    fp.write('{:2d}\n'.format(1))
    fp.write('{:12d}{:12d}{:12d}{:12d}\n'.format(len(freqs), 3, 3, 3))
    for i, freq in enumerate(freqs):
        fp.write(f'{0:12d}{0:12d}\n')
    for i, freq in enumerate(freqs):
        comp = meta[freq][name].shape[0]
        fp.write(f' {xs: 0.10E} {ys: 0.10E} {xe: 0.10E} {ye: 0.10E}\n')
        fp.write(f'{nx:12d}{ny:12d}{0:12d}\n')
        data = np.empty((n_xy, 2 * comp))
        for idx in range(comp):
            i0, i1 = 2 * idx, 2 * idx + 1
            data[:, i0] = meta[freq][name][idx].reshape(n_xy, order='C').real
            data[:, i1] = meta[freq][name][idx].reshape(n_xy, order='C').imag
        for p in range(n_xy):
            fp.write(''.join([float_to_string(val)
                     for val in data[p, :]]) + '\n')
