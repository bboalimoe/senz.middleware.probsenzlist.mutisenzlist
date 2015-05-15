"""Unit test for prob2muti.py"""

__author__ = 'jiaying.lu'

import unittest
from numpy import log
from prob2muti import _probSenz_zip

class TestBasicMethods(unittest.TestCase):

    def test_probSenz_zip(self):
        # case 1
        probSenzList_elem = {
                             'motion': {'Running':1.29321983128e-78},
                             'location': {'school':3.14},
                             'sound': {'talk': 2.3324e-12},
                            }
        senzList_elem_candidate = [{'motion': 'Running', 'sound': 'talk', 'location': 'school', 'prob': -204.9844026873817}]
        self.assertEqual(senzList_elem_candidate, _probSenz_zip(probSenzList_elem, log(1e-90)))
        self.assertEqual([], _probSenz_zip(probSenzList_elem, log(1e-70)))


        # case 2
        probSenzList_elem = {
                             "motion": {
                                 "Riding": 9.94268884532027e-11,
                                 "Walking": 0.8979591835334749,
                                 "Running": 0.08163265323813619,
                                 "Driving": 0.02040816312895674,
                                 "Sitting": 7.69994010250898e-98
                             },
                             "location": {
                                 "restaurant": 0.213423,
                                 "resident": 0.235434542,
                             },
                             "sound": {
                                 "talk":0.234234523454,
                             }
                            }
        senzList_elem_candidate = [{'motion': 'Riding', 'sound': 'talk', 'location': 'resident', 'prob': -25.929353317267509}, {'motion': 'Riding', 'sound': 'talk', 'location': 'restaurant', 'prob': -26.027510126917882}, {'motion': 'Walking', 'sound': 'talk', 'location': 'resident', 'prob': -3.0053854503466702}, {'motion': 'Walking', 'sound': 'talk', 'location': 'restaurant', 'prob': -3.1035422599970444}, {'motion': 'Running', 'sound': 'talk', 'location': 'resident', 'prob': -5.4032807208219689}, {'motion': 'Running', 'sound': 'talk', 'location': 'restaurant', 'prob': -5.5014375304723435}, {'motion': 'Driving', 'sound': 'talk', 'location': 'resident', 'prob': -6.789575090790148}, {'motion': 'Driving', 'sound': 'talk', 'location': 'restaurant', 'prob': -6.8877319004405217}]
        self.assertEqual(senzList_elem_candidate, _probSenz_zip(probSenzList_elem, log(1e-30)))
        self.assertEqual([], _probSenz_zip(probSenzList_elem, 0))


if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)
