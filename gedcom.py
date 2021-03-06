import prettytable as pt
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def convert_date(date_arr):
    date_obj = datetime.strptime(' '.join(date_arr), '%d %b %Y').date()
    return date_obj


class Gedcom():
    def __init__(self, input_url):
        self.line_list = []
        self.record_list = []
        self.output_list = []
        self.output_url = ""
        self.individual_list = []
        self.family_list = []
        self.error_list = []
        self.tier_0_tag = ['HEAD', 'TRLR', 'NOTE']
        self.tier_1_tag = ['NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV']
        self.tier_2_tag = ['DATE']
        self.load_file(input_url)
        self.separate_line()
        self.create_indi_object()
        self.create_fam_object()

    # Load designated text file by line
    # Store into self.line_list
    def load_file(self, input_url):
        if input_url == '':
            input_url = "./example.ged"
        input_stream = open(input_url, "r")
        self.line_list = input_stream.readlines()
        input_stream.close()

        for i in range(len(self.line_list)):
            self.line_list[i] = self.line_list[i].strip('\n')

        for line in self.line_list:
            if len(line) == 0:
                self.line_list.remove(line)

    # Separate every line in line_list into list
    # Store into self.record_list
    def separate_line(self):
        for idx in range(len(self.line_list)):
            self.record_list.append(self.line_list[idx].split(' '))

    # Identify individuals object in self.record_list
    # Store into self.individual_list
    def create_indi_object(self):
        idx = 0
        today = datetime.today().date()
        while idx < len(self.record_list):
            if self.record_list[idx][0] == '0' and self.record_list[idx][1] != 'HEAD' \
                    and self.record_list[idx][1] != 'NOTE' and self.record_list[idx][1] != 'TRLR' \
                    and self.record_list[idx][2] == 'INDI':
                indi_obj = {}
                indi_obj['ID'] = self.record_list[idx][1]
                idx += 1
                while self.record_list[idx][0] != '0':
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'NAME':
                        indi_obj['Name'] = ' '.join(self.record_list[idx][2:])
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'SEX':
                        indi_obj['Gender'] = self.record_list[idx][2]
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'BIRT':
                        idx += 1
                        if self.record_list[idx][0] == '2' and self.record_list[idx][1] == 'DATE':
                            indi_obj['Birthday'] = convert_date(self.record_list[idx][2:])
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'DEAT':
                        idx += 1
                        if self.record_list[idx][0] == '2' and self.record_list[idx][1] == 'DATE':
                            indi_obj['Death'] = convert_date(self.record_list[idx][2:])
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'FAMC':
                        indi_obj['Child'] = self.record_list[idx][2]
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'FAMS':
                        indi_obj['Spouse'] = self.record_list[idx][2]
                    if 'Birthday' in indi_obj.keys() and 'Death' not in indi_obj.keys():
                        indi_obj['Age'] = today.year - indi_obj['Birthday'].year \
                                          - ((today.month, today.day)
                                             < (indi_obj['Birthday'].month, indi_obj['Birthday'].day))
                        indi_obj['Alive'] = True
                    if 'Birthday' in indi_obj.keys() and 'Death' in indi_obj.keys():
                        indi_obj['Age'] = indi_obj['Death'].year - indi_obj['Birthday'].year \
                                          - ((indi_obj['Death'].month, indi_obj['Death'].day)
                                             < (indi_obj['Birthday'].month, indi_obj['Birthday'].day))
                        indi_obj['Alive'] = False
                    idx += 1
                self.individual_list.append(indi_obj)
                # print(indi_obj)
            else:
                idx += 1

    # Identify family objects in self.record_list
    # Store into self.family_list
    def create_fam_object(self):
        idx = 0
        while idx < len(self.record_list):
            if self.record_list[idx][0] == '0' and self.record_list[idx][1] != 'HEAD' \
                    and self.record_list[idx][1] != 'NOTE' and self.record_list[idx][1] != 'TRLR' \
                    and self.record_list[idx][2] == 'FAM':
                fam_obj = {}
                fam_obj['ID'] = self.record_list[idx][1]
                fam_obj['Children'] = []
                idx += 1
                while self.record_list[idx][0] != '0':
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'HUSB':
                        fam_obj['Husband ID'] = self.record_list[idx][2]
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'WIFE':
                        fam_obj['Wife ID'] = self.record_list[idx][2]
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'CHIL':
                        fam_obj['Children'].append(self.record_list[idx][2])
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'MARR':
                        idx += 1
                        if self.record_list[idx][0] == '2' and self.record_list[idx][1] == 'DATE':
                            fam_obj['Married'] = convert_date(self.record_list[idx][2:])
                    if self.record_list[idx][0] == '1' and self.record_list[idx][1] == 'DIV':
                        idx += 1
                        if self.record_list[idx][0] == '2' and self.record_list[idx][1] == 'DATE':
                            fam_obj['Divorced'] = convert_date(self.record_list[idx][2:])
                    idx += 1
                self.family_list.append(fam_obj)
                # print(fam_obj)
            else:
                idx += 1

    # Set self.output_url for pretty table and error check output
    def set_output_url(self, output_url):
        self.output_url = output_url

    # Print all objects in self.individual_list and self.family_list
    # On console and store into txt file with PrettyTable
    def print_pretty_table(self):
        indi_pt = pt.PrettyTable()
        indi_pt.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
        for individual in self.individual_list:
            if 'Death' in individual.keys():
                table_death = str(individual['Death'])
            else:
                table_death = 'NA'
            if 'Child' in individual.keys():
                table_child = individual['Child']
            else:
                table_child = 'NA'
            if 'Spouse' in individual.keys():
                table_spouse = individual['Spouse']
            else:
                table_spouse = 'NA'
            indi_pt.add_row([individual['ID'], individual['Name'], individual["Gender"], str(individual['Birthday']),
                             individual['Age'], individual['Alive'], table_death, table_child, table_spouse])
        print(indi_pt)

        fam_pt = pt.PrettyTable()
        fam_pt.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]
        for family in self.family_list:
            for individual in self.individual_list:
                if individual['ID'] == family['Husband ID']:
                    family['Husband Name'] = individual['Name']
                if individual['ID'] == family['Wife ID']:
                    family['Wife Name'] = individual['Name']
            if 'Children' in family.keys():
                table_children = family['Children']
            else:
                table_children = 'NA'
            if 'Divorced' in family.keys():
                table_divorced = str(family['Divorced'])
            else:
                table_divorced = 'NA'
            fam_pt.add_row([family['ID'], str(family['Married']), table_divorced, family['Husband ID'],
                            family['Husband Name'], family['Wife ID'], family["Wife Name"], table_children])
        print(fam_pt)

        output_stream = open(self.output_url, "w")
        output_stream.write("Individuals:\n")
        output_stream.write(str(indi_pt))
        output_stream.write("\n")
        output_stream.write("Families:\n")
        output_stream.write(str(fam_pt))
        output_stream.write("\n")
        output_stream.close()

    def create_arrow_output(self):
        for i in range(len(self.line_list)):
            line_arr = self.line_list[i].split(' ')
            output_str = '<-- '
            if line_arr[0] == '0':
                if line_arr[1] in self.tier_0_tag and len(line_arr) == 2:
                    output_str += '0|' + line_arr[1] + '|Y'
                elif line_arr[1] in self.tier_0_tag and len(line_arr) > 2:
                    output_str += '0|' + line_arr[1] + '|Y|' + str(' '.join(line_arr[2:]))
                elif len(line_arr) == 3 and line_arr[2] == 'INDI':
                    output_str += '0|INDI|Y|' + line_arr[1]
                elif len(line_arr) == 3 and line_arr[2] == 'FAM':
                    output_str += '0|FAM|Y|' + line_arr[1]
                elif len(line_arr) == 2:
                    output_str += '0|' + line_arr[1] + '|N'
                else:
                    output_str += '0|' + line_arr[1] + '|N|' + str(' '.join(line_arr[2:]))
            if line_arr[0] == '1':
                if line_arr[1] in self.tier_1_tag:
                    output_str += '1|' + line_arr[1] + '|Y|' + str(' '.join(line_arr[2:]))
                else:
                    output_str += '1|' + line_arr[1] + '|N|' + str(' '.join(line_arr[2:]))
            if line_arr[0] == '2':
                if line_arr[1] in self.tier_2_tag:
                    output_str += '2|' + line_arr[1] + '|Y|' + str(' '.join(line_arr[2:]))
                else:
                    output_str += '2|' + line_arr[1] + '|N|' + str(' '.join(line_arr[2:]))
            self.output_list.append(output_str)

    def print_arrow_records(self):
        for i in range(len(self.line_list)):
            print('--> ' + self.line_list[i])
            print(self.output_list[i])
