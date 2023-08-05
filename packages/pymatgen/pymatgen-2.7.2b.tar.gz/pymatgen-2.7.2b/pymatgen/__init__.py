__author__ = ", ".join(["Shyue Ping Ong", "Anubhav Jain", "Geoffroy Hautier",
                        "William Davidson Richard", "Stephen Dacek",
                        "Michael Kocher", "Dan Gunter", "Shreyas Cholia",
                        "Vincent L Chevrier", "Rickard Armiento"])
__date__ = "May 12 2013"
__version__ = "2.7.2b"

import json
#Useful aliases for commonly used objects and modules.

from .core import *
from .serializers.json_coders import PMGJSONEncoder, PMGJSONDecoder, \
    pmg_dump, pmg_load
from .electronic_structure.core import Spin, Orbital
from .util.io_utils import zopen
from .io.smartio import read_structure, write_structure, read_mol, write_mol
from .matproj.rest import MPRester
