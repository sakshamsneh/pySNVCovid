import os
import re
from datetime import datetime
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


@app.route("/")
@app.route("/home/")
def home():
    return render_template("home.html")

# New functions
@app.route("/display/<filename>")
def display(filename=None):
    df = pd.read_csv(os.path.join(os.getcwd(), filename),
                     index_col=0, encoding="cp1252")
    data = df.head(20).to_html(
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
            return redirect(url_for('display', filename=filen))
        else:
            return redirect(url_for('home'))
