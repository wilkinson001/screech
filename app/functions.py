import os
import re
from math import modf
import mysql.connector
from mysql.connector import errorcode
from sys import exit
import atexit
from collections import Counter
from sklearn import tree
from scipy.stats import iqr
import pandas as pd
#######################
##      CONSTANTS    ##
#######################
non_xl_types=["csv","txt","tab"]
xl_types=["xls","xlsx","xlm","xlsm"]
#coltypes are database friendly type names
col_type_reg=["int","float","varchar(2000)"]
#regex also in functions file
regex={"ftype":"(.*)[.]{1}([A-z]+)$",
    "int":"^[0-9]*$",
    "float":"^[0-9]*[.]{1}[0-9]*$",
    "date":"""(^([1-9]|[1-2][0-9]|3[0-1])(/|-|.)(1[0-2]|0?[0-9])(/|-|.)([0-9]{2}|[0-9]{4})$|
    ^([0-9]{2}|[0-9]{4})(/|-|.)(1[0-2]|0?[0-9])(/|-|.)([1-9]|[1-2][0-9]|3[0-1])$)""",
    "varchar(2000)":".*"}
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
discrete_threshold=0.2
continuous_threshold=0.5


def ftypeParser(filename):
    #check if file exists at location
    if(os.path.isfile(filename)):
        #split path to path and file
        path_head,path_tail = os.path.split(filename)
        #regex match file name and ext
        match = re.search(regex['ftype'],path_tail)
        #if there is a match
        if(match):
            #return bool, file name, file ext, path to file
            return True, match.group(1),match.group(2), path_head
        else:
            print("Error, filename is not valid")
            return False,"","",""
    else:
        print("Error, file not found at location given")    
        return False,"","",""

def IntFloat(columns, mc_list, col_number):
    invalid=0
    for z in range(0, len(columns[0])):
        if type(columns[col_number][z]) is float:
            frac, i = modf(columns[col_number][z])
            if frac>0:
                invalid+=1
    return invalid

def IntString(columns, mc_list, col_number):
    invalid=0
    for z in range(0, len(columns)):
        if type(columns[col_number][z]) is str:
            search = re.sub('[£$€%]','',columns[col_number][z])
            match = re.search(regex['int'], search)
            if match == False:
                invalid+=1
    return invalid  

def FloatString(columns, mc_list, col_number):
    invalid=0
    for z in range(0, len(columns)):
        if type(columns[col_number][z]) is str:
            search = re.sub('[£$€%]','',columns[col_number][z])
            match = re.search(regex['float'], search)
            if match == False:
                invalid+=1
    return invalid

def BoolInt(columns, mc_list, col_number):
    invalid=0
    for z in range(0, len(columns)):
        if type(columns[col_number][z]) is int:
            match = re.search('[10]', columns[col_number][z])
            if match == False:
                invalid+=1
    return invalid

def BoolString(columns, mc_list, col_number):
    invalid=0
    for z in range(0, len(columns)):
        if type(columns[col_number][z]) is str:
            match = re.search('(true|false|t|f)', columns[col_number][z].lower())
            if match == False:
                invalid+=1
    return invalid

def DateString(columns, mc_list, col_number):
    invalid=0
    #TODO
    return invalid

def db_connect():
    try:
        conn=mysql.connector.connect(user='screech', password='screech', host='db', database='screech', allow_local_infile=True)
        print("successful database connection")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return 0
    return conn


def query(sql, opts=""):
    c=db_connect()
    curs=c.cursor()
    if opts=="":
        curs.execute(sql)
    else:
        curs.execute(sql, opts)
    return curs, c

def get_file_list(user):
    c=db_connect()
    curs=c.cursor()
    sql=('select filename, username, date, dbtable from screech.files a inner join '
         'screech.tables b on (a.id=b.fid) inner join'
         '(select id, username from screech.users where username = "'+user+'")c on (b.uid=c.id)')
    curs.execute(sql)
    rows = curs.fetchall()
    r=[]
    z=curs.rowcount
    print(z)
    for (filename, owner, date, dbtable) in rows:
        r.append([filename, owner, date, dbtable])
    return z, r

