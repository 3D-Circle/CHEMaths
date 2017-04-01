$(document).ready(function () {
    // input box
    var MQ = MathQuill.getInterface(2);
    var inputBox = $('#input')[0];
    var config = {
        handlers: {edit: function() {
            console.log(mathField.latex());
            // update status labels
        }}
    };
    var mathField = MQ.MathField(inputBox, config);
    mathField.focus();
    mathField.write("H_2 + O_2 \\rightarrow H_2O");
    
    // buttons
    $('#rightarrow').click(function () {
        mathField.cmd('\\rightarrow');
        mathField.focus();
    });
    $('#sup').click(function () {
        mathField.cmd('^');
        mathField.focus();
    });
    $('#sub').click(function () {
        mathField.cmd('_');
        mathField.focus();
    });
    $('#left-parenthesis').click(function () {
        mathField.cmd('(');
        mathField.focus();
    });
    $('#right-parenthesis').click(function () {
        mathField.cmd('\)');
        mathField.focus();
    });
    $('#plus').click(function () {
        mathField.cmd('+');
        mathField.focus();
    });
    $('#colon').click(function () {
        mathField.cmd(':') ;
        mathField.focus();
    });
    $('#semi-colon').click(function () {
        mathField.cmd(';');
        mathField.focus();
    });
    
    // confirm input
    var input = $("<input>")
                    .attr("type", "text")
                    .attr("name", "input").val(mathField.latex())
    $("#confirm").append($(input));
    // TODO:
    // - ajax to call python functions
    // - labels
});
