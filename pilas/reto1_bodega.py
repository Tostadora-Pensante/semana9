stack = []
CAPACIDAD = 5


def pausar():
    input("Ingrese cualquier tecla para continuar...")


def push(item):
    if not is_full():
        stack.append(item)
        return "Elemento apilado..."
    return "Pila llena..."


def isEmpty():
    return len(stack) == 0


def is_full():
    return len(stack) == CAPACIDAD


def peek():
    if not isEmpty():
        return f"Tope de la pila: {stack[-1]}"
    return "Pila vacía..."


def pop():
    if not isEmpty():
        return f"Elemento desapilado: {stack.pop()}"
    return "Pila vacía..."


def show():
    if isEmpty():
        return "Pila vacía..."

    message = ""
    for item in reversed(stack):
        message += f" | {item:>6} |\n"

    message += " └ " + "-" * 8 + "┘\n"
    return message


def menu():
    while True:
        print("=" * 13)
        print("Actividades con Pilas")
        print("1. Apilar")
        print("2. Desapilar")
        print("3. Consultar tope")
        print("4. Mostrar pila")
        print("0. Salir")

        try:
            opcion = int(input("Seleccione una opción (0-4): "))
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número.")
            continue

        if opcion < 0 or opcion > 4:
            print("Opción inválida. Seleccione un número entre 0 y 4.")
            continue

        if opcion == 0:
            print("Saliendo del programa...")
            break

        elif opcion == 1:
            item = input("Ingrese el elemento a apilar: ")
            print(push(item))

        elif opcion == 2:
            print(pop())

        elif opcion == 3:
            print(peek())

        elif opcion == 4:
            print(show())

        pausar()


menu()