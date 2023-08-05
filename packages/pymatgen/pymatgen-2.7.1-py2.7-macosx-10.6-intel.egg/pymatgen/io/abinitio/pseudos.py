"""
This module provides objects describing the basic parameters of the pseudopotentials used in Abinit,
a parser to instantiate pseudopotential objects from file and a simple database to access the official pseudopotential tables.
"""
from __future__ import division, print_function

import os
import os.path
import sys
import abc
import collections
import json
import cPickle as pickle
import cStringIO as StringIO
import numpy as np

from warnings import warn
from pprint import pprint

from pymatgen.core.periodic_table import PeriodicTable
from pymatgen.core.physical_constants import Ha_eV, Ha2meV
from pymatgen.util.num_utils import iterator_from_slice
#from pymatgen.serializers.json_coders import MSONable

__all__ = [
'Pseudo',
'PseudoDatabase',
]

__author__ = "Matteo Giantomassi"
__copyright__ = "Copyright 2013, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Matteo Giantomassi"
__email__ = "gmatteo at gmail.com"
__status__ = "Development"
__date__ = "$Feb 21, 2013M$"

##########################################################################################
# Tools and helper functions.

class FrozenDict(dict):
    "A dictionary that does not permit to redefine its keys"

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, val):
        if key in self:
            raise KeyError("Cannot overwrite existent key: %s" % str(key))
        dict.__setitem__(self, key, val)

    def update(self, *args, **kwargs):
        for (k, v) in dict(*args, **kwargs).iteritems():
            self[k] = v

def nested_dict_items(nested):
    "Iterate over the items of a nested Mapping (e.g. a dictionary)."

    for (key, value) in nested.items():
        if isinstance(value, collections.Mapping):
            for (inner_key, inner_value) in nested_dict_items(value):
                yield inner_key, inner_value
        else:
            yield key, value

def _read_nlines(filename, nlines):
    """
    Read at most nlines lines from file filename.
    If nlines is < 0, the entire file is read.
    """
    if nlines < 0:
        with open(filename, 'r') as fh:
            return fh.readlines()

    lines = []
    with open(filename, 'r') as fh:
        for (lineno, line) in enumerate(fh):
            if lineno == nlines: break
            lines.append(line)
        return lines

def read_dojo_report(filename):
    with open(filename, "r") as fh:
         lines = fh.readlines()
         try:
             start = lines.index("<DOJO_REPORT>\n")
         except ValueError:
             return {}
         stop = lines.index("</DOJO_REPORT>\n")

         return json.loads("".join(l for l in lines[start+1:stop]))

_l2str = {
    0: "s",
    1: "p",
    2: "d",
    3: "f",
    4: "g",
    5: "h",
    6: "i",
}

def l2str(l):
    "Convert the angular momentum l (int) to string."
    try:
        return _l2str[l]
    except KeyError:
        return "Unknown: received l = %s" % l

# TODO
# Should become an API common for the different codes that requires pseudos
def get_abinit_psp_dir(code="ABINIT"):
    import ConfigParser
    import pymatgen

    if code + "_PSP_DIR" in os.environ:
        return os.environ[code + "_PSP_DIR"]

    elif os.path.exists(os.path.join(os.path.dirname(pymatgen.__file__), "pymatgen.cfg")):
        module_dir = os.path.dirname(pymatgen.__file__)
        config = ConfigParser.SafeConfigParser()
        config.readfp(open(os.path.join(module_dir, "pymatgen.cfg")))
        return config.get(code, "pspdir")

    return None

##########################################################################################
_periodic_table = PeriodicTable()

