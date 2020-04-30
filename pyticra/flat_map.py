from __future__ import division

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapz

from pygrasp.output import load_grd, save_grd


class FlatMap(object):
    """
    This is an abstract class that contains methods useful for
    maps.

    """

    # Subclasses should define these.
    shape = ()
    data_type = None
    keys = {}

    def __init__(self):
        self.x = np.array([0.])
        self.y = np.array([0.])
        self.map = np.zeros((self.x.size, self.y.size) + self.shape,
                            dtype=self.data_type)

    # Improve exception raising.
    def __getitem__(self, key):
        try:
            use = int(self.keys.get(key, key)),
        except (ValueError, TypeError):
            use = tuple(int(self.keys.get(k, k)) for k in key)
        if len(use) != len(self.shape):
            raise ValueError(
                "Key {!r} does not match map shape {!r}".format(key, self.shape))
        return self.map[(slice(None), slice(None)) + use]

    def dx(self):
        """
        Return the pixel spacing in x.
        """
        return (self.x[-1] - self.x[0]) / (self.x.size - 1)

    def dy(self):
        """
        Return the pixel spacing in y.
        """
        return (self.y[-1] - self.y[0]) / (self.y.size - 1)

    def recenter(self, x, y):
        """
        Shift the map (0, 0) point to the given coordinates,
        preserving all other aspects of the pixelization. The given
        coordinates do not have to be within the map bounds.
        """
        x0 = (self.x[-1] + self.x[0]) / 2
        y0 = (self.y[-1] + self.y[0]) / 2
        self.x -= x - x0
        self.y -= y - y0

    def indices(self, x, y, clip=False):
        """
        Return the grid pixel indices (i_x, i_y) corresponding to the
        given arrays of grid coordinates. Arrays x and y must have the
        same size. Also return a boolean array of the same length that
        is True where the pixels are within the grid bounds and False
        elsewhere.

        If clip is False, a ValueError is raised if any of the pixel
        centers are outside the grid bounds, and array within will be
        all True. If clip is True, then the i_x and i_y values where
        within is False will be nonsense; the safe thing is to use
        only i_x[within] and i_y[within].
        """
        if x.size != y.size:
            raise ValueError("Arrays x and y must have the same length.")
        # This is a workaround for the behavior of int_: when given an
        # array of size 1 it returns an int instead of an array.
        if x.size == 1:
            i_x = np.array([np.int(np.round((x[0] - self.x[0]) / self.dx()))])
            i_y = np.array([np.int(np.round((y[0] - self.y[0]) / self.dy()))])
        else:
            i_x = np.int_(np.round_((x - self.x[0]) / self.dx()))
            i_y = np.int_(np.round_((y - self.y[0]) / self.dy()))
        within = ((0 <= i_x) & (i_x < self.x.size) &
                  (0 <= i_y) & (i_y < self.y.size))
        if not clip and not all(within):
            raise ValueError(
                "Not all points are inside the grid bounds, and clipping is not allowed.")
        return i_x, i_y, within

    def single_indices(self, x, y):
        """
        Return the grid pixel indices (i_x, i_y) corresponding to the
        given grid coordinates, where x and y are numbers.
        same size. Also return a boolean that
        is True if the point pixels are within the grid bounds and False
        elsewhere.
        """
        i_x = int(round((x - self.x[0]) / self.dx()))
        i_y = int(round((y - self.y[0]) / self.dy()))
        if not ((0 <= i_x) & (i_x < self.x.size) & (0 <= i_y) & (i_y < self.y.size)):
            raise ValueError("The point is not inside the grid bounds.")
        return i_x, i_y

    def coordinates(self, x, y):
        """
        Return two arrays (c_x, c_y) containing the pixel center
        coordinates corresponding to the given (x, y) coordinates,
        which must all be within the map bounds.
        """
        i_x, i_y, within = self.indices(x, y, clip=False)
        return self.x[i_x], self.y[i_y]

    def single_coordinates(self, x, y):
        """
        Return two numbers (c_x, c_y) representing the pixel center
        coordinates corresponding to the given (x, y)
        coordinates. Raise a ValueError if the given point is not
        within the map bounds.
        """
        i_x, i_y = self.single_indices(x, y)
        return self.x[i_x], self.y[i_y]

    def save_npy(self, folder):
        """
        Save x.npy, y.npy, and map.npy arrays to the given folder, which must not exist.
        """
        os.mkdir(folder)
        np.save(os.path.join(folder, 'map.npy'), self.map)
        np.save(os.path.join(folder, 'x.npy'), self.x)
        np.save(os.path.join(folder, 'y.npy'), self.y)

    def load_npy(self, folder):
        """
        Return this instance after loading x.npy, y.npy, and map.npy
        arrays from the given folder. This allows, for example,
        mueller = MuellerMap().load_npy('/saved/mueller/map/folder')
        """
        map = np.load(os.path.join(folder, 'map.npy'))
        if map.shape[2:] != self.shape:
            raise ValueError(
                "Array shape {} does not match map shape {}.".format(map.shape, self.shape))
        if map.dtype != self.data_type:
            raise ValueError("Array data type {} does not match map data type {}.".format(
                map.dtype, self.data_type))
        self.map = map
        self.x = np.load(os.path.join(folder, 'x.npy'))
        self.y = np.load(os.path.join(folder, 'y.npy'))
        return self

    @classmethod
    def coadd(cls, maps):
        # Check pixel spacing; np.spacing(1) is the difference between
        # 1 and the next float, or about 2.2e-16 on my machine.
        tolerance = np.spacing(1)
        m0 = maps[0]
        if not all([abs(m.dx() - m0.dx()) < tolerance and
                    abs(m.dy() - m0.dy()) < tolerance for m in maps]):
            raise ValueError(
                "Cannot coadd maps with different pixel spacings.")
        # Find the edges of the new map and its pixelization.
        x_min = min([m.x[0] for m in maps])
        x_max = max([m.x[-1] for m in maps])
        y_min = min([m.y[0] for m in maps])
        y_max = max([m.y[-1] for m in maps])
        # Check that this is ideal.
        nx = 1 + int(round((x_max - x_min) / m0.dx()))
        ny = 1 + int(round((y_max - y_min) / m0.dy()))
        coadded = cls()
        coadded.x = np.linspace(x_min, x_max, nx)
        coadded.y = np.linspace(y_min, y_max, ny)
        coadded.map = np.zeros((nx, ny) + cls.shape, dtype=cls.data_type)
        for m in maps:
            i_x, i_y, within = coadded.indices(m.x, m.y)
            # This uses broadcasting
            coadded.map[i_x[0]:i_x[-1] + 1, i_y[0]:i_y[-1] + 1] += m.map
        return coadded

    # In progress
    def make_plot(self, a, title="", xlabel="", ylabel="", color=plt.cm.hot, vmin=None, vmax=None):
        """
        Return a plot of the given array with horizontal axis self.x
        and vertical axis self.y. The array is transposed so that the
        first axis is horizontal and the second axis is vertical. The
        [0, 0] element of the array is in the lower left corner.
        """
        if vmin is None:
            vmin = np.min(a)
        if vmax is None:
            vmax = np.max(a)
        plt.ioff()
        w = 3.5
        h = 3
        fig = plt.figure(figsize=(w, h), dpi=200)
        cbar_ax = fig.add_axes((2.9 / w, 0.4 / h, 0.1 / w, 2.3 / h))
        cbar_ax.tick_params(direction='out', labelsize=4)
        image_ax = fig.add_axes((0.5 / w, 0.4 / h, 2.3 / w, 2.3 / h))
        image_ax.tick_params(direction='out', labelsize=4)
        image = image_ax.imshow(a.T,
                                cmap=color,
                                aspect='equal',
                                interpolation='nearest',
                                vmin=vmin,
                                vmax=vmax,
                                origin='lower',
                                extent=(self.x[0], self.x[-1], self.y[0], self.y[-1]))
        fig.colorbar(image, cax=cbar_ax)
        fig.suptitle(title)
        image_ax.set_xlabel(xlabel)
        image_ax.set_ylabel(ylabel)
        return fig

    def show_plot(self, a, title="", xlabel="", ylabel="", color=plt.cm.hot, vmin=None, vmax=None):
        """
        Display and return a plot of the given array; see make_plot()
        for usage.
        """
        fig = self.make_plot(a, title, xlabel, ylabel, color, vmin, vmax)
        plt.ion()
        plt.show()
        return fig

    def save_plot(self, filename, a, title="", xlabel="", ylabel="", color=plt.cm.hot, vmin=None, vmax=None):
        """
        Save a plot of the given array; see make_plot() for usage.
        """
        interactive = plt.isinteractive()
        fig = self.make_plot(a, title, xlabel, ylabel, color, vmin, vmax)
        plt.savefig(filename)
        if interactive:
            plt.ion()
            return fig
        else:
            plt.close()

    def make_contour(self, a, contours=None, title="", xlabel="", ylabel="", color=plt.cm.jet):
        """
        Return a contour plot of the given array with horizontal axis
        self.x and vertical axis self.y. The array is transposed so
        that the first axis is horizontal and the second axis is
        vertical. The [0, 0] element of the array is in the lower left
        corner.
        """
        if contours is None:
            contours = np.linspace(np.min(a.flatten()),
                                   np.max(a.flatten()), 10)
        plt.ioff()
        fig = plt.figure()
        plt.contour(a.T,
                    contours,
                    cmap=color,
                    extent=(self.x[0], self.x[-1], self.y[0], self.y[-1]))
        plt.colorbar(format='%3.3g')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        return fig

    def show_contour(self, a, contours=None, title="", xlabel="", ylabel="", color=plt.cm.jet):
        """
        Display and return a contour plot of the given array; see
        make_plot() for usage.
        """
        fig = self.make_contour(a, contours, title, xlabel, ylabel, color)
        plt.ion()
        plt.show()
        return fig

    def save_contour(self, filename, a, contours=None, title="", xlabel="", ylabel="", color=plt.cm.jet):
        """
        Save a contour plot of the given array; see make_plot() for usage.
        """
        interactive = plt.isinteractive()
        fig = self.make_contour(a, contours, title, xlabel, ylabel, color)
        plt.savefig(filename)
        if interactive:
            plt.ion()
            return fig
        else:
            plt.close()

    def cut(self, map_or_component, angle, center=(0, 0), single_sided=False):
        """
        Document me!
        """
        try:
            map = self[map_or_component]
        except TypeError:
            map = map_or_component
        angle = np.mod(angle, 2 * np.pi)
        # This shifts the line slightly, but ensures that the center
        # pixel is always part of the cut.
        x0, y0 = self.single_coordinates(*center)
        if (np.pi / 4 < angle < 3 * np.pi / 4 or
                5 * np.pi / 4 < angle < 7 * np.pi / 4):
            parity = np.sign(np.sin(angle))
            y = self.y[::parity]
            nonnegative = parity * (y - y0) >= 0
            # There is no vectorized cotangent.
            x = x0 + (y - y0) * np.cos(angle) / np.sin(angle)
        else:
            parity = np.sign(np.cos(angle))
            x = self.x[::parity]
            nonnegative = parity * (x - x0) >= 0
            y = y0 + (x - x0) * np.tan(angle)
        i_x, i_y, within = self.indices(x, y, clip=True)
        i_x = i_x[within]
        i_y = i_y[within]
        nonnegative = nonnegative[within]
        r = np.sqrt((self.x[i_x] - x0)**2 + (self.y[i_y] - y0)
                    ** 2) * np.where(nonnegative, 1, -1)
        cut = map[i_x, i_y]
        if single_sided:
            return r[nonnegative], cut[nonnegative]
        else:
            return r, cut

    def integrate(self, map_or_component):
        """
        Document me!
        """
        try:
            map = self[map_or_component]
        except TypeError:
            map = map_or_component
        return trapz(trapz(map, self.y, 1), self.x, 0)


