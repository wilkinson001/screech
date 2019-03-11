import pandas as pd
import os
import numpy as np
import re
from collections import Counter
from app import functions
import mysql.connector
import atexit
from sys import exit

#######################
##      CONSTANTS    ##
#######################
non_xl_types=["csv","txt","tab"]
xl_types=["xls","xlsx","xlm","xlsm"]
col_type_reg=["int","float"]
#regex also in functions file
regex={"ftype":"(.*)[.]{1}([A-z]+)$","int":"^[0-9]*$","float":"^[0-9]*[.]{1}[0-9]*$"}
seperators={
        "commas":",",
        "pipes":"|",
        "tabs":"\t"
        }
col_data_types={
        "int": ["float","string","bool"],
        "float":["int","string"],
        "string":["date","bool","float","int"],
        "bool":["int","string"],
        "date":["string"]
        }
#######################
#######################
##      USERNAME     ##
## Change in future  ##
username='owilkinson'
#######################


#close database connection on error or program exit
@atexit.register
def db_close():
    if 'conn' in locals():
        conn.close()
#try db connection or exit on error
conn= functions.db_connect()

#create db cursor
cursor = conn.cursor()
#get filename from user input
fname = input("Enter path and filename:\n")

#call ftypeparser function
bool_match, file_name, file_ext, file_path = functions.ftypeParser(fname)

#check if match
if(bool_match):
    print(file_path," ",file_name," ",file_ext)
else:
    print("Error")
    exit()
