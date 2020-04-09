'''The purpose of this file is to read and analyze a GEDCOM file. This program will save information about individuals and families in lists (or collections) so that they can be examined later. 
It can be assumed that the number of individuals in any file is always less than 5000, and the number of families is always less than 1000. 
After reading all of the data, the program will print the unique identifiers and names of each of the individuals in order by their unique identifiers in a pretty table. 
Then, for each family, print the unique identifiers and names of the husbands and wives, in order by unique family identifiers.'''

from prettytable import PrettyTable
from collections import defaultdict
import datetime
from dateutil.relativedelta import *
import sys

class Read_GEDCOM:
    '''This class will read and analyze the GEDCOM file so that it can sort the data into the Individual and Family classes.'''
    def __init__(self, path, ptables = True, print_all_errors = True):
        self.path = path
        self.family = dict() #The key is the FamID and the value is the instance for the Family class object for that specific FamID
        self.individuals = dict() #The key is the IndiID and the value is the instance for the Individual class object for that specific IndiID
        self.error_list = [] #This is a list of errors that will be evaluated for testing purposes
        self.family_ptable = PrettyTable(field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        self.individuals_ptable = PrettyTable(field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
        self.recentDeathTable = PrettyTable(field_names=["ID", "Name", "Death"])  # create a ptable for recent deaths
        self.recentSurvivorTable = PrettyTable(field_names=["Dead Relative ID", "Dead Relative Name", "Survivor ID", "Survivor Name", "Relation"])
        self.upcomingAnniversariesTable = PrettyTable(field_names=["Family ID", "Marriage Date", "Husband", "Wife"])
        self.orphansTable = PrettyTable(field_names=["Child ID", "Child Name", "Family ID"])
        self.recentBirthsTable = PrettyTable(field_names=["ID", "Name", "Birthday"])
        self.deceased_table = PrettyTable(field_names=["ID", "Name", "Death Day"])
        self.childrenInOrderTable = PrettyTable(field_names=["Family ID", "Children"])
        self.upcomingBirthdaysTable = PrettyTable(field_names=["ID", "Name", "Birthday"])
        self.illegitimateDatesList = []
        self.illegitimateDatesErrorList = []
        self.nonUniqueIDsList = []
        self.nonUniqueIDsErrors = []
        self.analyze_GEDCOM()
        if ptables: #Makes pretty tables for the data
            self.create_indi_ptable()
            self.create_fam_ptable()
        self.fewerThan15Siblings()
        self.checkDatesAfterToday()
        self.checkBirthAfterMarriage()
        self.noMarriagesToChildren()
        self.listMultipleBirths()
        self.listRecentSurvivors()
        self.marriageAfter14()
        self.birthBeforeMarriageOfParents()
        self.birthsLessThanFive()
        self.uniqueFirstNameInFamily()
        self.orderSiblingsByAge()
        self.correspondingEntries()
        self.correctGenderForRole()
        self.maleLastNames()
        self.siblingSpacing()
        self.uniqueFamiliesBySpouses()
        self.listLargeAgeDifferences()
        self.printIllegitimateDateErrors()
        self.parentsNotTooOld()
        self.upcomingAnniversaries()
        self.recentBirths()
        self.birthBeforeDeathOfParents()
        self.list_deceased()
        self.less_than_150_years_old()
        self.listUpcomingBirthdays()
        self.listOrphans()
        self.printNonUniqueIDsErrors()
        self.uniqueNameAndBirthDate()
        self.user_story_errors = UserStories(self.family, self.individuals, self.error_list, print_all_errors).add_errors #Checks for errors in user stories

    
    def analyze_GEDCOM(self):
        '''The purpose of this function is to read the GEDCOM file line by line and evaluate if a new instance of Family or Individual needs to be made. Each line is further evaluated using the parse_info function that is defined below.'''
        ind, fam, date_identifier_line, indiv_or_fam = "", "", [], "NA" #The lines are analyzed to see if they are for an individuals information or the family's information. Each line is marked accordingly and analyzed appropriately
        for tokens in self.file_reading_gen(self.path, sep = " "): #Goes line by line in the GEDCOM file and analyzes the tokens of each line

            if len(tokens) >= 2 and tokens[0] == '0' and tokens[1] in ["HEAD", "TRLR", "NOTE"]: #Skips the line if it is HEAD TRLR or NOTE because it does not need to be evaluated
                continue
            elif len(tokens) == 3 and tokens[0] == '0' and tokens[2] == "INDI":
                indiv_or_fam = "individual" #Marks the line as individual so that the parse_info function can identify it accordingly
                ind = tokens[1].replace("@", "") #The GEDCOM file has unnecessary @ symbols and this will get rid of them
                if self.checkUniqueID(ind, indiv_or_fam) ==  True: #Makes sure the ind ID is unique
                    self.individuals[ind] = Individual() #The instance of the Individual class object is created for this specific IndiID
                else:
                    indiv_or_fam = "NA" # alerts parser to not parse any more lines
                continue
            elif len(tokens) == 3 and tokens[0] == '0' and tokens[2] == "FAM":
                indiv_or_fam = "family" #Marks the line as family so that the parse_info function can identify it accordingly
                fam = tokens[1].replace("@", "")
                if self.checkUniqueID(fam, indiv_or_fam) == True: #Makes sure the fam ID is unique
                    self.family[fam] = Family() #The instance of the Family class object is created for this specific FamID
                else:
                    indiv_or_fam = "NA" # alerts parser to not parse any more lines
                continue
            if indiv_or_fam in ["family", "individual"]: #This will detect that no new individual or family was created but this line will still be parsed for specific information
                self.parse_info(tokens, date_identifier_line, ind, fam, indiv_or_fam)

            date_identifier_line = tokens #Each previous line will be saved to be used by the parse_info function to identify what kind of DATE the line is. Each DATE line in the GEDCOM file is preceded by a tag that identifies what kind of date it is
    
    def parse_info(self, tokens, date_identifier_line, ind, fam, indiv_or_fam):
        '''This will parse the information from each line that is sent from the analyze_GEDCOM function. The information will be stored in the appropriate place in the appropriate class.'''
        if len(tokens) == 2:
            return #A line of this length is not important to evaluate unless it is being evaluated to determine what the DATE is for
        else:
            level, tag, arguments = tokens
            if level == "1" and tag in ["NAME", "SEX", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL"]: #Makes sure that only valid lines are read in the GEDCOM file that correspond specifically for level 1 information with the indicated tags
                arguments = arguments.replace("@", "")
                if indiv_or_fam == "individual": #If the line was marked to correspond to an individual, then the line will be parsed and evaluated for the IndiID's name, sex, children, and the spouses will be added to a set to maintain uniqueness
                    if tag == "NAME":
                        self.individuals[ind].name = arguments
                    elif tag == "SEX":
                        self.individuals[ind].sex = arguments
                    elif tag == "FAMC":
                        self.individuals[ind].famc = arguments
                    elif tag == "FAMS":
                        self.individuals[ind].fams.add(arguments)
                elif indiv_or_fam == "family": #If the line was marked to correspond to a family, then the line will be parsed and evaluated for the FamID's husband ID, wife ID, and children added to a set for uniqueness
                    if tag == "HUSB":
                        self.family[fam].husband = arguments
                    elif tag == "WIFE":
                        self.family[fam].wife = arguments
                    elif tag == "CHIL":
                        self.family[fam].children.add(arguments)
            elif level == "2" and tag == "DATE" and date_identifier_line[1] in ["BIRT", "DEAT", "MARR", "DIV"]: #Makes sure that only valid lines are read in the GEDCOM file that correspond to level 2 information with the specific tag DATE. The date_identifier line should also be one of the indicated tags
                date_identifier_level, date_identifier_tag = date_identifier_line[0], date_identifier_line[1] #As previously mentioned, the date_identifier line will be divided into its level and tag to evaluate what the specific date corresponds to
                try:
                    arguments = datetime.datetime.strptime(arguments, "%d %b %Y").date() 
                except ValueError:
                    self.illegitimateDatesList.append(arguments)
                    illegitimateDate = arguments
                    arguments = "ILLEGITIMATE"
                if date_identifier_level == "1" and date_identifier_tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                    if indiv_or_fam == "individual": #Parses birthday and death day information for an individual
                        if date_identifier_tag == "BIRT":
                            if arguments == "ILLEGITIMATE":
                                error = f"ERROR: US42: Individual {ind} had an illegitimate birth date of {illegitimateDate}"
                                self.illegitimateDatesErrorList.append(error)
                            self.individuals[ind].birth = arguments
                        elif date_identifier_tag == "DEAT":
                            if arguments == "ILLEGITIMATE":
                                error = f"ERROR: US42: Individual {ind} had an illegitimate death date of {illegitimateDate}"
                                self.illegitimateDatesErrorList.append(error)
                            self.individuals[ind].death = arguments
                    elif indiv_or_fam == "family": #Parses marriage date and divorce date information for a family
                        if date_identifier_tag == "MARR":
                            if arguments == "ILLEGITIMATE":
                                error = f"ERROR: US42: Family {fam} had an illegitimate marriage date of {illegitimateDate}"
                                self.illegitimateDatesErrorList.append(error)
                            self.family[fam].marriage = arguments
                        elif date_identifier_tag == "DIV":
                            if arguments == "ILLEGITIMATE":
                                error = f"ERROR: US42: Family {fam} had an illegitimate divorce date of {illegitimateDate}"
                                self.illegitimateDatesErrorList.append(error)
                            self.family[fam].divorce = arguments

    #Function for US01's unittest: Returns a list of id's (ind or fam) that
    #have dates after the current date
    def checkDatesAfterToday(self):
        with open("Sprintoutput.txt", "a") as f:
            currentDate  = datetime.date.today()
            idList = []
            for ind in self.individuals:
                if self.individuals[ind].birth != "ILLEGITIMATE" and  self.individuals[ind].birth > currentDate:
                    print(f"ERROR: INDIVIDUAL: {ind} US01: Birthday {self.individuals[ind].birth} occurs in the future", file=f)
                    idList.append(ind)
                if self.individuals[ind].death != None and self.individuals[ind].death != "ILLEGITIMATE" and self.individuals[ind].death > currentDate:
                    print(f"ERROR: INDIVIDUAL: {ind} US01: Death {self.individuals[ind].death} occurs in the future", file=f)
                    idList.append(ind)
            for fam in self.family:
                if self.family[fam].marriage != "ILLEGITIMATE" and self.family[fam].marriage > currentDate:
                    print(f"ERROR: FAMILY: {fam} US01: Marriage {self.family[fam].marriage} occurs in the future", file=f)
                    idList.append(fam)
                if self.family[fam].divorce != "NA" and self.family[fam].divorce != "ILLEGITIMATE" and self.family[fam].divorce > currentDate:
                    print(f"ERROR: FAMILY: {fam} US01: Divorce {self.family[fam].divorce} occurs in the future", file=f)
                    idList.append(fam)
        return idList

    #Function for US36's unittest: Returns a list of id's that have death dates within the past 30 days.
    def listRecentDeaths(self):
        ''' Lists the individuals with death dates within the past 30 days of today's date'''
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            today = datetime.date.today()
            dateFrom30DaysAgo = datetime.date.today() - datetime.timedelta(30)
            for ind in self.individuals:
                if self.individuals[ind].death is not None and self.individuals[ind].death != "ILLEGITIMATE" and self.individuals[ind].death >= dateFrom30DaysAgo and self.individuals[ind].death < today:
                    self.recentDeathTable.add_row([ind, self.individuals[ind].name, self.individuals[ind].death])
                    idList.append(ind)
            print("LIST: US36: Recent Deaths:", file=f)
            print(self.recentDeathTable, file=f)
            return idList

    #Function for US02's unittest: Returns a list of individual id's that
    #have birth dates after their marriage dates
    def checkBirthAfterMarriage(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            for ind in self.individuals:
                birthDate = self.individuals[ind].birth
                famSet = self.individuals[ind].fams
                if famSet != "NA":
                    for fam in famSet:
                        marriageDate = self.family[fam].marriage
                        if birthDate != "ILLEGITIMATE" and marriageDate != "ILLEGITIMATE" and birthDate > marriageDate:
                            if self.individuals[ind].sex == "M":
                                sex = "Husband's"
                            else:
                                sex = "Wife's"
                            print(f"ERROR: FAMILY: {fam} US02: {sex} ({ind}) birthday {birthDate} occurs after marriage {marriageDate}", file=f)
                            idList.append(ind)
        return idList
    
    #Function for US17's unittest. No Marrriage to Children. Returns an error if in the family,
    #the husband id or wife id is also in the children's list.
    def noMarriagesToChildren(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for ind in self.individuals:
                famSet = self.individuals[ind].fams
                if famSet != "NA":
                    for fam in famSet:
                        childrenSet = self.family[fam].children
                        for child in childrenSet:
                            if self.individuals[ind].sex == "M" and child == self.family[fam].wife:
                                print(f"ERROR: INDIVIDUAL: {ind}. US17: No Marriage to Children; {self.individuals[ind].name} has a wife: {self.family[fam].wife} who is also a child: {self.family[fam].wife}", file=f)
                                idList.append(ind)
                            elif self.individuals[ind].sex == "F" and child == self.family[fam].husband:
                                print(f"ERROR: INDIVIDUAL: {ind}. US17: No Marriage to Children; {self.individuals[ind].name} has a husband: {self.family[fam].husband} who is also a child: {self.family[fam].husband}", file=f)
                                idList.append(ind)
        return idList
    
    #Function for US32's unittest. List all multiple births in a GEDCOM file.
    #Finding twins, triplets, etc.
    def listMultipleBirths(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for ind in self.individuals:
                for ind2 in self.individuals:
                    if self.individuals[ind].famc == self.individuals[ind2].famc and self.individuals[ind].name != self.individuals[ind2].name:
                        if self.individuals[ind].birth != "ILLEGITIMATE" and self.individuals[ind2].birth != "ILLEGITIMATE" and self.individuals[ind].birth == self.individuals[ind2].birth:
                            print(f"ERROR: INDIVIDUALS: {ind} and {ind2}. US32: List all multiple Births; {self.individuals[ind].name} has the same birthday as: {self.individuals[ind2].name}", file=f)
                            if (ind in idList):
                                continue
                            else:
                                idList.append(ind)
        return idList
    
    #Function for US14's unittest. No more than five siblings should be born at the same time
    def birthsLessThanFive(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for ind in self.individuals:
                famSet = self.individuals[ind].fams
                if famSet != "NA":
                    for fam in famSet:
                        birthday_list = list()
                        childrenSet = self.family[fam].children
                        for child in childrenSet:
                            if self.individuals[ind].birth != "ILLEGITIMATE":
                                birthday_list.append(self.individuals[ind].birth)
                        count_dict = dict((i, birthday_list.count(i)) for i in birthday_list)
                        list_birthdays = count_dict.values()
                        if len(list_birthdays) == 0 or max(list_birthdays) <= 5:
                            continue
                        else:
                            print(f"ERROR: FAMILY: {fam}. US14: Number of children born in a single birth should not be greater than 5", file=f)
                            idList.append(fam)
        return idList

    #Function for US25's unittest. Unique first names in families
    def uniqueFirstNameInFamily(self):
        idList = []
        with open("SprintOutput.txt", "a") as f:
            for ind in self.individuals:
                for ind2 in self.individuals:
                    if ind != ind2:
                        if self.individuals[ind].name == self.individuals[ind2].name:
                            if self.individuals[ind].birth != "ILLEGITIMATE" and self.individuals[ind2].birth != "ILLEGITIMATE":
                                if self.individuals[ind].birth == self.individuals[ind2].birth and self.individuals[ind].famc == self.individuals[ind2].famc:
                                    print(f"ERROR: INDIVIDUALS: {ind} and {ind2}. US25: No more than one child with the same name and birth date should appear in a family", file=f)
                                    idList.append(ind)
        return idList

    # Function for US15's unittest. No more than five siblings should be born at the same time
    def fewerThan15Siblings(self):
        '''
        Loops through all families in the output and checks if each family has less than 15 siblings.
        If a family has greater than 15 siblings, an error is thrown.
        '''
        idList = []
        with open("Sprintoutput.txt", "a") as f:
            for fam in self.family:
                if len(self.family[fam].children) >= 15:
                    idList.append(fam)
                    print(f"WARNING: FAMILY: US15: {fam}: More than 15 siblings are in this family", file = f)
        return idList

     #Function for US26's unittest: All family roles (spouse, child) specified in an individual record should have
    #corresponding entries in the corresponding family records. Likewise, all individual roles (spouse, child)
    # specified in family records should have corresponding entries in the corresponding  individual's records.
    # I.e. the information in the individual and family records should be consistent.
    def correspondingEntries(self):
        idList = []
        with open("Sprintoutput.txt", "a") as f:
            for ind in self.individuals:
                if self.individuals[ind].famc == "NA" and self.individuals[ind].fams == "NA":
                    continue
                else:
                    # Checks if individual has a spouse and corresponding entree
                    if self.individuals[ind].fams != "NA":
                        fam = self.individuals[ind].fams
                        for fa in fam:
                            if ind != self.family[fa].husband and ind != self.family[fa].wife:
                                print(f"WARNING: INDIVIDUAL: US26: {ind}: does not have corresponding entree as a spouse in family {fa}", file = f)
                                idList.append(ind)
                    # Checks if individual has a child and corresponding entree
                    if self.individuals[ind].famc != "NA":
                        fam = self.individuals[ind].famc
                        if ind not in self.family[fam].children:
                            print(f"WARNING: INDIVIDUAL: US26: {ind}: does not have corresponding entree as a child in family {fam}", file = f)
                            idList.append(ind)
        return idList      

    # Function for US28: List siblings in families by decreasing age, i.e. oldest siblings first
    def orderSiblingsByAge(self):
        idList = []
        with open("Sprintoutput.txt", "a") as f:
            for fam in self.family:
                if(self.family[fam].children != 'NA' and len(self.family[fam].children) > 1):
                    chil = dict()
                    for c in self.family[fam].children:
                        age = self.individuals[c].age
                        chil[c] = age
                    sortedChil = sorted(chil.items(), key=lambda item: item[1], reverse = True)
                    self.childrenInOrderTable.add_row([fam, sortedChil])
                idList.append(fam)
            print("LIST: US28: Order Siblings by Age:", file=f)
            print(self.childrenInOrderTable, file=f)
        return idList

    # Function for US21's unittest. Husbands must be males and wives must be females.
    def correctGenderForRole(self):
        with open("Sprintoutput.txt", "a") as f:
            indIDList = [] #return id's of individuals who do not have the correct role gender
            individualsDict = self.individuals
            familyDict = self.family
            for famID in familyDict:
                husbandID = familyDict[famID].husband
                wifeID = familyDict[famID].wife
                if individualsDict[husbandID].sex != "M":
                    print(f"ERROR: FAMILY: {famID} US21: Husband ({husbandID}) does not have the correct gender for role", file=f)
                    indIDList.append(husbandID)
                elif individualsDict[wifeID].sex != "F":
                    print(f"ERROR: FAMILY: {famID} US21: Wife ({wifeID}) does not have the correct gender for role", file=f)
                    indIDList.append(wifeID)
        return indIDList

    #function for US16's unittest. Males in the same family should have the same last name.
    def maleLastNames(self):  # us16
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for fam in self.family:
                family = self.family[fam]
                father_name = self.individuals[family.husband].name.split('/')
                for child in family.children:
                    if self.individuals[child].sex == "M":
                        child_name = self.individuals[child].name.split('/')
                        if child_name[1] != father_name[1]:
                            idList.append(child)
                            print(f"WARNING: US16: {self.individuals[family.husband].name} and {self.individuals[child].name} have different last names.",file=f)
            return idList

    #Function for US13's unittest. Birth dates of siblings should be more than 8 months apart or less than 2 days apart
    def siblingSpacing(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for fam in self.family:
                family = self.family[fam]
                for child in family.children:
                    currBirthday = self.individuals[child].birth #first child's birthday
                    for children in family.children:
                        sibBirthday = self.individuals[children].birth #one siblings birthday
                        if currBirthday != "ILLEGITIMATE" and sibBirthday != "ILLEGITIMATE":
                            diff = abs(currBirthday - sibBirthday)
                        if(diff > datetime.timedelta(days=2) and diff < datetime.timedelta(days=243)):
                            idList.append(child)
                            idList.append(children)
                            print(f"ERROR: US13: {self.individuals[child].name } and {self.individuals[children].name} have birthdays too close together", file=f)
            idList = list(dict.fromkeys(idList))
            return idList

    # Function for US24. No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    def uniqueFamiliesBySpouses(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for fam in self.family:
                family = self.family[fam]
                h_name = self.individuals[family.husband].name
                w_name = self.individuals[family.wife].name
                marriage_date = family.marriage
                for famo in self.family:
                    if(fam != famo and self.individuals[self.family[famo].husband].name == h_name and self.individuals[self.family[famo].wife].name == w_name and self.family[famo].marriage == marriage_date):
                        print(f"ERROR: US 24: {fam} and {famo} is an identical families", file=f)
                        idList.append(fam)
            return idList

    # Function for US34. List all couples who were married when the older spouse was more than twice as old as the younger spouse.
    def listLargeAgeDifferences(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for fam in self.family:
                family = self.family[fam]
                years_married = datetime.date.today().year - family.marriage.year
                if years_married >= 0 and self.individuals[family.wife].age != "NA" and self.individuals[family.husband].age != "NA":
                    husband_married_age = int(self.individuals[family.husband].age) - years_married
                    wife_married_age = int(self.individuals[family.wife].age) - years_married
                    if husband_married_age > 2*wife_married_age or wife_married_age > 2*husband_married_age:
                        idList.append(family.husband)
                        idList.append(family.wife)
                        print(f"ERROR: US34: {family.husband} and {family.wife} have a large age difference", file=f)
            return idList

    # Function for US42's unittest. Return the list of illegitimate dates that were accumulated
    # throughout the parser.
    def getIllegitimateDates(self):
        return self.illegitimateDatesList

    def printIllegitimateDateErrors(self):
        with open("Sprintoutput.txt", "a") as f:
            for error in self.illegitimateDatesErrorList:
                print(error, file=f)

    # Function for US12's unittest: Mother should be less than 60 years older than her children 
    # and father should be less than 80 years older than his children.
    def parentsNotTooOld(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            families = self.family
            individuals = self.individuals
            for famID in families:
                motherAge = individuals[families[famID].wife].age
                fatherAge = individuals[families[famID].husband].age
                for childID in families[famID].children:
                    if individuals[childID].alive != False and motherAge != "NA" and individuals[childID].age != "NA" and int(motherAge) - int(individuals[childID].age) >= 60 and individuals[families[famID].wife].alive != False:
                        print(f"WARNING: US12: In family {famID}, Mother {families[famID].wife} is 60 or more years older than child {childID}", file=f)
                        idList.append(families[famID].wife)
                    if individuals[childID].alive != False and fatherAge != "NA" and individuals[childID].age != "NA" and int(fatherAge) - int(individuals[childID].age) >= 80 and individuals[families[famID].husband].alive != False:
                        print(f"WARNING: US12: In family {famID}, Father {families[famID].husband} is 80 or more years older than child {childID}", file=f)
                        idList.append(families[famID].husband)
        return idList

    # Function for US39's unittest: List all living couples in a GEDCOM file whose 
    # marriage anniversaries occur in the next 30 days.
    def upcomingAnniversaries(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            todaysDate = datetime.date.today()
            dateIn30Days = datetime.date.today() + datetime.timedelta(30)
            for famID in self.family:
                if self.individuals[self.family[famID].husband].death != "ILLEGITIMATE" and self.individuals[self.family[famID].wife].death != "ILLEGITIMATE":
                    if self.family[famID].marriage < todaysDate:
                        updatedMarriageDate = (self.family[famID].marriage).replace(year=todaysDate.year)
                        if (updatedMarriageDate + datetime.timedelta(30)) >= dateIn30Days:
                            if updatedMarriageDate <= dateIn30Days:
                                self.upcomingAnniversariesTable.add_row([famID, self.family[famID].marriage, self.family[famID].husband, self.family[famID].wife])
                                idList.append(famID)
            print("LIST: US39: Upcoming Anniversaries:", file=f)
            print(self.upcomingAnniversariesTable, file=f)
        return idList

    # Function for US33's unittest: List all orphaned children (both parents dead 
    # and child < 18 years old) in a GEDCOM file
    def listOrphans(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            for famID, fam in self.family.items():
                if self.individuals[fam.husband].alive == False and self.individuals[fam.wife].alive == False:
                    for childID in fam.children:
                        if self.individuals[childID].age < 18 and self.individuals[childID].age > 0 and self.individuals[childID].alive == True:
                            self.orphansTable.add_row([childID, self.individuals[childID].name, famID])
                            idList.append(childID)
            print("LIST: US33: Orphaned Children:", file=f)
            print(self.orphansTable, file=f)
        return idList

    # Function for US22's unittest. Returns the list of non-unique ID's
    def getNonUniqueIDsList(self):
        return self.nonUniqueIDsList

    # Prints non-unique error messages to the output file
    def printNonUniqueIDsErrors(self):
        with open("Sprintoutput.txt", "a") as f:
            for error in self.nonUniqueIDsErrors:
                print(error, file=f)

    # Function for US22: All individual IDs should be unique 
    # and all family IDs should be unique. This function gets called in 
    # the parser to detect repeated IDs.
    def checkUniqueID(self, id, indiv_or_fam):
        with open("Sprintoutput.txt", "a") as f:
            isUnique = True
            if indiv_or_fam == "individual":
                if id in list(self.individuals.keys()):
                    self.nonUniqueIDsList.append(id)
                    error = f"ERROR: US22: Individual {id} from the GEDCOM file was not added to the individuals table because {id} is not a unique id"
                    self.nonUniqueIDsErrors.append(error)
                    isUnique = False
            elif indiv_or_fam == "family":
                if id in list(self.family.keys()):
                    self.nonUniqueIDsList.append(id)
                    error = f"ERROR: US22: Family {id} was not added to the families table because {id} is not a unique id"
                    self.nonUniqueIDsErrors.append(error)
                    isUnique = False
        return isUnique

    # Function for US35's unittest: List all people in a GEDCOM file who were born in the last 30 days
    def recentBirths(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            today = datetime.date.today()
            dateFrom30DaysAgo = today - relativedelta(months=1)
            for indID in self.individuals:
                if self.individuals[indID].birth != "ILLEGITIMATE":
                    if self.individuals[indID].birth > dateFrom30DaysAgo and self.individuals[indID].birth < today:
                        self.recentBirthsTable.add_row([indID, self.individuals[indID].name, self.individuals[indID].birth])
                        idList.append(indID)
            print("LIST: US35: Recent Births:", file = f)
            print(self.recentBirthsTable, file = f)
            return idList

    # Function for US09's unittest: Child should be born before death of mother and before 9 months after death of father
    def birthBeforeDeathOfParents(self):
        with open("Sprintoutput.txt", "a") as f:
            idList = []
            for famID in self.family:
                fam = self.family[famID]
                mother_death = self.individuals[fam.wife].death if self.individuals[fam.wife].death != None else "NA"
                father_death = self.individuals[fam.husband].death if self.individuals[fam.husband].death != None else "NA"
                father_death_after_9_months = father_death + relativedelta(months=9) if father_death != "NA" else "NA"
                for childID in fam.children:
                    child_bday = self.individuals[childID].birth
                    if mother_death != "NA" and child_bday > mother_death or father_death_after_9_months != "NA" and child_bday > father_death_after_9_months:
                        print(f"ERROR: US09: FAMILY: Child {childID} of Family {famID} is not born before death of their mother or before 9 months after the death of their father.", file = f)
                        idList.append(childID)
            return idList

    def file_reading_gen(self, path, sep = "\t"):
        '''This is a file reading generator that reads the GEDCOM function line by line. The function will first check for bad inputs and raise an error if it detects any.'''
        try: #This tries to open the file and returns an error if it can not open the file. The code continues if opening the file is successful
            fp = open(path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"Can't open {path}!")
        else:
            with fp:
                for line in fp:
                    separate_line = line.strip().split(sep, 2) #Each line is stripped and seperated by the indicated seperator which in this case is a space. Each seperate line is yielded on each call to next()
                    yield separate_line

    def create_indi_ptable(self):
        '''This creates a Pretty Table that is an Individual summary of each individuals ID, Name, Gender, Birthday, Age, whether they are alive or not, death date, children, and spouses.'''
        print("Individual Table")
        for ID, individual in self.individuals.items():
            individual.check_alive() #Calls this specific function to acquire whether the person is alive or not and what their age is.
            if individual.fams == set(): #This just makes the table look cleaner by replacing empty sets with NA
                individual.fams = "NA"
            self.individuals_ptable.add_row([ID, individual.name, individual.sex, individual.birth, individual.age, individual.alive, individual.death, individual.famc, individual.fams])
        print(self.individuals_ptable)
        #write individuals table to output file
        with open("Sprintoutput.txt", "w") as f:
            print("Individuals", file=f)
            print(self.individuals_ptable, file=f)

    # US10 implemented by Alden Radoncic
    def marriageAfter14(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for famID, fam in self.family.items():
                if fam.marriage != "ILLEGITIMATE":
                    if self.individuals[fam.husband].calculateAge2(fam.marriage) < 14 or self.individuals[fam.wife].calculateAge2(fam.marriage) < 14:
                        idList.append(famID)
                        print(f"WARNING: FAMILY: US10: {famID}: One or both spouses were less than 14 years old at the time of marriage.", file = f)
            return idList

    def birthBeforeMarriageOfParents(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for famID, fam in self.family.items():
                dateOf9MonthsAfterDivorce = fam.divorce + relativedelta(months=9) if fam.divorce != "NA" and fam.divorce != "ILLEGITIMATE" else "NA"
                for child in fam.children:
                    childBirth = self.individuals[child].birth
                    if childBirth != "ILLEGITIMATE" and fam.marriage != "ILLEGITIMATE":
                        if childBirth < fam.marriage or dateOf9MonthsAfterDivorce != "NA" and childBirth > dateOf9MonthsAfterDivorce:
                            idList.append(child)
                            print(f"WARNING: FAMILY: US08: {famID}: Child {child} is born before the marriage of their parents (or born 9 months after their family's divorce).", file = f)
            return idList
             
    def listRecentSurvivors(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            individualDeaths = self.listRecentDeaths()
            for ind in individualDeaths:
                individual = self.individuals[ind]
                individualFamilies = individual.fams
                if individualFamilies != "NA":
                    for fam in individualFamilies:
                        family = self.family[fam]
                        if individual.sex == "M" and self.individuals[family.wife].death is None:
                            idList.append(family.wife)
                            self.recentSurvivorTable.add_row([ind, individual.name, family.wife, self.individuals[family.wife].name, "Spouse"])
                        elif individual.sex == "F" and self.individuals[family.husband].death is None:
                            idList.append(family.husband)
                            self.recentSurvivorTable.add_row([ind, individual.name, family.husband, self.individuals[family.husband].name, "Spouse"])
                        for child in family.children:
                            if self.individuals[child].death is None:
                                idList.append(child)
                                self.recentSurvivorTable.add_row([ind, individual.name, child, self.individuals[child].name, "Child"])
            print("LIST: US37: Recent Survivors:", file=f)
            print(self.recentSurvivorTable, file = f)
            return idList

    def less_than_150_years_old(self):
        ''' US07 Death should be less than 150 years after birth for dead people, and current date should be less than 150 years after birth for all living people'''
        with open("SprintOutput.txt", "a") as f:
            idList = [] #Stores the ID of the people who are older than 150 years old in a list for testing purposes
            for indID in self.individuals:
                if self.individuals[indID].age == "NA": #Skips the person if they apparantly do not have an age attributed to them
                    pass
                elif self.individuals[indID].age >= 150:
                    idList.append(indID)
                    print(f"ERROR: INDIVIDUAL: US07 {self.individuals[indID].name} age is {self.individuals[indID].age} which is older than 150 years old.", file=f)
            return idList
    
    def list_deceased(self):
        '''US29: List all deceased individuals in a GEDCOM file'''
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for indID in self.individuals:
                if self.individuals[indID].death != None:
                    idList.append(indID)
                    self.deceased_table.add_row([indID, self.individuals[indID].name, self.individuals[indID].death])
            print("LIST: US29: List Deceased: ", file = f) #Creates and adds individuals who have died to a new pretty table
            print(self.deceased_table, file = f)
            return idList

    def listUpcomingBirthdays(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            for indID in self.individuals:
                if self.individuals[indID].alive:
                    curr_bday = self.individuals[indID].birth
                    today = datetime.date.today()
                    date_30days_from_today = today + relativedelta(days=30)
                    if curr_bday != "ILLEGITIMATE" and (today.month, today.day) < (curr_bday.month, curr_bday.day) <= (date_30days_from_today.month, date_30days_from_today.day):
                        idList.append(indID)
                        self.upcomingBirthdaysTable.add_row([indID, self.individuals[indID].name, self.individuals[indID].birth])
            print(f"LIST: US38: Upcoming Birthdays:", file=f)
            print(self.upcomingBirthdaysTable, file=f)
            return idList

    def uniqueNameAndBirthDate(self):
        with open("SprintOutput.txt", "a") as f:
            idList = []
            uniqueInds = set()
            for indID in self.individuals:
                ind = (self.individuals[indID].name, self.individuals[indID].birth)
                if ind in uniqueInds:
                    print(f"ERROR: INDIVIDUAL: US23: {indID}: Individual {indID} has the same name and birth date as an earlier (lower ID numbered) individual", file=f)
                    idList.append(indID)
                else:
                    uniqueInds.add(ind)
            return idList

    def create_fam_ptable(self):
        '''This creates a Pretty Table that is a Family summary of each family's ID, when they were married, when they got divorced, the Husband ID, the Husband Name, the Wife ID, the Wife Name, and their children.'''
        print("Family Table")
        for ID, fam in self.family.items():
            self.family_ptable.add_row([ID, fam.marriage, fam.divorce, fam.husband, self.individuals[fam.husband].name, fam.wife, self.individuals[fam.wife].name, fam.children])   
        print(self.family_ptable)
        #append families table to output file
        with open("Sprintoutput.txt", "a") as f:
            print("Families", file=f)
            print(self.family_ptable, file=f)

class Individual:
    '''This class will hold all the information for each individual according to their IndiID. This includes their name, sex, birthday, age, whether they are alive, death date, and their children and spouses.'''
    def __init__(self, name = "NA", sex = "NA", birth = None, age = "NA", alive = True, death = None, famc = "NA"):
        self.name = name
        self.sex = sex
        self.birth = birth
        self.age = age
        self.alive = alive 
        self.death = death
        self.famc = famc
        self.fams = set()

    def check_alive(self):
        '''The purpose of this function is to check whether a person is alive or not and sets the individuals age based on calling the calculateAge function'''
        self.alive = (self.death == None) #Returns true if self.death == None because that means the person is not dead.
        if self.birth == "ILLEGITIMATE":
            self.alive = False
        try:
            self.calculateAge()
        except:
            raise ValueError("The birth or death records appear to be messed up! Check them for errors!")
    
    # Function for US25's unittest. Include person's current age when listing individuals
    def calculateAge(self, customDate = "NA"):
        '''Calculates the age of an individual'''
        if (customDate != "NA"):
            lastDate = customDate
        elif (self.alive): # Check if alive to see whether to use today's date or death date for age calculation
            lastDate = datetime.datetime.today()
        else:
            lastDate = self.death

        if lastDate != "ILLEGITIMATE" and self.birth != "ILLEGITIMATE":
            self.age = lastDate.year - self.birth.year - int((lastDate.month, lastDate.day) < (self.birth.month, self.birth.day)) # Tuple comparison to check if today's date is before or after current/death date
        else:
            self.age = "NA"
        return self.age

    # Function to calculate age without updating an individual's age
    def calculateAge2(self, customDate = "NA"):
        '''Calculates the age of an individual'''
        if (customDate != "NA"):
            lastDate = customDate
        elif (self.alive): # Check if alive to see whether to use today's date or death date for age calculation
            lastDate = datetime.datetime.today()
        else:
            lastDate = self.death

        if lastDate != "ILLEGITIMATE" and self.birth != "ILLEGITIMATE":
            age = lastDate.year - self.birth.year - int((lastDate.month, lastDate.day) < (self.birth.month, self.birth.day)) # Tuple comparison to check if today's date is before or after current/death date
        else:
            age = "NA"
        return age

class Family:
    '''This class will hold all of the information for each family according to their FamID. This includes the marriage date, divorce date, husband ID, wife ID, and a set of the children.'''
    def __init__(self):
        self.marriage = "NA"
        self.divorce = "NA"
        self.husband = "NA"
        self.wife = "NA"
        self.children = set()

class UserStories:
    '''This class is meant to store functions for testing errors in user stories'''
    def __init__(self, family_dict, individual_dict, error_list, print_all_errors):
        self.family = family_dict
        self.individuals = individual_dict
        self.add_errors = error_list
        self.birth_before_death()
        self.marriage_before_divorce()
        self.marriage_before_death()
        self.divorce_before_death()

        if print_all_errors == True:
            self.print_user_story_errors()


    def birth_before_death(self):
        '''US03 Birth Before Death: Birth should occur before death of an individual'''
        for individual in self.individuals.values():
            if individual.death != None and individual.death != "ILLEGITIMATE" and individual.birth != "ILLEGITIMATE" and (individual.death - individual.birth).days < 0:
                self.add_errors += [f"ERROR: INDIVIDUAL: US03: {individual.name}'s death occurs on {individual.death} which is before their birth on {individual.birth}"]
    
    def marriage_before_divorce(self):
        '''US04 Marriage Before Divorce: Marriage should occur before divorce of spouses, and divorce can only occur after marriage'''
        for families in self.family.values():
            if families.divorce != "NA" and families.divorce != "ILLEGITIMATE" and families.marriage != "ILLEGITIMATE" and (families.divorce - families.marriage).days < 0:
                self.add_errors += [f"ERROR: FAMILY: US04: {self.individuals[families.husband].name} and {self.individuals[families.wife].name} divorce occurs on {families.divorce} which is before their marriage on {families.marriage}"]
    
    def marriage_before_death(self):
        '''US05 Marriage should occur before death of either spouse'''
        for families in self.family.values():
            husband_death = self.individuals[families.husband].death
            wife_death = self.individuals[families.wife].death
            marriage_date = families.marriage
            if husband_death == None and wife_death == None: #If the wife and husband are still alive there is no further analysis needed
                break
            if husband_death != None: #Checks if the husband was dead before he and wife married and then checks if wife was dead before she and husband married
                if wife_death != None:
                    if wife_death != "ILLEGITIMATE" and marriage_date != "ILLEGITIMATE" and (wife_death - marriage_date).days < 0:
                        self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.wife].name}'s death on {wife_death}"]                        
                    elif husband_death != "ILLEGITIMATE" and marriage_date != "ILLEGITIMATE" and (husband_death - marriage_date).days < 0:
                        self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
                else:
                    if husband_death != "ILLEGITIMATE" and marriage_date != "ILLEGITIMATE" and (husband_death - marriage_date).days < 0:
                        self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
            else:
                if wife_death != "ILLEGITIMATE" and marriage_date != "ILLEGITIMATE" and (wife_death - marriage_date).days < 0:
                    self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.wife].name}'s death on {wife_death}"]
              
    def divorce_before_death(self):
        '''US06 Divorce can only occur before death of both spouses'''
        for families in self.family.values():
            husband_death = self.individuals[families.husband].death
            wife_death = self.individuals[families.wife].death
            divorce_date = families.divorce
            if husband_death == None and wife_death == None: #If the wife and husband are still alive there is no further analysis needed
                break
            elif divorce_date != "NA": #Checks if the husband was dead before he and wife divorced and then checks if wife was dead before she and husband divorced
                if husband_death != None:
                    if wife_death != None:
                        if wife_death != "ILLEGITIMATE" and divorce_date != "ILLEGITIMATE" and (wife_death - divorce_date).days < 0:
                            self.add_errors += [f"ERROR: FAMILY: US06: Divorced on {divorce_date} which is after {self.individuals[families.wife].name}'s death on {wife_death}"]
                        elif husband_death != "ILLEGITIMATE" and divorce_date != "ILLEGITIMATE" and (husband_death - divorce_date).days < 0:
                            self.add_errors += [f"ERROR: FAMILY: US06: Divorced on {divorce_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
                    else:
                        if husband_death != "ILLEGITIMATE" and divorce_date != "ILLEGITIMATE" and (husband_death - divorce_date).days < 0:
                            self.add_errors += [f"ERROR: FAMILY: US06: Divorced on {divorce_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
                else:
                    if wife_death != "ILLEGITIMATE" and divorce_date != "ILLEGITIMATE" and (wife_death - divorce_date).days < 0:
                        self.add_errors += [f"ERROR: FAMILY: US06: Divorced on {divorce_date} which is after {self.individuals[families.wife].name}'s death on {wife_death}"]
    


    def print_user_story_errors(self):
        '''This function will print all the errors that have been compiled into the list of errors'''
        for GEDCOM_error in sorted(self.add_errors):
            with open("Sprintoutput.txt", "a") as f:
                print(GEDCOM_error, file=f)
            print(GEDCOM_error)

def main():
    '''This runs the program.'''
    path = input("Insert path of GEDCOM file (if in the same directory, enter name of GEDCOM file):")
    Read_GEDCOM(path)
    

if __name__ == '__main__':
    main()
