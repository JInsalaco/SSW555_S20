'''The purpose of this file is to read and analyze a GEDCOM file. This program will save information about individuals and families in lists (or collections) so that they can be examined later. 
It can be assumed that the number of individuals in any file is always less than 5000, and the number of families is always less than 1000. 
After reading all of the data, the program will print the unique identifiers and names of each of the individuals in order by their unique identifiers in a pretty table. 
Then, for each family, print the unique identifiers and names of the husbands and wives, in order by unique family identifiers.'''

from prettytable import PrettyTable
from collections import defaultdict
import datetime
from dateutil.relativedelta import *

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
        # self.marriageAfter14()
        # self.birthBeforeMarriageOfParents()
        self.birthsLessThanFive()
        self.uniqueFirstNameInFamily()
        self.correctGenderForRole()
        self.maleLastNames()
        self.siblingSpacing()
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
                self.individuals[ind] = Individual() #The instance of the Individual class object is created for this specific IndiID
                continue
            elif len(tokens) == 3 and tokens[0] == '0' and tokens[2] == "FAM":
                indiv_or_fam = "family" #Marks the line as family so that the parse_info function can identify it accordingly
                fam = tokens[1].replace("@", "")
                self.family[fam] = Family() #The instance of the Family class object is created for this specific FamID
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
                arguments = datetime.datetime.strptime(arguments, "%d %b %Y").date() 
                if date_identifier_level == "1" and date_identifier_tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                    if indiv_or_fam == "individual": #Parses birthday and death day information for an individual
                        if date_identifier_tag == "BIRT":
                            self.individuals[ind].birth = arguments
                        elif date_identifier_tag == "DEAT":
                            self.individuals[ind].death = arguments
                    elif indiv_or_fam == "family": #Parses marriage date and divorce date information for a family
                        if date_identifier_tag == "MARR":
                            self.family[fam].marriage = arguments
                        elif date_identifier_tag == "DIV":
                            self.family[fam].divorce = arguments

    #Function for US01's unittest: Returns a list of id's (ind or fam) that
    #have dates after the current date
    def checkDatesAfterToday(self):
        with open("Sprintoutput.txt", "a") as f:
            currentDate  = datetime.date.today()
            idList = []
            for ind in self.individuals:
                if self.individuals[ind].birth > currentDate:
                    print(f"ERROR: INDIVIDUAL: {ind} US01: Birthday {self.individuals[ind].birth} occurs in the future", file=f)
                    idList.append(ind)
                if self.individuals[ind].death != None and self.individuals[ind].death > currentDate:
                    print(f"ERROR: INDIVIDUAL: {ind} US01: Death {self.individuals[ind].death} occurs in the future", file=f)
                    idList.append(ind)
            for fam in self.family:
                if self.family[fam].marriage > currentDate:
                    print(f"ERROR: FAMILY: {fam} US01: Marriage {self.family[fam].marriage} occurs in the future", file=f)
                    idList.append(fam)
                if self.family[fam].divorce != "NA" and self.family[fam].divorce > currentDate:
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
                if self.individuals[ind].death is not None and self.individuals[ind].death >= dateFrom30DaysAgo and self.individuals[ind].death < today:
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
                        if birthDate > marriageDate:
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
                        if self.individuals[ind].birth == self.individuals[ind2].birth:
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
                            birthday_list.append(self.individuals[ind].birth)
                        count_dict = dict((i, birthday_list.count(i)) for i in birthday_list)
                        list_birthdays = count_dict.values()
                        if max(list_birthdays) <= 5:
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
                        diff = abs(currBirthday - sibBirthday)
                        if(diff > datetime.timedelta(days=2) and diff < datetime.timedelta(days=243)):
                            idList.append(child)
                            idList.append(children)
                            print(f"ERROR: US13: {self.individuals[child].name } and {self.individuals[children].name} have birthdays too close together", file=f)
            idList = list(dict.fromkeys(idList))
            print(idList)
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
                if self.individuals[fam.husband].calculateAge(fam.marriage) < 14 or self.individuals[fam.wife].calculateAge(fam.marriage) < 14:
                    idList.append(famID)
                    print(f"WARNING: FAMILY: US10: {famID}: One or both spouses were less than 14 years old at the time of marriage.", file = f)
            return idList

    # def birthBeforeMarriageOfParents(self):
    #     with open("SprintOutput.txt", "a") as f:
    #         idList = []
    #         for famID, fam in self.family.items():
    #             for child in fam.children:
    #                 childBirth = self.individuals[child].birth
    #                 totalDivorceChildDiff = relativedelta.relativedelta(childBirth, fam.divorce).month if fam.divorce != "NA" else sys.maxsize
    #                 if childBirth < fam.marriage and fam.divorce == "NA" or childBirth > fam.divorce or childBirth < fam.divorce and totalDivorceChildDiff.month + (12 * totalDivorceChildDiff.years) > 9:
    #                     idList.append((famID, child))
    #                     print(f"WARNING: FAMILY: US08: {famID}: Child {child} is born before the marriage of their parents.", file = f)
    #         return idList
             
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
        self.age = lastDate.year - self.birth.year - int((lastDate.month, lastDate.day) < (self.birth.month, self.birth.day)) # Tuple comparison to check if today's date is before or after current/death date
        return self.age

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
        if print_all_errors == True:
            self.print_user_story_errors()


    def birth_before_death(self):
        '''US03 Birth Before Death: Birth should occur before death of an individual'''
        for individual in self.individuals.values():
            if individual.death != None and (individual.death - individual.birth).days < 0:
                self.add_errors += [f"ERROR: INDIVIDUAL: US03: {individual.name}'s death occurs on {individual.death} which is before their birth on {individual.birth}"]
    
    def marriage_before_divorce(self):
        '''US04 Marriage Before Divorce: Marriage should occur before divorce of spouses, and divorce can only occur after marriage'''
        for families in self.family.values():
            if families.divorce != "NA" and (families.divorce - families.marriage).days < 0:
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
                if (husband_death - marriage_date).days < 0:
                    self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
            else:
                if (wife_death - marriage_date).days < 0:
                    self.add_errors += [f"ERROR: FAMILY: US05: Married on {marriage_date} which is after {self.individuals[families.wife].name}'s death on {wife_death}"]
              
    def divorce_before_death(self):
        '''US06 Divorce can only occur before death of both spouses'''
        for families in self.family.values():
            husband_death = self.individuals[families.husband].death
            wife_death = self.individuals[families.wife].death
            divorce_date = families.divorce
            if husband_death == None and wife_death == None: #If the wife and husband are still alive there is no further analysis needed
                break
            elif divorce_date != None: #Checks if the husband was dead before he and wife divorced and then checks if wife was dead before she and husband divorced
                if husband_death != None:
                    if (husband_death - divorce_date).days < 0:
                        self.add_errors += [f"ERROR: FAMILY: US06: Divorced on {divorce_date} which is after {self.individuals[families.husband].name}'s death on {husband_death}"]
                else:
                    if (wife_death - divorce_date).days < 0:
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
