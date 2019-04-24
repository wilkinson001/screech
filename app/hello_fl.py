from flask import Flask, render_template, request, redirect, session
import os
from app import functions
import pandas as pd
import operator
import hashlib

app = Flask(__name__)
#change depending on setup
#app.config['UPLOAD_FOLDER']="E:\\onedrive\\y3\\dissertation\\flask\\uploads"
app.config['UPLOAD_FOLDER']='/uploads'
#app.config['UPLOAD_FOLDER']="C:\\Users\\owilkinson\\onedrive\\y3\\dissertation\\flask\\uploads"
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#set session key
app.secret_key=os.urandom(24)

@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        z, r = functions.get_file_list(username)
        return render_template('html_templates/main_template_01.html', res_len=z, res=r)
    return redirect("/login")

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method=='POST':
        user = request.form['username']
        pword = request.form['pword']
        #encrypt password before leaving function
        hashed = hashlib.md5()
        hashed.update(pword.encode('UTF-8'))
        #check db for user and password
        if(functions.checkUser(user, hashed.hexdigest())):
            #if true, create session and return to index
            session['username']=user
            return redirect("/")
    return render_template('html_templates/login.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method=='POST':
        fname = request.form['fname'].lower()
        lname = request.form['lname'].lower()
        pword = request.form['pword']
        user=fname[0]+lname
        c=1
        #check if username exists on database
        if(functions.checkUserExists(user)):
            while (functions.checkUserExists(user + str(c)) == True):
                c+=1
            username=user+str(c)
        else:
            username=user
        #encrypt password before leaving function
        hashed = hashlib.md5()
        hashed.update(pword.encode('UTF-8'))
        #add new user to database
        functions.createUser(username, hashed.hexdigest())
        session['username']=username
        return registered(username, pword)
    return render_template('html_templates/register.html')

@app.route("/registered")
def registered(user, pword):
    return render_template('html_templates/registered.html', username=user, password=pword)

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

@app.route("/recommend", methods=['POST'])
def recommend():
    if request.method=='POST':
        filename = request.form['selected']
        recommendation, data, pred, tree_input = functions.recommender(filename)
        #reorder recommendation into descending order
        sorted_rec=dict(sorted(recommendation.items(), key=operator.itemgetter(1), reverse=True))
        for frec in sorted_rec.keys():
            first_rec_key=frec
            break
        #get list of keys for d3 chart data processing
        keys_list=list(data[0].keys())
        #get max value for d3 chart domain mapping
        max_vals=[]
        #key_types=dict()
        counter=0
        for m in pred:
            max_vals.append(m[5])
            #key_types[keys_list[counter]]={'continuous': m[6], 'discrete':m[7], 'time_series':m[8]}
            counter+=1
        max_val=max(max_vals)
    return render_template(
        'html_templates/d3_template.html', 
        #r=recommendation,
        r=sorted_rec,
        d=data, 
        keys=keys_list, 
        maximum=max_val,
        prediction=tree_input,
        first_rec=first_rec_key
    )


@app.route("/use_chart", methods=['POST'])
def add_rec():
    if request.method=='POST':
        #get data from form
        recommendation=request.form['post_recommendation']
        chart=request.form['post_chart']
        #split tree input on comma
        r=recommendation.split(',')
        #insert into database for updated tree
        functions.updateTreeData(r, chart)
    return redirect('/')



def parse_file(infile, intable):
    fname, file_name, file_ext = functions.fparse_name(infile)
    
    if(file_ext in functions.non_xl_types):
        ncols, cols, maximum, fline = functions.fparse_attributes(fname)
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
        
        functions.fparse_db(numcols, fline, new_coltypes, file_name, fname, maximum, intable, session['username']) 
    
    elif(file_ext in functions.xl_types):
        print("excel operations")
    else:
        print("Invalid file type")
    
    return redirect('/')
