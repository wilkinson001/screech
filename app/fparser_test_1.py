from app import functions

fname, file_name, file_ext = functions.fparse_name(input("Enter path and filename:\n"))
    
ncols, cols, maximum, fline = functions.fparse_attributes(fname)

if(file_ext in functions.non_xl_types):

    #check if each row is consistent in file
    numcols = set(ncols).pop()
    if(len(set(ncols))==1):
        print("There are ",numcols," columns in the data")
    else:
        print("inconsistent number of columns")
        ################################################
        #add logic for user to decide in gui which sep #
        ################################################
    coltypes= functions.fparse_coltypes(cols, numcols)
    
    #split up fparse_2 more
    new_coltypes = functions.fparse_2(numcols, cols, coltypes)
    
    functions.fparse_db(numcols, fline, new_coltypes, file_name, fname, maximum, input("Please enter database table name:\n")) 

elif(file_ext in functions.xl_types):
    print("excel operations")
else:
    print("Invalid file type")