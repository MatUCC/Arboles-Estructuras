"""
Sistema de Búsqueda y Gestión de Inventario de Libros por ISBN
==============================================================
Caso de estudio: Biblioteca que registra libros en un Árbol Binario de Búsqueda (BST).

¿Por qué un BST?
- En una lista lineal, buscar un libro exige revisar, en el peor caso, TODOS los libros: O(n).
- En un BST, cada comparación descarta una rama completa del árbol (la mitad, si está
  balanceado), así que la búsqueda cuesta O(h), donde h es la altura del árbol.
  En un árbol razonablemente balanceado, h ≈ log2(n).

Regla del BST (clave = ISBN):
- Todo ISBN en el subárbol IZQUIERDO de un nodo es MENOR que el ISBN de ese nodo.
- Todo ISBN en el subárbol DERECHO de un nodo es MAYOR que el ISBN de ese nodo.
- No se permiten ISBN duplicados (un ISBN identifica a un único libro).

Ejecución:
    streamlit run app.py
"""

import streamlit as st


# =============================================================================
# 1. ESTRUCTURA DE DATOS
# =============================================================================

class Node:
    """
    Un nodo del árbol = un libro de la biblioteca.

    Atributos:
        isbn (int):          Clave de ordenamiento y búsqueda.
        titulo_libro (str):  Título del libro.
        autor (str):         Autor del libro.
        left (Node|None):    Puntero al hijo izquierdo (ISBN menores).
        right (Node|None):   Puntero al hijo derecho (ISBN mayores).
    """

    def __init__(self, isbn, titulo_libro, autor):
        self.isbn = isbn
        self.titulo_libro = titulo_libro
        self.autor = autor
        self.left = None
        self.right = None

    def es_hoja(self):
        """Un nodo es hoja cuando no tiene hijos."""
        return self.left is None and self.right is None