class Pseudo(object):
    """
    Abstract base class defining the methods that must be implemented by the concrete pseudopotential classes.
    """
    __metaclass__ = abc.ABCMeta

    @classmethod
    def aspseudo(cls, obj):
        """
        Convert obj into a pseudo. Accepts:

            * Pseudo object.
            * string defining a path.
        """
        if isinstance(obj, cls):
            return obj
        else:
            # Assumes path.
            return cls.from_filename(obj)

    @staticmethod
    def from_filename(filename):
        """
        Return a pseudopotential object from filename.
        Note: the parser knows the concrete class that should be instanciated
        """
        return PseudoParser().parse(filename)

    def __repr__(self):
        return "<%s at %s, name = %s>" % (
            self.__class__.__name__, id(self), self.name)

    def __str__(self):
        "String representation"
        lines = []
        app = lines.append
        app("<%s: %s>" % (self.__class__.__name__, self.name))
        app("  summary: " + self.summary.strip())
        app("  number of valence electrons: %s" % self.Z_val)
        app("  XC correlation (ixc): %s" % self._pspxc)  #FIXME
        app("  maximum angular momentum: %s" % l2str(self.l_max))
        app("  angular momentum for local part: %s" % l2str(self.l_local))
        app("  radius for non-linear core correction: %s" % self.nlcc_radius)
        return "\n".join(lines)

    @abc.abstractproperty
    def summary(self):
        "String summarizing the most important properties"

    @abc.abstractproperty
    def filepath(self):
        "Absolute path of the pseudopotential file"

    @property
    def name(self):
        "File basename"
        return os.path.basename(self.filepath)

    @abc.abstractproperty
    def Z(self):
        "The atomic number of the atom."

    @abc.abstractproperty
    def Z_val(self):
        "Valence charge"

    @property
    def element(self):
        "Pymatgen Element"
        return _periodic_table[self.Z]

    @property
    def symbol(self):
        "Element symbol."
        return self.element.symbol

    @abc.abstractproperty
    def l_max(self):
        "Maximum angular momentum"

    @abc.abstractproperty
    def l_local(self):
        "Angular momentum used for the local part"

    #@abc.abstractproperty
    #def xc_family(self):
    #    "XC family e.g LDA, GGA, MGGA."

    #@abc.abstractproperty
    #def xc_flavor(self):
    #    "XC flavor e.g PW, PW91, PBE."

    @property
    def xc_type(self):
        "XC identifier e.g LDA-PW, GGA-PBE, GGA-revPBE"
        return "-".join([self.xc_family, self.xc_flavor])

    @property
    def isnc(self):
        "True if norm-conserving pseudopotential"
        return isinstance(self, NcPseudo)

    @property
    def ispaw(self):
        "True if PAW pseudopotential"
        return isinstance(self, PawPseudo)

    #@abc.abstractproperty
    #def has_soc(self):
    #    "True if pseudo contains spin-orbit coupling."

    #@abc.abstractmethod
    #def num_of_projectors(self, l='s'):
    #    "Number of projectors for the angular channel l"

    #@abc.abstractmethod
    #def generation_mode
    #    "scalar scalar-relativistic, relativistic"

    @property
    def has_dojo_report(self):
        "True if self contains the DOJO_REPORT section."
        return self.dojo_report

    @property
    def dojo_level(self):
        "The maximum level of the DOJO trials passes by the pseudo."
        if not self.dojo_report:
            return None
        else:
            from pymatgen.io.abinitio.pseudo_dojo import dojo_key2level
            levels = [dojo_key2level(key) for key in self.dojo_report]
            return max(levels)

    #def dojo_rank(self):

    def read_dojo_report(self):
        return read_dojo_report(self.path)

    def write_dojo_report(self, report):
        # Create JSON string from report.
        jstring = json.dumps(report, indent=4, sort_keys=True) + "\n"

        # Read lines from file and insert jstring between the tags.
        with open(self.path, "r") as fh:
            lines = fh.readlines()
            try:
                start = lines.index("<DOJO_REPORT>\n")
            except ValueError:
                start = -1

            if start == -1:
               # DOJO_REPORT was not present.
               lines += ["\n", "<DOJO_REPORT>\n", jstring , "</DOJO_REPORT>\n",]
            else:
               stop = lines.index("</DOJO_REPORT>\n")
               lines.insert(stop, jstring)
               del lines[start+1:stop]

        #  Write new file.
        with open(self.path, "w") as fh:
            fh.writelines(lines)

    def remove_dojo_report(self):
        # Read lines from file and insert jstring between the tags.
        with open(self.path, "r") as fh:
            lines = fh.readlines()
            try:
                start = lines.index("<DOJO_REPORT>\n")
            except ValueError:
                start = -1

            if start == -1:
               return

            stop = lines.index("</DOJO_REPORT>\n")
            if stop == -1:
               return

            del lines[start+1:stop]
            #pprint(lines)

        # Write new file.
        with open(self.path, "w") as fh:
            fh.writelines(lines)

    def hint_for_accuracy(self, accuracy):
        """
        Returns an hint object with parameters such as ecut and aug_ratio for
        given accuracy. Returns None if no hint is available.

        Args:
            accuracy: ["low", "normal", "high"]
        """
        if self.has_dojo_report:
            return Hint.from_dict(self.dojo_report["hints"][accuracy])
        else:
            return None

    @property
    def has_hints(self):
        "True if self provides hints on the cutoff energy"
        for acc in ["low", "normal", "high"]:
            if self.hint_for_accuracy(acc) is None:
                return False
        return True

    def checksum(self):
        """
        Return the checksum of the pseudopotential file.

        The checksum is given by the tuple (basename, line_num, hexmd5)
        where basename if the file name, hexmd5 is the (hex) MD5 hash,
        and line_num is the number of lines in the file.
        """
        import hashlib
        hasher = hashlib.md5()
        with open(self.filepath, "r") as fh:
            hasher.update(fh.read())

        return self.name, len(text.splitlines()), hasher.hexdigest()

##########################################################################################

class NcPseudo(object):
    """
    Abstract class defining the methods that must be implemented
    by the concrete classes representing norm-conserving pseudopotentials.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def nlcc_radius(self):
        """
        Radius at which the core charge vanish (i.e. cut-off in a.u.).
        Returns 0.0 if nlcc is not used.
        """

    @property
    def has_nlcc(self):
        "True if the pseudo is generated with non-linear core correction."
        return self.nlcc_radius > 0.0

##########################################################################################

class PawPseudo(object):
    """
    Abstract class that defines the methods that must be implemented
    by the concrete classes representing PAW pseudopotentials.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def paw_radius(self):
        "Radius of the PAW sphere in a.u."

