var modes = [
    "this", "molecule", "equation", "empirical", "alkane"
];
var currentMode = "equation";
var MQ = MathQuill.getInterface(2);

// detect mode from latex string
function detectMode(latex) {
    if (latex.toLowerCase().includes("rightarrow")) {
            mode = "equation";
        } else if (latex.toLowerCase().includes("alkane")) {
            mode = "alkane";
        } else if (latex.includes(":")) {
            mode = "empirical";
        } else if (latex
        ) {
            mode = "molecule";
        } else {
            mode = "this"; // shows information on website
        }
    return mode;
}

function renderResult(mode, result) {
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

        // Molar mass TODO: add option to change units and adjust precision
        $('#molar_mass').html('<div>' + result.info['mr'] + '</div> g / mol')
        $('input#molar_mass_precision').val(2);

        // Components & percentages
        var composition = result.info.element_percentages;
        // this sorts dict keys according to concentration (http://stackoverflow.com/a/16794116/4489998)
        var sorted_elements = Object.keys(composition).sort(function(a,b){
            return composition[a]-composition[b]
        }).reverse();
         var array_to_round = sorted_elements.map(function(x) {
            return composition[x];
         });

        var precision = 2;  // TODO: Replace with slider
        python_round(array_to_round, precision, function(rounded_array) {
            var new_html = '';
            var element;
            var percentage;
            for (var i = 0; i < sorted_elements.length; i++) {
                element = sorted_elements[i];
                percentage = rounded_array.result[i];
                new_html += '<div class="component">' + element + '<br><i>' + percentage +'%</i></div>';
            }
            $('#components').html(new_html);
        })

        // Oxidation
        $('#oxidation').html(result.info.oxidation);


    } else if (mode == "equation") {
        // mr jingjie
        console.log(result);
        var reactants = result.reactants;
        var products = result.products;
        var coefficients = result.coefficients;
        var error = result.error;
        $("#info-equation > table").find("td").remove();
        if (error) {
            $("<td><span class='error'>" + error + "</span><td>").appendTo("#info-equation > table #reaction_type");
        } else {
            for (var i = 0; i < 2 * reactants.length - 1 + 1 + 2 * products.length - 1; i++) {
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
                        molecule = "\\rightarrow ";
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
                var coefficient_span_html = "<span class='data number' id='" + coefficient_id + "'>" + coefficient + "</span>";

                $("<td>" + coefficient_span_html + molecule_span_html + "</td>").appendTo("#info-equation > table #formula");
                $("<td>" + coefficient_span_html + "</td>").appendTo("#info-equation > table #coefficient");

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
        charsThatBreakOutOfSupSub: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        handlers: {
            edit: function () {
                // update render
                var latex = mainField.latex();
                var currentMode = detectMode(latex)
                render(currentMode);

                // ajax request for live preview
                $.ajax({
                    url: "/live_preview",
                    type: "post",
                    data: {
                        "mode": currentMode,
                        "latex": latex
                    },
                    success: function(response){
                        renderResult(currentMode, response);
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
    $('.status').click(function () {
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

        // precision sliders change detection
        $('input.precision').each(function() {
            // Look for changes in the value
            elem.bind("input", precision_change);
        });
    });
});

function precision_change(event) {
    var elem = event.target;
    var precision = elem.value;
    // get which value we have to change
    var num_to_change = event.target.id.split('_');
    num_to_change.pop()
    num_to_change = num_to_change.join('_');
}