#check if file extention in list
if(file_ext in non_xl_types):
    values={}
    cols=[]
    #read file as file object
    with open(fname) as fileobject:
        #get first line of file
        fline = fileobject.readline()
        #append to dict count of occurance of each sep type, add more to extend project
        values['pipes'] = fline.count("|")
        values['commas'] = fline.count(",")
        values['tabs'] = fline.count("\t")
        #find sep with most occurances
        maximum=max(values, key=values.get)
        #print(maximum)
        ncols=[]
        fline = fline.split(seperators[maximum])
        #iterate over lines in file -- need to limit somehow
        for line in fileobject:
            #remove any newline chars
            line=line.rstrip()
            #split row on delimeter identified above
            ncols.append(len(line.split(seperators[maximum])))
            cols.append(line.split(seperators[maximum]))
        #check if each row is consistent in file
        numcols = set(ncols).pop()
        if(len(set(ncols))==1):
            print("There are ",numcols," columns in the data")
        else:
            print("inconsistent number of columns")
            ################################################
            #add logic for user to decide in gui which sep #
            ################################################
        #calculate column types
        coltypes=[]
        for x in range(0, len(cols)):
            types=[]
            for z in range(0,numcols):
                #loop over column types
                for reg in range(0,len(col_type_reg)):
                    #regex match col types
                    re_match = re.search(regex[col_type_reg[reg]], cols[x][z])
                    if(re_match):
                        types.append(col_type_reg[reg])
            #append column types for row to coltypes list
            coltypes.append(types)
        #create empty list of size numcols
        new_coltypes=[None]*numcols
        #logic for inconsitant types in col
        for c in range(0,numcols):
            col=[]
            for p in range(0,len(coltypes)):
                #print(coltypes[p][c])
                col.append(coltypes[p][c])
            #get count of unique values in coltypes column
            col_counter = Counter(col)
            mc_list=[]
            #turn counter.most_common return into iteratable list
            for ctype, count in col_counter.most_common():
                mc_list.append([ctype, count])
            #check if two clear data types in column
            if(len(mc_list)==2):
                print("max type = ",mc_list[0][0]," count of ", mc_list[0][1])
                print("2nd type = ",mc_list[1][0]," count of ", mc_list[1][1])
                #generate bounds of +-15% of max count
                lbound = 0.85*mc_list[0][1]
                ubound = 1.15*mc_list[0][1]
                #similar count of types
                if(lbound<mc_list[1][1]<ubound):
                    print("User must decide which type to use")
                    ###########################
                    #add user selection in gui#
                    ###########################
                #different counts of types
                else:
                    #check max data type and decide how to process smaller data types
                    max_type=mc_list[0][0]
                    #do action based on max type
                    if max_type=="int":
                        #check sub types and convert if possible
                        if mc_list[1][0]=="float":
                            print("check if can convert from float to int")
                            inv= functions.IntFloat(cols, mc_list, c)
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to int")
                            inv= functions.IntFloat(cols, mc_list, c)
                        elif mc_list[1][0]=="bool":
                            print("cast from bool")
                            inv=0
                        else:
                            print("type cannot be converted to int, check your data")
                            inv=1
                        #after checking for invalid rows
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data")
                        else:
                            #set type to int
                            new_coltypes[c]=max_type
                    elif max_type=="float":
                        if mc_list[1][0]=="int":
                            print("convert from int")
                            inv=0
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to float")
                            inv= functions.FloatString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to float, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data")
                        else:
                            #set type to float
                            new_coltypes[c]='FLOAT(30)'
                    elif max_type=="bool":
                        if mc_list[1][0]=="int":
                            print("check if can convert from int to bool")
                            inv= functions.BoolInt(cols, mc_list, c)
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to bool")
                            inv= functions.BoolString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to bool, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data")
                        else:
                            #set type to bool
                            new_coltypes[c]=max_type
                    elif max_type=="string":
                        if mc_list[1][0]=="float":
                            print("cast from float")
                            inv=0
                        elif mc_list[1][0]=="int":
                            print("cast from int")
                            inv=0
                        elif mc_list[1][0]=="bool":
                            print("cast from bool")
                            inv=0
                        elif mc_list[1][0]=="date":
                            print("cast from date")
                            inv=0
                        else:
                            print("type cannot be converted to string, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data")
                        else:
                            #set type to varchar(200)
                            new_coltypes[c]='varchar(200)'
                    elif max_type=="date":
                        if mc_list[1][0]=="string":
                            print("check if can convert from string to date")
                            inv= functions.DateString(cols, mc_list, c)
                        else:
                            print("type cannot be converted to date, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data")
                        else:
                            #set type to date
                            new_coltypes[c]=max_type
                    else:
                        print("Cannot auto alter data type based on max type")
                        ###########################
                        #add user selection in gui#
                        ###########################
            #clear data type
            elif(len(mc_list)==1):
                print("type = ", mc_list[0][0])
                new_coltypes[c] = mc_list[0][0]
            #multiple types                  
            else:
                print("multiple types in column, check your data")
            
        ##################################################################
        #add logic to construct sql from data description                # 
        #(this will be seperated out so user can alter suggestion in gui)#
        ##################################################################
        table_name = input("Please enter database table name:\n")
        #add logic for already used tablename
        #construct create table
        sql="create table "+table_name+" ("
        for it in range(0,numcols):
            sql+=fline[it]+" "
            sql+=new_coltypes[it]
            if(it<numcols-1):
                sql+=", "
        sql+=")"
        
        print(sql)
        #will add logic to edit sql statment in gui then execute
        cursor.execute(sql)
        
        #grant permissions on new table
        sql='grant all privileges on screech.* to \'screech\'@\'%\' identified by \'screech\''
        print(sql)
        cursor.execute(sql)
        print("granted privileges")
        mysql.connector.RefreshOption.GRANT
        
        #construct insert from file        
        sql = 'load data infile "' +fname.replace('\\','\\\\')
        sql+='" into table ' + table_name + ' fields terminated by \''+seperators[maximum]+'\' ignore 1 lines'
        print(sql)
        cursor.execute(sql)
        conn.commit()
        print("inserted data sucessfully")
        
        
        #get user id for files table insert
        uid= functions.get_uid(username)
        print(uid)
        #insert date into files table
        sql='insert into screech.files (filename, owner, date, dbtable) values ("'
        sql+=str(file_name)+'",'+str(uid)+',CURDATE(),"'+str(table_name)
        sql+='")'
        print(sql)
        cursor.execute(sql)
        conn.commit()
        print("inserted data sucessfully")
        
        #get fid for current file
        fid= functions.get_fid(file_name, uid, table_name)
        #insert date into files table
        sql='insert into screech.tables (uid,fid) values ('
        sql+=str(uid)+','+str(fid)
        sql+=')'
        print(sql)
        cursor.execute(sql)
        conn.commit()
        print("inserted data sucessfully")
        
        
        
elif(file_ext in xl_types):
    print("excel operations")
else:
    print("Invalid file type")