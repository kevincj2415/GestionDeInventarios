from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from Usuario import Usuario
from pymongo import MongoClient
import datetime
import mysql.connector
import datetime
status = {'secionIniciada' : False,
    'nombre' : "",
    "correo" : "",
    "tipo" : "",
    'pedidos' : 0,
    'idUsuario' : 0,
    'idOrga' : "",
    }

app = Flask(__name__)

cliente = MongoClient("mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/")
app.db = cliente.gestion_inventairo


mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'gestion_inventarios'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)

@app.route('/contraseñaErrada')
def contraseñaErrada():
    return render_template('sitio/contraseñaErrada.html')

@app.route('/inicio')
def inicio():
    if status['secionIniciada']:
        return redirect('/inventario')
    else:
        return render_template('sitio/inicioSesion.html', status=status)

@app.route('/correoErrado')
def correoErrado():
    return render_template('sitio/correoErrado.html')

@app.route('/')
def index():
    sql = "SELECT * FROM productos "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    productos = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/index.html', productos=productos)

@app.route('/inicioSesion')
def InicioSesion():
    sql = "SELECT * FROM usuarios"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/iniciosesion.html', usuarios=usuarios)

@app.route('/registrarUsuario')
def registroUsuario():
    return render_template('sitio/RegistroUsuario.html')


