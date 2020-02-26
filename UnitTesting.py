import gedcom_parser
import unittest
import datetime

class TestUserStories(unittest.TestCase):
    def test_unittest(self): #this is a test unit test
        self.assertEqual('test'.upper(), 'TEST')

    def unit_calculateAge1(self): # for testing an alive individual
        ind_alive = gedcom_parser.Individual(alive = True, birth = datetime.datetime(2017, 2, 25))
        self.assertEqual(ind_alive.calculateAge(), 3)

if __name__ == '__main__':
    unittest.main()