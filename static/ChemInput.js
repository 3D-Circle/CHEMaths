var modes = [
    "this", "molecule", "equation", "empirical", "alkane"
];
var currentMode = "equation";

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
                        left: $(window).width()
                    }, 500);
                });

                $target.addClass('active').show().css({
                    right: -($target.width())
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
    var MQ = MathQuill.getInterface(2);
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
                        console.log(response);
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
                text = "H_2 + O_2 \\rightarrow H_2O";
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
