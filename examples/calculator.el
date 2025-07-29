program calculator {
    function add(a: integer, b: integer): integer {
        return a + b;
    }
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "Calculatrice El";
    show x + " + " + y + " = " + add(x, y);
}