def get_file(db_table):
    c=db_connect()
    curs=c.cursor(dictionary=True)
    sql=('select * from '+db_table)
    curs.execute(sql)
    rows=curs.fetchall()
    new_data={}
    for i in range(0,len(rows)):
        new_data.update({i: rows[i]})
    return new_data

def cols_from_json(data):
    
    keys=list(data[0].keys())
    print(keys)
    clean_data={}
    for key in keys:
        temp=[]
        for i in range(0, len(data)):
            temp.append(data[i][key])
        clean_data[key]=temp
    return clean_data

def get_uid(user):
    sql=('select id 	from screech.users where username = "'+user+'"')
    cur, c = query(sql)
    uid=0
    for (id) in cur:
        print("id=",id[0])
        uid=id[0]
    return uid

def checkUserExists(user):
    exists=False
    sql=('select id from screech.users where username = "'+user+'"')
    print(sql)
    cur, c = query(sql)
    for (id) in cur:
        exists=True
    return exists

def createUser(user, hashed):
    sql=('insert into screech.users (username, password) values ("'+user+'","'+hashed+'")')
    conn=db_connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return 0

def checkUser(user, hashed):
    exists=False
    sql=('select username from screech.users where username = "'+user+'" and password="'+hashed+'"')
    cur, c = query(sql)
    for username in cur:
        exists=True
    return exists

def get_fid(file_name, uid, table_name):
    sql=('select id 	from screech.files where filename = "'+str(file_name)+'" and owner='+str(uid)+' and dbtable="'+str(table_name)+'"')
    cur, c = query(sql)
    for (id) in cur:
        fid=id[0]
    return fid


def fparse_name(fname):
    #call ftypeparser on file
    bool_match, file_name, file_ext, file_path = ftypeParser(fname)
    #check if match
    if(bool_match):
        print(file_path," ",file_name," ",file_ext)
    else:
        print("Error")
        exit()
    return fname, file_name, file_ext

def fparse_attributes(fname):
        cols=[]
        values={}
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
            return ncols, cols, maximum, fline

def fparse_coltypes(cols, numcols):
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
    return coltypes

def fparse_db(numcols, fline, new_coltypes, file_name, fname, maximum, table_name, user):
    @atexit.register
    def db_close():
        if 'conn' in locals():
            conn.close()  
    
    conn=db_connect()

    #create db cursor
    cursor = conn.cursor()
  
    #add logic for already used tablename
    #construct create table
    sql="create table "+table_name+" ("
    for it in range(0,numcols):
        sql+=fline[it].replace("(","").replace(")","").replace(" ","_").replace("-","_")+" "
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
    sql = 'load data local infile "' +fname.replace('\\','\\\\')
    sql+='" into table ' + table_name + ' fields terminated by \''+seperators[maximum]+'\' ignore 1 lines'
    print(sql)
    cursor.execute(sql)
    conn.commit()
    print("inserted data sucessfully")
    
    
    #get user id for files table insert
    uid=get_uid(user)
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
    fid=get_fid(file_name, uid, table_name)
    #insert date into files table
    sql='insert into screech.tables (uid,fid) values ('
    sql+=str(uid)+','+str(fid)
    sql+=')'
    print(sql)
    cursor.execute(sql)
    conn.commit()
    print("inserted data sucessfully")
    conn.close()

