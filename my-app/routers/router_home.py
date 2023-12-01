from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from conexion.conexionBD import connectionBD

# Importando cenexión a BD
from controllers.funciones_home import *

PATH_URL = "public/empleados"


@app.route('/registrar-empleado', methods=['GET'])
def viewFormEmpleado():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-empleado', methods=['POST'])
def formEmpleado():
    if 'conectado' in session:
        if 'foto_empleado' in request.files:
            foto_perfil = request.files['foto_empleado']
            resultado = procesar_form_empleado(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_empleados'))
            else:
                flash('El empleado NO fue registrado.', 'error')
                return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/lista-de-empleados', methods=['GET'])
def lista_empleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/lista_empleados.html', empleados=sql_lista_empleadosBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-empleado/", methods=['GET'])
@app.route("/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def detalleEmpleado(idEmpleado=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idEmpleado es None o no está presente en la URL
        if idEmpleado is None:
            return redirect(url_for('inicio'))
        else:
            detalle_empleado = sql_detalles_empleadosBD(idEmpleado) or []
            return render_template(f'{PATH_URL}/detalles_empleado.html', detalle_empleado=detalle_empleado)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Buscadon de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            return render_template(f'{PATH_URL}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Recibir formulario para actulizar informacion de empleado
@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))


@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/inventario')
def inventory():
    # Verificar si el usuario está conectado
    if 'conectado' in session:
        # Obtener datos de la tabla de inventario
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Inventario")
        inventario_data = cursor.fetchall()

        # Cerrar la conexión
        cursor.close()
        conexion_MySQLdb.close()

        # Renderizar la plantilla con los datos del inventario
        return render_template('public/inventario/inventario.html', inventario=inventario_data)
    else:
        flash('Debes iniciar sesión para acceder al inventario.', 'error')
        return redirect(url_for('loginCliente'))

@app.route('/ventas')
def ventas():
    # Lógica para la página de ventas
    return render_template('public/ventas/ventas.html')



def sql_detalles_productoBD(id_producto):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    # Ejemplo de consulta SQL para obtener detalles del producto
    sql_query = "SELECT * FROM Inventario WHERE Id = %s" % id_producto
    print("Consulta SQL:", sql_query)
    cursor.execute("SELECT * FROM Inventario WHERE Id = %s", [id_producto])

    detalle_producto = cursor.fetchone()

    # Cerrar la conexión
    cursor.close()
    conexion_MySQLdb.close()

    return detalle_producto

#Ver detalles del producto
@app.route("/detalles-producto/", methods=['GET'])
@app.route("/detalles-producto/<int:idProducto>", methods=['GET'])
def detalleProducto(idProducto=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idProducto es None o no está presente en la URL
        if idProducto is None:
            return redirect(url_for('inventario'))
        else:
            detalle_producto = sql_detalles_productoBD(idProducto) or []
            return render_template('public/inventario/detalles_producto.html', detalle_producto=detalle_producto)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('loginCliente'))
    

@app.route("/actualizar-producto/<int:idProducto>", methods=['GET', 'POST'])
def actualizarExistenciaProducto(idProducto):
    if 'conectado' in session:
        if request.method == 'POST':
            # Obtener la nueva existencia del formulario
            nueva_existencia = request.form.get('existencia_producto')

            # Lógica para actualizar solo el campo de existencia en la base de datos
            data = {'form': {'existencia_producto': nueva_existencia, 'Id': idProducto}}
            procesar_actualizacion_existencia(data)

            flash('Existencia del producto actualizada exitosamente.', 'success')
            return redirect(url_for('inventory'))
        else:
            # Obtener detalles del producto para prellenar el formulario de actualización
            detalle_producto = sql_detalles_productoBD(idProducto) or []
            return render_template('public/inventario/actualizar_producto.html', detalle_producto=detalle_producto)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('loginCliente'))
    

@app.route('/borrar-producto/<string:idProducto>', methods=['GET'])
def borrarProducto(idProducto):
    resp = eliminarProductoInventario(idProducto)
    if resp:
        flash('El producto fue eliminado correctamente', 'success')
    else:
        flash('Hubo un error al intentar eliminar el producto', 'error')

    return redirect(url_for('inventory'))



@app.route('/registrarInventario')
def registrarInventario():
    # Lógica para la página de ventas
    return render_template('public/inventario/registrarInventario.html')



@app.route('/registrar-inventario', methods=['GET'])
def viewFormInventario():
    if 'conectado' in session:
        return render_template('public/inventario/registrarInventario.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-inventario', methods=['POST'])
def formInventario():
    if 'conectado' in session:
        resultado = procesar_form_inventario(request.form)

        if resultado:
            return redirect(url_for('inventory'))
        else:
            flash('El inventario NO fue registrado.', 'error')
            return render_template('')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))