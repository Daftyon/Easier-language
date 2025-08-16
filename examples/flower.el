PROGRAM Flower {
    // Set up the drawing
    speed(10);
    bgcolor("lightblue");
    color("red");
    width(2);
    
    // Draw a flower with petals
    SHOW("Drawing a flower...");
    var i : integer;
    var petals : integer = 12;
    var angle : integer = 360 / petals;
    
    // Draw petals
    for i = 0; i < petals; i = i + 1 {
        // Draw a petal
        color("pink");
        circle(50, 60);  // Draw an arc
        right(120);
        color("lightpink");
        circle(50, 60);  // Draw another arc for the petal
        right(120);
        
        // Position for next petal
        right(angle);
    }
    
    // Draw the flower center
    color("yellow");
    dot(30);
    
    // Draw stem
    penup();
    goto(0, -50);
    setheading(270);  // Point down
    pendown();
    color("green");
    width(5);
    forward(150);
    
    // Draw leaf
    left(60);
    width(3);
    circle(40, 120);
    
    SHOW("Click to exit");
    exitonclick();
}
