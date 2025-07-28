<p align="center">
    <h1 align="center">Custom Language</h1>
</p>


---

##### Program starts with "PROGRAM" keyword followed by "ID"(program name) </p>

 ```javascript
    PROGRAM Part10 { } 
```

#### Variable declaration
```javascript
    var x, y : integer;
    var s    : real; 
    var c    : string;
    var f    : boolean;
    
    var a1   : integer = 5;
    var c, s : string = "same values"
```

##### Assignment statements 
```javascript
    x = 1 * 2 + 3 - 4 / 5 * (1 + 2)
    f = true;
    s = 1.5;
    c = "My language"
```

##### Boolean expressions
```python
    flag = True and False or !False and (True and False)
    flag = 1 < 2 and 2 > 1 
```

#### Function declaration 
```javascript
    function foo(s: STRING) {
        VAR c : STRING;
    }   
```

#### Builtin functions
```javascript
    function foo(s: STRING) {
        ... 
        #print(s) 
    
        function bar() {
            return 2;
        }
        
        return bar(); 
    }   
    
    #print(foo("bar")); // #prints 2
```

#### Function call 
```javascript
    foo("Custom" + " " + "language");
```


#### If statement
```python
    x = 10 
    if x > 5 
    {
        #print("x is greater than 5");
    }
    elif x < 5
    {
        #print("x is less than 5")
    }
    else
    {
        #print("x equals to 5")
    }

    if true or false
    {
        #print("true")
    }
    
    if true and !false
    {
        #print("true")
    }
```

#### For loop   
```python
    for i = 0; i < 10; i = i + 1 {
        for j = 0; j < 10; j = j + 1 {
            for k = 0; k < 10; k = k + 1 {
                #print(i * j * k)
            }   
        }       
    }   
```
### While loop
```python
ALGORITHM example
{
    var x, y, counter : integer;
    x = 0;
    counter = 0;

    WHILE counter <= 10 DO {
        SHOW(x);
        x = x + 1;
        counter = counter + 1; 
    }
}

```

### test statement
```python
code {

}
```

### test statement
```python
ALGORITHM example
{
    var x, y, counter : integer;
    x = 0;
    counter = 0;

    DO 
    {
        SHOW(x);
        x = x + 1;
        counter = counter + 1; 
    } WHILE true 
}

```



#### Comments 
```
    // This is one line comment 
    
    {{
        This is multi-line comment
    }}
```

#### Program snippet
```python
    
ALGORITHM Part10
{
    function fib(n: int) {
        if n < 1 {
            return 0;
        }
        elif n < 3 {
            return 1;
        }
        return fib(n - 1) + fib(n - 2);
    }


    for i = 0; i < 10; i = i + 1 {
        #print(fib(i));
    }

}
```

ALGORITHM example
{
    
    var x: integer;
    SHOW(TRUE and FALSE);

        function foo(s: STRING) {
        VAR c : STRING;

            function fooq(s: STRING) {
        VAR c : STRING;
        
    }   
        fooq("ff");

    }  
    foo("ss");

  
       

}


