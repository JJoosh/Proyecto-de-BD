from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from conexion.conexionBD import connectionBD

import openpyxl
import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio

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

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    # Lógica para la página de ventas
    return render_template('public/ventas/Venta.html')


@app.route('/generar-reporte-ventas', methods=['POST'])
def generar_reporte_ventas_route():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_usuario = request.form.get('nombre_usuario')
        id_producto = request.form.get('id_producto')

        try:
            # Conectar a la base de datos
            connection = connectionBD()
            cursor = connection.cursor()

            # Obtener el ID de usuario basado en el nombre del usuario proporcionado
            select_user_id_query = "SELECT id FROM users WHERE name_surname = %s"
            cursor.execute(select_user_id_query, (nombre_usuario,))
            user_id = cursor.fetchone()

            if user_id:
                user_id = user_id[0]

                # Insertar datos en la tabla de Ventas
                insert_query = "INSERT INTO Ventas (UserId, InventarioId) VALUES (%s, %s)"
                cursor.execute(insert_query, (user_id, id_producto))

                # Realizar confirmación de la transacción
                connection.commit()

                flash('Venta realizada con éxito', 'success')
            else:
                # Manejar el caso en que no se encuentra el usuario
                flash('Usuario no encontrado', 'danger')

        except Exception as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            print(f"Error al insertar en la base de datos: {e}")
            connection.rollback()

        finally:
            # Cerrar la conexión
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Redirigir a la página de ventas (puedes ajustar la ruta según tu estructura de carpetas)
    return render_template('public/ventas/Venta.html')


@app.route('/VerReporte', methods=['GET', 'POST'])
def verreporte():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        Ventas.IdVentas,
                        Ventas.fecha_venta,
                        users.name_surname AS NombreUsuario,
                        Inventario.Nombre AS NombreProducto,
                        Ventas.UserId
                    FROM Ventas
                    JOIN users ON Ventas.UserId = users.id
                    JOIN Inventario ON Ventas.InventarioId = Inventario.Id
                """)
                cursor.execute(querySQL,)
                reporte_data = cursor.fetchall()

        return render_template('public/ventas/vistareporte.html', reporte=reporte_data)

    except Exception as e:
        print(f"Error en la función verreporte: {e}")
        flash('Ocurrió un error al obtener el reporte.', 'error')
        return redirect(url_for('loginCliente'))


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
        flash('Primero debes iniciar sesiópip install xlsxwriter --upgraden.', 'error')
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
    

@app.route("/descargar_reporte")
def descargar_reporte():
    if 'conectado' in session:
        return descargarreporte()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


def descargarreporte():
    venta = generarepVenta()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("ID de ventas","Nombre de Usuario", "Nombre del producto", "Fecha")

    hoja.append(cabeceraExcel)
    for registro in venta:
        print(registro)
        id_ventas = registro['IdVentas']
        fecha_venta = registro['fecha_venta']
        user_id = registro['NombreUsuario']
        inventario_id = registro['NombreProducto']

        hoja.append((id_ventas, user_id, inventario_id, fecha_venta))
    
    # Guardar el libro de trabajo como un archivo Excel
    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_venta_{id_ventas}_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)

def generarepVenta():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        Ventas.IdVentas,
                        Ventas.fecha_venta,
                        users.name_surname AS NombreUsuario,
                        Inventario.Nombre AS NombreProducto,
                        Ventas.UserId
                    FROM Ventas
                    JOIN users ON Ventas.UserId = users.id
                    JOIN Inventario ON Ventas.InventarioId = Inventario.Id
                """)
                cursor.execute(querySQL,)
                reporte_data = cursor.fetchall()

        return reporte_data

    except Exception as e:
        print(f"Error en la función verreporte: {e}")
        flash('Ocurrió un error al obtener el reporte.', 'error')
        return redirect(url_for('loginCliente'))
    
def sql_detalles_ventaBD(id_venta):
    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    # Consulta SQL para obtener detalles de la venta con información del usuario, producto y costo
    sql_query = """
        SELECT 
            Ventas.IdVentas,
            Ventas.fecha_venta,
            users.name_surname AS NombreUsuario,
            Inventario.Nombre AS NombreProducto,
            Inventario.Costo AS Costo,
            Ventas.UserId
        FROM Ventas
        JOIN users ON Ventas.UserId = users.id
        JOIN Inventario ON Ventas.InventarioId = Inventario.Id
        WHERE Ventas.IdVentas = %s
    """
    print("Consulta SQL:", sql_query)

    cursor.execute(sql_query, [id_venta])

    detalles_venta = cursor.fetchone()

    # Cerrar la conexión
    cursor.close()
    conexion_MySQLdb.close()

    return detalles_venta


@app.route("/ver_detalles/<int:idVenta>", methods=['GET'])
def verDetallesVenta(idVenta):
    if 'conectado' in session:
        detalles_venta = sql_detalles_ventaBD(idVenta) or []
        return render_template('public/ventas/detalles_venta.html', detalles_venta=detalles_venta)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('loginCliente'))