class GridMap(FlatMap):
    """
    A FlatMap created from a .grd file. The file handling logic is
    contained in pygrasp.output.

    This class can load near field, far field, and coupling .grd
    files.  It currently cannot load elliptically truncated
    grids. Implement subclasses if necessary.
    """
    data_type = np.complex
    # Subclasses should define the key to the map indices.

    def __init__(self, filename=None):
        if filename is None:
            self.shape = (1, 1)
            super(GridMap, self).__init__()
        else:
            self.load_grd(filename)

    def load_grd(self, filename):
        self.meta, self.map = load_grd(filename)
        self.shape = self.map.shape[2:]
        # Check that XS and XE are offsets.
        self.x = self.meta['XCEN'] + \
            np.linspace(self.meta['XS'], self.meta['XE'], self.meta['NX'])
        self.y = self.meta['YCEN'] + \
            np.linspace(self.meta['YS'], self.meta['YE'], self.meta['NY'])

    def save_grd(self, filename):
        save_grd(filename, self.meta, self.map)

    def load_npy(self, folder, components=2):
        """
        Load x.npy, y.npy, and map.npy arrays from the given
        folder. Shape is a tuple of length 2 that must match
        map[:2]. This is necessary because a generic GridMap can take
        different shapes depending on the number of components in the
        grid.
        """
        self.shape = (components,)
        return super(GridMap, self).load_npy(folder)

    def dB(self, component):
        """
        Return the given map component in decibels.
        """
        return 20 * np.log10(abs(self[component]))


