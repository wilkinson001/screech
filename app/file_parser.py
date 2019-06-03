import os
import re

from .constants import col_type_reg, regex, flat_types, xl_types, seperators
from .functions import fparse_db, fparse_2


class ValidationError(Exception):
    pass


class FileParser:
    attrs = {}

    def __init__(self, file, table, session):
        self.attrs['file'] = file
        self.attrs['table'] = table
        self.session = session
    
    def parse(self):
        self.parse_file_type()
        if self.attrs['file_ext'] in flat_types:
            self.parse_attributes()
            self.attrs['numcols'] = set(self.attrs['ncols']).pop()
            if not (len(set(self.attrs['ncols']))==1):
                raise ValidationError("inconsistent number of columns")
                # TODO: add logic for user to decide in gui which sep
            self.parse_column_types()
            self.attrs['new_coltypes'] = fparse_2(
                self.attrs['numcols'], 
                self.attrs['cols'], 
                self.attrs['coltypes']
            )
            fparse_db(
                self.attrs['numcols'], 
                self.attrs['fline'],
                self.attrs['new_coltypes'], 
                self.attrs['file_name'], 
                self.attrs['file'], 
                self.attrs['maximum'], 
                self.attrs['table'], 
                self.session['username']
            )
        elif self.attrs['file_ext'] in xl_types:
            raise ValidationError('Excel file types not currently implemented')
        else:
            raise ValidationError("Invalid file type")

    def parse_file_type(self):
        if(os.path.isfile(self.attrs['name'])):
            #split path to path and file
            path_head,path_tail = os.path.split(self.attrs['name'])
            #regex match file name and ext
            match = re.search(regex['ftype'],path_tail)
            #if there is a match
            if(match):
                self.attrs['file_name'] = match.group(1)
                self.attrs['file_ext'] = match.group(2) 
                self.attrs['file_path'] = path_head
            else:
                raise ValidationError("Error, filename is not valid")
        else:
            raise ValidationError("Error, file not found at location given")
    
    def parse_attributes(self):
        self.attrs['cols'] = []
        self.attrs['ncols'] = []
        with open(self.attrs['file_name']) as fileobject:
            #get first line of file
            fline = fileobject.readline()
            #append to dict count of occurance of each sep type, add more to extend project
            values = {sep: fline.count(seperators[sep]) for sep in seperators}
            #find sep with most occurances
            self.attrs['maximum']=max(values, key=values.get)
            self.attrs['fline'] = fline.split(seperators[self.attrs['maximum']])
            #iterate over lines in file -- need to limit somehow
            for line in fileobject:
                #remove any newline chars
                line=line.rstrip()
                #split row on delimeter identified above
                self.attrs['ncols'].append(len(line.split(seperators[self.attrs['maximum']])))
                self.attrs['cols'].append(line.split(seperators[self.attrs['maximum']]))

    def parse_column_types(self):
        self.attrs['coltypes'] = []
        for x in range(0, len(self.attrs['cols'])):
            types=[]
            for z in range(0, self.attrs['numcols']):
                #loop over column types
                for reg in range(0,len(col_type_reg)):
                    #regex match col types
                    re_match = re.search(regex[col_type_reg[reg]], self.attrs['cols'][x][z])
                    if(re_match):
                        types.append(col_type_reg[reg])
            #append column types for row to coltypes list
            self.attrs['coltypes'].append(types)
