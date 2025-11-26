from sqlalchemy.orm import Session
from models import Menu, Ingrediente, menu_ingrediente


class MenuCRUD:
    """Clase para manejar operaciones CRUD de menús"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear(self, nombre: str, descripcion: str, precio: float, ingredientes_data: list):
        """
        Crea un nuevo menú
        ingredientes_data: lista de tuplas (ingrediente_id, cantidad_requerida)
        """
        if not nombre or precio < 0:
            raise ValueError("Datos de menú inválidos")
        
        # Verificar ingredientes
        # Esto es un poco más complejo con la tabla de asociación, 
        # por simplicidad insertamos el menú y luego las relaciones
        
        nuevo_menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
        self.db.add(nuevo_menu)
        self.db.flush()  # Para obtener el ID del menú

        for ing_id, cantidad in ingredientes_data:
            if cantidad <= 0:
                self.db.rollback()
                raise ValueError("Cantidad de ingrediente debe ser positiva")
            
            stmt = menu_ingrediente.insert().values(menu_id=nuevo_menu.id, ingrediente_id=ing_id, cantidad=cantidad)
            self.db.execute(stmt)
            
        self.db.commit()
        self.db.refresh(nuevo_menu)
        return nuevo_menu
    
    def leer_todos(self):
        """Obtiene todos los menús"""
        return self.db.query(Menu).all()
    
    def eliminar(self, menu_id: int):
        """Elimina un menú"""
        menu = self.db.query(Menu).filter(Menu.id == menu_id).first()
        if menu:
            # SQLAlchemy maneja la eliminación en la tabla de asociación si está configurado cascade, 
            # pero por seguridad podemos limpiar manualmente o confiar en el ORM.
            # En este caso simple, borramos el menú.
            self.db.delete(menu)
            self.db.commit()
            return True
        return False
