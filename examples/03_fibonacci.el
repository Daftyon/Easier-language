ALGORITHM fibonacci {
    show "==== Fibonacci Sequence ====";
    
    var n1: integer = 0;
    var n2: integer = 1;
    var next: integer = 0;
    var count: integer = 10;
    
    show "First " + count + " Fibonacci numbers:";
    show n1;
    show n2;
    
    for i: integer = 3; i <= count; i = i + 1 {
        next = n1 + n2;
        show next;
        n1 = n2;
        n2 = next;
    }
}