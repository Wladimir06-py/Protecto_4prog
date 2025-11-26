import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import tkinter as tk
from database import get_db, engine, Base
from models import Cliente, Ingrediente, Menu

# Configuración inicial
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Restaurante")
        self.geometry("1100x700")

        # Inicializar base de datos
        Base.metadata.create_all(bind=engine)

        # Layout principal
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_clientes = self.tabview.add("Clientes")
        self.tab_ingredientes = self.tabview.add("Ingredientes")
        self.tab_menus = self.tabview.add("Menús")
        self.tab_compras = self.tabview.add("Comprar")
        self.tab_estadisticas = self.tabview.add("Estadísticas")

        self.setup_clientes_tab()
        self.setup_ingredientes_tab()
        self.setup_menus_tab()
        self.setup_compras_tab()
        self.setup_estadisticas_tab()

    # --- CLIENTES ---
    def setup_clientes_tab(self):
        frame_form = ctk.CTkFrame(self.tab_clientes)
        frame_form.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_form, text="Nombre:").pack(side="left", padx=5)
        self.entry_cliente_nombre = ctk.CTkEntry(frame_form)
        self.entry_cliente_nombre.pack(side="left", padx=5)

        ctk.CTkLabel(frame_form, text="Correo:").pack(side="left", padx=5)
        self.entry_cliente_correo = ctk.CTkEntry(frame_form)
        self.entry_cliente_correo.pack(side="left", padx=5)

        ctk.CTkButton(frame_form, text="Agregar Cliente", command=self.agregar_cliente).pack(side="left", padx=10)
        ctk.CTkButton(frame_form, text="Actualizar Lista", command=self.cargar_clientes).pack(side="left", padx=10)

        # Treeview para lista
        self.tree_clientes = ttk.Treeview(self.tab_clientes, columns=("ID", "Nombre", "Correo"), show="headings")
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nombre", text="Nombre")
        self.tree_clientes.heading("Correo", text="Correo")
        self.tree_clientes.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(self.tab_clientes, text="Eliminar Seleccionado", command=self.eliminar_cliente, fg_color="red").pack(pady=5)

        self.cargar_clientes()

    def agregar_cliente(self):
        nombre = self.entry_cliente_nombre.get()
        correo = self.entry_cliente_correo.get()
        db = next(get_db())
        try:
            from crud.cliente_crud import ClienteCRUD
            ClienteCRUD(db).crear(nombre, correo)
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
            self.entry_cliente_nombre.delete(0, 'end')
            self.entry_cliente_correo.delete(0, 'end')
            self.cargar_clientes()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def cargar_clientes(self):
        for i in self.tree_clientes.get_children():
            self.tree_clientes.delete(i)
        db = next(get_db())
        from crud.cliente_crud import ClienteCRUD
        clientes = ClienteCRUD(db).leer_todos()
        for c in clientes:
            self.tree_clientes.insert("", "end", values=(c.id, c.nombre, c.correo))

    def eliminar_cliente(self):
        selected = self.tree_clientes.selection()
        if not selected:
            return
        item = self.tree_clientes.item(selected[0])
        cliente_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
            db = next(get_db())
            try:
                from crud.cliente_crud import ClienteCRUD
                ClienteCRUD(db).eliminar(cliente_id)
                self.cargar_clientes()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    # --- INGREDIENTES ---
    def setup_ingredientes_tab(self):
        frame_top = ctk.CTkFrame(self.tab_ingredientes)
        frame_top.pack(pady=10, padx=10, fill="x")

        ctk.CTkButton(frame_top, text="Cargar CSV", command=self.cargar_csv_ingredientes).pack(side="left", padx=10)
        ctk.CTkButton(frame_top, text="Actualizar Lista", command=self.cargar_ingredientes).pack(side="left", padx=10)

        self.tree_ingredientes = ttk.Treeview(self.tab_ingredientes, columns=("ID", "Nombre", "Stock", "Unidad"), show="headings")
        self.tree_ingredientes.heading("ID", text="ID")
        self.tree_ingredientes.heading("Nombre", text="Nombre")
        self.tree_ingredientes.heading("Stock", text="Stock")
        self.tree_ingredientes.heading("Unidad", text="Unidad")
        self.tree_ingredientes.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_ingredientes()

    def cargar_csv_ingredientes(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            db = next(get_db())
            from crud.ingrediente_crud import IngredienteCRUD
            if IngredienteCRUD(db).cargar_desde_csv(filepath):
                messagebox.showinfo("Éxito", "Ingredientes cargados")
                self.cargar_ingredientes()
            else:
                messagebox.showerror("Error", "Error al cargar CSV")

    def cargar_ingredientes(self):
        for i in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(i)
        db = next(get_db())
        from crud.ingrediente_crud import IngredienteCRUD
        ingredientes = IngredienteCRUD(db).leer_todos()
        for ing in ingredientes:
            self.tree_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.stock, ing.unidad))

    # --- MENUS ---
    def setup_menus_tab(self):
        frame_form = ctk.CTkFrame(self.tab_menus)
        frame_form.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_menu_nombre = ctk.CTkEntry(frame_form)
        self.entry_menu_nombre.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_form, text="Precio:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_menu_precio = ctk.CTkEntry(frame_form)
        self.entry_menu_precio.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame_form, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_menu_desc = ctk.CTkEntry(frame_form, width=300)
        self.entry_menu_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        # Selección de ingredientes
        frame_ing = ctk.CTkFrame(self.tab_menus)
        frame_ing.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(frame_ing, text="Ingredientes (ID:Cantidad, sep por coma):").pack(side="left", padx=5)
        self.entry_menu_ingredientes = ctk.CTkEntry(frame_ing, width=400, placeholder_text="Ej: 1:0.5, 2:1")
        self.entry_menu_ingredientes.pack(side="left", padx=5)

        ctk.CTkButton(frame_ing, text="Crear Menú", command=self.crear_menu).pack(side="left", padx=10)
        ctk.CTkButton(frame_ing, text="Refrescar", command=self.cargar_menus).pack(side="left", padx=10)

        self.tree_menus = ttk.Treeview(self.tab_menus, columns=("ID", "Nombre", "Precio", "Descripción"), show="headings")
        self.tree_menus.heading("ID", text="ID")
        self.tree_menus.heading("Nombre", text="Nombre")
        self.tree_menus.heading("Precio", text="Precio")
        self.tree_menus.heading("Descripción", text="Descripción")
        self.tree_menus.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_menus()

    def crear_menu(self):
        nombre = self.entry_menu_nombre.get()
        try:
            precio = float(self.entry_menu_precio.get())
        except ValueError:
            messagebox.showerror("Error", "Precio inválido")
            return
        desc = self.entry_menu_desc.get()
        ing_str = self.entry_menu_ingredientes.get()

        ingredientes_data = []
        try:
            for item in ing_str.split(','):
                if ':' in item:
                    id_str, cant_str = item.split(':')
                    ingredientes_data.append((int(id_str.strip()), float(cant_str.strip())))
        except ValueError:
            messagebox.showerror("Error", "Formato de ingredientes inválido. Use ID:Cantidad")
            return

        if not ingredientes_data:
            messagebox.showerror("Error", "Debe agregar al menos un ingrediente")
            return

        db = next(get_db())
        try:
            from crud.menu_crud import MenuCRUD
            MenuCRUD(db).crear(nombre, desc, precio, ingredientes_data)
            messagebox.showinfo("Éxito", "Menú creado")
            self.cargar_menus()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_menus(self):
        for i in self.tree_menus.get_children():
            self.tree_menus.delete(i)
        db = next(get_db())
        from crud.menu_crud import MenuCRUD
        menus = MenuCRUD(db).leer_todos()
        for m in menus:
            self.tree_menus.insert("", "end", values=(m.id, m.nombre, m.precio, m.descripcion))

    # --- COMPRAS ---
    def setup_compras_tab(self):
        frame_sel = ctk.CTkFrame(self.tab_compras)
        frame_sel.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_sel, text="ID Cliente:").pack(side="left", padx=5)
        self.entry_compra_cliente_id = ctk.CTkEntry(frame_sel, width=50)
        self.entry_compra_cliente_id.pack(side="left", padx=5)

        ctk.CTkLabel(frame_sel, text="ID Menú:").pack(side="left", padx=5)
        self.entry_compra_menu_id = ctk.CTkEntry(frame_sel, width=50)
        self.entry_compra_menu_id.pack(side="left", padx=5)

        ctk.CTkLabel(frame_sel, text="Cantidad:").pack(side="left", padx=5)
        self.entry_compra_cantidad = ctk.CTkEntry(frame_sel, width=50)
        self.entry_compra_cantidad.pack(side="left", padx=5)

        ctk.CTkButton(frame_sel, text="Agregar al Carrito", command=self.agregar_al_carrito).pack(side="left", padx=10)
        ctk.CTkButton(frame_sel, text="Finalizar Compra", command=self.finalizar_compra, fg_color="green").pack(side="left", padx=10)

        self.carrito = []
        self.tree_carrito = ttk.Treeview(self.tab_compras, columns=("ID Menú", "Cantidad"), show="headings")
        self.tree_carrito.heading("ID Menú", text="ID Menú")
        self.tree_carrito.heading("Cantidad", text="Cantidad")
        self.tree_carrito.pack(fill="both", expand=True, padx=10, pady=10)

    def agregar_al_carrito(self):
        try:
            menu_id = int(self.entry_compra_menu_id.get())
            cantidad = int(self.entry_compra_cantidad.get())
            if cantidad <= 0: raise ValueError
            self.carrito.append((menu_id, cantidad))
            self.tree_carrito.insert("", "end", values=(menu_id, cantidad))
        except ValueError:
            messagebox.showerror("Error", "ID o Cantidad inválidos")

    def finalizar_compra(self):
        try:
            cliente_id = int(self.entry_compra_cliente_id.get())
        except ValueError:
            messagebox.showerror("Error", "ID Cliente inválido")
            return

        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return

        db = next(get_db())
        try:
            from crud.pedido_crud import PedidoCRUD
            pedido = PedidoCRUD(db).crear(cliente_id, self.carrito)
            msg = f"Pedido creado! Total: ${pedido.total}"
            if getattr(pedido, 'boleta_path', None):
                msg += f"\nBoleta guardada en: {pedido.boleta_path}"
            messagebox.showinfo("Éxito", msg)
            self.carrito = []
            for i in self.tree_carrito.get_children():
                self.tree_carrito.delete(i)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- ESTADISTICAS ---
    def setup_estadisticas_tab(self):
        frame_ctrl = ctk.CTkFrame(self.tab_estadisticas)
        frame_ctrl.pack(pady=10, padx=10, fill="x")

        self.combo_graficos = ctk.CTkComboBox(frame_ctrl, values=["Ventas por Fecha", "Menús Más Vendidos", "Uso de Ingredientes"])
        self.combo_graficos.pack(side="left", padx=10)

        ctk.CTkButton(frame_ctrl, text="Generar Gráfico", command=self.generar_grafico).pack(side="left", padx=10)

        self.frame_grafico = ctk.CTkFrame(self.tab_estadisticas)
        self.frame_grafico.pack(fill="both", expand=True, padx=10, pady=10)

    def generar_grafico(self):
        # Limpiar frame anterior
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        tipo = self.combo_graficos.get()
        db = next(get_db())
        
        # Crear instancia de la clase Graficos
        from graficos import Graficos
        graficador = Graficos(db, self.frame_grafico)
        
        exito = False
        if tipo == "Ventas por Fecha":
            exito = graficador.graficar_ventas_por_fecha()
        elif tipo == "Menús Más Vendidos":
            exito = graficador.graficar_menus_mas_vendidos()
        elif tipo == "Uso de Ingredientes":
            exito = graficador.graficar_uso_ingredientes()
        
        if not exito:
            ctk.CTkLabel(self.frame_grafico, text="No hay datos disponibles para graficar").pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