class BinaryTree:
    """
    Árbol Binario de Búsqueda que organiza el inventario por ISBN.
    La raíz es el primer libro registrado en el sistema.
    """

    def __init__(self):
        self.root = None
        self.size = 0

    # -------------------------------------------------------------------------
    # INSERCIÓN
    # -------------------------------------------------------------------------
    def insert(self, isbn, titulo, autor):
        """
        Registra un nuevo libro respetando la regla del BST.

        Funcionamiento jerárquico:
        1. Si el árbol está vacío, el libro se convierte en la RAÍZ.
        2. Si no, se parte de la raíz y se compara el ISBN nuevo con el del nodo actual:
             - Menor  -> se desciende por la rama izquierda (left).
             - Mayor  -> se desciende por la rama derecha (right).
             - Igual  -> el ISBN ya existe: se rechaza (no hay duplicados).
        3. Se repite el descenso hasta encontrar un puntero vacío (None);
           ahí se "cuelga" el nuevo nodo, que queda como HOJA.

        Retorna:
            (bool, list): (True si se insertó, ruta de ISBN recorridos hasta el padre).
        """
        nuevo = Node(isbn, titulo, autor)
        ruta = []

        # Caso 1: árbol vacío -> el primer libro es la raíz.
        if self.root is None:
            self.root = nuevo
            self.size += 1
            return True, ruta

        # Caso 2: descender desde la raíz (versión iterativa, sin riesgo de
        # desbordar la pila de recursión con árboles muy profundos).
        actual = self.root
        while True:
            ruta.append(actual.isbn)

            if isbn == actual.isbn:
                # El ISBN ya está registrado: no se duplica.
                return False, ruta

            if isbn < actual.isbn:
                # El nuevo ISBN es MENOR -> pertenece al subárbol izquierdo.
                if actual.left is None:
                    actual.left = nuevo      # Hueco libre: se inserta aquí.
                    self.size += 1
                    return True, ruta
                actual = actual.left         # Seguir bajando por la izquierda.
            else:
                # El nuevo ISBN es MAYOR -> pertenece al subárbol derecho.
                if actual.right is None:
                    actual.right = nuevo     # Hueco libre: se inserta aquí.
                    self.size += 1
                    return True, ruta
                actual = actual.right        # Seguir bajando por la derecha.

    # -------------------------------------------------------------------------
    # BÚSQUEDA
    # -------------------------------------------------------------------------
    def search(self, isbn):
        """
        Busca un libro por ISBN de forma optimizada.

        Funcionamiento jerárquico:
        - Se empieza en la raíz y en cada nodo se toma UNA sola decisión:
            * ISBN igual  -> libro encontrado.
            * ISBN menor  -> el libro solo puede estar a la izquierda.
            * ISBN mayor  -> el libro solo puede estar a la derecha.
        - Cada decisión descarta por completo la otra rama, por eso no hace
          falta revisar todo el inventario (a diferencia de una lista lineal).
        - Si se llega a un puntero None, el libro no existe en el árbol.

        Retorna:
            (dict|None, list): (datos del libro o None, ruta de ISBN visitados).
        """
        actual = self.root
        ruta = []

        while actual is not None:
            ruta.append(actual.isbn)

            if isbn == actual.isbn:
                return {
                    "isbn": actual.isbn,
                    "titulo": actual.titulo_libro,
                    "autor": actual.autor,
                }, ruta

            # Descartar la mitad del árbol que no puede contener el ISBN.
            actual = actual.left if isbn < actual.isbn else actual.right

        return None, ruta

    # -------------------------------------------------------------------------
    # RECORRIDO IN-ORDER
    # -------------------------------------------------------------------------
    def in_order_asc(self):
        """
        Recorre el árbol en orden: IZQUIERDA -> NODO -> DERECHA.

        Gracias a la regla del BST, este recorrido visita los ISBN de menor a
        mayor, por lo que devuelve el catálogo ORDENADO ascendentemente sin
        necesidad de aplicar ningún algoritmo de ordenamiento adicional.
        """
        resultado = []
        self._in_order(self.root, resultado)
        return resultado

    def _in_order(self, nodo, resultado):
        if nodo is None:
            return
        self._in_order(nodo.left, resultado)          # 1. Subárbol izquierdo (menores)
        resultado.append({                            # 2. Nodo actual
            "ISBN": nodo.isbn,
            "Título": nodo.titulo_libro,
            "Autor": nodo.autor,
            "Tipo de nodo": self._tipo_nodo(nodo),
        })
        self._in_order(nodo.right, resultado)         # 3. Subárbol derecho (mayores)

    # -------------------------------------------------------------------------
    # UTILIDADES (métricas para la interfaz)
    # -------------------------------------------------------------------------
    def _tipo_nodo(self, nodo):
        if nodo is self.root:
            return "Raíz"
        return "Hoja" if nodo.es_hoja() else "Padre"

    def height(self):
        """Altura del árbol = nº de niveles. Determina el costo máximo de búsqueda."""
        return self._height(self.root)

    def _height(self, nodo):
        if nodo is None:
            return 0
        return 1 + max(self._height(nodo.left), self._height(nodo.right))

    def to_dot(self):
        """Genera el árbol en formato Graphviz DOT para dibujarlo en Streamlit."""
        lineas = ["digraph BST {", 'node [shape=box, style="rounded,filled", fillcolor="#E8F0FE", fontname="Helvetica"];']

        def visitar(nodo):
            if nodo is None:
                return
            etiqueta = f"{nodo.isbn}\\n{nodo.titulo_libro[:22]}"
            color = "#FFD966" if nodo is self.root else ("#C6EFCE" if nodo.es_hoja() else "#E8F0FE")
            lineas.append(f'"{nodo.isbn}" [label="{etiqueta}", fillcolor="{color}"];')
            for hijo, lado in ((nodo.left, "izq"), (nodo.right, "der")):
                if hijo is not None:
                    lineas.append(f'"{nodo.isbn}" -> "{hijo.isbn}" [label="{lado}"];')
                    visitar(hijo)

        visitar(self.root)
        lineas.append("}")
        return "\n".join(lineas)


# =============================================================================
# 2. VALIDACIÓN DE ISBN
# =============================================================================

def normalizar_isbn(texto):
    """
    Acepta ISBN con o sin guiones/espacios (ej. 978-0-13-468599-1) y lo
    convierte a entero para poder compararlo numéricamente en el árbol.
    Devuelve None si no tiene 10 o 13 dígitos.
    """
    limpio = texto.replace("-", "").replace(" ", "").strip()
    if limpio.isdigit() and len(limpio) in (10, 13):
        return int(limpio)
    return None


# =============================================================================
# 3. FRONTEND (STREAMLIT)
# =============================================================================

st.set_page_config(page_title="Biblioteca BST", page_icon="📚", layout="wide")

