ALGORITHM advanced_features {
    // Arrays and collections
    var numbers: array[integer] = [1, 2, 3, 4, 5];
    var total: integer = 0;
    
    show "==== Advanced El Features ====";
    
    // Array iteration
    for num in numbers {
        total = total + num;
    }
    show "Sum of array: " + total;
    
    // String manipulation
    var text: string = "  El ALGORITHMming Language  ";
    show "Original: '" + text + "'";
    show "Trimmed: '" + trim(text) + "'";
    show "Uppercase: '" + upper(trim(text)) + "'";
    
    // Date and time
    show "Current timestamp: " + timestamp();
}