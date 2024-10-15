from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Usuario(UserMixin):
    def __init__(self,usuario:dict):
        self.id = usuario.get('ID')  # ID es necesario para Flask-Login
        self.nombre = usuario.get('nombre', '')
        self.correo = usuario.get('correo', '')
        self.contraseña = usuario.get('contraseña', '')
        self.tipo = usuario.get('tipo', 'usuario')  # Por defecto 'usuario'
        self.pedidos = usuario.get('pedidos', '')   # Inicializa 'pedidos' de manera segura
        
        
    def set_password(self, password):
        self.contraseña = generate_password_hash(password)
        return self.contraseña

    def check_password(self, password):
        return check_password_hash(self.contraseña, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.correo)
    
    

        