# Streamlit vuelve a ejecutar el script en cada interacción, así que el árbol
# se guarda en session_state para que no se pierda entre clics.
if "arbol" not in st.session_state:
    arbol = BinaryTree()
    # Libros de ejemplo. El primero (9780262033848) queda como RAÍZ.
    ejemplos = [
        (9780262033848, "Introduction to Algorithms", "Thomas H. Cormen"),
        (9780132350884, "Clean Code", "Robert C. Martin"),
        (9780307474728, "Cien años de soledad", "Gabriel García Márquez"),
        (9780201633610, "Design Patterns", "Erich Gamma et al."),
        (9780596007126, "Head First Design Patterns", "Eric Freeman"),
        (9780134685991, "Effective Java", "Joshua Bloch"),
        (9788437604947, "Pedro Páramo", "Juan Rulfo"),
    ]
    for isbn, titulo, autor in ejemplos:
        arbol.insert(isbn, titulo, autor)
    st.session_state.arbol = arbol

arbol: BinaryTree = st.session_state.arbol

st.title("📚 Inventario de la Biblioteca por ISBN")
st.caption("Gestión de libros con un Árbol Binario de Búsqueda (BST)")

# ---------------------------- Sidebar: registro ------------------------------
with st.sidebar:
    st.header("➕ Registrar nuevo libro")
    with st.form("form_registro", clear_on_submit=True):
        isbn_txt = st.text_input("ISBN (10 o 13 dígitos)", placeholder="978-0-13-468599-1")
        titulo = st.text_input("Título")
        autor = st.text_input("Autor")
        enviado = st.form_submit_button("Registrar", use_container_width=True)

    if enviado:
        isbn = normalizar_isbn(isbn_txt)
        if isbn is None:
            st.error("ISBN inválido: debe tener 10 o 13 dígitos.")
        elif not titulo.strip() or not autor.strip():
            st.error("El título y el autor son obligatorios.")
        else:
            ok, ruta = arbol.insert(isbn, titulo.strip(), autor.strip())
            if ok:
                st.success(f"Libro registrado: «{titulo.strip()}»")
                if ruta:
                    lado = "izquierdo" if isbn < ruta[-1] else "derecho"
                    st.info(
                        "Ruta de inserción: " + " → ".join(map(str, ruta))
                        + f"\n\nQuedó como hijo **{lado}** de {ruta[-1]}."
                    )
                else:
                    st.info("Es el primer libro: quedó como **raíz** del árbol.")
            else:
                st.warning("Ese ISBN ya está registrado en el inventario.")

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Libros", arbol.size)
    c2.metric("Altura", arbol.height())
    st.caption("La altura es el máximo de comparaciones que necesita una búsqueda.")

    if st.button("🗑️ Vaciar inventario", use_container_width=True):
        st.session_state.arbol = BinaryTree()
        st.rerun()

# ---------------------------- Buscador principal -----------------------------
st.subheader("🔎 Buscar libro por ISBN")
consulta = st.text_input("Ingresa el ISBN a buscar", placeholder="9780132350884")

if consulta:
    isbn_buscado = normalizar_isbn(consulta)
    if isbn_buscado is None:
        st.error("ISBN inválido: debe tener 10 o 13 dígitos.")
    else:
        libro, ruta = arbol.search(isbn_buscado)
        if libro:
            st.success(f"**{libro['titulo']}** — {libro['autor']}")
        else:
            st.error("No se encontró ningún libro con ese ISBN.")
        st.caption(
            f"Nodos visitados ({len(ruta)} de {arbol.size}): "
            + (" → ".join(map(str, ruta)) if ruta else "árbol vacío")
        )

st.divider()

# ---------------------------- Inventario in-order ----------------------------
col_tabla, col_arbol = st.columns([3, 2])

with col_tabla:
    st.subheader("📖 Inventario ordenado (recorrido in-order)")
    catalogo = arbol.in_order_asc()
    if catalogo:
        st.dataframe(catalogo, use_container_width=True, hide_index=True)
    else:
        st.info("El inventario está vacío. Registra un libro desde la barra lateral.")

with col_arbol:
    st.subheader("🌳 Estructura del árbol")
    if arbol.root:
        st.graphviz_chart(arbol.to_dot())
        st.caption("🟨 Raíz · 🟦 Padre · 🟩 Hoja")
    else:
        st.info("Sin nodos todavía.")
