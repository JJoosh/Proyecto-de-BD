let carrito = [];
let total = 0;

function agregarAlCarrito(producto, precio) {
    carrito.push({ producto, precio });
    total += precio;

    actualizarCarrito();
}

function actualizarCarrito() {
    const listaCarrito = document.getElementById('lista-carrito');
    const totalElement = document.getElementById('total');

    // Limpiar el contenido previo
    listaCarrito.innerHTML = '';

    // Actualizar la lista del carrito
    carrito.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.producto}: $${item.precio.toFixed(2)}`;
        listaCarrito.appendChild(li);
    });

    // Actualizar el total
    totalElement.textContent = `Total: $${total.toFixed(2)}`;
}
