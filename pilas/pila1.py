stack = []


def push(item,capacity):
    if not is_full(capacity):
        stack.append(item)
        return "Elemento apilado..."
    return "fila llena"

def isEmpty():
    return not len(stack)

def is_full(capacity):
    return len(stack) == capacity

def peek():
    if not isEmpty():
        return stack[-1]
    return "Pila vacia..."

def pop():
    if not isEmpty():
        return f"Elemento desapilado: {stack.pop()}"
    return "Pila vacia..."

def show():
    if isEmpty():
        return "Pila vacia" 

    
    message = ""
    for item in reversed(stack):
        message += f" | {item :>6} |\n"

        message += f" └ " + "-"*8 + "┘\n" 
    return message

capacity = int(input("Dame el size de la pila: "))
       

while True:
    item = input("Dime un valor: ")
    print(push(item, capacity))
    answer = input("Desea ingresar otro dato? [S|N]: ")
    if answer.lower() == "n":
        break

print(show())

print("Mostrar tope: ")
print(peek())
print(peek())


print("Desapilar")
while True:
    answer = input("Desea desapilar [S|N]")
    if answer.lower() == "s":
        print(pop())
    elif answer.lower() == "n":
        break
    else:
        print("Opcion invalida...")