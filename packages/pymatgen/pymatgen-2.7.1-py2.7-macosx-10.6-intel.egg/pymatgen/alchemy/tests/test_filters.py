#!/usr/bin/env python

from pymatgen.alchemy.filters import ContainsSpecieFilter, \
    SpecieProximityFilter, RemoveDuplicatesFilter
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
from pymatgen.core.periodic_table import Specie
from pymatgen.io.cifio import CifParser
from pymatgen.alchemy.transmuters import StandardTransmuter
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.serializers.json_coders import PMGJSONDecoder

import os
import json
import unittest

test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                        'test_files')


class ContainsSpecieFilterTest(unittest.TestCase):

    def test_filtering(self):
        coords = list()
        coords.append([0, 0, 0])
        coords.append([0.75, 0.75, 0.75])
        coords.append([0.5, 0.5, 0.5])
        coords.append([0.25, 0.25, 0.25])
        lattice = Lattice([[3.0, 0.0, 0.0],
                           [1.0, 3.0, 0.00],
                           [0.00, -2.0, 3.0]])
        s = Structure(lattice,
                      [{"Si4+": 0.5, "O2-": 0.25, "P5+": 0.25},
                       {"Si4+": 0.5, "O2-": 0.25, "P5+": 0.25},
                       {"Si4+": 0.5, "O2-": 0.25, "P5+": 0.25},
                       {"Si4+": 0.5, "O2-": 0.25, "P5+": 0.25}], coords)

        species1 = [Specie('Si', 5), Specie('Mg', 2)]
        f1 = ContainsSpecieFilter(species1, strict_compare=True, AND=False)
        self.assertFalse(f1.test(s), 'Incorrect filter')
        f2 = ContainsSpecieFilter(species1, strict_compare=False, AND=False)
        self.assertTrue(f2.test(s), 'Incorrect filter')
        species2 = [Specie('Si', 4), Specie('Mg', 2)]
        f3 = ContainsSpecieFilter(species2, strict_compare=True, AND=False)
        self.assertTrue(f3.test(s), 'Incorrect filter')
        f4 = ContainsSpecieFilter(species2, strict_compare=False, AND=False)
        self.assertTrue(f4.test(s), 'Incorrect filter')

        species3 = [Specie('Si', 5), Specie('O', -2)]
        f5 = ContainsSpecieFilter(species3, strict_compare=True, AND=True)
        self.assertFalse(f5.test(s), 'Incorrect filter')
        f6 = ContainsSpecieFilter(species3, strict_compare=False, AND=True)
        self.assertTrue(f6.test(s), 'Incorrect filter')
        species4 = [Specie('Si', 4), Specie('Mg', 2)]
        f7 = ContainsSpecieFilter(species4, strict_compare=True, AND=True)
        self.assertFalse(f7.test(s), 'Incorrect filter')
        f8 = ContainsSpecieFilter(species4, strict_compare=False, AND=True)
        self.assertFalse(f8.test(s), 'Incorrect filter')

    def test_to_from_dict(self):
        species1 = ['Si5+', 'Mg2+']
        f1 = ContainsSpecieFilter(species1, strict_compare=True, AND=False)
        d = f1.to_dict
        self.assertIsInstance(ContainsSpecieFilter.from_dict(d),
                              ContainsSpecieFilter)


class SpecieProximityFilterTest(unittest.TestCase):

    def test_filter(self):
        filename = os.path.join(test_dir, "Li10GeP2S12.cif")
        p = CifParser(filename)
        s = p.get_structures()[0]
        sf = SpecieProximityFilter({"Li": 1})
        self.assertTrue(sf.test(s))
        sf = SpecieProximityFilter({"Li": 2})
        self.assertFalse(sf.test(s))
        sf = SpecieProximityFilter({"P": 1})
        self.assertTrue(sf.test(s))
        sf = SpecieProximityFilter({"P": 5})
        self.assertFalse(sf.test(s))

    def test_to_from_dict(self):
        sf = SpecieProximityFilter({"Li": 1})
        d = sf.to_dict
        self.assertIsInstance(SpecieProximityFilter.from_dict(d),
                              SpecieProximityFilter)

class RemoveDuplicatesFilterTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(test_dir, "TiO2_entries.json"), 'r') as fp:
            entries = json.load(fp, cls=PMGJSONDecoder)
        self._struct_list = [e.structure for e in entries]
        self._sm = StructureMatcher()

    def test_filter(self):
        transmuter = StandardTransmuter.from_structures(self._struct_list)
        fil = RemoveDuplicatesFilter()
        transmuter.apply_filter(fil)
        out = self._sm.group_structures(transmuter.transformed_structures)
        self.assertEqual(self._sm.find_indexes(
            transmuter.transformed_structures, out),
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_to_from_dict(self):
        fil = RemoveDuplicatesFilter()
        d = fil.to_dict
        self.assertIsInstance(RemoveDuplicatesFilter().from_dict(d),
                              RemoveDuplicatesFilter)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
