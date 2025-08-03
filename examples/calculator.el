ALGORITHM calculator {
    function add(a: integer, b: integer): integer {
        return a + b;
    }
    
    function multiply(a: integer, b: integer): integer {
        return a * b;
    }
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "El Calculator";
    show x + " + " + y + " = " + add(x, y);
    show x + " * " + y + " = " + multiply(x, y);
}