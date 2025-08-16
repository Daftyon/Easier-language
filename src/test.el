
ALGORITHM testfix {
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
    for i = 0; i < 360; i = i + 5 {
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

    // Move to a new position
    // penup();
    // goto(-100, -100);
    // pendown();
    
    // // Draw a circle
    // SHOW("Drawing a circle...");
    // color("green");
    // circle(50);
    
    // // Draw a triangle
    // penup();
    // goto(100, -100);
    // pendown();
    // color("purple");
    
    // SHOW("Drawing a triangle...");
    // var j : integer;
    // for j = 0; j < 3; j = j + 1 {
    //     forward(100);
    //     left(120);
    // }
    
    // // Draw a star
    // penup();
    // goto(-100, 100);
    // pendown();
    // color("orange");
    
    // SHOW("Drawing a star...");
    // var k : integer;
    // for k = 0; k < 5; k = k + 1 {
    //     forward(100);
    //     right(144);
    // }
    
    // // Hide the turtle and wait for a click to exit
    // SHOW("Click on the window to exit.");
    // exitonclick();
}