import os
import re
from datetime import datetime
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
df = pd.DataFrame()


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


@app.route('/api/column', methods=['GET', 'POST'])
def ret_values():
    global df
    column = request.args['column']
    if request.method == 'GET':
        return jsonify(collist=list(df[column].dropna().unique()))
    elif request.method == 'POST':
        # write/filter df on the column unique values, return/update table from here
        values = request.args['values']
        data = df[df[column].isin(values)].head(100).to_html(
            classes="table table-hover table-dark table-responsive table-sm")
        return jsonify(data=data)
