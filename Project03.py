'''The purpose of this file is to read and analyze a GEDCOM file. This program will save information about individuals and families in lists (or collections) so that they can be examined later. 
It can be assumed that the number of individuals in any file is always less than 5000, and the number of families is always less than 1000. 
After reading all of the data, the program will print the unique identifiers and names of each of the individuals in order by their unique identifiers in a pretty table. 
Then, for each family, print the unique identifiers and names of the husbands and wives, in order by unique family identifiers.'''

from prettytable import PrettyTable
from collections import defaultdict
import datetime

class Read_GEDCOM:
    '''This class will read and analyze the GEDCOM file so that it can sort the data into the Individual and Family classes.'''
    def __init__(self, path, ptables = True):
        self.path = path
        self.family = dict() #The key is the FamID and the value is the instance for the Family class object for that specific FamID
        self.individuals = dict() #The key is the IndiID and the value is the instance for the Individual class object for that specific IndiID
        self.family_ptable = PrettyTable(field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        self.individuals_ptable = PrettyTable(field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
        self.analyze_GEDCOM() 
        if ptables: #Makes pretty tables for the data
            self.create_indi_ptable()
            self.create_fam_ptable()

    
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
        with open("Project03output.txt", "w") as f:
            print("Individuals", file=f)
            print(self.individuals_ptable, file=f)

    def create_fam_ptable(self):
        '''This creates a Pretty Table that is a Family summary of each family's ID, when they were married, when they got divorced, the Husband ID, the Husband Name, the Wife ID, the Wife Name, and their children.'''
        print("Family Table")
        for ID, fam in self.family.items():
            self.family_ptable.add_row([ID, fam.marriage, fam.divorce, fam.husband, self.individuals[fam.husband].name, fam.wife, self.individuals[fam.wife].name, fam.children])   
        print(self.family_ptable)
        #append families table to output file
        with open("Project03output.txt", "a") as f:
            print("Families", file=f)
            print(self.family_ptable, file=f)

class Individual:
    '''This class will hold all the information for each individual according to their IndiID. This includes their name, sex, birthday, age, whether they are alive, death date, and their children and spouses.'''
    def __init__(self):
        self.name = "NA"
        self.sex = "NA"
        self.birth = None
        self.age = "NA"
        self.alive = True 
        self.death = None 
        self.famc = "NA"
        self.fams = set()

    def check_alive(self):
        '''The purpose of this function is to check whether a person is alive or not and what their age is.'''
        self.alive = (self.death == None) #Returns true if self.death == None because that means the person is not dead.
        try:
            if (self.alive): #If the person is alive then this will calculate their birthday based on the current year
                self.age = (datetime.datetime.today().year - self.birth.year)
            else: #If the person is dead this will calculate their age when they died
                self.age = (self.death.year - self.birth.year)
        except:
            raise ValueError("The birth or death records appear to be messed up! Check them for errors!")   

class Family:
    '''This class will hold all of the information for each family according to their FamID. This includes the marriage date, divorce date, husband ID, wife ID, and a set of the children.'''
    def __init__(self):
        self.marriage = "NA"
        self.divorce = "NA"
        self.husband = "NA"
        self.wife = "NA"
        self.children = set()

def main():
    '''This runs the program.'''
    path = 'AldenRadoncic-TargaryenFamily-Test2ForProject03.ged'
    Read_GEDCOM(path)
    

if __name__ == '__main__':
    main()
