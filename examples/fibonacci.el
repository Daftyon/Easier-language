ALGORITHM fibonacci {
    function fib(n: integer): integer {
        if n <= 1 {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }
    
    show "Fibonacci Sequence:";
    for i: integer = 0; i < 10; i = i + 1 {
        show "F(" + i + ") = " + fib(i);
    }
}