#!/usr/bin/env python

"""
Module implementing an XYZ file object class.
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Apr 17, 2012"

import re

from pymatgen.core.structure import Molecule


class XYZ(object):
    """
    Basic class for importing and exporting Molecules or Structures in XYZ
    format.

    .. note::
        Exporting periodic structures in the XYZ format will lose information
        about the periodicity. Essentially, only cartesian coordinates are
        written in this format and no information is retained about the
        lattice.
    """
    def __init__(self, mol, coord_precision=6):
        """
        Args:
            mol:
                Input molecule
        """
        self._mol = mol
        self.precision = coord_precision

    @property
    def molecule(self):
        """
        Returns molecule associated with this XYZ.
        """
        return self._mol

    @staticmethod
    def from_string(contents):
        """
        Creates XYZ object from a string.

        Args:
            contents:
                String representing an XYZ file.

        Returns:
            XYZ object
        """
        lines = contents.split("\n")
        num_sites = int(lines[0])
        coords = []
        sp = []
        coord_patt = re.compile(
            "(\w+)\s+([0-9\-\.]+)\s+([0-9\-\.]+)\s+([0-9\-\.]+)"
        )
        for i in xrange(2, 2 + num_sites):
            m = coord_patt.search(lines[i])
            if m:
                sp.append(m.group(1))  # this is 1-indexed
                coords.append(map(float, m.groups()[1:4]))  # this is 0-indexed
        return XYZ(Molecule(sp, coords))

    @staticmethod
    def from_file(filename):
        """
        Creates XYZ object from a file.

        Args:
            filename:
                XYZ filename

        Returns:
            XYZ object
        """
        with open(filename, "r") as f:
            return XYZ.from_string(f.read())

    def __str__(self):
        output = [str(len(self._mol)), self._mol.composition.formula]
        fmtstr = "{{}} {{:.{0}f}} {{:.{0}f}} {{:.{0}f}}".format(self.precision)
        for site in self._mol:
            output.append(fmtstr.format(site.specie, site.x, site.y, site.z))
        return "\n".join(output)

    def write_file(self, filename):
        """
        Writes XYZ to file.

        Args:
            filename:
                File name of output file.
        """
        with open(filename, "w") as f:
            f.write(self.__str__())