##########################################################################################

class AbinitPseudo(Pseudo):
    """
    An AbinitPseudo is a pseudopotential whose file contains an abinit header.
    """
    def __init__(self, path, header):

        self.path     = path
        self._summary = header.summary
        self.dojo_report = header.dojo_report
        #self.pspcod  = header.pspcod

        for (attr_name, desc) in header.items():
            value = header.get(attr_name, None)

            # Hide these attributes since one should always use the public interface.
            setattr(self, "_" + attr_name, value)

    @property
    def summary(self):
        return self._summary.strip()

    @property
    def filepath(self):
        return os.path.abspath(self.path)

    @property
    def Z(self):
        return self._zatom

    @property
    def Z_val(self):
        "Number of valence electrons."
        return self._zion

    @property
    def l_max(self):
        return self._lmax

    @property
    def l_local(self):
        return self._lloc

##########################################################################################

class NcAbinitPseudo(NcPseudo, AbinitPseudo):
    """
    Norm-conserving pseudopotential in the Abinit format.
    """

    @property
    def summary(self):
        return self._summary.strip()

    @property
    def filepath(self):
        return os.path.abspath(self.path)

    @property
    def Z(self):
        return self._zatom

    @property
    def Z_val(self):
        "Number of valence electrons."
        return self._zion

    @property
    def l_max(self):
        return self._lmax

    @property
    def l_local(self):
        return self._lloc

    @property
    def nlcc_radius(self):
        return self._rchrg

##########################################################################################

class PawAbinitPseudo(PawPseudo, AbinitPseudo):
    "Paw pseudopotential in the Abinit format."

    @property
    def paw_radius(self):
        return self._r_cut

    #def orbitals(self):

##########################################################################################

class Hint(collections.namedtuple("Hint", "ecut aug_ratio")):
    """
    Suggested value for the cutoff energy [Hartree units] and the augmentation ratio (PAW pseudo)
    """
    @property
    def to_dict(self):
        #d["@module"] = self.__class__.__module__
        #d["@class"] = self.__class__.__name__
        return {f: getattr(self, f) for f in self._fields}

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k,v in d.items() if not k.startswith("@")})

##########################################################################################

def _dict_from_lines(lines, key_nums, sep=None):
    """
    Helper function to parse formatted text structured like:

    value1 value2 ... sep key1, key2 ...

    key_nums is a list giving the number of keys for each line. 0 if line should be skipped.
    sep is a string denoting the character that separates the keys from the value (None if
    no separator is present).

    Return dict{key1 : value1, key2 : value2, ...}
    """

    if isinstance(lines, basestring):
        lines = [lines]

    if not isinstance(key_nums, collections.Iterable):
        key_nums = list(key_nums)

    if len(lines) != len(key_nums):
        err_msg = "lines = %s\n key_num =  %s" % (str(lines), str(key_nums))
        raise ValueError(err_msg)

    kwargs = FrozenDict()

    for (i, nk) in enumerate(key_nums):
        if nk == 0: continue
        line = lines[i]

        tokens = [t.strip() for t in line.split()]
        values, keys = tokens[:nk], "".join([t for t in tokens[nk:]])
        keys = keys.split(",")

        if sep is not None:
            check = keys[0][0]
            if check != sep:
                raise RuntimeError("Expecting sep %s, got %s" % (sep, check))
            keys[0] = keys[0][1:]

        if len(values) != len(keys):
            raise RuntimeError("%s: %s\n %s len(keys) != len(value) %s" %
                (filename, line, keys, values))

        kwargs.update(zip(keys, values))

    return kwargs

##########################################################################################

class AbinitHeader(dict):
    "Dictionary whose keys can be also accessed as attributes."

    def __getattr__(self, name):
        try:
            # Default behaviour
            return super(AbinitHeader, self).__getattribute__(name)
        except AttributeError:
            try:
                # Try in the dictionary.
                return self[name]
            except KeyError as exc:
                raise AttributeError(str(exc))

##########################################################################################

def _int_from_str(string):
    float_num = float(string)
    int_num = int(float_num)
    if float_num == int_num:
        return int_num
    else:
        raise TypeError("Cannot convert string %s to int" % string)

