PROGRAM DrawingApp {
    // Set up the drawing
    speed(0);  // Fastest speed
    bgcolor("white");
    width(3);
    
    SHOW("Simple Drawing App");
    SHOW("-----------------");
    SHOW("Left click and drag to draw");
    SHOW("Press 'c' to clear the screen");
    SHOW("Press 'q' to quit");
    
    // Function to handle mouse movement
    function start_drawing(x, y) {
        pendown();
        goto(x, y);
    }
    
    function stop_drawing() {
        penup();
    }
    
    function move_to(x, y) {
        if (is_pen_down) {
            goto(x, y);
        }
    }
    
    // Function to clear the screen
    function clear_screen() {
        clear();
        penup();
        goto(0, 0);
        SHOW("Screen cleared!");
    }
    
    // Set up event handlers
    on_click(start_drawing);
    on_release(stop_drawing);
    on_drag(move_to);
    
    // Keyboard controls
    on_key("c", clear_screen);
    on_key("q", exitonclick);
    
    // Keep the window open
    done();
}
