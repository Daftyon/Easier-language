ALGORITHM example {SHOW("hello from el "); 

var grade: string = "B";

    
    switch (grade) {
        case "A":
        case "B":
            SHOW("Excellent or Good");
            break;
        case "C":
            SHOW("Average");
            break;
        default:
            show("Needs improvement");
            break;
    }
//    const GREETING: string = "Hello, World!";
    
//     show(GREETING);
    
    // This will cause a semantic error:
    // GREETING = "Goodbye!"; // Error: Cannot assign to constant
    
    // Constants must be initialized:
    // const UNINITIALIZED: integer; // Error: Constants must be initialized
    //   var weather_good: boolean = realistic;        // 50% probability
    // var traffic_light: boolean = true;
    // var will_rain: boolean = realistic;
    
    // // Using realistic in conditions
    // if (weather_good and !will_rain) {
    //     show("Good day for outdoor activity");
    // } else {
    //     show("Maybe stay inside");
    // }
}