def fparse_2(numcols, cols, coltypes):        
        #create empty list of size numcols
        new_coltypes=[None]*numcols
        #logic for inconsitant types in col
        print(coltypes)
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
                    #user selection in console
                    new_coltypes[c]=input("Please enter which column type to use, either:",mc_list[0][0]," or ", mc_list[1][0])
                #different counts of types
                else:
                    #check max data type and decide how to process smaller data types
                    max_type=mc_list[0][0]
                    #do action based on max type
                    if max_type=="int":
                        #check sub types and convert if possible
                        if mc_list[1][0]=="float":
                            print("check if can convert from float to int")
                            inv=IntFloat(cols,mc_list,c)
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to int")
                            inv=IntFloat(cols,mc_list,c)
                        elif mc_list[1][0]=="bool":
                            print("cast from bool")
                            inv=0
                        else:
                            print("type cannot be converted to int, check your data")
                            inv=1
                        #after checking for invalid rows
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data, meanwhile casting to string")
                            #default cast to string
                            new_coltypes[c]="varchar(2000)"
                        else:
                            #set type to int
                            new_coltypes[c]=max_type
                    elif max_type=="float":
                        if mc_list[1][0]=="int":
                            print("convert from int")
                            inv=0
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to float")
                            inv=FloatString(cols,mc_list,c)
                        else:
                            print("type cannot be converted to float, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data, meanwhile casting to string")
                            #default cast to string
                            new_coltypes[c]="varchar(2000)"
                        else:
                            #set type to float
                            new_coltypes[c]='FLOAT(30)'
                    elif max_type=="bool":
                        if mc_list[1][0]=="int":
                            print("check if can convert from int to bool")
                            inv=BoolInt(cols,mc_list,c)
                        elif mc_list[1][0]=="string":
                            print("check if can convert from string to bool")
                            inv=BoolString(cols,mc_list,c)
                        else:
                            print("type cannot be converted to bool, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data, meanwhile casting to string")
                            #default cast to string
                            new_coltypes[c]="varchar(2000)"
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
                            print("Error, cannot convert to this type, check your data, meanwhile casting to string")
                            #default cast to string
                            new_coltypes[c]="varchar(2000)"
                        else:
                            #set type to varchar(2000)
                            new_coltypes[c]='varchar(2000)'
                    elif max_type=="date":
                        if mc_list[1][0]=="string":
                            print("check if can convert from string to date")
                            inv=DateString(cols,mc_list,c)
                        else:
                            print("type cannot be converted to date, check your data")
                        if(inv>0):
                            print("Error, cannot convert to this type, check your data, meanwhile casting to string")
                            #default cast to string
                            new_coltypes[c]="varchar(2000)"
                        else:
                            #set type to date
                            new_coltypes[c]=max_type
                    else:
                        print("Max type is unkown to system")
                                                
            #clear data type
            elif(len(mc_list)==1):
                print("type = ", mc_list[0][0])
                new_coltypes[c] = mc_list[0][0]
            #multiple types                  
            else:
                print("multiple types in column, check your data")
        return new_coltypes

def tree_setup(data, target):
    clf = tree.DecisionTreeClassifier(random_state=0)      
    clf = clf.fit(data, target)
    return clf


def getTreeData():
    c=db_connect()
    curs=c.cursor()
    sql=('select n_cols,n_rows,n_cont,n_disc,n_ts,target from screech.tree_data')
    curs.execute(sql)
    rows = curs.fetchall()
    data=[]
    target_=[]
    z=curs.rowcount
    print(z)
    for (n_cols,n_rows,n_cont,n_disc,n_ts,target) in rows:
        data.append([n_cols,n_rows,n_cont,n_disc,n_ts])
        target_.append(target)
    return data, target_

def updateTreeData(data, target):
    c=db_connect()
    curs=c.cursor()
    sql='insert into screech.tree_data (n_cols,n_rows,n_cont,n_disc,n_ts,target) values('
    for x in data:
        sql+=x+','
    sql+="'"+target+"')"
    print(sql)
    curs.execute(sql)
    c.commit()
    print("inserted data sucessfully")
    
    return 0

