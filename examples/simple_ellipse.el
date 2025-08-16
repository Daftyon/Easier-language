ALGORITHM DrawEllipse {
    // Variable declarations
    var steps : integer = 100;
    var x_radius : integer = 100;
    var y_radius : integer = 50;
    var start_x : real;
    var start_y : real;
    var angle : real;
    var x : real;
    var y : real;
    var i : integer;
    var angle_step : real;
    
    // Initialize drawing
    SHOW("Drawing an ellipse...");
    speed(10);
    bgcolor("white");
    color("blue");
    width(2);
    
    // Set start position
    penup();
    goto(-100, 0);
    start_x = xcor();
    start_y = ycor();
    angle_step = 360.0 / steps;
    
    // Draw the ellipse
    pendown();
    for i = 1; i <= steps; i = i + 1 {
        angle = i * angle_step;
        x = x_radius * cos(angle);
        y = y_radius * sin(angle);
        goto(start_x + x, start_y + y);
    }
    
    // Show completion message
    penup();
    goto(-200, 200);
    color("black");
    SHOW("Ellipse complete! Click to exit.");
    
    // Wait for click to exit
    exitonclick();
}
