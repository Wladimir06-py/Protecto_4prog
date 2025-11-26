from sqlalchemy.orm import Session
from models import Cliente
import re


class ClienteCRUD:
    """Clase para manejar operaciones CRUD de clientes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def validar_correo(correo):
        """Valida el formato de un correo electrónico"""
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, correo) is not None
    
    def crear(self, nombre: str, correo: str):
        """Crea un nuevo cliente"""
        if not nombre or not correo:
            raise ValueError("Nombre y correo son obligatorios")
        if not self.validar_correo(correo):
            raise ValueError("Formato de correo inválido")
        
        existente = self.db.query(Cliente).filter(Cliente.correo == correo).first()
        if existente:
            raise ValueError("El correo ya está registrado")

        nuevo_cliente = Cliente(nombre=nombre, correo=correo)
        self.db.add(nuevo_cliente)
        self.db.commit()
        self.db.refresh(nuevo_cliente)
        return nuevo_cliente
    
    def leer_todos(self):
        """Obtiene todos los clientes"""
        return self.db.query(Cliente).all()
    
    def actualizar(self, cliente_id: int, nombre: str = None, correo: str = None):
        """Actualiza los datos de un cliente"""
        cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return None
        
        if nombre: 
            cliente.nombre = nombre
        if correo:
            if not self.validar_correo(correo):
                raise ValueError("Formato de correo inválido")
            # Verificar unicidad si cambia el correo
            if correo != cliente.correo:
                existente = self.db.query(Cliente).filter(Cliente.correo == correo).first()
                if existente:
                    raise ValueError("El correo ya está registrado")
            cliente.correo = correo
            
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def eliminar(self, cliente_id: int):
        """Elimina un cliente"""
        cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return False
        
        # Verificar si tiene pedidos
        if cliente.pedidos:
            raise ValueError("No se puede eliminar un cliente con pedidos asociados")
            
        self.db.delete(cliente)
        self.db.commit()
        return True