class NcAbinitHeader(AbinitHeader):
    """
    The abinit header found in the NC pseudopotential files.
    """
    _attr_desc = collections.namedtuple("att", "default astype")

    _vars = {
        # Mandatory
        "zatom"        : _attr_desc(None, _int_from_str),
        "zion"         : _attr_desc(None, float),
        "pspdat"       : _attr_desc(None, float),
        "pspcod"       : _attr_desc(None, int),
        "pspxc"        : _attr_desc(None, int),
        "lmax"         : _attr_desc(None, int),
        "lloc"         : _attr_desc(None, int),
        "r2well"       : _attr_desc(None, float),
        "mmax"         : _attr_desc(None, float),
        # Optional variables for non linear-core correction. HGH does not have it.
        "rchrg"        : _attr_desc(0.0,  float), # radius at which the core charge vanish (i.e. cut-off in a.u.)
        "fchrg"        : _attr_desc(0.0,  float),
        "qchrg"        : _attr_desc(0.0,  float),
    }
    del _attr_desc

    def __init__(self, summary, **kwargs):

        super(NcAbinitHeader, self).__init__()

        self.summary = summary.strip()

        for (key, desc) in NcAbinitHeader._vars.items():
            default, astype = desc.default, desc.astype

            value = kwargs.pop(key, None)

            if value is None:
                value = default
                if default is None:
                    raise RuntimeError("Attribute %s must be specified" % key)
            else:
                try:
                    value = astype(value)
                except:
                    raise RuntimeError("Conversion Error for key, value %s" % (key, value))

            self[key] = value

        # Add dojo_report
        self["dojo_report"] = kwargs.pop("dojo_report", {})

        if kwargs:
            msg = "kwargs should be empty but got %s" % str(kwargs)
            raise RuntimeError(msg)

    @staticmethod
    def fhi_header(filename, ppdesc):
        "Parse the FHI abinit header."
        # Example:
        # Troullier-Martins psp for element  Sc        Thu Oct 27 17:33:22 EDT 1994
        #  21.00000   3.00000    940714                zatom, zion, pspdat
        #    1    1    2    0      2001    .00000      pspcod,pspxc,lmax,lloc,mmax,r2well
        # 1.80626423934776     .22824404341771    1.17378968127746   rchrg,fchrg,qchrg

        lines = _read_nlines(filename, -1)

        header = _dict_from_lines(lines[:4], [0, 3, 6, 3])
        summary = lines[0]

        header["dojo_report"] = read_dojo_report(filename)

        return NcAbinitHeader(summary, **header)

    @staticmethod
    def hgh_header(filename, ppdesc):
        "Parse the HGH abinit header."
        # Example:
        #Hartwigsen-Goedecker-Hutter psp for Ne,  from PRB58, 3641 (1998)
        #   10   8  010605 zatom,zion,pspdat
        # 3 1   1 0 2001 0  pspcod,pspxc,lmax,lloc,mmax,r2well

        lines = _read_nlines(filename, -1)

        header = _dict_from_lines(lines[:3], [0, 3, 6])
        summary = lines[0]

        header["dojo_report"] = read_dojo_report(filename)

        return NcAbinitHeader(summary, **header)

    @staticmethod
    def tm_header(filename, ppdesc):
        "Parse the TM abinit header."
        # Example:
        #Troullier-Martins psp for element Fm         Thu Oct 27 17:28:39 EDT 1994
        #100.00000  14.00000    940714                zatom, zion, pspdat
        #   1    1    3    0      2001    .00000      pspcod,pspxc,lmax,lloc,mmax,r2well
        #   0   4.085   6.246    0   2.8786493        l,e99.0,e99.9,nproj,rcpsp
        #   .00000000    .0000000000    .0000000000    .00000000   rms,ekb1,ekb2,epsatm
        #   1   3.116   4.632    1   3.4291849        l,e99.0,e99.9,nproj,rcpsp
        #   .00000000    .0000000000    .0000000000    .00000000   rms,ekb1,ekb2,epsatm
        #   2   4.557   6.308    1   2.1865358        l,e99.0,e99.9,nproj,rcpsp
        #   .00000000    .0000000000    .0000000000    .00000000   rms,ekb1,ekb2,epsatm
        #   3  23.251  29.387    1   2.4776730        l,e99.0,e99.9,nproj,rcpsp
        #   .00000000    .0000000000    .0000000000    .00000000   rms,ekb1,ekb2,epsatm
        #   3.62474762267880     .07409391739104    3.07937699839200   rchrg,fchrg,qchrg

        lines = _read_nlines(filename, -1)
        header = []

        for (lineno, line) in enumerate(lines):
            header.append(line)
            if lineno == 2: # Read lmax.
                tokens = line.split()
                pspcod, pspxc, lmax = map(int, tokens[:3])
                if tokens[-1].strip() != "pspcod,pspxc,lmax,lloc,mmax,r2well":
                    raise RuntimeError("%s: Invalid line\n %s"  % (filename, line))
                lines = lines[3:]
                break

        # TODO
        # Parse the section with the projectors.
        #0   4.085   6.246    0   2.8786493        l,e99.0,e99.9,nproj,rcpsp
        #.00000000    .0000000000    .0000000000    .00000000   rms,ekb1,ekb2,epsatm
        projectors = collections.OrderedDict()
        for idx in range(2*(lmax+1)):
            line = lines[idx]
            if idx % 2 == 0: proj_info = [line,]
            if idx % 2 == 1:
                proj_info.append(line)
                d = _dict_from_lines(proj_info, [5,4])
                projectors[int(d["l"])] = d

        # Add the last line with info on nlcc.
        header.append(lines[idx+1])
        summary = header[0]

        header = _dict_from_lines(header, [0,3,6,3])

        header["dojo_report"] = read_dojo_report(filename)

        return NcAbinitHeader(summary, **header)

