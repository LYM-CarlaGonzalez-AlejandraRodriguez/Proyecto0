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
    comandos = {"M", "R", "C", "B", "c", "b", "P", "J", "G"}
    instrucciones = {"move:", "turn:", "face:", "put:", "pick:", "jump:", "goto:", "goTo:",
                     "if:", "while:", "for:", "nop", "proc:", "repeatTimes:", "canMove:", "canJump:", "facing:"}
    estructuras = {"if:", "while:", "for:", "then:", "else:", "do:", "repeat:"}
    condiciones = {"facing:", "canPut:", "canPick:", "canMove:", "canJump:", "not:"}
    constantes = {"#north", "#south", "#west", "#east", "#front", "#back", "#right", "#left", "#balloons", "#chips"}

    t = []
    palabra_actual = ""
    dentro_variables = False  

    for i in range(len(codigo)):
        char = codigo[i]

        if char in "[]":
            if palabra_actual:
                t.append(palabra_actual)
                palabra_actual = ""
            t.append(char)

        elif char == "|":
            dentro_variables = not dentro_variables
            if palabra_actual:
                t.append(palabra_actual)
                palabra_actual = ""

        elif char == ",":
            if dentro_variables and palabra_actual:
                t.append(palabra_actual)
                palabra_actual = ""

        elif char.isspace():
            if palabra_actual:
                t.append(palabra_actual)
                palabra_actual = ""

        elif char == ":":
            palabra_actual += char
            if palabra_actual in instrucciones or palabra_actual in estructuras or palabra_actual in condiciones:
                t.append(palabra_actual)
                palabra_actual = ""

        elif char == ".":
            if palabra_actual:
                t.append(palabra_actual)
                palabra_actual = ""

        else:
            palabra_actual += char  

    if palabra_actual:
        t.append(palabra_actual)

    tokens_filtrados = []
    for token in t:
        if (token in comandos or token in instrucciones or token in estructuras or
                token in condiciones or token in constantes or token in ["[", "]", ":=", "VARIABLES"]):
            tokens_filtrados.append(token)
        elif token.isidentifier():
            tokens_filtrados.append(token)
        elif token.endswith(":"):
            tokens_filtrados.append(token)
        elif token.isdigit():
            tokens_filtrados.append(token)
        else:
            print(f"Error: Token inválido detectado → {token}")  
            return []  

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
            if token == "while:":
                esperando_condicion = True
            else:
                esperando_bloque = True  

        elif esperando_condicion and token in {"canMove:", "canJump:", "facing:", "not:"}:
            nodo_actual.append(token)
            esperando_condicion = False  #se encontró una condición, ahora esperar comando o bloque

        elif esperando_bloque and token in {"move:", "turn:", "face:", "put:", "pick:", "jump:", "goto:", "goTo:"}:
            nodo_actual.append(token)
            esperando_bloque = False  #se encontró un comando después de if:, while:, etc

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
                print("Error: ] sin [ previo")
                return False, None
            stack.pop()
            if stack:
                nodo_actual = stack[-1][0]
            else:
                nodo_actual = raiz["Programa"]

        elif token == "else:":
            if not stack or stack[-1][1] != "if:":
                print("Error: else: sin un if: previo.")
                return False, None
            else_nodo = {"else:": []}
            stack[-1][0].append(else_nodo)
            nodo_actual = else_nodo["else:"]

        else:
            nodo_actual.append(token)

    if len(stack) <0:
        print("Error: Bloques abiertos sin cerrar")
        return False, None

    return True, raiz
def analizar(cod):
    if not validar_corchetes(cod):
        print("Error: Los bloques de código no están balanceados")
        return False, None
    
    ta = definir(cod)
    
    print("t Generados:", ta)  
    
    if not ta:
        print("Error: No se detectaron checks válidos en el código")
        return False, None

    valido, arbol = parse(ta)
    
    if not valido:
        print("Error: Estructura del código inválida")
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

# Código de prueba
code = """
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

es_valido, arbol_parseo = analizar(code)

if es_valido:
    print("Código válido")
    print("\nÁrbol de parseo:")
    imprimir_arbol(arbol_parseo)
else:
    print("Código inválido")

