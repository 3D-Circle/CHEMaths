var modes = [
    "this", "molecule", "equation", "empirical", "alkane"
];
var currentMode = "equation";
var MQ = MathQuill.getInterface(2);


function renderResult(result) {
    var mode = result.mode;
    render(mode);
    var syntax = result.syntax;
    var error = result.error;
    if (syntax == true) {
        $("#syntax_check_status").removeClass("syntax_error");
        $("#syntax_check_error_text").text("No problems found :)")
    } else {
        $("#syntax_check_status").addClass("syntax_error");
    }
    if (error) {
        $("#syntax_check_error_text").text(error);
    }
    if (mode == "molecule") {
        if (error) {
            // There are problems, so nothing will be rendered
            $('#molecular_formula').html('<p class=error>' + error + '</p>');
        } else  {
            // Molecular formula
            var molecular_formula = '';
            for (key in result.molecule) {
                if (key != 'sign') {
                    if (result.molecule[key] == 1) {
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
            $('#molar_mass>div').data('fullfloat', result.info['mr']);
            python_round([result.info['mr']], $('input#molar_mass_precision').val(), function (response) {
                $('#molar_mass>div').html(response.result);
            })

            // Components & percentages
            var composition = result.info.element_percentages;
            // this sorts dict keys according to concentration (http://stackoverflow.com/a/16794116/4489998)
            var sorted_elements = Object.keys(composition).sort(function(a,b){
                return composition[a]-composition[b]
            }).reverse();
            var array_to_round = sorted_elements.map(function(x) {
                return composition[x];
            });
            $("#components").html('');  //clean up components
            var precision = $('#components_precision').val();
            python_round(array_to_round, precision, function(rounded_array) {
                var element;
                var percentage;
                for (var i = 0; i < sorted_elements.length; i++) {
                    element = sorted_elements[i];
                    percentage = rounded_array.result[i];
                    $('#components').append('<div class="component" id="'+ element + '">' + element +
                    '<br><i><div>' + percentage +'</div>%</i></div>');
                }
                // check for multiple ids and remove duplicates
                var dup_id;
                $('[id]').each(function(){
                    var ids = $('[id="'+this.id+'"]');
                    if(ids.length>1 && ids[0]==this) {
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
            $('#oxidation').html(result.info.oxidation);

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

        // remove old data
        $("#info-equation > table").find("td").remove();
        // get and add new data
        if (error) {
            $("<td><span class='error'>" + error + "</span><td>").appendTo("#info-equation > table #reaction_type");
        } else {
            var total_length = 2 * reactants.length - 1 + 1 + 2 * products.length - 1;
            $("<td colspan=" + total_length + "><b>" + reaction_type + "</b></td>").appendTo("#info-equation > table #reaction_type");
            for (var i = 0; i < total_length; i++) {
                var molecule = "";
                var coefficient = "";
                var mole_index = null;
                var mass_index = null;
                if (i < 2 * reactants.length - 1) {
                    if (i % 2 == 0) {
                        var index = i / 2;
                        molecule = reactants[index];
                        coefficient = coefficients[index];
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
                        mole_index = reactants.length + index;
                        mass_index = reactants.length + index;
                    } else {
                        molecule = "+";
                    }
                }
                // create <td>'s
                var molecule_id = "equation-formula" + i;
                var coefficient_id = "equation-coefficient" + i;
                var mole_id = "equation-mole" + i;
                var mass_id = "equation-mass" + i;

                var molecule_span_html = "<span id='" + molecule_id + "'>" + molecule + "</span>"; // just in case
                var coefficient_span_html = "<span class='number'>" + coefficient + "</span>";
                var mole_span_html = "<span id='" + mole_id + "'></span>";
                var mass_span_html = "<span id='" + mass_id + "'></span>";

                if (coefficient != 1) {
                    molecule_span_html = coefficient_span_html + molecule_span_html;
                }

                // add to DOM
                var data_table = "#info-equation > table ";
                $("<td>" + molecule_span_html + "</td>").appendTo(data_table + "#formula");
                $("<td id='" + coefficient_id + "'>" + coefficient_span_html + "</td>").appendTo(data_table + "#coefficient");
                $("<td>" + mole_span_html + "</td>").appendTo(data_table + "#mole");
                $("<td>" + mass_span_html + "</td>").appendTo(data_table + "#mass");

                // add color themes
                var trivial = false;
                if (coefficient == "0") {
                    $("#" + molecule_id).addClass("nil");
                    if (i != 0 || i != 2 * reactants.length) {
                        $("#" + "equation-formula" + (i - 1)).addClass("nil");
                    }
                    $("#" + molecule_id).parent().addClass("trivial");
                    $("#" + coefficient_id).addClass("trivial");
                    $("#" + mole_id).parent().addClass("trivial");
                    $("#" + mass_id).parent().addClass("trivial");
                    trivial = true;
                }

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
                $("#" + mole_id).parent().addClass(color_theme_class);
                $("#" + mass_id).parent().addClass(color_theme_class);

                // render latex
                var molecule_span = $("#" + molecule_id)[0];
                molecule_display = MQ.StaticMath(molecule_span);
                molecule_display.latex(molecule);

                if ((mole_index !== null && mass_index !== null) && !trivial) {
                    var mole_span = $("#" + mole_id)[0];
                    var mass_span = $("#" + mass_id)[0];
                    $(mole_span).addClass("sub_field");
                    $(mass_span).addClass("sub_field");
                    mole_input = MQ.MathField(mole_span);
                    mass_input = MQ.MathField(mass_span);  // TODO add config and ajax
                }
            }
        }
    } else if (mode == "empirical") {
        // TODO this and fix float point issues
    } else if (mode == "alkane") {

    }
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
    var mainField = MQ.MathField(inputBox, {
        supSubsRequireOperand: true,
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
    renderResult({'mode': "this", "syntax": true, "error": "Welcome! Feed me chemistry :)"});

    // confirm input
    $('#mainField').submit(function (e) {
        $('<input />').attr('type', 'hidden')
            .attr('name', 'input')
            .attr('value', currentMode + '||' + mainField.latex())
            .appendTo(this);
        return true;
    });
    $('#input').keypress(function (e) {
        // submit form when enter is pressed
        if (e.which == 13) {
            $('#mainField').submit();
            return false;
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
            case "alkane":
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
