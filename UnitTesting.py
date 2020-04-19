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
        self.assertCountEqual(['I9','I10', 'F1', 'I40', 'F7', 'F8'], obj.checkDatesAfterToday())

    def test_birth_after_marriage2(self): # tests US02: birth cannot occur after marriage
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2', 'I8', 'I40'], obj.checkBirthAfterMarriage())

    def test_noMarriagesToChildren(self): # for when a parent is married to a child
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I2'],obj.noMarriagesToChildren())

    def test_listMultipleBirths(self): # tests US32 for checking when someone in the same family is born on the same day
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I30', 'I31', 'I32', 'I33', 'I34', 'I35'],obj.listMultipleBirths())

    def test_listRecentDeaths(self): # tests US36: ListRecentDeaths
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I3'], obj.listRecentDeaths())
    
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
        GEDCOM_file_errors = ["ERROR: FAMILY: US05: Married on 2023-04-08 which is after Lyanna /Stark/'s death on 2020-03-31", "ERROR: FAMILY: US05: Married on 0305-04-29 which is after Maggy /Tyrell/'s death on 0304-07-23"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)

    def test_divorce_before_death(self):
        '''US06 Unit Test: This is a test to see if the parser will catch instances of the death of an individual occuring before their divorce'''
        GEDCOM_file_errors = ["ERROR: FAMILY: US06: Divorced on 0325-09-06 which is after Olenna /Tyrell/'s death on 0324-08-08"]
        for error in GEDCOM_file_errors:
            self.assertIn(error, gedcom_parser.Read_GEDCOM('TargaryenFamily15Siblings.ged', False, False).user_story_errors)
    
    def test_less_than_150_years_old(self):
        '''US07 Unit Test: This is a test to see if the parser will catch instances of an individual living to be older than 150 years old.'''
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I1', 'I2', 'I3', 'I6', 'I10', 'I21', 'I22', 'I23', 'I24', 'I25', 'I26', 'I27', 'I28', 'I30', 'I31', 'I32', 'I33', 'I34', 'I35', 'I48'], obj.less_than_150_years_old())

    def test_listRecentSurvivors(self): # tests US15: There should be fewer than 15 siblings in a family
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I2', 'I1', 'I37'], obj.listRecentSurvivors())

    def test_marriageAfter14(self): # tests US10: Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old) 
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], obj.marriageAfter14())

    def test_birthBeforeMarriage(self): # tests US08: Children should be born after marriage of parents (and not more than 9 months after their divorce)
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I38', 'I37', 'I37', 'I1', 'I4', 'I5', 'I22', 'I20', 'I23', 'I9', 'I12', 'I15', 'I16', 'I17', 'I14', 'I21', 'I10', 'I11', 'I18', 'I2', 'I13', 'I19', 'I40', 'I46', 'I39'], obj.birthBeforeMarriageOfParents())

    def test_birthsLessThanFive(self): # tests US17: No more than five siblings should be born at the same time
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['F2', 'F3'],obj.birthsLessThanFive())
        
    def test_uniqueFirstNameInFamily(self): # tests US25: Unique first names in families
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I17', 'I18'],obj.uniqueFirstNameInFamily())
        
    def test_correspondingEntries(self): # tests US26's unittest: Corresponding Entries
       obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
       self.assertEqual(['I19', 'I23', 'I45', 'I48'], obj.correspondingEntries())
    
    def test_orderSiblingsByAge(self): # tests US 28: Order Children By Age
       obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
       self.assertEqual(['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'],obj.orderSiblingsByAge())

    def test_correctGenderForRole(self):
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I7', 'I39', 'I20', 'I24'], obj.correctGenderForRole())

    def test_maleLastNames(self): # tests US16: Males in family must have the same last name
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertEqual(['I1'],obj.maleLastNames())

    def test_siblingSpacing(self):  # tests US13: Siblings must be more than 8 months or less than a day apart
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I33', 'I36', 'I31', 'I34', 'I32', 'I35', 'I20', 'I46', 'I30', 'I17', 'I22', 'I21', 'I15', 'I18', 'I2', 'I10', 'I12', 'I11', 'I13'], obj.siblingSpacing())

    def test_illegitimateDates(self): # tests US42: Reject illegitimate dates
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["35 NOV 0290"], obj.getIllegitimateDates())

    def test_parentsNotTooOld(self): # tests US12: Parents not too old
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I2", "I2"], obj.parentsNotTooOld())

    def test_upcomingAnniversaries(self): # tests US39: List all upcoming wedding anniversaries
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["F5"], obj.upcomingAnniversaries())
    
    def test_recentBirths(self): # tests US35: List all recent births in last 30 days
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I44'], obj.recentBirths())

    def test_birthBeforeDeathOfParents(self): # tests US09: Children should be born before death of mother and before 9 months after the death of their father
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I25', 'I37', 'I31', 'I29', 'I33', 'I27', 'I30', 'I6', 'I36', 'I28', 'I35', 'I32', 'I45', 'I24', 'I34', 'I26', 'I46', 'I12', 'I9', 'I10', 'I20', 'I2', 'I23', 'I19', 'I11', 'I14', 'I13', 'I40', 'I39'], obj.birthBeforeDeathOfParents())
    
    def test_list_deceased(self): # tests US29: List all deceased individuals in a GEDCOM file
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15', 'I16', 'I17', 'I18', 'I19', 'I20', 'I29', 'I36', 'I38', 'I42', 'I43'], obj.list_deceased())

    def test_uniqueFamiliesBySpouses(self): # tests US24: 
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['F1', 'F7'], obj.uniqueFamiliesBySpouses())

    def test_listLargeAgeDifferences(self): # tests US34: 
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I2', 'I4', 'I7', 'I8', 'I6', 'I39', 'I24', 'I42', 'I35', 'I40'], obj.listLargeAgeDifferences())

    def test_listOrphans(self): # tests US33: List orphans
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I39", "I37"], obj.listOrphans())

    def test_uniqueIDs(self): # tests US22: Reject non-unique IDs
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I47", "I45"], obj.getNonUniqueIDsList())

    def test_listUpcomingBirthdays(self): # tests US38: List upcoming birthdays
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I1", "I2", "I48"], obj.listUpcomingBirthdays())

    def test_uniqueNameAndBirthDate(self): # tests US23: all individuals should have unique names and birthdates
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I18", "I48"], obj.uniqueNameAndBirthDate())

    def test_noBigamy(self): # tests US11: no Bigamy
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I2"], obj.noBigamy())

    def test_noSiblingMarriage(self):
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(["I7", "I8"], obj.noSiblingMarriage())
    
    def test_firstCousinsShouldNotMarry(self): #Tests US19: First cousins should not marry
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I40', 'I35'], obj.firstCousinsShouldNotMarry())
    
    def test_auntsAndUncles(self): #Tests US20: Aunts and Uncles should not marry nieces or nephews
        obj = gedcom_parser.Read_GEDCOM("TargaryenFamily15Siblings.ged")
        self.assertCountEqual(['I39', 'I6', 'I40', 'I35'], obj.auntsAndUncles())

if __name__ == '__main__':
    unittest.main()