# Determine whether these are useful.
class UVFarGrid(GridMap):
    shape = (2,)
    keys = {'u': 0,
            'v': 1}


class UVNearGrid(GridMap):
    shape = (3,)
    keys = {'u': 0,
            'v': 1,
            'r': 2}


class JonesMap(FlatMap):

    shape = (2, 2)
    data_type = np.complex
    keys = {'co': 0,
            'cx': 1}

    def __init__(self, co=None, cx=None, normalize=True):
        """
        Create a new empty JonesMap or create one from two GridMap instances.
        """
        if co is None and cx is None:
            super(JonesMap, self).__init__()
        else:
            if not all(co.x == cx.x):
                raise ValueError("Map x values differ.")
            self.x = co.x.copy()
            if not all(co.y == cx.y):
                raise ValueError("Map y values differ.")
            self.y = co.y.copy()
            # Create a Jones matrix map with
            # map.shape = (x.size, y.size, 2, 2)
            self.map = np.empty((self.x.size, self.y.size) + self.shape,
                                dtype=self.data_type)
            self.map[:, :, :, 0] = co.map.copy()
            self.map[:, :, :, 1] = cx.map.copy()
            # If each feed is normalized to radiate 4 pi W total, then
            # this normalization produces Jones matrices such that
            # sum(abs(jones[0, 0])**2) + sum(abs(jones[1, 0])**2) \lesssim 1,
            # sum(abs(jones[0, 1])**2) + sum(abs(jones[1, 1])**2) \lesssim 1,
            # and Mueller matrices made from this Jones matrix satisfy
            # sum(mueller[i, i]) \lesssim 1
            # for i in (0, 1, 2, 3); that is, the integrals of the
            # diagonal maps should be nearly 1.
            if normalize:
                self.map /= np.sqrt(4 * np.pi)

    def dB(self, component):
        """
        Return the given map component in decibels.
        """
        return 20 * np.log10(abs(self[component]))


