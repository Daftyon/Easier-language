program fibonacci {
    function fib(n: integer): integer {
        if n <= 1 {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }
    
    show "Fibonacci: " + fib(7);
}