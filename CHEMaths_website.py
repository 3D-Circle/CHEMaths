# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
from flask import Flask, render_template, request, redirect
from CHEMaths import process_formula, smart_calculate, process_and_balance_equation, get_ratio, Alkane
from .latex_parser import latex2chem
app = Flask(__name__)


@app.route("/")
def home():
    """renders home page of CHEMaths"""
    return render_template('index.html', name="homepage")


@app.route("/", methods=['POST'])
def process():
    """processes input from home page"""
    raw_input = request.form['input']
    print(raw_input)
    # processed_input = latex2chem(chem_input)
    mode, latex_input = raw_input.split("||")
    if mode == "molecule":
        pass
    elif mode == "equation":
        return process_and_balance_equation(latex_input, parser=latex2chem, split_token=("+", "\\rightarrow"))
    elif mode == "empirical":
        pass
    elif mode == "alkane":
        input_arguments = latex_input.split("::")
        size = int(input_arguments[1]) if len(input_arguments) == 2 else 1
        return "<div style='font-family: courier'>"\
               + Alkane(size).__str__().replace('\n', '<br/>')\
               + "</div>"
    else:
        return render_template('index.html', name="homepage")
    # return redirect('index.html', code=302, Response=None)  # TODO render results

if __name__ == "__main__":
    app.run()
