$(document).ready(function() {
    var MQ = MathQuill.getInterface(2)
    var inputBox = document.getElementById('input');
    var config = {
        handlers: {edit: function() {
            console.log(mathField.latex());
        }}
    };
    var mathField = MQ.MathField(inputBox, config);
    mathField.focus();
    mathField.write("H_2");
});