##########################################################################################

class PawAbinitHeader(AbinitHeader):
    """
    The abinit header found in the PAW pseudopotential files.
    """
    _attr_desc = collections.namedtuple("att", "default astype")

    _vars = {
        "zatom"           : _attr_desc(None, float),
        "zion"            : _attr_desc(None, float),
        "pspdat"          : _attr_desc(None, float),
        "pspcod"          : _attr_desc(None, int),
        "pspxc"           : _attr_desc(None, int),
        "lmax"            : _attr_desc(None, int),
        "lloc"            : _attr_desc(None, int),
        "mmax"            : _attr_desc(None, int),
        "r2well"          : _attr_desc(None, float),
        "pspfmt"          : _attr_desc(None, str),
        "creatorID"       : _attr_desc(None, int),
        "basis_size"      : _attr_desc(None, int),
        "lmn_size"        : _attr_desc(None, int),
        "orbitals"        : _attr_desc(None, list),
        "number_of_meshes": _attr_desc(None, int),
        "r_cut"           : _attr_desc(None, float), # r_cut(PAW) in the header
        "shape_type"      : _attr_desc(None, int),
        "rshape"          : _attr_desc(None, float),
    }
    del _attr_desc

    def __init__(self, summary, **kwargs):

        super(PawAbinitHeader, self).__init__()

        self.summary = summary.strip()

        for (key, desc) in PawAbinitHeader._vars.items():
            default, astype = desc.default, desc.astype

            value = kwargs.pop(key, None)

            if value is None:
                value = default
                if default is None:
                    raise RuntimeError("Attribute %s must be specified" % key)
            else:
                try:
                    value = astype(value)
                except:
                    raise RuntimeError("Conversion Error for key, value %s" % (key, value))

            self[key] = value

        if kwargs:
            raise RuntimeError("kwargs should be empty but got %s" % str(kwargs))

    @staticmethod
    def paw_header(filename, ppdesc):
        "Parse the PAW abinit header."
        # Example
        #C  (US d-loc) - PAW data extracted from US-psp (D.Vanderbilt) - generated by USpp2Abinit v2.3.0
        #   6.000   4.000 20090106               : zatom,zion,pspdat
        #  7 11  1 0   560 0.                    : pspcod,pspxc,lmax,lloc,mmax,r2well
        # paw4 2230                              : pspfmt,creatorID
        #  4  8                                  : basis_size,lmn_size
        # 0 0 1 1                                : orbitals
        # 5                                      : number_of_meshes
        # 1 2  560 1.5198032759E-04 1.6666666667E-02 : mesh 1, type,size,rad_step[,log_step]
        # 2 2  556 1.5198032759E-04 1.6666666667E-02 : mesh 2, type,size,rad_step[,log_step]
        # 3 2  576 1.5198032759E-04 1.6666666667E-02 : mesh 3, type,size,rad_step[,log_step]
        # 4 2  666 1.5198032759E-04 1.6666666667E-02 : mesh 4, type,size,rad_step[,log_step]
        # 5 2  673 1.5198032759E-04 1.6666666667E-02 : mesh 5, type,size,rad_step[,log_step]
        #  1.5550009124                          : r_cut(PAW)
        # 3 0.                                   : shape_type,rshape

        if ppdesc.format != "paw4":
            raise NotImplementedError("format != paw4 are not supported")

        lines = _read_nlines(filename, -1)

        summary = lines[0]
        header = _dict_from_lines(lines[:5], [0, 3, 6, 2, 2], sep=":")

        lines = lines[5:]
        # TODO
        # Parse orbitals and number of meshes.
        header["orbitals"] = [int(t) for t in lines[0].split(":")[0].split()]
        header["number_of_meshes"] = num_meshes = int(lines[1].split(":")[0])

        #print filename, header

        # Skip meshes =
        lines = lines[2+num_meshes:]
        #for midx in range(num_meshes):
        #    l = midx + 1

        #print lines[0]
        header["r_cut"] = float(lines[0].split(":")[0])
        #print lines[1]
        header.update(_dict_from_lines(lines[1], [2], sep=":"))

        header["dojo_report"] = read_dojo_report(filename)

        return PawAbinitHeader(summary, **header)

##########################################################################################

class PseudoParserError(Exception):
    pass

