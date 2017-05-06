# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
from flask import Flask, jsonify, render_template, request
from latex_parser import latex_valid, determine_mode
from CHEMaths import Molecule

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
        if not error:
            parsed_molecule = syntax_check[1]
            molecule = Molecule(parsed_molecule, raw_string=latex)
            return jsonify({
                'error': error,
                'mode': mode,
                'syntax': syntax_check[0],
                'molecule': parsed_molecule,
                'info': {
                    'mr': molecule.mr,
                    'element_percentages': molecule.calculate_percentages(),
                    'oxidation': {
                        element: str(molecule.calculate_oxidation()[element])
                        for element in molecule.calculate_oxidation().keys()
                    }
                }
            })
    elif mode == 'equation':
        if not error:
            reactants, products, equation = syntax_check[1]
            return jsonify({
                'mode': mode,
                'syntax': syntax_check[0],
                'reaction_type': equation.get_reaction_type(),
                'reactants': reactants,
                'products': products,
                'coefficients': equation.balance(),
                'mr': equation.calculate_relative_formula_masses(),
                'error': error
            })
    elif mode == 'organic':
        if not error:
            functional_group = syntax_check[1]
            return jsonify({
                'organic-name': functional_group.get_name().capitalize(),
                'molecular-formula': functional_group.molecule.latex_molecular_formula,
                'isomers-number': functional_group.calculate_isomer_numbers(),
                'combustion-enthalpy': str(functional_group.calculate_combustion_enthalpy()) + " kJ mol<sup>-1</sup>",
                'lewis-structure': functional_group.get_lewis(sep='<br/>'),
                'mode': mode,
                'syntax': syntax_check[0]
            })
    return jsonify({
        'error': error,
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


@app.route("/equation_mass2mole", methods=['POST'])
def equation_mass_to_mole():
    """Convert """
    masses_array = request.values.get('masses')

if __name__ == "__main__":
    app.run()
