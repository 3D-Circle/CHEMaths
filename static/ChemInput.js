var modes = [
    "this", "molecule", "equation", "empirical", "alkane"
];
var currentMode = "equation";
var MQ = MathQuill.getInterface(2);


function renderResult(result) {
    var mode = result.mode;
    render(mode);
    if (mode == "molecule") {
        // Molecular formula
        var molecular_formula = '';
        for (key in result.molecule) {
            if (key != 'sign') {
                molecular_formula += key + '_{' + result.molecule[key] + '}';
            }
        }
        $('#molecular_formula').html(molecular_formula);

        // Name
        $('#name').html('To be implemented...');

        // Molar mass TODO: add option to change units ?
        $('#molar_mass').html('<div></div> g / mol')
        $('#molar_mass>div').data('fullfloat', result.info['mr']);
        python_round([result.info['mr']], $('input#molar_mass_precision').val(), function (response) {
            $('#molar_mass>div').html(response.result);
        })
        console.log($('#molar_mass>div').data('fullfloat'));


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
        var precision = 2;  // TODO: Replace with slider
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
        var dummy = $('.precision').map(function (e) {

            }
        );


    } else if (mode == "equation") {
        // mr jingjie
        console.log(result);
        var reaction_type = result.reaction_type;
        var reactants = result.reactants;
        var products = result.products;
        var coefficients = result.coefficients;
        var error = result.error;

        // remove old data
        $("#info-equation > table").find("td").remove();
        // add new data
        if (error) {
            $("<td><span class='error'>" + error + "</span><td>").appendTo("#info-equation > table #reaction_type");
        } else {
            var total_length = 2 * reactants.length - 1 + 1 + 2 * products.length - 1;
            $("<td colspan=" + total_length + "><b>" + reaction_type + "</b></td>").appendTo("#info-equation > table #reaction_type");
            for (var i = 0; i < total_length; i++) {
                var molecule = "";
                var coefficient = "";
                if (i < 2 * reactants.length - 1) {
                    if (i % 2 == 0) {
                        var index = i / 2;
                        molecule = reactants[index];
                        coefficient = coefficients[index];
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
                    } else {
                        molecule = "+";
                    }
                }

                var molecule_id = "equation-formula" + i;
                var coefficient_id = "equation-coefficient" + i;

                var molecule_span_html = "<span class='data' id='" + molecule_id+ "'>" + molecule + "</span>";
                var coefficient_span_html = "<span class='data number'>" + coefficient + "</span>";

                if (coefficient != 1) {
                    molecule_span_html = coefficient_span_html + molecule_span_html;
                }

                $("<td>" + molecule_span_html + "</td>").appendTo("#info-equation > table #formula");
                $("<td id='" + coefficient_id + "'>" + coefficient_span_html + "</td>").appendTo("#info-equation > table #coefficient");

                if (coefficient == "0") {
                    $("#" + molecule_id).addClass("nil");
                    if (i != 0 || i != 2 * reactants.length) {
                        $("#" + "equation-formula" + (i - 1)).addClass("nil");
                    }
                }

                if (molecule == "\\rightarrow") {
                    $("#" + molecule_id).parent().addClass("left_is_reactants_right_is_products");
                    $("#" + coefficient_id).addClass("left_is_reactants_right_is_products");
                }

                var molecule_span = $("#" + molecule_id)[0]
                molecule_display = MQ.StaticMath(molecule_span);
                molecule_display.latex(molecule);
            }
        }
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

// python round function takes precision as an argument
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
    render("this");

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
    var components = target_wrapper.find(".component");  //will be empty if there are none
    var current_full_float_array;
    if (components.length) {
        for (var i = 0; i < components.length; i++) {
            var current_component_id = $(components[i]).attr('id');
            current_full_float_array = [$('#' + current_component_id).find('i').find('div').data('fullfloat')];
            python_round(current_full_float_array, precision, function (response) {
                $('#' + current_component_id).find('i').find('div').html(response.result);
            })

        }
    } else {
        current_full_float_array = [target_wrapper.find('div').data('fullfloat')];
        python_round(current_full_float_array, precision, function (response) {
            target_wrapper.find('div').html(response.result);
        })
    }
}
