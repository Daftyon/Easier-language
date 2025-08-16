PROGRAM Spiral {
    // Set up the drawing
    speed(0);  // Fastest speed
    bgcolor("black");
    width(2);
    
    SHOW("Drawing a colorful spiral...");
    var colors : array[7] of string = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"];
    var i : integer;
    var size : integer = 5;
    var angle : integer = 91;  // Slightly more than 90 degrees creates a spiral
    
    for i = 0; i < 200; i = i + 1 {
        // Cycle through colors
        color(colors[i % 7]);
        
        // Draw a line and turn
        forward(size);
        right(angle);
        
        // Increase the length of the line
        size = size + 3;
    }
    
    // Hide the turtle
    penup();
    goto(0, 0);
    color("white");
    SHOW("Spiral complete! Click to exit.");
    exitonclick();
}
