from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

# Tabla de asociación entre Menu e Ingrediente
menu_ingrediente = Table(
    'menu_ingrediente', Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True),
    Column('ingrediente_id', Integer, ForeignKey('ingredientes.id'), primary_key=True),
    Column('cantidad', Float, nullable=False) # Cantidad del ingrediente requerida para este menú
)

# Tabla de asociación entre Pedido y Menu (Detalle del Pedido)
pedido_menu = Table(
    'pedido_menu', Base.metadata,
    Column('pedido_id', Integer, ForeignKey('pedidos.id'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True),
    Column('cantidad', Integer, nullable=False),
    Column('subtotal', Float, nullable=False)
)

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)

    pedidos = relationship("Pedido", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(nombre='{self.nombre}', correo='{self.correo}')>"

class Ingrediente(Base):
    __tablename__ = 'ingredientes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    stock = Column(Float, nullable=False)
    unidad = Column(String, nullable=False) # Ej: kg, litros, unidades

    menus = relationship("Menu", secondary=menu_ingrediente, back_populates="ingredientes")

    def __repr__(self):
        return f"<Ingrediente(nombre='{self.nombre}', stock={self.stock} {self.unidad})>"

class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)

    ingredientes = relationship("Ingrediente", secondary=menu_ingrediente, back_populates="menus")
    pedidos = relationship("Pedido", secondary=pedido_menu, back_populates="menus")

    def __repr__(self):
        return f"<Menu(nombre='{self.nombre}', precio={self.precio})>"

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.now)
    total = Column(Float, default=0.0)
    boleta_path = Column(String)

    cliente = relationship("Cliente", back_populates="pedidos")
    menus = relationship("Menu", secondary=pedido_menu, back_populates="pedidos")

    def __repr__(self):
        return f"<Pedido(id={self.id}, fecha='{self.fecha}', total={self.total})>"
