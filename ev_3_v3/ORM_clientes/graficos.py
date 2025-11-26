import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy.orm import Session
from models import Pedido, Menu, Ingrediente, pedido_menu, menu_ingrediente
from sqlalchemy import func
import datetime


class Graficos:
    """Clase para generar gráficos estadísticos del restaurante"""
    
    def __init__(self, db: Session, frame):
        """
        Inicializa la clase de gráficos
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            frame: Frame de tkinter donde se mostrará el gráfico
        """
        self.db = db
        self.frame = frame
    
    def graficar_ventas_por_fecha(self):
        """Genera un gráfico de barras con las ventas agrupadas por fecha"""
        # Agrupar ventas por fecha (día)
        resultados = self.db.query(
            func.date(Pedido.fecha).label('fecha'),
            func.sum(Pedido.total).label('total')
        ).group_by(func.date(Pedido.fecha)).all()

        if not resultados:
            return False

        fechas = [r.fecha for r in resultados]
        totales = [r.total for r in resultados]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.bar(fechas, totales, color='skyblue')
        ax.set_title("Ventas por Fecha")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Total Vendido ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return True

    def graficar_menus_mas_vendidos(self):
        """Genera un gráfico de torta con los 5 menús más vendidos"""
        # Consultar cantidad de veces que se ha vendido cada menú
        resultados = self.db.query(
            Menu.nombre,
            func.sum(pedido_menu.c.cantidad).label('total_vendido')
        ).join(pedido_menu).group_by(Menu.id).order_by(func.sum(pedido_menu.c.cantidad).desc()).limit(5).all()

        if not resultados:
            return False

        nombres = [r.nombre for r in resultados]
        cantidades = [r.total_vendido for r in resultados]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.pie(cantidades, labels=nombres, autopct='%1.1f%%', startangle=90)
        ax.set_title("Menús Más Vendidos")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return True

    def graficar_uso_ingredientes(self):
        """Genera un gráfico de barras horizontales con los 10 ingredientes más usados"""
        # Estimar uso de ingredientes basado en pedidos
        # Esto es una aproximación basada en la definición actual de los menús
        # Si los menús cambian, esto refleja la definición actual, no la histórica exacta si no se guardó snapshot
        
        # Consulta compleja: Join Pedido -> PedidoMenu -> Menu -> MenuIngrediente -> Ingrediente
        resultados = self.db.query(
            Ingrediente.nombre,
            func.sum(pedido_menu.c.cantidad * menu_ingrediente.c.cantidad).label('total_usado')
        ).select_from(Pedido)\
        .join(pedido_menu)\
        .join(Menu)\
        .join(menu_ingrediente)\
        .join(Ingrediente)\
        .group_by(Ingrediente.id)\
        .order_by(func.sum(pedido_menu.c.cantidad * menu_ingrediente.c.cantidad).desc())\
        .limit(10).all()

        if not resultados:
            return False

        nombres = [r.nombre for r in resultados]
        cantidades = [r.total_usado for r in resultados]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.barh(nombres, cantidades, color='lightgreen')
        ax.set_title("Top 10 Ingredientes Usados")
        ax.set_xlabel("Cantidad")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return True

