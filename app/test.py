from flask import Flask, render_template, request
import json
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/prepare_data")
def prepare_some_data():
    output = {}
    output['some_data'] = [5,2,1,6,4,8]
    output['some_text'] = 'data values'
    return json.dumps(output)


if __name__ == "__main__":
    app.run(host='localhost',port=7234,debug=True)