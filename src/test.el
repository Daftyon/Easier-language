ALGORITHM testproofs {
    theorem simple: true;
    
    proof simple {
        true;
        QED;
    }
    
    theorem threevalued: realistic or realistic;
    
    proof threevalued {
        realistic or true;  
        QED;
    }
    theorem noncontradiction: ! (true and false);
    proof noncontradiction {
        ! (false and false);  // false negated is true
        QED;
    }
    SHOW("Proofs working!");
}
