ALGORITHM DrawEllipse {
    // Variable declarations
    var steps : integer = 100;
    var x_radius : integer = 100;
    var y_radius : integer = 50;
    var center_x : integer = 0;
    var center_y : integer = 0;
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
    
    // Calculate angle step
    angle_step = 360.0 / steps;
    
    // Move to starting point
    penup();
    x = x_radius * cos(0);
    y = y_radius * sin(0);
    goto(center_x + x, center_y + y);
    pendown();
    
    // Draw the ellipse
    for i = 1; i <= steps; i = i + 1 {
        angle = i * angle_step;
        x = x_radius * cos(angle);
        y = y_radius * sin(angle);
        goto(center_x + x, center_y + y);
    }
    
    // Show completion message
    penup();
    goto(-200, 200);
    color("black");
    SHOW("Ellipse complete! Click to exit.");
    
    // Wait for click to exit
    exitonclick();
}
