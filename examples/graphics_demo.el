PROGRAM GraphicsDemo {
    // Set up the drawing
    speed(10);  // Fastest speed
    bgcolor("lightblue");
    color("red");
    width(2);
    
    // Draw a square
    #print("Drawing a square...");
    var i : integer;
    for i = 0; i < 4; i = i + 1 {
        forward(100);
        right(90);
    }
    
    // Move to a new position
    penup();
    goto(-100, -100);
    pendown();
    
    // Draw a circle
    #print("Drawing a circle...");
    color("green");
    circle(50);
    
    // Draw a triangle
    penup();
    goto(100, -100);
    pendown();
    color("purple");
    
    #print("Drawing a triangle...");
    var j : integer;
    for j = 0; j < 3; j = j + 1 {
        forward(100);
        left(120);
    }
    
    // Draw a star
    penup();
    goto(-100, 100);
    pendown();
    color("orange");
    
    #print("Drawing a star...");
    var k : integer;
    for k = 0; k < 5; k = k + 1 {
        forward(100);
        right(144);
    }
    
    // Hide the turtle and wait for a click to exit
    #print("Click on the window to exit.");
    exitonclick();
}
