import os
import re
from datetime import datetime
import pandas as pd
import json
from flask import Flask, redirect, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
df = pd.DataFrame()

maskdict = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


def start_df(filename):
    global df
    df = pd.read_csv(os.path.join(os.getcwd(), filename),
                     index_col=0, encoding="cp1252")


@app.route("/")
@app.route("/home/")
def home():
    return render_template("home.html")


@app.route("/display/<filename>")
def display(filename=None):
    global df
    data = df.head(100).to_html(
        classes="table table-hover table-dark table-responsive table-sm")
    collist = df.columns
    return render_template("table.html", data=data, collist=collist)


@app.route('/api/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['csvfile']
        if f and allowed_file(f.filename):
            filen = secure_filename(f.filename)
            f.save(os.path.join(os.getcwd(), filen))
            start_df(filen)
            return redirect(url_for('display', filename=filen))
        else:
            return redirect(url_for('home'))


@app.route('/api/column', methods=['GET'])
def ret_col_values():
    global df
    column = request.args['column']
    if request.method == 'GET':
        return jsonify(collist=list(df[column].dropna().unique()))


@app.route('/api/columnvalues', methods=['POST'])
def get_selcol_values():
    global df
    global maskdict
    if request.method == 'POST':
        data = request.get_json()
        column = data['column']
        if column[0] in maskdict.keys():
            del maskdict[column[0]]
        if('values' in data):
            values = data['values']
            maskdict[column] = values
        return jsonify(data=True)


@app.route('/api/graph', methods=['GET'])
def get_graph_data():
    graph_fields = json.loads(request.args.get('graph_fields'))
    global df
    global maskdict
    s = pd.Series()
    if maskdict:
        column = list(maskdict.keys())[0]
        values = maskdict[column]
        s = df[column].isin(values)
        for column, values in list(maskdict.items())[1:]:
            k = df[column].isin(values)
            s &= k
    if s.empty:
        return df[graph_fields].to_json(orient="index")
    else:
        return df[s][graph_fields].to_json(orient="index")
