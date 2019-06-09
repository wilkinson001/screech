from collections import Counter
import os
import re

from .constants import col_type_reg, regex, flat_types, xl_types, seperators
from .functions import fparse_db, fparse_2


class ValidationError(Exception):
    pass


class FileParser:
    attrs = {}

    def __init__(self, infile, table, session):
        self.attrs["file"] = infile
        self.attrs["table"] = table
        self.session = session

    def parse(self):
        self.parse_file_type()
        if self.attrs["file_ext"] in flat_types:
            self.parse_attributes()
            self.attrs["numcols"] = set(self.attrs["ncols"]).pop()
            if not (len(set(self.attrs["ncols"])) == 1):
                raise ValidationError("inconsistent number of columns")
                # TODO: add logic for user to decide in gui which sep
            self.parse_column_types()
            self.attrs["new_coltypes"] = fparse_2(
                self.attrs["numcols"], self.attrs["cols"], self.attrs["coltypes"]
            )
            fparse_db(
                self.attrs["numcols"],
                self.attrs["fline"],
                self.attrs["new_coltypes"],
                self.attrs["file_name"],
                self.attrs["file"],
                self.attrs["maximum"],
                self.attrs["table"],
                self.session["username"],
            )
        elif self.attrs["file_ext"] in xl_types:
            raise ValidationError("Excel file types not currently implemented")
        else:
            raise ValidationError("Invalid file type")

    def parse_file_type(self):
        if os.path.isfile(self.attrs["file"]):
            # split path to path and file
            path_head, path_tail = os.path.split(self.attrs["file"])
            # regex match file name and ext
            match = re.search(regex["ftype"], path_tail)
            # if there is a match
            if match:
                self.attrs["file_name"] = match.group(1)
                self.attrs["file_ext"] = match.group(2)
                self.attrs["file_path"] = path_head
            else:
                raise ValidationError("Error, filename is not valid")
        else:
            raise ValidationError("Error, file not found at location given")

    def parse_attributes(self):
        self.attrs["cols"] = []
        self.attrs["ncols"] = []
        with open(self.attrs["file_name"]) as fileobject:
            # get first line of file
            fline = fileobject.readline()
            # append to dict count of occurance of each sep type, add more to extend project
            values = {sep: fline.count(seperators[sep]) for sep in seperators}
            # find sep with most occurances
            self.attrs["maximum"] = max(values, key=values.get)
            self.attrs["fline"] = fline.split(seperators[self.attrs["maximum"]])
            # iterate over lines in file -- need to limit somehow
            for line in fileobject:
                # remove any newline chars
                line = line.rstrip()
                # split row on delimeter identified above
                self.attrs["ncols"].append(
                    len(line.split(seperators[self.attrs["maximum"]]))
                )
                self.attrs["cols"].append(line.split(seperators[self.attrs["maximum"]]))

    def parse_column_types(self):
        self.attrs["coltypes"] = []
        for x in range(0, len(self.attrs["cols"])):
            types = []
            for z in range(0, self.attrs["numcols"]):
                # loop over column types
                for reg in range(0, len(col_type_reg)):
                    # regex match col types
                    re_match = re.search(
                        regex[col_type_reg[reg]], self.attrs["cols"][x][z]
                    )
                    if re_match:
                        types.append(col_type_reg[reg])
            # append column types for row to coltypes list
            self.attrs["coltypes"].append(types)

    def coerce_columns(self):
        self.new_coltypes = [None] * self.attrs["numcols"]
        for c in range(0, self.attrs["numcols"]):
            col = []
            for p in range(0, len(self.attrs["coltypes"])):
                col.append(self.attrs["coltypes"][p][c])
            col_counter = Counter(col)
            mc_list = [[ctype, count] for ctype, count in col_counter.most_common()]
            if len(mc_list) == 2:
                # generate bounds of +-15% of max count
                lbound = 0.85 * mc_list[0][1]
                ubound = 1.15 * mc_list[0][1]
                # similar count of types
                if lbound < mc_list[1][1] < ubound:
                    # user selection in console
                    new_coltypes[c] = input(
                        "Please enter which column type to use, either:",
                        mc_list[0][0],
                        " or ",
                        mc_list[1][0],
                    )
                # different counts of types
                else:
                    # check max data type and decide how to process smaller data types
                    max_type = mc_list[0][0]
                    # do action based on max type
                    if max_type == "int":
                        # check sub types and convert if possible
                        if mc_list[1][0] == "float":
                            print("check if can convert from float to int")
                            inv = IntFloat(cols, mc_list, c)
                        elif mc_list[1][0] == "string":
                            print("check if can convert from string to int")
                            inv = IntFloat(cols, mc_list, c)
                        elif mc_list[1][0] == "bool":
                            print("cast from bool")
                            inv = 0
                        else:
                            print("type cannot be converted to int, check your data")
                            inv = 1
                        # after checking for invalid rows
                        if inv > 0:
                            print(
                                "Error, cannot convert to this type, check your data, meanwhile casting to string"
                            )
                            # default cast to string
                            new_coltypes[c] = "varchar(2000)"
                        else:
                            # set type to int
                            new_coltypes[c] = max_type
                    elif max_type == "float":
                        if mc_list[1][0] == "int":
                            print("convert from int")
                            inv = 0
                        elif mc_list[1][0] == "string":
                            print("check if can convert from string to float")
                            inv = FloatString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to float, check your data")
                        if inv > 0:
                            print(
                                "Error, cannot convert to this type, check your data, meanwhile casting to string"
                            )
                            # default cast to string
                            new_coltypes[c] = "varchar(2000)"
                        else:
                            # set type to float
                            new_coltypes[c] = "FLOAT(30)"
                    elif max_type == "bool":
                        if mc_list[1][0] == "int":
                            print("check if can convert from int to bool")
                            inv = BoolInt(cols, mc_list, c)
                        elif mc_list[1][0] == "string":
                            print("check if can convert from string to bool")
                            inv = BoolString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to bool, check your data")
                        if inv > 0:
                            print(
                                "Error, cannot convert to this type, check your data, meanwhile casting to string"
                            )
                            # default cast to string
                            new_coltypes[c] = "varchar(2000)"
                        else:
                            # set type to bool
                            new_coltypes[c] = max_type
                    elif max_type == "string":
                        if mc_list[1][0] == "float":
                            print("cast from float")
                            inv = 0
                        elif mc_list[1][0] == "int":
                            print("cast from int")
                            inv = 0
                        elif mc_list[1][0] == "bool":
                            print("cast from bool")
                            inv = 0
                        elif mc_list[1][0] == "date":
                            print("cast from date")
                            inv = 0
                        else:
                            print("type cannot be converted to string, check your data")
                        if inv > 0:
                            print(
                                "Error, cannot convert to this type, check your data, meanwhile casting to string"
                            )
                            # default cast to string
                            new_coltypes[c] = "varchar(2000)"
                        else:
                            # set type to varchar(2000)
                            new_coltypes[c] = "varchar(2000)"
                    elif max_type == "date":
                        if mc_list[1][0] == "string":
                            print("check if can convert from string to date")
                            inv = DateString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to date, check your data")
                        if inv > 0:
                            print(
                                "Error, cannot convert to this type, check your data, meanwhile casting to string"
                            )
                            # default cast to string
                            new_coltypes[c] = "varchar(2000)"
                        else:
                            # set type to date
                            new_coltypes[c] = max_type
                    else:
                        print("Max type is unkown to system")

            # clear data type
            elif len(mc_list) == 1:
                print("type = ", mc_list[0][0])
                new_coltypes[c] = mc_list[0][0]
            # multiple types
            else:
                print("multiple types in column, check your data")
        return new_coltypes