class MuellerMap(FlatMap):

    shape = (4, 4)
    data_type = np.float
    keys = {'T': 0,
            'Q': 1,
            'U': 2,
            'V': 3}
    inverse_keys = {0: 'T',
                    1: 'Q',
                    2: 'U',
                    3: 'V'}

    A = np.mat(np.array([[1, 0, 0, 1],
                         [1, 0, 0, -1],
                         [0, 1, 1, 0],
                         [0, 1j, -1j, 0]]))
    AI = A.getI()

    def __init__(self, jones_map=None):
        """
        Create a new empty MuellerMap or create one from a JonesMap instance.
        """
        if jones_map is None:
            super(MuellerMap, self).__init__()
        else:
            self.x = jones_map.x.copy()
            self.y = jones_map.y.copy()
            J = jones_map.map
            self.map = np.empty((self.x.size, self.y.size) + self.shape,
                                dtype=self.data_type)
            for x in range(self.x.size):
                for y in range(self.y.size):
                    J_xy = np.mat(J[x, y])
                    # The matrix cast is redundant since numpy takes *
                    # to mean matrix multiplication when either element
                    # is a matrix.
                    M_xy = self.A * \
                        np.mat(np.kron(J_xy, J_xy.conj())) * self.AI
                    if np.any(M_xy.imag):
                        raise ValueError("Nonzero complex value in M.")
                    self.map[x, y] = M_xy.real

    # Figure out how to create a title and axes labels.
    def contour_tile(self, color=None, suptitle="", figsize=(5, 5.5)):
        plt.ioff()
        fig = plt.figure(figsize=figsize)
        plt.suptitle(suptitle)
        for i in range(4):
            for j in range(4):
                # Verify.
                name = self.inverse_keys[i] + self.inverse_keys[j]
                sub = plt.subplot(4, 4, 4 * i + j + 1)
                sub.axes.get_xaxis().set_visible(False)
                sub.axes.get_yaxis().set_visible(False)
                c = np.linspace(np.min(self[i, j]), np.max(self[i, j]), 8)
                if all(c == 0):
                    plt.plot()
                else:
                    plt.contour(self[i, j].T,
                                contours=c,
                                cmap=color)
                sub.title.set_text(name)
        plt.ion()
        plt.show()
        return fig

    def plot_tile(self, color=None, suptitle="", figsize=(5, 5.5)):
        plt.ioff()
        fig = plt.figure(figsize=figsize)
        plt.suptitle(suptitle)
        for i in range(4):
            for j in range(4):
                name = self.inverse_keys[i] + self.inverse_keys[j]
                sub = plt.subplot(4, 4, 4 * i + j + 1)
                sub.axes.get_xaxis().set_visible(False)
                sub.axes.get_yaxis().set_visible(False)
                plt.imshow(self[i, j].T,
                           cmap=color,
                           aspect='equal',
                           interpolation='nearest',
                           origin='lower')
                sub.title.set_text(name)
        plt.ion()
        plt.show()
        return fig