class PseudoParser(object):
    """
    Responsible for parsing pseudopotential files and returning pseudopotential objects.

    Usage::
        pseudo = PseudoParser().parse("filename")
    """
    Error = PseudoParserError

    #: Supported values of pspcod
    ppdesc = collections.namedtuple("ppdesc", "pspcod name psp_type format")

    # TODO Recheck
    _pspcodes = collections.OrderedDict( {
        1 : ppdesc(1, "TM",  "NC", None),
        3 : ppdesc(3, "HGH", "NC", None),
        #4 : ppdesc(4, "NC",     , None),
        #5 : ppdesc(5, "NC",     , None),
        6 : ppdesc(6, "FHI", "NC", None),
        7 : ppdesc(6, "PAW_abinit_text", "PAW", None),
        #8 : ppdesc(8, "NC", None),
       10 : ppdesc(10, "HGHK", "NC", None),
    })
    del ppdesc

    def __init__(self):
        # List of files that have been parsed succesfully.
        self._parsed_paths = []

        # List of files that could not been parsed.
        self._wrong_paths  = []

    def scan_directory(self, dirname, exclude_exts=None):
        """
        Analyze the files contained in directory dirname.
        Args:
            dirname:
                directory path
            exclude_exts:
                list of file extensions that should be skipped.

        :return: List of pseudopotential objects.
        """
        if exclude_exts is None:
            exclude_exts = []

        for (i, ext) in enumerate(exclude_exts):
            if not ext.strip().startswith("."):
                exclude_exts[i] =  "." + ext.strip()

        # Exclude files depending on the extension.
        paths = []
        for fname in os.listdir(dirname):
            root, ext = os.path.splitext(fname)
            if ext not in exclude_exts:
                paths.append(os.path.join(dirname, fname))

        pseudos = []
        for path in paths:
            # parse the file and generate the pseudo.
            pseudo = self.parse(path)

            if pseudo is not None:
                pseudos.append(pseudo)
                self._parsed_paths.extend(path)
            else:
                self._wrong_paths.extend(path)

        return pseudos

    def read_ppdesc(self, filename):
        """
        Read the pseudopotential descriptor from file filename.

        :return: Pseudopontential descriptor. None if filename is not a valid pseudopotential file.
        :raise: `PseudoParserError` if fileformat is not supported.
        """

        if filename.endswith(".xml"):
            raise self.Error("XML pseudo not supported yet")

        else:
            # Assume file with the abinit header.
            lines = _read_nlines(filename, -1)

            for (lineno, line) in enumerate(lines):

                if lineno == 2:
                    try:
                        tokens = line.split()
                        pspcod, pspxc = map(int, tokens[:2])
                    except:
                        msg = "%s: Cannot parse pspcod, pspxc in line\n %s" % (filename, line)
                        sys.stderr.write(msg)
                        return None

                    if tokens[-1].strip() != "pspcod,pspxc,lmax,lloc,mmax,r2well":
                        raise self.Error("%s: Invalid line\n %s"  % (filename, line))
                        return None

                    if pspcod not in self._pspcodes:
                        raise self.Error("%s: Don't know how to handle pspcod %s\n"  % (filename, pspcod))

                    ppdesc = PseudoParser._pspcodes[pspcod]

                    if pspcod == 7:
                        # PAW -> need to know the format pspfmt
                        tokens = lines[lineno+1].split()
                        pspfmt, creatorID = tokens[:2]
                        if tokens[-1].strip() != "pspfmt,creatorID":
                            raise self.Error("%s: Invalid line\n %s"  % (filename, line))
                            return None
                        ppdesc = ppdesc._replace(format = pspfmt)

                    return ppdesc

            return None

    def parse(self, filename):
        """
        Read and parse a pseudopotential file.

        :return: pseudopotential object or None if filename is not
                 a valid pseudopotential file.
        """
        path = os.path.abspath(filename)

        ppdesc = self.read_ppdesc(path)

        if ppdesc is None: return None

        psp_type = ppdesc.psp_type

        parsers = {
         "FHI"              : NcAbinitHeader.fhi_header,
         "TM"               : NcAbinitHeader.tm_header,
         "HGH"              : NcAbinitHeader.hgh_header,
         "HGHK"             : NcAbinitHeader.hgh_header,
         "PAW_abinit_text"  : PawAbinitHeader.paw_header,
        }

        #try:
        header = parsers[ppdesc.name](path, ppdesc)
        #except Exception as exc:
        #    raise self.Error(str(exc))

        root, ext = os.path.splitext(path)

        # Add the content of input file (if present).
        # The name of the input is name + ".ini"
        input = None
        input_path = root + ".ini"
        if os.path.exists(input_path):
            with open(input_path, 'r') as fh:
                input = fh.read()

        if psp_type == "NC":
            pseudo = NcAbinitPseudo(path, header)
        elif psp_type == "PAW":
            pseudo = PawAbinitPseudo(path, header)
        else:
            raise NotImplementedError("psp_type not in [NC, PAW]")

        return pseudo

##########################################################################################

