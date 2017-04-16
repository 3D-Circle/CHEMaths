# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
from flask import Flask, jsonify, render_template, request, redirect
from latex_parser import latex2chem, latex_valid, determine_mode
from CHEMaths import smart_calculate, process_and_balance_equation, get_ratio, Alkane
from CHEMaths import determine_reaction_type

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def home():
    """renders home page of CHEMaths"""
    return render_template('index.html', name="homepage")


@app.route("/live_preview", methods=['POST'])
def live_process():
    """processes input dynamically"""
    latex = request.values.get(
        'latex'
    ).replace("\\ ", '').replace(" ", '').replace("\\left(", '(').replace(r"\right)", ')')
    mode = determine_mode(latex)
    syntax_check = latex_valid(latex, mode)
    error = syntax_check[1] if not syntax_check[0] else None
    if mode == 'this':
        return jsonify({
            'mode': mode,
            'syntax': syntax_check[0],
            'error': syntax_check[1]  # more like a welcoming note than an error :)
        })
    elif mode == 'molecule':
        if error:
            return jsonify({
                'error': error,
                'mode': mode,
                'syntax': syntax_check[0]
            })
        else:
            parsed_molecule = syntax_check[1]
            return jsonify({
                'error': error,
                'mode': mode,
                'syntax': syntax_check[0],
                'molecule': parsed_molecule,
                'info': smart_calculate(parsed_molecule, {})  # TODO: make the empty dict editable
            })
    elif mode == 'equation':
        reaction_type, reactants, products, coefficients = None, None, None, None
        if not error:
            reactants, products, coefficients = syntax_check[1]
            reaction_type = determine_reaction_type(reactants, products, coefficients)
            coefficients = [f'{fraction.numerator}' for fraction in coefficients]
        return jsonify({
            'mode': mode,
            'syntax': syntax_check[0],
            'reaction_type': reaction_type,
            'reactants': reactants,
            'products': products,
            'coefficients': coefficients,
            'error': error
        })
    else:
        return jsonify({
            'mode': mode,
            'syntax': syntax_check[0]
        })


@app.route('/round', methods=['GET', 'POST'])
def python_round():
    """Round the input number to the input precision from the request,
    simply because rounding in javascript is AWFUL."""
    num_array = request.form.getlist("num_array[]", type=float)
    precision = int(request.values.get('precision', 2))
    return jsonify({
        'result': [format(round(i, precision), f'.{precision}f') for i in num_array]
    })


@app.route("/results", methods=['POST'])
def process():
    """processes input from home page and redirect to result tab"""

    return render_template('index.html', name="homepage")
    # return redirect('index.html', code=302, Response=None)  # TODO render results

if __name__ == "__main__":
    app.run()
