program control_flow {
    show "==== Control Flow Demo ====";
    
    var x: integer = 15;
    
    if x > 10 {
        show x + " is greater than 10";
    } else {
        show x + " is not greater than 10";
    }
    
    show "Counting from 1 to 5:";
    for i: integer = 1; i <= 5; i = i + 1 {
        show "Count: " + i;
    }
}