

ALGORITHM testfix {
    theorem simple: true;
        definition even: true;                    // x is even if x mod 2 = 0 (simplified)

        axiom identity: true === true;
 axiom excludedmiddle: true or ! true;
    proof simple {
        hypothesis h1: false;
        test t1: h1: realistic;
        realistic;
        QED;
    }
    
    SHOW("Fixed!");
}