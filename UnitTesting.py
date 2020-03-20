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
        self.assertCountEqual(['I9','I10', 'F1', 'I40'], obj.checkDatesAfterToday())

    def test_birth_after_marriage2(self): # tests US02: birth cannot occur after marriage
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2', 'I8'], obj.checkBirthAfterMarriage())

    def test_noMarriagesToChildren(self): # for when a parent is married to a child
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2'],obj.noMarriagesToChildren())

    def test_listMultipleBirths(self): # tests US32 for checking when someone in the same family is born on the same day
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I30', 'I31', 'I32', 'I33', 'I34', 'I35'],obj.listMultipleBirths())

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

    def test_marriage_before_death(self):
        '''US05 Unit Test: This is a test to see if the parser will catch instances of the death of an individual occuring before their marriage'''
        GEDCOM_file_errors = ["ERROR: FAMILY: US05: Married on 2023-04-08 which is after Lyanna /Stark/'s death on 2020-03-03", "ERROR: FAMILY: US05: Married on 0305-04-29 which is after Maggy /Tyrell/'s death on 0304-07-23"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)

    def test_divorce_before_death(self):
        '''US06 Unit Test: This is a test to see if the parser will catch instances of the death of an individual occuring before their divorce'''
        GEDCOM_file_errors = ["ERROR: FAMILY: US06: Divorced on 0325-09-06 which is after Olenna /Tyrell/'s death on 0324-08-08"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)

    def test_listRecentSurvivors(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I2', 'I1', 'I37', 'I39', 'I40', 'I41'], obj.listRecentSurvivors())

    def test_marriageAfter14(self): # tests US10: Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old) 
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F3', 'F4', 'F5', 'F6'], obj.marriageAfter14())

    def test_birthBeforeMarriage(self): # tests US08: Children should be born after marriage of parents (and not more than 9 months after their divorce)
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I38', 'I37', 'I1', 'I4', 'I5', 'I22', 'I20', 'I23', 'I9', 'I12', 'I15', 'I16', 'I17', 'I14', 'I21', 'I10', 'I11', 'I18', 'I2', 'I13', 'I19', 'I40'], obj.birthBeforeMarriageOfParents())

    def test_birthsLessThanFive(self): # tests US17: No more than five siblings should be born at the same time
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F2', 'F3', 'F3'],obj.birthsLessThanFive())
        
    def test_uniqueFirstNameInFamily(self): # tests US25: Unique first names in families
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I17', 'I18'],obj.uniqueFirstNameInFamily())

    def test_correctGenderForRole(self):
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I7', 'I39', 'I20', 'I24'], obj.correctGenderForRole())

    def test_maleLastNames(self): # tests US16: Males in family must have the same last name
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I1'],obj.maleLastNames())

    def test_siblingSpacing(self):  # tests US13: Siblings must be more than 8 months or less than a day apart
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I33', 'I36', 'I31', 'I34', 'I32', 'I35', 'I30', 'I17', 'I22', 'I21', 'I15', 'I18', 'I2', 'I10', 'I12', 'I11', 'I13'], obj.siblingSpacing())

    def test_illegitimateDates(self): # tests US42: Reject illegitimate dates
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["35 NOV 0290"], obj.getIllegitimateDates())

if __name__ == '__main__':
    unittest.main()