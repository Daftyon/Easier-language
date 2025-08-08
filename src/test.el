ALGORITHM testfix {
    theorem simple: true;
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