@app.route('/sitio/registrarUsuario', methods = ['POST'])
def registrarUsuario():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    pedidos = 0
    usuario = {'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo, 'pedidos':pedidos}
    usuario = Usuario(usuario)
    usuario.set_password(contraseña)
    sql = "INSERT INTO usuarios (nombre, correo, contraseña, tipo, pedidos) VALUES (%s, %s, %s, %s, %s)"
    datos = (nombre, correo, usuario.contraseña, tipo, pedidos)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/inicioSesion')
    
@app.route('/sitio/iniciarSesion', methods = ['POST'])
def iniciarSesion():
    global status
    correo = request.form['email']
    contraseña = request.form['password']
    
    # Consulta a la base de datos
    sql = "SELECT * FROM usuarios WHERE correo = %s"
    datos = (correo,)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    user = cursor.fetchone()
    
    # Verificar si el usuario fue encontrado
    if user is None:
        return redirect('/correoErrado')

    # Crear objeto Usuario
    usuario = Usuario(user)
    
    # Verificar si la contraseña es correcta
    if not usuario.check_password(contraseña):
        return redirect('/contraseñaErrada')
    else:
    # Si la contraseña es correcta, iniciar sesión
        status['secionIniciada'] = True
        status['idUsuario'] = user['ID']
        status['nombre'] = usuario.nombre
        status['correo'] = usuario.correo
        status['tipo'] = usuario.tipo
        status['pedidos'] = usuario.pedidos
        com = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
        if com != None:
            status['idOrga'] = com['ido']
        else:
            status['idOrga'] = 'Error'
        print(status['idOrga'])
        return redirect('/inventario')

#inventario
@app.route('/inventario')
def inventario():
    productos = [producto for producto in app.db.productos.find({"creadorId": status['idUsuario']})]
    """sql = "SELECT * FROM productos "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    productos = cursor.fetchall()
    conexion.commit()"""
    return render_template('sitio/amd_inventario.html', productos=productos)


@app.route('/sitio/guardar', methods = ['POST'])
def guardar():
    global status
    idp = request.form['ID']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    producto = {'idp':idp, 'nombre': nombre,'descripcion': descripcion,'precio': precio,'cantidad': cantidad,'creadorId': status['idUsuario']}
    """sql = "INSERT INTO productos(nombre,descripcion,precio,cantidad) VALUES (%s,%s,%s,%s)"
    datos = (nombre,descripcion,precio,cantidad)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    app.db.productos.insert_one(producto)
    return redirect('/inventario')

@app.route('/sitio/borrarInventario/<int:codigo>')
def borrar(codigo):
    """ sql = "DELETE FROM productos WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    conexion.commit()"""
    idp = str(codigo)
    app.db.productos.delete_one({'idp': idp})
    return redirect('/inventario')

@app.route('/sitio/editarInventario/<int:codigo>')
def ediatarInventario(codigo):
    """sql = "SELECT * FROM productos WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    producto = cursor.fetchone()
    conexion.commit()"""
    idp = str(codigo)
    producto =  app.db.productos.find_one({"idp": idp})
    return render_template('/sitio/editarInventario.html', producto=producto)

@app.route('/sitio/actualizar', methods = ['POST'])
def actualizar():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    id = request.form['id']
    producto = {'nombre': nombre,'descripcion': descripcion,'precio': precio,'cantidad': cantidad,'creadorId': status['idUsuario']}
    """sql = "UPDATE productos set nombre= %s, descripcion= %s, precio=%s, cantidad= %s WHERE id= %s"
    datos = (nombre,descripcion, precio, cantidad, id)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    app.db.productos.update_one({'idp': id}, {'$set': producto})
    return redirect('/inventario')

#usuarios

@app.route('/usuario')
def usuarios():
    global status
    """sql = "SELECT * FROM usuarios "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    conexion.commit()"""
    comunidad = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
    usuarios = [usuario for usuario in comunidad['integrantes']]
    return render_template('/sitio/amd_usuario.html', usuarios = usuarios)

@app.route('/sitio/actualizar_user', methods = ['POST'])
def actualizar_user():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    idu = request.form['idu']
    usuario = {'idu':idu,'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo}
    usuario = Usuario(usuario)
    usuario.set_password(contraseña)
    user = {'idu':idu,'nombre':nombre, 'correo':correo, 'contraseña':usuario.contraseña, 'tipo':tipo}
    """sql = "UPDATE usuarios set nombre= %s, correo=%s,contraseña=%s,tipo=%s,pedidos=%s WHERE ID= %s"
    datos = (nombre, correo,usuario.contraseña,tipo,pedidos, id)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    comunidad = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
    usuarios = [usuario for usuario in comunidad['integrantes']]
    idu = str(idu)
    for usuariol in usuarios:
        if usuariol['idu'] == idu:
            usuarios.remove(usuariol)
            usuarios.append(user)
            app.db.Comunidad.update_one({'idCreador': status['idUsuario'] }, {'$set': {'integrantes': usuarios}})   
        else:
            print ("Error")
    return redirect('/usuario')

@app.route('/sitio/borrarUsuario/<int:codigo>')
def borrarUsusario(codigo):
    global status
    """sql = "DELETE FROM usuarios WHERE ID = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    conexion.commit()"""
    comunidad = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
    usuarios = [usuario for usuario in comunidad['integrantes']]
    idu = str(codigo)
    for usuariol in usuarios:
        if usuariol['idu'] == idu:
            usuarios.remove(usuariol)
            app.db.Comunidad.update_one({'idCreador': status['idUsuario'] }, {'$set': {'integrantes': usuarios}})   
        else:
            print ("Error")
    return redirect('/usuario')

@app.route('/sitio/editarUsuario/<int:id>')
def editarUsuario(id):
    global status
    """sql = "SELECT * FROM usuarios WHERE ID = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (id,))
    usuario = cursor.fetchone()
    conexion.commit()"""
    comunidad = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
    usuarios = [usuario for usuario in comunidad['integrantes']]
    idu = str(id)
    usuario = {}
    for usuariol in usuarios:
        if usuariol['idu'] == idu:
            usuario = usuariol
        else:
            usuario = None
    return render_template('/sitio/editarUsuario.html', usuario = usuario)

@app.route('/sitio/guardarUsuario', methods = ['POST'])
def guardarUsuario():
    idu = request.form['idu']
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    usuario = {'idu':idu,'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo}
    usuario = Usuario(usuario)
    usuario.set_password(contraseña)
    user = usuario = {'idu':idu,'nombre':nombre, 'correo':correo, 'contraseña':usuario.contraseña, 'tipo':tipo}
    comunidad = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
    usuarios = [usuario for usuario in comunidad['integrantes']]
    usuarios.append(user)
    app.db.Comunidad.update_one({'idCreador': status['idUsuario'] }, {'$set': {'integrantes': usuarios}})
    """sql = "INSERT INTO usuarios(nombre, correo,contraseña,tipo,pedidos) VALUES (%s,%s,%s,%s,%s)"
    datos = (nombre, correo,usuario.contraseña,tipo,pedidos)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    
    return redirect('/usuario')

#Proveedores 

@app.route('/proveedores')
def proveedores():
    global status
    """sql = "SELECT * FROM proveedores "
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql)
    proveedores = cursor.fetchall()
    conexion.commit()"""
    proveedores = [proveedor for proveedor in app.db.proveedores.find({'ido': status['idOrga']})]
    return render_template('/sitio/amd_proveedores.html', proveedores = proveedores)

@app.route('/sitio/actualizar_proveedor', methods = ['POST'])
def actualizar_proveedor():
    global status
    nombre = request.form['nombre']
    contacto = request.form['contacto']
    telefono = request.form['telefono']
    email = request.form['email']
    idp = request.form['idp']
    """sql = "UPDATE proveedores set nombre= %s, contacto=%s,telefono=%s,email=%s WHERE id= %s"
    datos = (nombre, contacto,telefono,email,id)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    app.db.proveedores.update_one({'idp': idp }, {'$set':{'idp':idp, 'ido':status['idOrga'],'nombre':nombre, 'contacto':contacto, 'telefono':telefono, 'email':email}})
    return redirect('/proveedores')

@app.route('/sitio/borrarProveedor/<int:codigo>')
def borrarProveedor(codigo):
    """sql = "DELETE FROM proveedores WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (codigo,))
    conexion.commit()"""
    idp = str(codigo)
    app.db.proveedores.delete_one({'idp':idp}) 
    return redirect('/proveedores')

@app.route('/sitio/editarProveedor/<int:id>')
def editarProveedor(id):
    global status
    """sql = "SELECT * FROM proveedores WHERE id = %s"
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, (id,))
    proveedor = cursor.fetchone()
    conexion.commit()"""
    idp = str(id)
    proveedor = app.db.proveedores.find_one({'idp':idp})
    
    return render_template('/sitio/editarProveedor.html', proveedor = proveedor)

@app.route('/sitio/guardarProveedor', methods = ['POST'])
def guardarProveedor():
    idp = request.form['idp']
    nombre = request.form['nombre']
    contacto = request.form['contacto']
    telefono = request.form['telefono']
    email = request.form['email']
    """sql = "INSERT INTO proveedores(nombre, contacto,telefono,email) VALUES (%s,%s,%s,%s)"
    datos = (nombre, contacto,telefono,email)
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()"""
    proveedor = {'idp':idp, 'ido':status['idOrga'], 'nombre':nombre,'contacto':contacto,'telefono':telefono,'email':email}
    app.db.proveedores.insert_one(proveedor)
    return redirect('/proveedores')

@app.route('/configuracion')
def configuracion():
    global status
    return render_template('/sitio/configuracion.html', status=status)

@app.route('/sitio/crearOrganizacion', methods = ['POST'])
def CrearOrganizacion():
    global status
    nombre = request.form['nombre']
    ido = request.form['ido']
    organizacion = {'idCreador': status['idUsuario'],'ido': ido,'nombre':nombre, 'integrantes': []}
    app.db.Comunidad.insert_one(organizacion)
    return redirect('/usuario')

if __name__ == '__main__':
    app.run(debug = True, port=5700)