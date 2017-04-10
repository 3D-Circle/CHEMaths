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
        // alors Mr Takla :)
    } else if (mode == "equation") {
        // ah c'est moi ici oké
        console.log(result);
        var reactants = result.reactants;
        var products = result.products;
        var coefficients = result.coefficients;
        var error = result.error;
        $("#info-equation > table").find(".error, .data").remove();
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
                var molecule_id = "equation-formula" + index;
                var coefficient_id = "equation-coefficient" + index;
                $("<td><span class='data' id='" + molecule_id+ "'>" + molecule + "</span></td>").appendTo("#info-equation > table #formula");
                $("<td><span class='data number' id='" + coefficient_id + "'>" + coefficient + "</span></td>").appendTo("#info-equation > table #coefficient");

//                var molecule_col = MQ.StaticMath($('#' + molecule_id)[0]);
//                var coefficient_col = MQ.StaticMath($('#' + coefficient_id)[0]);
//                console.log(molecule);
//                console.log(coefficient);
//
//                molecule_col.latex(molecule);
//                coefficient_col.latex(coefficient);
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
    });
});
