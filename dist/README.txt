# El Programming Language v1.0.0

## 🚀 Utilisation

### Commandes de base:
- `el.exe --version`           : Afficher la version
- `el.exe --help`              : Afficher l'aide
- `el.exe fichier.el`          : Exécuter un fichier El
- `el.exe -i`                  : Mode interactif (REPL)
- `el.exe -c "code"`           : Exécuter du code directement

### Exemples:
```bash
# Exécuter un exemple
el.exe examples\hello_world.el

# Mode interactif
el.exe -i

# Code direct
el.exe -c "program test { show 'Hello El!'; }"
```

## 📝 Syntaxe El

```el
program mon_programme {
    var nom: string = "El";
    var age: integer = 1;
    
    show "Bonjour " + nom + "!";
    
    function saluer(nom: string): string {
        return "Salut " + nom + "!";
    }
    
    show saluer("Développeur");
}
```

## 📚 Exemples inclus
- `hello_world.el` : Programme Hello World
- `calculator.el`  : Calculatrice simple  
- `fibonacci.el`   : Suite de Fibonacci

Créé par l'équipe El Language
