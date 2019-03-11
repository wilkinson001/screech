from flask import Flask, render_template, request, redirect
import os
from app import functions

print(os.getcwd())

app = Flask(__name__)
#change depending on setup
#app.config['UPLOAD_FOLDER']="E:\\onedrive\\y3\\dissertation\\flask\\uploads"
app.config['UPLOAD_FOLDER']="C:\\Users\\owilkinson\\onedrive\\y3\\dissertation\\flask\\uploads"

@app.route("/")
def index():
    z, r = functions.get_file_list("owilkinson")
    return render_template('html_templates/main_template_01.html', res_len=z, res=r)


@app.route("/local_file", methods = ['POST'])
def local():
    local_file=request.form['local_file']
    t=request.form['table_name']
    if local_file=="":
        print("no file submitted")
    else:
        print("Filename is: "+local_file)
    #call fileparser on local_file
    return parse_file(local_file,t)

@app.route("/upload", methods=['POST'])
def upload_file():
    if request.method=='POST':
        t=request.form['table_name']
        f=request.files['remote_file']
        f.save(os.path.join(app.config["UPLOAD_FOLDER"],f.filename))
        print("Saved file "+f.filename)
        #call file parser on saved file: os.path.join(app.config["UPLOAD_FOLDER"],f.filename)
    return parse_file(os.path.join(app.config["UPLOAD_FOLDER"],f.filename), t)

@app.route("/D3")
def d3():
    return render_template('html_templates/d3_template.html')


def parse_file(infile, intable):
    fname, file_name, file_ext = functions.fparse_name(infile)
        
    ncols, cols, maximum, fline = functions.fparse_attributes(fname)
    
    if(file_ext in functions.non_xl_types):
    
        #check if each row is consistent in file
        numcols = set(ncols).pop()
        if(len(set(ncols))==1):
            print("There are ",numcols," columns in the data")
        else:
            print("inconsistent number of columns")
            return redirect('/')
            ################################################
            #add logic for user to decide in gui which sep #
            ################################################
        coltypes= functions.fparse_coltypes(cols, numcols)
        
        #split up fparse_2 more
        new_coltypes = functions.fparse_2(numcols, cols, coltypes)
        
        functions.fparse_db(numcols, fline, new_coltypes, file_name, fname, maximum, intable) 
    
    elif(file_ext in functions.xl_types):
        print("excel operations")
    else:
        print("Invalid file type")
    
    return redirect('/')


@app.route("/test")
def test():
    #get data for d3 charts
    data = functions.get_file("test")
    #get data for analysis
    clean= functions.cols_from_json(data)
    print(clean)
    keys=list(clean.keys())
    predictions=[]
    for key in keys:
        iqr= functions.calc_iqr(clean[key])
        std_dev= functions.calc_std_dev(clean[key])
        mean= functions.calc_mean(clean[key])
        data_min= functions.calc_min(clean[key])
        data_max= functions.calc_max(clean[key])
        tree=""
        tree_input=[iqr, std_dev, mean, data_min, data_max]
        print(tree_input)
        predicition ="test"# functions.tree_prediction(tree, tree_input)
        predictions.append(predicition)
    return redirect('/')