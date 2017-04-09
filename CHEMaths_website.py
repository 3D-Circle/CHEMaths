# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
import json
from string import ascii_uppercase
from flask import Flask, render_template, request, redirect
from CHEMaths import latex2chem, latex_valid
from CHEMaths import smart_calculate, process_and_balance_equation, get_ratio, Alkane
app = Flask(__name__)


@app.route("/")
def home():
    """renders home page of CHEMaths"""
    return render_template('index.html', name="homepage")


@app.route("/live_preview", methods=['POST'])
def live_process():
    """processes input dynamically"""
    mode = request.values.get('mode', None)
    latex = request.values.get('latex', None)
    print(mode, latex)
    return json.dumps({'result': latex2chem(latex)})


@app.route("/results", methods=['POST'])
def process():
    """processes input from home page and redirect to result tab"""

    return render_template('index.html', name="homepage")
    # return redirect('index.html', code=302, Response=None)  # TODO render results

if __name__ == "__main__":
    app.run()
