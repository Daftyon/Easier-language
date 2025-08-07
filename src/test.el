
ALGORITHM example {
    SHOW("hello from el "); 
    axiom basic_truth: true; 
    var marketStable: boolean = realistic;
    var companyStrong: boolean = true;

    if (marketStable and companyStrong) {
        SHOW("Proceed with caution");  
    }
    
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
            SHOW("Needs improvement");
            break;
    }

    const GREETING: string = "Hello, World!";
    SHOW(GREETING);
}
