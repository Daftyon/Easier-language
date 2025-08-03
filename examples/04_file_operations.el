ALGORITHM file_operations {
    var filename: string = "test_output.txt";
    
    show "==== File Operations Demo ====";
    
    // Write to file
    write_file(filename, "Hello from El Language!\nThis is a test file.\n");
    show "File written: " + filename;
    
    // Read from file
    var content: string = read_file(filename);
    show "File content:";
    show content;
}