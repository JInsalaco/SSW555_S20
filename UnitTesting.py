import gedcom_parser
import unittest
import datetime

class TestUserStories(unittest.TestCase):
    def test_unittest(self): #this is a test unit test
        self.assertEqual('test'.upper(), 'TEST')

    def test_calculateAge1(self): # for testing an alive individual
        ind_alive = gedcom_parser.Individual(alive = True, birth = datetime.datetime(2017, 2, 25))
        self.assertEqual(ind_alive.calculateAge(), 3)

    def test_calculateAge2(self): # for testing a dead individual
        ind_alive = gedcom_parser.Individual(alive = False, birth = datetime.datetime(1960, 4, 1), death = datetime.datetime(2004, 2, 2))
        self.assertEqual(ind_alive.calculateAge(), 43)

    def test_fewerThan15Siblings1(self): # for when no family has greater than 15 children
        obj = gedcom_parser.Read_GEDCOM("AldenRadoncic-TargaryenFamily-Test2ForProject03.ged")
        self.assertEqual([], obj.fewerThan15Siblings())
    
    def test_fewerThan15Siblings1(self): # for when no family has greater than 15 children
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F3'], obj.fewerThan15Siblings())

    def test_noMarriagesToChildren(self): # for when a parent is married to a child
        obj = gedcom_parser.Read_GEDCOM("jackLiTest.ged")
        self.assertEqual(['I2', 'I3'],obj.noMarriagesToChildren())

    def test_listMultipleBirths(self): # for checking when someone is born on the same day
        obj = gedcom_parser.Read_GEDCOM("jackLiTest.ged")
        self.assertEqual(['I1', 'I11'],obj.listMultipleBirthds())


if __name__ == '__main__':
    unittest.main()