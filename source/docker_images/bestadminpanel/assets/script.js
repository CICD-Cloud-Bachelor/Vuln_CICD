document.addEventListener('DOMContentLoaded', function() {

    console.log("JavaScript is loaded and running!");

    var buttons = document.querySelectorAll('button');
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            alert('Button clicked!');
        });
    });
});
