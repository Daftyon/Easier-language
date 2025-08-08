ALGORITHM testfix {
    theorem simple: true;
    
    proof simple {
        hypothesis h1: false;
        test t1: h1: realistic;
        realistic;
        QED;
    }
    
    SHOW("Fixed!");
}
