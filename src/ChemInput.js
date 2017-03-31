$(document).ready(function () {
    // input box
    var MQ = MathQuill.getInterface(2)
    var inputBox = document.getElementById('input')
    var config = {
        handlers: {edit: function() {
            console.log(mathField.latex());
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
    $('#confirm').click(function () {
        var input = mathField.latex();
        $.ajax({
            type: "POST",
            url: "/Users/yangjingjie/PycharmProjects/CHEMaths",
            data: {param: input}
        }).done(function (  ) {
            alert("HELLO!");
        });
    });
    
    // TODO:
    // - ajax to call python functions
    // - labels
});
