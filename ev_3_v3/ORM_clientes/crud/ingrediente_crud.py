from sqlalchemy.orm import Session
from models import Ingrediente
import csv


class IngredienteCRUD:
    """Clase para manejar operaciones CRUD de ingredientes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear(self, nombre: str, stock: float, unidad: str):
        """Crea un nuevo ingrediente"""
        if not nombre or stock < 0:
            raise ValueError("Nombre inválido o stock negativo")
        
        # Verificar duplicados
        existente = self.db.query(Ingrediente).filter(Ingrediente.nombre == nombre).first()
        if existente:
            raise ValueError(f"El ingrediente '{nombre}' ya existe.")

        nuevo_ingrediente = Ingrediente(nombre=nombre, stock=stock, unidad=unidad)
        self.db.add(nuevo_ingrediente)
        self.db.commit()
        self.db.refresh(nuevo_ingrediente)
        return nuevo_ingrediente
    
    def leer_todos(self):
        """Obtiene todos los ingredientes"""
        return self.db.query(Ingrediente).all()
    
    def actualizar(self, ingrediente_id: int, nombre: str = None, stock: float = None, unidad: str = None):
        """Actualiza los datos de un ingrediente"""
        ingrediente = self.db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
        if not ingrediente:
            return None
        
        if nombre: 
            ingrediente.nombre = nombre
        if stock is not None: 
            if stock < 0: 
                raise ValueError("Stock no puede ser negativo")
            ingrediente.stock = stock
        if unidad: 
            ingrediente.unidad = unidad
        
        self.db.commit()
        self.db.refresh(ingrediente)
        return ingrediente
    
    def eliminar(self, ingrediente_id: int):
        """Elimina un ingrediente"""
        ingrediente = self.db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
        if ingrediente:
            self.db.delete(ingrediente)
            self.db.commit()
            return True
        return False
    
    def cargar_desde_csv(self, filepath: str):
        """Carga ingredientes desde un archivo CSV"""
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nombre = row.get('nombre')
                    stock = float(row.get('stock') or row.get('cantidad', 0))
                    unidad = row.get('unidad')
                    
                    if nombre and stock >= 0 and unidad:
                        existente = self.db.query(Ingrediente).filter(Ingrediente.nombre == nombre).first()
                        if existente:
                            existente.stock += stock  # Sumar al stock existente
                        else:
                            nuevo = Ingrediente(nombre=nombre, stock=stock, unidad=unidad)
                            self.db.add(nuevo)
                self.db.commit()
                return True
        except Exception as e:
            self.db.rollback()
            print(f"Error cargando CSV: {e}")
            return False
