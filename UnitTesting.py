import gedcom_parser
import unittest
import datetime

class TestUserStories(unittest.TestCase):
    def test_unittest(self): #this is a test unit test
        self.assertEqual('test'.upper(), 'TEST')

    def test_calculateAge(self): # tests US27: include individual ages
        ind_alive = gedcom_parser.Individual(alive = True, birth = datetime.datetime(2017, 2, 25))
        self.assertEqual(ind_alive.calculateAge(), 3)

    def test_calculateAge2(self): # tests US27: include individual ages
        ind_alive = gedcom_parser.Individual(alive = False, birth = datetime.datetime(1960, 4, 1), death = datetime.datetime(2004, 2, 2))
        self.assertEqual(ind_alive.calculateAge(), 43)

    def test_fewerThan15Siblings(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("AldenRadoncic-TargaryenFamily-Test2ForProject03.ged")
        self.assertEqual([], obj.fewerThan15Siblings())
    
    def test_fewerThan15Siblings2(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F3'], obj.fewerThan15Siblings())

    def test_dates_after_today(self): # tests US01: dates cannot be in the future
        obj = gedcom_parser.Read_GEDCOM("SkywalkerFamilyErrors.ged")
        self.assertEqual(['I1', 'I4', 'F3'], obj.checkDatesAfterToday())

    def test_birth_after_marriage(self): # tests US02: birth cannot occur after marriage
        obj = gedcom_parser.Read_GEDCOM("SkywalkerFamilyErrors.ged")
        self.assertEqual(['I2', 'I3', 'I9'], obj.checkBirthAfterMarriage())

    def test_dates_after_today2(self): # tests US01: dates cannot be in the future
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I9','I10', 'F1'], obj.checkDatesAfterToday())

    def test_birth_after_marriage2(self): # tests US02: birth cannot occur after marriage
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2', 'I8'], obj.checkBirthAfterMarriage())

    def test_noMarriagesToChildren(self): # for when a parent is married to a child
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2'],obj.noMarriagesToChildren())

    def test_listMultipleBirths(self): # for checking when someone in the same family is born on the same day
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I27', 'I33'],obj.listMultipleBirths())

    def test_listRecentDeaths(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I3', 'I6', 'I20'], obj.listRecentDeaths())
    
    def test_birth_before_death(self):
        '''US03: Unit Test: This is a test to see if the parser will catch instances of a persons death occuring before their birth.'''
        GEDCOM_file_errors = ["ERROR: INDIVIDUAL: US03: Viserys /Targaryen/'s death occurs on 0298-10-19 which is before their birth on 2021-09-06"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)
    
    def test_divorce_before_marriage(self):
        '''US04 Unit Test: This is a test to see if the parser will catch instances of the divorce occuring before the marriage'''
        GEDCOM_file_errors = ["ERROR: FAMILY: US04: Aerys /Targaryen/ and Rhaella /Targaryen/ divorce occurs on 0260-06-01 which is before their marriage on 0260-06-06"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)

    def test_listRecentSurvivors(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I2', 'I1', 'I37', 'I39', 'I40', 'I41'], obj.listRecentSurvivors())


if __name__ == '__main__':
    unittest.main()