from sqlalchemy.orm import Session
from models import Pedido, Menu, pedido_menu, Ingrediente, menu_ingrediente, Cliente
from utils.boleta_generator import generar_boleta
import datetime


class PedidoCRUD:
    """Clase para manejar operaciones CRUD de pedidos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear(self, cliente_id: int, menus_data: list):
        """
        Crea un nuevo pedido
        menus_data: lista de tuplas (menu_id, cantidad)
        """
        if not menus_data:
            raise ValueError("El pedido debe tener al menos un menú")

        # Calcular total y verificar stock
        total_pedido = 0
        items_pedido = []

        # Diccionario para acumular consumo de ingredientes y verificar stock globalmente para este pedido
        consumo_ingredientes = {}

        for menu_id, cantidad in menus_data:
            menu = self.db.query(Menu).filter(Menu.id == menu_id).first()
            if not menu:
                raise ValueError(f"Menú ID {menu_id} no encontrado")
            
            subtotal = menu.precio * cantidad
            total_pedido += subtotal
            items_pedido.append((menu, cantidad, subtotal))

            # Verificar ingredientes del menú
            # Necesitamos consultar la tabla de asociación para saber qué ingredientes usa este menú
            ingredientes_menu = self.db.execute(
                menu_ingrediente.select().where(menu_ingrediente.c.menu_id == menu_id)
            ).fetchall()

            for row in ingredientes_menu:
                ing_id = row.ingrediente_id
                cant_requerida = row.cantidad * cantidad
                consumo_ingredientes[ing_id] = consumo_ingredientes.get(ing_id, 0) + cant_requerida

        # Verificar stock disponible
        for ing_id, cantidad_total in consumo_ingredientes.items():
            ingrediente = self.db.query(Ingrediente).filter(Ingrediente.id == ing_id).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente ID {ing_id} no encontrado")
            if ingrediente.stock < cantidad_total:
                raise ValueError(f"Stock insuficiente para {ingrediente.nombre}. Requerido: {cantidad_total}, Disponible: {ingrediente.stock}")

        # Si todo está bien, crear el pedido y descontar stock
        nuevo_pedido = Pedido(cliente_id=cliente_id, total=total_pedido, fecha=datetime.datetime.now())
        self.db.add(nuevo_pedido)
        self.db.flush()

        for menu, cantidad, subtotal in items_pedido:
            stmt = pedido_menu.insert().values(pedido_id=nuevo_pedido.id, menu_id=menu.id, cantidad=cantidad, subtotal=subtotal)
            self.db.execute(stmt)

        # Descontar stock
        for ing_id, cantidad_total in consumo_ingredientes.items():
            ingrediente = self.db.query(Ingrediente).filter(Ingrediente.id == ing_id).first()
            ingrediente.stock -= cantidad_total

        self.db.commit()
        self.db.refresh(nuevo_pedido)

        # Generar Boleta PDF
        cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        cliente_nombre = cliente.nombre if cliente else "Cliente"
        
        items_boleta = []
        for menu, cantidad, subtotal in items_pedido:
            items_boleta.append((menu.nombre, cantidad, menu.precio, subtotal))
            
        try:
            boleta_path = generar_boleta(nuevo_pedido.id, cliente_nombre, nuevo_pedido.fecha, items_boleta, nuevo_pedido.total)
            nuevo_pedido.boleta_path = boleta_path
            self.db.commit()
        except Exception as e:
            print(f"Error generando boleta: {e}")
            # No fallamos el pedido si falla la boleta, pero logueamos

        return nuevo_pedido
    
    def leer_por_cliente(self, cliente_id: int):
        """Obtiene todos los pedidos de un cliente"""
        return self.db.query(Pedido).filter(Pedido.cliente_id == cliente_id).all()
