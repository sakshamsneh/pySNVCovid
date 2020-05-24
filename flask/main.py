import os
import re
from datetime import datetime
import pandas as pd
import json
from flask import Flask, redirect, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
df = pd.DataFrame()

masklist = []


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
    global masklist
    if request.method == 'POST':
        data = request.get_json()
        column = data['column']
        values = data['values']
        masklist.append(df[column].isin(values))
        return jsonify(data=True)


@app.route('/api/graph', methods=['GET'])
def get_graph_data():
    graph_fields = json.loads(request.args.get('graph_fields'))
    global df
    global masklist
    s = pd.Series()
    if masklist:
        s = masklist[0]
        if len(masklist) > 1:
            for m in masklist[1:]:
                s &= m
    if s.empty:
        return df[graph_fields].to_json()
    else:
        return df[s][graph_fields].to_json()
