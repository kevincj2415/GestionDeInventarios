from flask import Flask, jsonify, render_template, request, redirect, url_for, flash,session
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
import requests

import secrets
import string

def generar_codigo_seguro(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

PIXABAY_API_KEY = "47289007-1c84d3d414f613c857c6ded8f"
BASE_URL = "https://api.pexels.com/v1/search"

status = {'secionIniciada' : False,
    'nombre' : "",
    "correo" : "",
    "tipo" : "",
    'pedidos' : 0,
    'idUsuario' : 0,
    'idOrga' : "",
    'tipoUs' : ""
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
            status['idOrga'] = ''
        print(status['idOrga'])
        return redirect('/inventario')

#inventario
@app.route('/inventario')
def inventario():
    productos = [producto for producto in app.db.productos.find({"idOrga": status['idOrga']})]
    return render_template('sitio/amd_inventario.html', productos=productos)


@app.route('/sitio/guardar', methods = ['POST'])
def guardar():
    global status
    idp = generar_codigo_seguro()
    productos = app.db.productos.find()
    for producto in productos:
        if producto['idp'] == idp:
            break
        else:
            idp = generar_codigo_seguro()
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    producto = {'idp':idp,'idOrga':status['idOrga'], 'nombre': nombre,'descripcion': descripcion,'precio': precio,'cantidad': cantidad,'creadorId': status['idUsuario']}
    app.db.productos.insert_one(producto)
    return redirect('/inventario')

@app.route('/sitio/borrarInventario/<codigo>')
def borrar(codigo):
    idp = codigo
    app.db.productos.delete_one({'idp': idp})
    return redirect('/inventario')

@app.route('/sitio/editarInventario/<codigo>')
def ediatarInventario(codigo):
    idp = codigo
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
    app.db.productos.update_one({'idp': id}, {'$set': producto})
    return redirect('/inventario')

#usuarios

@app.route('/usuario')
def usuarios():
    global status
    usuarios = app.db.usuarios.find({'idOrga': status['idOrga']})
    return render_template('/sitio/amd_usuario.html', usuarios = usuarios, status = status)

@app.route('/sitio/actualizar_user', methods = ['POST'])
def actualizar_user():
    global status
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    idu = request.form['idu']
    app.db.usuarios.update_one({'idu': idu }, {'$set': {'idu':idu,'idOrga':status['idOrga'],'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo}})
    return redirect('/usuario')

@app.route('/sitio/borrarUsuario/<codigo>')
def borrarUsusario(codigo):
    global status
    idu = codigo
    app.db.usuarios.delete_one({'idu': idu})
    return redirect('/usuario')

@app.route('/sitio/editarUsuario/<id>')
def editarUsuario(id):
    global status
    idu = str(id)
    usuario = app.db.usuarios.find_one({'idu': idu})
    return render_template('/sitio/editarUsuario.html', usuario = usuario)

@app.route('/sitio/guardarUsuario', methods = ['POST'])
def guardarUsuario():
    idu = generar_codigo_seguro()
    usuarios = app.db.usuarios.find()
    for usuario in usuarios:
        if usuario['idu'] == idu:
            break
        else:
            idu = generar_codigo_seguro()
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    usuario = {'idu':idu,'idOrga':status['idOrga'],'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo}
    app.db.usuarios.insert_one(usuario)
    return redirect('/usuario')

#Proveedores 

@app.route('/proveedores')
def proveedores():
    global status
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
    app.db.proveedores.update_one({'idp': idp }, {'$set':{'idp':idp, 'ido':status['idOrga'],'nombre':nombre, 'contacto':contacto, 'telefono':telefono, 'email':email}})
    return redirect('/proveedores')

@app.route('/sitio/borrarProveedor/<codigo>')
def borrarProveedor(codigo):
    idp = codigo
    app.db.proveedores.delete_one({'idp':idp}) 
    return redirect('/proveedores')

@app.route('/sitio/editarProveedor/<id>')
def editarProveedor(id):
    global status
    idp = id
    proveedor = app.db.proveedores.find_one({'idp':idp})
    
    return render_template('/sitio/editarProveedor.html', proveedor = proveedor)

@app.route('/sitio/guardarProveedor', methods = ['POST'])
def guardarProveedor():
    idp = generar_codigo_seguro()
    proveedores = app.db.productos.find()
    for proveedor in proveedores:
        if proveedor['idp'] == idp:
            break
        else:
            idp = generar_codigo_seguro()
    nombre = request.form['nombre']
    contacto = request.form['contacto']
    telefono = request.form['telefono']
    email = request.form['email']
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
    descripcion = request.form['descripcion']
    organizacion = {'idCreador': status['idUsuario'],'ido': ido,'nombre':nombre, 'descripcion':descripcion}
    app.db.Comunidad.insert_one(organizacion)
    status['idOrga'] = ido
    return redirect('/configuracion')

@app.route('/sitio/iniciarSesionOrganizacion', methods = ['POST'])
def iniciarSesionOrganizacion():
    global status
    correo = request.form['email']
    contraseña = request.form['password']
    
    # Consulta a la base de datos
    user = app.db.usuarios.find_one({'correo': correo})
    
    # Verificar si el usuario fue encontrado
    if user is None:
        return redirect('/correoErrado')

    
    # Verificar si la contraseña es correcta
    if user['contraseña']!= contraseña:
        return redirect('/contraseñaErrada')
    else:
    # Si la contraseña es correcta, iniciar sesión
        status['secionIniciada'] = True
        status['idUsuario'] = user['idu']
        status['nombre'] = user['nombre']
        status['correo'] = user['correo']
        status['tipo'] = user['tipo']
        status['idOrga'] = user['idOrga']
        return redirect('/inventario')
    
    
    
@app.route('/sitio/cerrarSesion')
def cerrarSesion():
    global status
    status = {'secionIniciada' : False,
    'nombre' : "",
    "correo" : "",
    "tipo" : "",
    'pedidos' : 0,
    'idUsuario' : 0,
    'idOrga' : "",
    'tipoUs' : ""
    }
    return render_template("sitio/index.html")
    
def buscar_imagenes(query):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        hits = data.get("hits", [])
        if hits:  # Verifica si hay resultados en "hits"
            return hits[0]  # Devuelve solo el primer resultado como diccionario
        else:
            print("No se encontraron imágenes para la consulta.")
            return "No se encontraron imágenes para la consulta."  # Devuelve un diccionario vacío si no hay resultados
    else:
        print(f"Error al conectar con la API: {response.status_code}")
        return "Error al conectar con la API:"


@app.route('/tienda')
def tienda():
    tiendas = app.db.Comunidad.find({})
    print(buscar_imagenes('roseria'))
    return render_template("sitio/tienda.html", tiendas=tiendas )

def elegir_imagen(palabra):
    datos = buscar_imagenes(palabra)
    if datos != "No se encontraron imágenes para la consulta.":
        img = datos['webformatURL']
        return img
    elif datos == "Error al conectar con la API:":
        return "https://via.placeholder.com/400x200"
    else:
        return "https://via.placeholder.com/400x200"  # Devuelve un placeholder si no hay resultados

app.jinja_env.globals.update(elegir_imagen=elegir_imagen)

@app.route('/productos/<id>')
def productos(id):
    productos = app.db.productos.find({'idOrga': id})
    return render_template("sitio/productos.html", productos=productos )
    
@app.route('/realizar_pedido', methods=['POST'])
def realizar_pedido():
    global status
    data = request.get_json()  # Obtener los datos en formato JSON
    productos = data.get('productos', [])
    total = data.get('total', 0)

    # Aquí puedes hacer lo que necesites con los datos del carrito (guardar en la base de datos, procesar el pago, etc.)
    app.db.pedidos.insert_one(data)
    app.db.pedidos.update_one({'id': data.get('id', ""), }, {'$set':{'idOrga': status['idOrga'], 'fecha': datetime.now()}})
    for producto in productos:
        idp = producto['id']
        hl = app.db.productos.find_one({'idp':idp})
        cantidad = int(hl['cantidad'])
        guar = cantidad - producto['cantidad']
        app.db.productos.update_one({'idp': idp, }, {'$set':{'cantidad':str(guar)}} )

    return jsonify({"message": "Pedido realizado correctamente", "status": "success"}), 200


if __name__ == '__main__':
    app.run(debug = True, port=5700)