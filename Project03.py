from prettytable import PrettyTable
from collections import defaultdict
import os
import datetime

class Read_GEDCOM:

    def __init__(self, path, ptables = True):
        self.path = path
        self.family = dict()
        self.individuals = dict()
        self.family_ptable = PrettyTable(field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        self.individuals_ptable = PrettyTable(field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
        self.analyze_GEDCOM()
        if ptables:
            self.create_indi_ptable()
            self.create_fam_ptable()

    
    def analyze_GEDCOM(self):

        ind, fam, date_identifier_line, indiv_or_fam = "", "", [], "NA"

        for tokens in self.file_reading_gen(self.path, sep = " "):

            if len(tokens) >= 2 and tokens[0] == '0' and tokens[1] in ["HEAD", "TRLR", "NOTE"]:
                continue
            elif len(tokens) == 3 and tokens[0] == '0' and tokens[2] == "INDI":
                indiv_or_fam = "individual"
                ind = tokens[1].replace("@", "")
                self.individuals[ind] = Individual()
                continue
            elif len(tokens) == 3 and tokens[0] == '0' and tokens[2] == "FAM":
                indiv_or_fam = "family"
                fam = tokens[1].replace("@", "")
                self.family[fam] = Family()
                continue
            if indiv_or_fam in ["family", "individual"]:
                self.parse_info(tokens, date_identifier_line, ind, fam, indiv_or_fam)

            date_identifier_line = tokens
    
    def parse_info(self, tokens, date_identifier_line, ind, fam, indiv_or_fam):
        if len(tokens) == 2:
            return
        else:
            level, tag, arguments = tokens
            if level == "1" and tag in ["NAME", "SEX", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL"]:
                arguments = arguments.replace("@", "")
                if indiv_or_fam == "individual":
                    if tag == "NAME":
                        self.individuals[ind].name = arguments
                    elif tag == "SEX":
                        self.individuals[ind].sex = arguments
                    elif tag == "FAMC":
                        self.individuals[ind].famc = arguments
                    elif tag == "FAMS":
                        self.individuals[ind].fams.add(arguments)
                elif indiv_or_fam == "family":
                    if tag == "HUSB":
                        self.family[fam].husband = arguments
                    elif tag == "WIFE":
                        self.family[fam].wife = arguments
                    elif tag == "CHIL":
                        self.family[fam].children.add(arguments)
            elif level == "2" and tag == "DATE" and date_identifier_line[1] in ["BIRT", "DEAT", "MARR", "DIV"]: 
                date_identifier_level, date_identifier_tag = date_identifier_line[0], date_identifier_line[1]
                arguments = datetime.datetime.strptime(arguments, "%d %b %Y").date()
                if date_identifier_level == "1" and date_identifier_tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                    if indiv_or_fam == "individual":
                        if date_identifier_tag == "BIRT":
                            self.individuals[ind].birth = arguments
                        elif date_identifier_tag == "DEAT":
                            self.individuals[ind].death = arguments
                    elif indiv_or_fam == "family":
                        if date_identifier_tag == "MARR":
                            self.family[fam].marriage = arguments
                        elif date_identifier_tag == "DIV":
                            self.family[fam].divorce = arguments



    def file_reading_gen(self, path, sep = "\t"):
        try:
            fp = open(path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"Can't open {path}!")
        else:
            with fp:
                for line in fp:
                    separate_line = line.strip().split(sep, 2)
                    yield separate_line

    def create_indi_ptable(self):
        print("Individual Table")
        for ID, individual in self.individuals.items():
            individual.check_alive()
            if individual.fams == set():
                individual.fams = "NA"
            self.individuals_ptable.add_row([ID, individual.name, individual.sex, individual.birth, individual.age, individual.alive, individual.death, individual.famc, individual.fams])
        print(self.individuals_ptable)

    def create_fam_ptable(self):
        print("Family Table")
        for ID, fam in self.family.items():
            self.family_ptable.add_row([ID, fam.marriage, fam.divorce, fam.husband, self.individuals[fam.husband].name, fam.wife, self.individuals[fam.wife].name, fam.children])   
        print(self.family_ptable)

class Individual:
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
        self.alive = (self.death == None)
        try:
            if (self.alive):
                self.age = (datetime.datetime.today().year - self.birth.year)
            else:
                self.age = (self.death.year - self.birth.year)
        except:
            raise ValueError("The birth or death records appear to be messed up! Check them for errors!")   

class Family:
    def __init__(self):
        self.marriage = "NA"
        self.divorce = "NA"
        self.husband = "NA"
        self.wife = "NA"
        self.children = set()

def main():
    
    path = 'GEDCOM_Test.ged'
    Read_GEDCOM(path)
    

if __name__ == '__main__':
    main()