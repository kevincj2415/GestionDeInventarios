from flask import Flask, redirect, render_template, request
from flask import *
from flask_mysqldb import MySQL



app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'gestion_inventarios'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)

@app.route('/')
def index():
    sql = "SELECT * FROM productos "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    productos = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/index.html', productos=productos)


@app.route('/sitio/guardar', methods = ['POST'])
def guardar():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    sql = "INSERT INTO productos(nombre,descripcion,precio,cantidad) VALUES (%s,%s,%s,%s)"
    datos = (nombre,descripcion,precio,cantidad)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/')

@app.route('/sitio/borrar/<int:codigo>')
def borrar(codigo):
    sql = "DELETE FROM productos WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    conexion.commit()
    return redirect('/')

@app.route('/sitio/editar/<int:codigo>')
def ediatar(codigo):
    sql = "SELECT * FROM productos WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    producto = cursor.fetchone()
    conexion.commit()
    return render_template('/sitio/editar.html', producto=producto)

@app.route('/sitio/actualizar', methods = ['POST'])
def actualizar():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    
    id = request.form['id']
    sql = "UPDATE productos set nombre= %s, descripcion= %s, precio=%s, cantidad= %s WHERE id= %s"
    datos = (nombre,descripcion, precio, cantidad, id)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/')

#PARTE PARCIAL CORTE 1

@app.route('/usuario')
def usuarios():
    sql = "SELECT * FROM usuarios "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    conexion.commit()
    return render_template('/sitio/amd_usuario.html', usuarios = usuarios)

@app.route('/sitio/actualizar_user', methods = ['POST'])
def actualizar_user():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    pedidos = request.form['pedidos']
    id = request.form['ID']
    sql = "UPDATE usuarios set nombre= %s, correo=%s,contraseña=%s,tipo=%s,pedidos=%s WHERE ID= %s"
    datos = (nombre, correo,contraseña,tipo,pedidos, id)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/usuario')

@app.route('/sitio/borrarUsuario/<int:codigo>')
def borrarUsusario(codigo):
    sql = "DELETE FROM usuarios WHERE ID = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    conexion.commit()
    return redirect('/usuario')

@app.route('/sitio/editarUsuario/<int:id>')
def editarUsuario(id):
    sql = "SELECT * FROM usuarios WHERE ID = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (id,))
    usuario = cursor.fetchone()
    conexion.commit()
    return render_template('/sitio/editarUsuario.html', usuario = usuario)

@app.route('/sitio/guardarUsuario', methods = ['POST'])
def guardarUsuario():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    pedidos = request.form['pedidos']
    sql = "INSERT INTO usuarios(nombre, correo,contraseña,tipo,pedidos) VALUES (%s,%s,%s,%s,%s)"
    datos = (nombre, correo,contraseña,tipo,pedidos)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/usuario')

if __name__ == '__main__':
    app.run(debug = True)