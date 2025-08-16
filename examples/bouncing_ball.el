PROGRAM BouncingBall {
    // Set up the drawing
    speed(0);
    bgcolor("black");
    penup();
    
    // Ball properties
    var x : integer = 0;
    var y : integer = 0;
    var x_speed : integer = 5;
    var y_speed : integer = 5;
    var gravity : real = 0.4;
    var bounce : real = -0.7;
    var friction : real = 0.99;
    var colors : array[6] of string = ["red", "orange", "yellow", "green", "blue", "purple"];
    var color_index : integer = 0;
    
    // Draw boundary
    width(3);
    color("white");
    goto(-200, 200);
    pendown();
    goto(200, 200);
    goto(200, -200);
    goto(-200, -200);
    goto(-200, 200);
    penup();
    
    SHOW("Bouncing Ball Animation - Click to exit");
    
    // Animation loop
    while (true) {
        // Update position
        x = x + x_speed;
        y = y + y_speed;
        
        // Apply gravity
        y_speed = y_speed - gravity;
        
        // Bounce off walls
        if (x > 180 || x < -180) {
            x_speed = x_speed * bounce * -1;
            color_index = (color_index + 1) % 6;
            color(colors[color_index]);
        }
        
        // Bounce off floor and ceiling
        if (y < -180) {
            y = -180;
            y_speed = y_speed * bounce * -1;
            x_speed = x_speed * friction;
            color_index = (color_index + 1) % 6;
            color(colors[color_index]);
        }
        
        // Stop at ceiling
        if (y > 180) {
            y = 180;
            y_speed = y_speed * bounce;
            x_speed = x_speed * friction;
        }
        
        // Draw the ball
        goto(x, y);
        dot(20);
        
        // Small delay to control speed
        // (In a real implementation, you'd use a proper timing function)
        var i : integer;
        for i = 0; i < 10000; i = i + 1 {
            // Just waste some time
        }
        
        // Clear the previous position
        color("black");
        dot(22);
        color(colors[color_index]);
        
        // Check for exit
        if (x > 200 && y > 200) {
            break;
        }
    }
    
    goto(0, 0);
    color("white");
    SHOW("Animation complete! Click to exit.");
    exitonclick();
}
