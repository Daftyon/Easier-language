PROGRAM DrawEllipse {
    // Set up the drawing
    SHOW("Drawing an ellipse...");
    speed(10);  // Fast drawing speed
    bgcolor("white");
    color("blue");
    width(2);
    
    // Draw a horizontal ellipse
    SHOW("Drawing a horizontal ellipse...");
    color("blue");
    penup();
    goto(-100, 0);
    pendown();
    
    // Draw the ellipse directly
    var steps = 100;
    var x_radius = 100;
    var y_radius = 50;
    var start_x = xcor();
    var start_y = ycor();
    var angle : real;
    var x : real;
    var y : real;
    var i : integer;
    var angle_step = 360.0 / steps;
    
    // Move to starting point
    penup();
    x = x_radius * cos(0);
    y = y_radius * sin(0);
    goto(start_x + x, start_y + y);
    pendown();
    
    // Draw the ellipse
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
    SHOW("Ellipse drawing complete! Click to exit.");
    
    // Wait for click to exit
    exitonclick();
}
