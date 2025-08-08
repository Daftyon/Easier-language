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
    
    SHOW("Proofs working!");
}
