var modes = [
    "this", "molecule", "equation", "empirical", "organic"
];
var count = 0;  // keep record of how many times render_results is called
var MQ = MathQuill.getInterface(2);
var mainField;  // global variable
var molecule_mass_entry, molecule_mole_entry, masses_input, moles_input;
var currentMode = 'this';
var urlData;  // pre-written in index.html


function retrieveUrlData() {
    var data = {
        'mode': currentMode,
        'Input': mainField.latex(),
    };

    var sub_inputs = {};

    if (currentMode == 'molecule') {
        var mass = molecule_mass_entry.latex();
        var mole = molecule_mole_entry.latex();

        sub_inputs.mass = mass;
        sub_inputs.mole = mole;
    }
    if (currentMode == 'equation') {
        sub_inputs.masses = [];
        sub_inputs.moles = [];

        for (var i = 0; i < masses_input.length; i++) {
            sub_inputs.masses.push(masses_input[i].latex());
            sub_inputs.moles.push(moles_input[i].latex());
        }
    }

    data.inputs = JSON.stringify(sub_inputs);

    return $.param(data);
}


function renderResult(result) {
    var mode = currentMode = result.mode;
    render(mode);
    var syntax = result.syntax;
    var error = result.error;
    if (syntax === true) {
        $("#syntax_check_status").removeClass("syntax_error");
    } else {
        $("#syntax_check_status").addClass("syntax_error");
    }
    if (mode === "molecule") {
        if (error) {
            // There are problems, so nothing will be rendered
            $('#molecular_formula').html('<p class=error>' + error + '</p>');
        } else {
            // Molecular formula
            var molecular_formula = '';
            for (key in result.molecule) {
                if (key !== 'sign') {
                    if (result.molecule[key] === 1) {
                        molecular_formula += key;
                    } else {
                        molecular_formula += key + '_{' + result.molecule[key] + '}';
                    }
                }
            }

            $('#molecular_formula').html('<span></span>');  // TODO: order the elements correctly
            var molecular_formula_span = $('#molecular_formula>span')[0];
            molecular_formula_display = MQ.StaticMath(molecular_formula_span);
            molecular_formula_display.latex(molecular_formula);

            // Name
            $('#name').html('To be implemented...');

            // Molar mass TODO: add option to change units ?
            $('#molar_mass').html('<div></div> g / mol')
            $('#molar_mass>div').data('fullfloat', result.info.mr);
            python_round([result.info.mr], $('input#molar_mass_precision').val(), function (response) {
                $('#molar_mass>div').html(response.result);
            });

            // Components & percentages
            var composition = result.info.element_percentages;
            // this sorts dict keys according to concentration (http://stackoverflow.com/a/16794116/4489998)
            var sorted_elements = Object.keys(composition).sort(function (a, b) {
                return composition[a] - composition[b];
            }).reverse();
            var array_to_round = sorted_elements.map(function (x) {
                return composition[x];
            });
            $("#components").html('');  //clean up components
            var precision = $('#components_precision').val();
            python_round(array_to_round, precision, function (rounded_array) {
                var element;
                var percentage;
                for (var i = 0; i < sorted_elements.length; i++) {
                    element = sorted_elements[i];
                    percentage = rounded_array.result[i];
                    $('#components').append(
                        '<div class="component" id="' + element + '">'
                        + element + '<br><i><div>' + percentage
                        + '</div>%</i></div>'
                    );
                }
                // check for multiple ids and remove duplicates
                var dup_id;
                $('[id]').each(function(){
                    var ids = $('[id="'+this.id+'"]');
                    if(ids.length > 1 && ids[0] == this) {
                        dup_id = this.id;
                    }
                });
                $('#' + dup_id).remove();

                for (var i = 0; i < sorted_elements.length; i++) {
                    element = sorted_elements[i];
                    true_percentage = array_to_round[i];
                    $('#' + element).find('div').data('fullfloat', true_percentage);
                }
            });

            // Oxidation
            $("#info-molecule > table").find(".component").remove();
            var oxidation = result.info.oxidation;
            for (var element in oxidation) {
                if (oxidation.hasOwnProperty(element)) {  // typical js
                    var oxidation_number = oxidation[element];
                    $('#oxidation').append(
                        '<div class=component>'
                        + element
                        + '<br/><i>' + oxidation_number + '</i>'
                        + "</div>"
                    );
                }
            }

            // Mass and mole

            molecule_mole_entry = MQ.MathField($('#molecule_mole_entry')[0], {
                handlers: {
                    edit: function () {
                        var current_molecule = mainField.latex();

                        if (molecule_mole_entry.latex().includes('*')) {
                            molecule_mole_entry.blur()
                            $.when(molecule_mole_entry.latex(
                                molecule_mole_entry.latex().replace('*', '\\times')
                            )).then(molecule_mole_entry.focus());
                        }

                        if ($('#molecule_mole_entry').hasClass('mq-focused')) {
                            $.ajax({
                                url: "/mass_mole",
                                type: "post",
                                data: {
                                    "molecule_latex": current_molecule,
                                    "mole": molecule_mole_entry.latex(),
                                },
                                success: function (data) {
                                    // set the other one to calculated value
                                    if (data['error']) {
                                        console.warn(data['error'])
                                        molecule_mole_entry.blur()
                                        $.when(molecule_mole_entry.latex(data['correct'])).then(molecule_mole_entry.focus());
                                        //molecule_mole_entry.focus()
                                    } else if (data['mass']) {
                                        molecule_mass_entry.latex(data['mass']);
                                    } else {
                                        molecule_mass_entry.latex('0')
                                    }
                                }
                            });
                        }
                    }
                }
            })
            molecule_mole_entry.latex(urlData.inputs.mole ? urlData.inputs.mole : '');

            molecule_mass_entry = MQ.MathField($('#molecule_mass_entry')[0], {
                handlers: {
                    edit: function () {
                        var current_molecule = mainField.latex();

                        if (molecule_mass_entry.latex().includes('*')) {
                            molecule_mass_entry.blur()
                            $.when(molecule_mass_entry.latex(
                                molecule_mass_entry.latex().replace('*', '\\times')
                            )).then(molecule_mass_entry.focus());
                        }

                        if ($('#molecule_mass_entry').hasClass('mq-focused')) {
                            $.ajax({
                                url: "/mass_mole",
                                type: "post",
                                data: {
                                    "molecule_latex": current_molecule,
                                    "mass": molecule_mass_entry.latex(),
                                },
                                success: function (data) {
                                    // set the other one to calculated value
                                    if (data['error']) {
                                        console.warn(data['error'])
                                        molecule_mass_entry.blur()
                                        $.when(molecule_mass_entry.latex(data['correct'])).then(molecule_mass_entry.focus());
                                        //molecule_mole_entry.focus()
                                    } else if (data['mole']) {
                                        molecule_mole_entry.latex(data['mole']);
                                    } else {
                                        molecule_mole_entry.latex('0')
                                    }
                                }
                            });
                        }
                    }
                }
            })
            molecule_mass_entry.latex(urlData.inputs.mass ? urlData.inputs.mass : '');

            // Set all precision range inputs to 2
            $.makeArray($('.precision')).map(function (slider) {
                    return $(slider).val(2);
                }
            );
        }

    } else if (mode == "equation") {
        // mr jingjie
        var reaction_type = result.reaction_type;
        var reactants = result.reactants;
        var products = result.products;
        var coefficients = result.coefficients;
        var relative_formula_mass = result.mr;
        // for reconstruction of Equation
        var parsed = result.parsed;
        
        masses_input = [];
        moles_input = [];

        var local_MQ_config = {
            spaceBehavesLikeTab: true,
            supSubsRequireOperand: true,
            handlers: {
                edit: function(mathField) {
                    var mass_array_latex = [];
                    var mole_array_latex = [];
                    masses_input.forEach(function (MQinput, _, _) {
                        mass_array_latex.push(MQinput.latex());
                    });
                    moles_input.forEach(function (MQinput, _, _) {
                        mole_array_latex.push(MQinput.latex());
                    });

                    $.ajax({
                        url: "/mass_mole_equation",
                        type: "POST",
                        data: JSON.stringify({
                                'components': parsed,
                                'mass_array': mass_array_latex,
                                'mole_array': mole_array_latex
                        }),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            console.log(data);
                            reaction_masses = data.reaction_masses;
                            reaction_moles = data.reaction_moles;
                            for (var i = 0; i < reaction_masses.length; i++) {
                                index = i * 2;
                                $('#equation-reaction-mass' + index).text(reaction_masses[i]);
                                $('#equation-reaction-mole' + index).text(reaction_moles[i]);
                            }
                        }
                    })
                },
            }
        };

        // remove old data
        $("#info-equation > table").find("td").remove();
        // get and add new data
        if (error) {
            $("<td><span class='error'>" + error + "</span><td>").appendTo("#info-equation > table #reaction_type");
        } else {
            // ARCHIVE FOR READABILITY
            // var total_length = 2 * reactants.length - 1 + 1 + 2 * products.length - 1;
            var total_length = 2 * reactants.length + 2 * products.length - 1;
            $("<td colspan=" + total_length + "><b>" + reaction_type + "</b></td>").appendTo("#info-equation > table #reaction_type");

            for (var i = 0; i < total_length; i++) {
                var molecule = "";
                var coefficient = "";
                var mr = "";
                var mole_index = null;
                var mass_index = null;
                if (i < 2 * reactants.length - 1) {
                    if (i % 2 == 0) {
                        var index = i / 2;
                        molecule = reactants[index];
                        coefficient = coefficients[index];
                        mr = relative_formula_mass[index];
                        mole_index = index;
                        mass_index = index;
                    } else {
                        molecule = "+";
                    }
                } else if (i == 2 * reactants.length - 1) {
                        molecule = "\\rightarrow";
                } else {
                    if (i % 2 == 0) {
                        var index = (i - 2 * reactants.length) / 2;
                        molecule = products[index];
                        coefficient = coefficients[reactants.length + index];
                        mr = relative_formula_mass[reactants.length + index];
                        mole_index = reactants.length + index;
                        mass_index = reactants.length + index;
                    } else {
                        molecule = "+";
                    }
                }
                // create <td>'s
                var molecule_id = "equation-formula" + i;
                var coefficient_id = "equation-coefficient" + i;
                var mr_id = "equation-mr" + i;
                var mole_id = "equation-mole" + i;
                var mass_id = "equation-mass" + i;
                var mole_reaction_id = "equation-reaction-mole" + i;
                var mass_reaction_id = "equation-reaction-mass" + i;

                var molecule_span_html = "<span id='" + molecule_id + "'>" + molecule + "</span>"; // just in case
                var coefficient_span_html = "<span class='number'>" + coefficient + "</span>";
                var mr_span_html = "<span id='" + mr_id + "'>" + mr + "</span>";
                var mole_span_html = "<span id='" + mole_id + "'></span>";
                var mass_span_html = "<span id='" + mass_id + "'></span>";
                var mole_reaction_span_html = "<span id='" + mole_reaction_id + "'>";
                var mass_reaction_span_html = "<span id='" + mass_reaction_id + "'>"

                if (coefficient > 1) {
                    molecule_span_html = coefficient_span_html + molecule_span_html;
                }

                // add to DOM
                var data_table = "#info-equation > table ";
                $("<td>" + molecule_span_html + "</td>").appendTo(data_table + "#formula");
                $("<td id='" + coefficient_id + "'>" + coefficient_span_html + "</td>").appendTo(data_table + "#coefficient");
                $("<td>" + mr_span_html + "</td>").appendTo(data_table + "#mr");
                $("<td>" + mole_span_html + "</td>").appendTo(data_table + "#mole");
                $("<td>" + mass_span_html + "</td>").appendTo(data_table + "#mass");
                $("<td>" + mole_reaction_span_html + "</td>").appendTo(data_table + "#reaction-mole");
                $("<td>" + mass_reaction_span_html + "</td>").appendTo(data_table + "#reaction-mass");

                var color_theme_class = "";
                switch (molecule) {
                    case "\\rightarrow":
                        color_theme_class = "left_is_reactants_right_is_products";
                        break;
                    case "+":
                        color_theme_class = "trivial";
                }

                $("#" + molecule_id).parent().addClass(color_theme_class);
                $("#" + coefficient_id).addClass(color_theme_class);
                $("#" + mr_id).parent().addClass(color_theme_class)
                $("#" + mole_id).parent().addClass(color_theme_class);
                $("#" + mass_id).parent().addClass(color_theme_class);
                $("#" + mole_reaction_id).parent().addClass(color_theme_class);
                $("#" + mass_reaction_id).parent().addClass(color_theme_class);

                // render latex
                var molecule_span = $("#" + molecule_id)[0];
                var molecule_display = MQ.StaticMath(molecule_span);
                molecule_display.latex(molecule);

                if (mole_index !== null && mass_index !== null) {
                    var mole_span = $("#" + mole_id)[0];
                    var mass_span = $("#" + mass_id)[0];
                    $(mole_span).addClass("sub_field");
                    $(mass_span).addClass("sub_field");
                    
                    var local_MQ_config1 = $.extend({}, local_MQ_config);  // VERY REQUIRED
                    var local_MQ_config2 = $.extend({}, local_MQ_config);  // VERY REQUIRED
                    
                    var mole_input = MQ.MathField(mole_span, local_MQ_config1);  // if removed, this will not work
                    var mass_input = MQ.MathField(mass_span, local_MQ_config2);  // if removed, this will not work
                    
                    masses_input.push(mass_input);
                    moles_input.push(mole_input);
                }
            }
            for (var i = 0; i < masses_input.length; i++) {
                masses_input[i].latex(urlData.inputs.masses[i] ? urlData.inputs.masses[i] : '');
                moles_input[i].latex(urlData.inputs.moles[i] ? urlData.inputs.moles[i] : '');
            }
        }
    } else if (mode == "empirical") {
        // TODO this and fix float point issues
    } else if (mode == "organic") {
        var error = result.error;
        if (error) {
            $('#organic-name').html('<p class=error>' + error + '</p>');
        } else {
            for (var key in result) {
                if (key != 'mode' && key != 'syntax') {
                    if (key == 'lewis-structure') {
                        $('td#' + key).html('<pre>' + result[key] + '</pre>');
                    } else if (key == 'molecular-formula' || key == 'condensed-structural-formula') {
                        alkane_molecule_display = MQ.StaticMath($('td#' + key + '>span')[0]);
                        alkane_molecule_display.latex(result[key]);
                    } else {
                        $('td#' + key).html(result[key]);
                    }
            }
        }
        }
    }
    count++;
}