class PseudoTable(collections.Sequence):
    """
    Define the pseudopotentials from the element table.
    Individidual elements are accessed by name, symbol or atomic number.

    For example, the following all retrieve iron:

    print elements[26]
    Fe
    print elements.Fe
    Fe
    print elements.symbol('Fe')
    Fe
    print elements.name('iron')
    Fe
    print elements.isotope('Fe')
    Fe
    """
    @classmethod
    def astable(cls, items):
        if isinstance(items, cls):
            return items
        return cls(items)

    def __init__(self, pseudos):
        """
        Args:
            pseudos:
                List of pseudopotentials or filepaths
        """
        # Store pseudos in a default dictionary with z as key.
        # Note that we can have more than one pseudo for given z.
        # hence the values are lists of pseudos.

        if not isinstance(pseudos, collections.Iterable):
            pseudos = [pseudos]

        self._pseudos_with_z = collections.defaultdict(list)

        for pseudo in pseudos:
            p = pseudo
            if not isinstance(pseudo, Pseudo):
                p = Pseudo.from_filename(pseudo)

            self._pseudos_with_z[p.Z].append(p)

        for z in self.zlist:
            pseudo_list = self._pseudos_with_z[z]
            symbols = [p.symbol for p in pseudo_list]
            symbol = symbols[0]
            if any(symb != symbol for symb in symbols):
                raise ValueError("All symbols must be equal while they are: %s" % str(symbols))
            setattr(self, symbol, pseudo_list)

    def __getitem__(self, Z):
        """
        Retrieve pseudos for the atomic number z.
        Accepts both int and slice objects.
        """
        if isinstance(Z, slice):
            assert Z.stop is not None
            pseudos = []
            for znum in iterator_from_slice(Z):
                pseudos.extend(self._pseudos_with_z[znum])
            return pseudos
        else:
            return self._pseudos_with_z[Z]

    def __len__(self):
        return len(list(self._iter__()))

    def __iter__(self):
        "Process the elements in Z order."
        for z in self.zlist:
            for pseudo in self._pseudos_with_z[z]:
                yield pseudo

    def __repr__(self):
        return "<%s at %s, long_name = %s>" % (self.__class__.__name__, id(self), self.long_name)

    #def __str__(self):
    #    strio = StringIO.StringIO()
    #    self.print_table(stream=strio)
    #    strio.seek(0)
    #    return strio.read()

    @property
    def allnc(self):
        "True if all pseudos are norm-conserving"
        return all(p.isnc for p in self)

    @property
    def allpaw(self):
        "True if all pseudos are PAW"
        return all(p.ispaw for p in self)

    @property
    def long_name(self):
        return "-".join([getattr(self, key) for key in ["psp_type", "xc_type", "name"]])

    @property
    def zlist(self):
        "Ordered list with the atomic numbers available in the table."
        zlist = list(self._pseudos_with_z.keys())
        zlist.sort()
        return zlist

    def iscomplete(self, zmax=118):
        """
        True if table is complete i.e. all elements with z < zmax
        have at least on pseudopotential
        """
        for z in range(1, zmax):
            if not self[z]: return False
        return True

    def pseudos_with_symbol(self, symbol):
        """
        Return the list of pseudopotentials in the table the with given symbol.
        Return an empty list if no pseudo is avaiable
        """
        try:
            return getattr(self, str(symbol))
        except AttributeError:
            return []

    def pseudo_from_name(self, name):
        "Return the pseudo in the table with the given name"
        for pseudo in self:
            if pseudo.name == name:
                return pseudo
        return None

    def list_properties(self, *props, **kw):
        """
        Print a list of elements with the given set of properties.

        Args:
            *prop1*, *prop2*, ... : string
                Name of the properties to print
            *format*: string
                Template for displaying the element properties, with one
                % for each property.

        :Returns: None

        For example, print a table of mass and density.

        from periodictable import elements
        elements.list('symbol','mass','density', format="%-2s: %6.2f u %5.2f g/cm^3")
        H :   1.01 u   0.07 g/cm^3
        He:   4.00 u   0.12 g/cm^3
        Li:   6.94 u   0.53 g/cm^3
        ...
        Bk: 247.00 u  14.00 g/cm^3
        """
        format = kw.pop('format',None)
        assert len(kw) == 0

        for pseudo in self:
            try:
                L = tuple(getattr(pseudo,p) for p in props)
            except AttributeError:
                # Skip elements which don't define all the attributes
                continue

            # Skip elements with a value of None
            if any(v is None for v in L):
                continue

            if format is None:
                print(" ".join(str(p) for p in L))
            else:
                #try:
                print(format % L)
                #except:
                #    print "format",format,"args",L
                #    raise

    def print_table(self, stream=sys.stdout, filter_function=None):
        """
        A pretty ASCII printer for the periodic table, based on some filter_function.

        Args:
            filter_function:
                A filtering function taking a Pseudo as input and returns a boolean.
                For example, setting filter_function = lambda el: el.X > 2 will print
                a periodic table containing only elements with electronegativity > 2.
        """
        for row in range(1, 10):
            rowstr = []
            for group in range(1, 19):
                el = Element.from_row_and_group(row, group)
                if el and ((not filter_function) or filter_function(el)):
                    rowstr.append("{:3s}".format(el.symbol))
                else:
                    rowstr.append("   ")
            print(" ".join(rowstr))

##########################################################################################

