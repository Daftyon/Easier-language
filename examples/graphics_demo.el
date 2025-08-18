program graphics_demo {
    show "Graphics demonstration starting...";
    
    // Set colors
    color("blue");
    bgcolor("white");
    
    // Draw a square
    show "Drawing a square...";
    for i: integer = 0; i < 4; i = i + 1 {
        forward(100);
        right(90);
    }
    
    // Move to new position
    penup();
    goto(150, 0);
    pendown();
    
    // Draw a triangle
    show "Drawing a triangle...";
    color("red");
    for i: integer = 0; i < 3; i = i + 1 {
        forward(100);
        right(120);
    }
    
    // Draw a circle
    penup();
    goto(-50, -50);
    pendown();
    color("green");
    circle(30);
    
    show "Graphics demonstration complete!";
}