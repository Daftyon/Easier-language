ALGORITHM DrawOval {
    // Variable declarations
    var i : integer;
    
    // Initialize drawing
    SHOW("Drawing an oval...");
    speed(10);
    bgcolor("white");
    color("blue");
    width(2);
    
    // Draw an oval using two half-circles
    penup();
    goto(0, -75);  // Starting position
    pendown();
    
    // Draw top half of oval (wider arc)
    for i = 0; i < 180; i = i + 5 {
        forward(3);
        right(1);
    }
    
    // Draw bottom half of oval (narrower arc)
    for i = 0; i < 180; i = i + 5 {
        forward(1);
        right(1);
    }
    
    // Show completion message
    penup();
    goto(-200, 200);
    color("black");
    SHOW("Oval complete! Click to exit.");
    
    // Wait for click to exit
    exitonclick();
}