class PseudoDatabase(dict):

    _save_file = "pseudo_database.pickle"
    #
    #        "TM"
    #"LDA"   "HGH"
    #"GGA"   "HGK"
    #        "FHI"
    #        "USERS"

    #"LDA"   "ATOMPAW"
    #"GGA"   "USPP"
    #        "USERS"

    # xc_type = xc_family-[xc_flavor]
    # dirname = psp_type _ xc_type _ table_name
    PSP_TYPES = ["NC", "PAW"]

    XC_FAMILIES = ["LDA", "GGA"]

    XC_FLAVOR   = ["PBE", "PW91"]

    XC_TYPES = ["LDA", "GGA"]

    def __new__(cls, dirpath=None, force_reload=False):
        new = dict.__new__(cls)

        if dirpath is None:
            return new

        dirpath = os.path.abspath(dirpath)

        cached_database = os.path.join(dirpath, cls._save_file)

        if not os.path.exists(cached_database) or force_reload:
            new = PseudoDatabase.__build(new, dirpath)
        else:
            new = PseudoDatabase.__from_filename(new, cached_database)

        return new

    def __init__(self, dirpath=None, force_reload=False):
        pass

    def __len__(self):
        return len([self.all_pseudos])

    def __build(self, top):
        print("Building new database...")

        new_database = PseudoDatabase()

        for key in self.PSP_TYPES:
            new_database[key] = None

        parser = PseudoParser()

        for psp_type in self.PSP_TYPES:
            new_database[psp_type] = dict.fromkeys(self.XC_TYPES, dict())

        for (dirpath, dirnames, filenames) in os.walk(top):
            for dirname in dirnames:

                try:
                    psp_type, xc_type, table_type = os.path.basename(dirname).split("_")
                except:
                    err_msg = "Malformatted name for directory %s" % dirname
                    raise RuntimeError(err_msg)
                #print(psp_type, xc_type, table_type)

                if psp_type not in self.PSP_TYPES or xc_type not in self.XC_TYPES:
                    raise ValueError("Don't know how to handle %s %s" % (psp_type, xc_type))

                pseudos = parser.scan_directory( os.path.join(dirpath, dirname),
                    exclude_exts = [".py", ".ini", ".sh", ".gz", ".pl", ".txt", ".swp", ".data", "pickle",])

                table = PseudoTable(pseudos)

                new_database[psp_type][xc_type][table_type] = table

        # Save the database.
        cached_database = os.path.join(top, self._save_file)

        new_database.save(cached_database)

        return new_database

    def __from_filename(self, filename):

        cached_database = filename
        if cached_database is None: cached_database = self._save_file

        print("Loading database from: %s" % cached_database)

        # Read the database from the cpickle file.
        # Use file locking mechanism to prevent IO from other processes.
        #with FileLock(database_path + ".lock") as lock:
        with open(cached_database, "r") as fh:
            database = pickle.load(fh)

        #assert database.dirpath == os.path.split(abspath(cached_database))[0]
        return database

    @property
    def LDA_HGH_PPTABLE(self):
        return self["NC"]["LDA"]["HGH"]

    @property
    def GGA_FHI_PPTABLE(self):
        return self["NC"]["GGA"]["FHI"]

    @property
    def GGA_HGHK_PPTABLE(self):
        return self["NC"]["GGA"]["HGHK"]

    @property
    def path(self):
        return self._path

    @property
    def dirname(self):
        return os.path.dirname(self._path)

    def save(self, filename=None, protocol=-1):

        cached_database = filename
        if cached_database is None: cached_database = self._save_file

        print("Saving database on file %s" % cached_database)

        # Save the database in the cpickle file.
        # Use file locking mechanism to prevent IO from other processes.
        #with FileLock(cached_database) as lock:

        self._path = cached_database

        with open(cached_database, "w") as fh:
            pickle.dump(self, fh, protocol=protocol)

    @property
    def all_pseudos(self):
        "Return a list with all the pseudopotentials in the database"
        pseudos = []
        for (k, table) in nested_dict_items(self):
            pseudos.extend([p for p in table])
        return pseudos

    def write_hash_table(self, filename):
        #with open(filename, "w") as fh
        fh = sys.stdout

        def tail2(path):
            head, tail0 = os.path.split(path)
            head, tail1 = os.path.split(head)
            return os.path.join(tail1, tail0)

        fh.write("# relative_path, md5 num_line\n")
        for pseudo in self.all_pseudos():
            #print type(pseudo), pseudo
            checksum = pseudo.checksum()
            relative_path = tail2(pseudo.path)
            fh.write("%s %s %s\n" % (relative_path, checksum[0], checksum[1]))

    def table(self, psp_type, xc_type):
        return self[psp_type][xc_type].values()

    def nc_tables(self, xc_type):
        "Iterate over the norm-conserving tables with XC type xc_type."
        return self.table("NC", xc_type)

    def paw_tables(self, psp_type, xc_type):
        "Iterate over the PAW tables with XC type xc_type."
        return self.table("PAW", xc_type)

    def nc_pseudos(self, symbol, xc_type, table_type=None, **kwargs):
        "Return a list of :class:`Pseudo` instances."
        pseudos = []
        for table in self.nc_tables(xc_type):
            if table_type is not None and table_type != table.type: continue
            pseudos.extend( table.pseudos_with_symbol(symbol) )

        return pseudos

    #def paw_pseudos(self, symbol, xc_type, table_type=None, **kwargs):

    #def find_all(self, symbol, xc_type):

##########################################################################################