// update render
function render(mode) {
    for (var i = 0; i < modes.length; i++) {
        var option = modes[i];
        if (option == mode) {
        // update status label
            $("#" +  option).addClass("selected");
            // update right panel for additional information
            var $target = $("#info-" + option);
            var $other = $target.siblings('.active');

            if (!$target.hasClass('active')) {
                $other.each(function(index, self) {
                    var $this = $(self);
                    $this.removeClass('active').animate({
                        left: $this.width()
                    }, 500);
                });

                $target.addClass('active').show().css({
                    left: -($target.width())
                }).animate({
                    left: 0
                }, 500);
            }
        } else {
            // update status label
            $('#' + option).removeClass("selected");
        }
    }
}

// python round function takes precision as an argument (unlike js!)
function python_round(num_array, precision, callback) {
    // if you want only one value, use an array with one element
    $.ajax({
        url: "/round",
        type: "post",
        data: {
            "num_array": num_array,
            "precision": precision
        },
        success: callback
    });
}


$(document).ready(function () {
    // set up input box
    var inputBox = $('#input')[0];
    mainField = MQ.MathField(inputBox, {
//        spaceBehavesLikeTab: true,
        supSubsRequireOperand: true,
        charsThatBreakOutOfSupSub: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        handlers: {
            edit: function () {
                // update render
                var latex = mainField.latex();
                if (latex.includes("->")) {
                    var new_latex = latex.replace("->", "\\rightarrow ");
                    mainField.latex(new_latex);
                    latex = mainField.latex();
                }

                // ajax request for live preview
                $.ajax({
                    url: "/live_preview",
                    type: "post",
                    data: {
                        "latex": latex
                    },
                    success: function(response){
                        renderResult(response);
                    }
                });
            }
        }
    });

    mainField.focus();
    mainField.latex(urlData.Input);

    $('#enter').hover(function () {
        $('#enter')[0].href = '?' + retrieveUrlData();
    })

    $(document).keypress(function(e) {
        if(e.which == 13) {
            $('#enter')[0].href = '?' + retrieveUrlData();

            $('#enter')[0].click();
        }
    });

    // set up buttons for symbols for input box
    $('#rightarrow').click(function () {
        mainField.cmd('\\rightarrow');
        mainField.focus();
    });
    $('#sup').click(function () {
        mainField.cmd('^');
        mainField.focus();
    });
    $('#sub').click(function () {
        mainField.cmd('_');
        mainField.focus();
    });
    $('#left-parenthesis').click(function () {
        mainField.cmd('(');
        mainField.focus();
    });
    $('#right-parenthesis').click(function () {
        mainField.cmd(')');
        mainField.focus();
    });
    $('#plus').click(function () {
        mainField.cmd('+');
        mainField.focus();
    });
    $('#colon').click(function () {
        mainField.cmd(':') ;
        mainField.focus();
    });
    $('#semi-colon').click(function () {
        mainField.cmd(';');
        mainField.focus();
    });


    // show template when status label is clicked
    $('.status').click(function (e) {
        var mode = $(this).attr('id');
        var text;
        switch(mode) {
            case "molecule":
                text = "O_2";
                break;
            case "equation":
                text = "H_2O \\rightarrow O_2 + H^+ + e^-";
                break;
            case "empirical":
                text = "K: 1.82, I: 5.93, O: 2.24";
                break;
            case "organic":
                text = "alkane::5";
                break;
            default:
                text = "";
        }
        mainField.latex(text);
        mainField.focus();
        mainField.moveToLeftEnd();
        mainField.select();

        e.stopImmediatePropagation();

    });

  // gitter chat for feedback
  ((window.gitter = {}).chat = {}).options = {
    room: 'CHEMaths/Lobby'
  };


    // precision sliders change detection
    $('input.precision').each(function() {
        var elem = $(this);
        // Look for changes in the value
        elem.bind("input", precision_change);
    });

});

function precision_change(event) {
    // change digits upon precision range input change
    var elem = event.target;
    var precision = elem.value;
    // get which value we have to change
    var target_wrapper_id = elem.id.split('_');
    target_wrapper_id.pop();
    target_wrapper_id = target_wrapper_id.join('_');
    var target_wrapper = $('#' + target_wrapper_id);
    var components = target_wrapper.find(".component").toArray();  //will be empty if there are none
    var current_full_float_array;
    if (components.length) {
        var current_component_id;
        components.forEach(function(current_component) {
            current_component_id = $(current_component).attr('id');
            current_full_float_array = [$('#' + current_component_id).find('i').find('div').data('fullfloat')];
            (function(c_id) {
                python_round(current_full_float_array, precision, function (response) {
                    $('#' + c_id).find('i').find('div').html(response.result);
                })
            })(current_component_id)
        });
    } else {
        current_full_float_array = [target_wrapper.find('div').data('fullfloat')];
        python_round(current_full_float_array, precision, function (response) {
            target_wrapper.find('div').html(response.result);
        })
    }
}
