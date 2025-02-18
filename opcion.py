def validar_corchetes(cod):
    stack = []
    for char in cod:
        if char == "[":
            stack.append(char)
        elif char == "]":
            if not stack:
                return False  
            stack.pop()
    return len(stack) == 0  


def definir(codigo):
    comandos = {"M", "R", "C", "B", "c", "b", "P", "J", "G", "n", "m"}
    instrucciones = {"move:", "turn:", "face:", "put:", "pick:", "jump:", "goto:", "goTo:",
                     "if:", "while:", "for:", "nop", "proc", "repeatTimes:", "canMove:", "canJump:", "facing:",
                     "InDir:", "ofType:", "do:", "then:", "andBalloons:", "putChips:", ":", "put", "=", "goNorth", "inDir:", "goWest", "with:"}
    estructuras = {"if:", "while:", "for:", "then:", "else:", "do:", "repeat:"}
    condiciones = {"facing:", "canPut:", "canPick:", "canMove:", "canJump:", "not:"}
    constantes = {"#north", "#south", "#west", "#east", "#front", "#back", "#right", "#left", "#balloons", "#chips"}

    palabras_reservadas = comandos | instrucciones | estructuras | condiciones | constantes | {"[", "]", ":=", "VARIABLES"}
    variables_definidas = set()
    procedimientos_definidos = set()
    tokens = []
    palabra_actual = ""
    dentro_variables = False  
    esperando_proc_nombre = False  

    for i in range(len(codigo)):
        char = codigo[i]

        if char in "[]":
            if palabra_actual:
                tokens.append(palabra_actual)
                palabra_actual = ""
            tokens.append(char)

        elif char == "|":
            dentro_variables = not dentro_variables
            if not dentro_variables:
                tokens.append("VARIABLES")
            palabra_actual = ""

        elif char == ",":
            if dentro_variables and palabra_actual:
                variables_definidas.add(palabra_actual)
                tokens.append(palabra_actual)
                palabra_actual = ""

        elif char.isspace():
            if palabra_actual:
                if dentro_variables:
                    variables_definidas.add(palabra_actual)
                elif esperando_proc_nombre:
                    procedimientos_definidos.add(palabra_actual)
                    esperando_proc_nombre = False  
                tokens.append(palabra_actual)
                palabra_actual = ""

        elif char == ":":
            palabra_actual += char
            if palabra_actual in palabras_reservadas:
                tokens.append(palabra_actual)
                if palabra_actual == "proc:":
                    esperando_proc_nombre = True  
                palabra_actual = ""

        elif char == ".":
            if palabra_actual:
                tokens.append(palabra_actual)
                palabra_actual = ""

        else:
            palabra_actual += char  

    if palabra_actual:
        tokens.append(palabra_actual)

    # filtar si hay errores
    tokens_filtrados = []
    for token in tokens:
        if token not in palabras_reservadas and token not in variables_definidas and token not in procedimientos_definidos and not token.isdigit():
            print(f"Token inválido detectado → {token}")  
            return []  

        tokens_filtrados.append(token)

    return tokens_filtrados


def parse(tokens):
    stack = []
    raiz = {"Programa": []}
    nodo_actual = raiz["Programa"]
    
    esperando_bloque = False  
    esperando_condicion = False  

    for i in range(len(tokens)):
        token = tokens[i]

        if token in {"proc:", "if:", "while:", "for:"}:
            nuevo_nodo = {token: []}
            nodo_actual.append(nuevo_nodo)
            stack.append((nuevo_nodo[token], token))  
            nodo_actual = nuevo_nodo[token]
            if token == "while:" or token == "if:":
                esperando_condicion = True
            else:
                esperando_bloque = True  

        elif esperando_condicion and token in {"canMove:", "canJump:", "facing:", "not:"}:
            nodo_actual.append(token)
            esperando_condicion = False  

        elif esperando_bloque and token in {"move:", "turn:", "face:", "put:", "pick:", "jump:", "goto:", "goTo:",
                     "if:", "while:", "for:", "nop", "proc:", "repeatTimes:", "canMove:", "canJump:", "facing:",
                     "inDir:", "ofType:", "do:", "then:", "andBalloons:", "putChips:"}:
            nodo_actual.append(token)
            esperando_bloque = False  

        elif esperando_bloque and token == "[":
            esperando_bloque = False  
            nuevo_nodo = {"Bloque": []}
            nodo_actual.append(nuevo_nodo)
            stack.append((nuevo_nodo["Bloque"], "Bloque"))
            nodo_actual = nuevo_nodo["Bloque"]

        elif token == "[":
            nuevo_nodo = {"Bloque": []}
            nodo_actual.append(nuevo_nodo)
            stack.append((nuevo_nodo["Bloque"], "Bloque"))
            nodo_actual = nuevo_nodo["Bloque"]

        elif token == "]":
            if not stack:
                print("Error: ] sin [ previo.")
                return False, None
            stack.pop()
            if stack:
                nodo_actual = stack[-1][0]
            else:
                nodo_actual = raiz["Programa"]

        elif token == "else:":
            if not stack or stack[-1][1] != "if:":
                print("else: sin un if: previo.")
                return False, None
            else_nodo = {"else:": []}
            stack[-1][0].append(else_nodo)
            nodo_actual = else_nodo["else:"]

        else:
            nodo_actual.append(token)

    if len(stack) < 0:
        print("Bloques abiertos sin cerrar.")
        return False, None

    return True, raiz


def analizar(cod):
    if not validar_corchetes(cod):
        print("Los bloques de código no están balanceados.")
        return False, None
    
    tokens = definir(cod)
    
    if not tokens:
        return False, None  #nocontinuar si hay errores

    valido, arbol = parse(tokens)
    
    if not valido:
        print("Estructura del código inválida.")
        return False, None

    return True, arbol


def imprimir_arbol(arbol, nivel=0):
    for clave, valor in arbol.items():
        print("  " * nivel + str(clave))
        if isinstance(valor, list):
            for elemento in valor:
                if isinstance(elemento, dict):
                    imprimir_arbol(elemento, nivel + 1)
                else:
                    print("  " * (nivel + 1) + str(elemento))

def leer_archivo(filename):
    with open(filename, 'r') as file:
        return file.read()


# Código principal
if __name__ == "__main__":
    filename = input("Ingrese el nombre del archivo: ")
    code = leer_archivo(filename)
    
    es_valido, arbol_parseo = analizar(code)

    if es_valido:
        print("Código válido")
        print("\nÁrbol de parseo:")
        imprimir_arbol(arbol_parseo)
    else:
        print("Código inválido")
# Código de prueba
""" code =
|nom x y one|

proc putChips: n andBalloons: m [ 
    |c, b| 
    c := n .
    b := m .
    put : c ofType: #chips .  put: b ofType:  #balloons ] 

proc goNorth  [ 
    while: canMove: 1 inDir: #north do: [ move: 1 InDir: #north . ] 
]


proc goWest [ 
   if: canMove: 1 InDir: #west then: [move: 1 InDir: #west]  else: [nop .]]

[ 
    goTo: 3 with: 3 .
    putChips: 2 andBalloons: 1 .
]
"""
"""
es_valido, arbol_parseo = analizar(code)

if es_valido:
    print("Código válido")
    print("\nÁrbol de parseo:")
    imprimir_arbol(arbol_parseo)
else:
    print("Código inválido")
"""