def calc_iqr(data):
    #get iqr from data
    iqr_value = iqr(data)    
    return iqr_value

def tree_predicition(tree, input_data):
    #run tree prediciton
    prediction=tree.predict_proba(input_data)
    #get order of output classes
    classes=tree.classes_
    output={}
    #map probability to output class
    for p,c in zip(prediction[0], classes):
        output[c] = p
    return output

def isDiscrete(data):
    discrete=False
    d=pd.Series(data)
    #get count of unique values and total count
    num_uniq = d.nunique()
    count = d.count()
    #check if percentage is less than threshold
    if (num_uniq/count)<=discrete_threshold:
        discrete=True
    return discrete

def isContinuous(data):
    continuous=False
    d=pd.Series(data)
    #get count of unique values and total count
    num_uniq = d.nunique()
    count = d.count()
    #check if percentage is less than threshold
    if (num_uniq/count)>=continuous_threshold:
        continuous=True
    return continuous

def isTimeSeries(data):
    time_series=False
    #get data into series
    d=pd.Series(data)
    #set counter of results to 0
    counter=0
    #get count of datapoints
    count=d.count()
    #check column name for date indicator
    header=False
    header_list=['year','date']
    for head in header_list:
        if re.search(head, d.name):
            header=True
    #loop over datapoints
    for x in d:
        #if point matches date regex, incerment counter
        match=re.search(regex['date'],str(x))
        if(match):
            counter+=1
    #if the count of matches is ge half total count, set to True
    if counter>=0.5*count or header:
        time_series=True
    return time_series

def generateTreeInput(data):
    #cast features to int
    nrows=int(data[0][0])
    ncols=len(data)
    n_cont=0
    n_disc=0
    n_ts=0
    #count bools from each col
    for col in data:
        if col[6]:
            n_cont+=1
        if col[7]:
            n_disc+=1
        if col[8]:
            n_ts+=1
    #add all features to list
    dataset=[[nrows, ncols, n_cont, n_disc, n_ts]]
    return dataset


def recommender(filename):
    #get data -- change to get from selected in front end
    data = get_file(filename)
    #get data for analysis and insert into dataframe
    clean=cols_from_json(data)
    test=pd.DataFrame(clean)
    #get basic statistics from data
    res = test.describe(include='all')
    #get keys to access dataframe
    keys=list(res.keys())
    pred=[]
    #loop over dataframe
    for key in keys:
        #get basic features from describe
        iqr=""#calc_iqr(clean[key])
        std_dev=res[key]['std']
        mean=res[key]['mean']
        data_min=res[key]['min']
        data_max=res[key]['max']
        count=res[key]['count']
        #add bools for data types
        continuous=isContinuous(res[key])
        discrete=isDiscrete(res[key])
        time_series=isTimeSeries(test[key])
        #add features to list
        data=[count, iqr, std_dev, mean, data_min, data_max, continuous, discrete, time_series]
        #add predicition to list
        pred.append(data)
    #get tree data, expand and pass to tree setup
    tree = tree_setup(*getTreeData())
    #generate data input for tree prediction
    tree_input = generateTreeInput(pred)
    #get recommendation from tree
    recommendations = tree_predicition(tree, tree_input)
    #reorder data_dict with x axis var first
    reordered_data = reorder_cols( test , pred)
    #return dict rather than df
    data_dict=reordered_data.to_dict('records')
    return recommendations, data_dict, pred, tree_input

def reorder_cols(data, info):
    #get list of columns from data
    cols=list(data.columns.values)
    #loop over booleans for data types
    for i in range(6,9):
        #loop over number of cols
        for x in range(0, len(cols)):
            #if bool is set
            if(info[x][i] and x>0):
                #pop col and append to front of list
                temp=cols.pop(x)
                temp2=info.pop(x)
                cols.insert(0, temp)
                info.insert(0, temp2)
    #reorder data with new col list
    reordered=data[cols]
    return reordered