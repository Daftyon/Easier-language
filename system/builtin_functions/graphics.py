import turtle
from typing import Optional, Tuple

class Graphics:
    def __init__(self):
        self.screen = None
        self.t = None
        self.is_pen_down = True
        self._init_turtle()
    
    def _init_turtle(self):
        if self.screen is None:
            self.screen = turtle.Screen()
            self.screen.title("Easier Language Graphics")
            self.t = turtle.Turtle()
            self.t.speed(0)  # Fastest speed
    
    def forward(self, distance: float):
        """Move the turtle forward by the specified distance."""
        self._init_turtle()
        self.t.forward(distance)
    
    def backward(self, distance: float):
        """Move the turtle backward by the specified distance."""
        self._init_turtle()
        self.t.backward(distance)
    
    def right(self, angle: float):
        """Turn turtle right by angle degrees."""
        self._init_turtle()
        self.t.right(angle)
    
    def left(self, angle: float):
        """Turn turtle left by angle degrees."""
        self._init_turtle()
        self.t.left(angle)
    
    def penup(self):
        """Pull the pen up -- no drawing when moving."""
        self._init_turtle()
        self.t.penup()
        self.is_pen_down = False
    
    def pendown(self):
        """Pull the pen down -- drawing when moving."""
        self._init_turtle()
        self.t.pendown()
        self.is_pen_down = True
    
    def goto(self, x: float, y: float):
        """Move turtle to an absolute position."""
        self._init_turtle()
        self.t.goto(x, y)
    
    def setposition(self, x: float, y: float):
        """Alias for goto."""
        self.goto(x, y)
    
    def setx(self, x: float):
        """Set the turtle's x coordinate."""
        self._init_turtle()
        self.t.setx(x)
    
    def sety(self, y: float):
        """Set the turtle's y coordinate."""
        self._init_turtle()
        self.t.sety(y)
    
    def setheading(self, angle: float):
        """Set the orientation of the turtle."""
        self._init_turtle()
        self.t.setheading(angle)
    
    def circle(self, radius: float, extent: Optional[float] = None, steps: Optional[int] = None):
        """Draw a circle with given radius."""
        self._init_turtle()
        if extent is not None and steps is not None:
            self.t.circle(radius, extent, steps)
        elif extent is not None:
            self.t.circle(radius, extent)
        else:
            self.t.circle(radius)
    
    def dot(self, size: Optional[float] = None, color: Optional[str] = None):
        """Draw a dot with given size and color."""
        self._init_turtle()
        if color is not None and size is not None:
            self.t.dot(size, color)
        elif size is not None:
            self.t.dot(size)
        else:
            self.t.dot()
    
    def color(self, *args):
        """Set the color of the pen."""
        self._init_turtle()
        self.t.color(*args)
    
    def bgcolor(self, *args):
        """Set the background color of the turtle screen."""
        self._init_turtle()
        self.screen.bgcolor(*args)
    
    def width(self, width: float):
        """Set the line thickness to width."""
        self._init_turtle()
        self.t.width(width)
    
    def speed(self, speed: int):
        """Set the turtle's speed (0-10)."""
        self._init_turtle()
        self.t.speed(speed)
    
    def clear(self):
        """Delete the turtle's drawings from the screen."""
        if self.t:
            self.t.clear()
    
    def reset(self):
        """Delete the turtle's drawings and reset its state."""
        if self.t:
            self.t.reset()
    
    def done(self):
        """Start event loop - call this when done with turtle graphics."""
        if self.screen:
            self.screen.mainloop()
    
    def exitonclick(self):
        """Go into mainloop until the mouse is clicked."""
        if self.screen:
            self.screen.exitonclick()

# Global graphics instance
graphics = Graphics()
