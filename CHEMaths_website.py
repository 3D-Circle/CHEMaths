# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
from flask import Flask, jsonify, render_template, request, redirect
from latex_parser import latex2chem, latex_valid
from CHEMaths import smart_calculate, process_and_balance_equation, get_ratio, Alkane

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def home():
    """renders home page of CHEMaths"""
    return render_template('index.html', name="homepage")


@app.route("/live_preview", methods=['POST'])
def live_process():
    """processes input dynamically"""
    mode = request.values.get('mode')
    latex = request.values.get('latex')
    if mode == 'molecule':
        return jsonify({
            'molecule': latex2chem(latex),
            'info': smart_calculate(latex2chem(latex), {})  # TODO: make the empty dict editable
        })
    elif mode == 'equation':
        result = process_and_balance_equation(
            latex,
            parser=latex2chem,
            regex=True,
            split_token=(r"[eA-Z][_A-Za-z\d]*(?:\^\{?\d*[\+-]\}?)?", '\\rightarrow '),
            return_string=False
        )
        reactants, products, coefficients, error = None, None, None, None
        try:
            reactants, products, coefficients = result
        except ValueError:  # too many values to unpack
            error = result
        else:
            coefficients = [
                f'{fraction.numerator}' for fraction in coefficients
            ]  # encode fractions in json
        return jsonify({
            'reactants': reactants,
            'products': products,
            'coefficients': coefficients,
            'error': error
        })


@app.route('/round', methods=['GET', 'POST'])
def python_round():
    num_array = request.form.getlist("num_array[]", type=float)
    precision = int(request.values.get('precision', 2))
    return jsonify({'result': [round(i, precision) for i in num_array]})


@app.route("/results", methods=['POST'])
def process():
    """processes input from home page and redirect to result tab"""

    return render_template('index.html', name="homepage")
    # return redirect('index.html', code=302, Response=None)  # TODO render results

if __name__ == "__main__":
    app.run()
