import customtkinter as ctk
import db_adapter
import Login.Login as pa
import pymsgbox

class CheckStockFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid config (Left: Stock Table, Right: Management & Warnings)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(self, text="INVENTORY & STOCK MANAGER", font=("Arial", 22, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Left Side: Stock Listing Table
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        
        tbl_title = ctk.CTkLabel(self.left_frame, text="Current Stock Levels", font=("Arial", 16, "bold"))
        tbl_title.grid(row=0, column=0, pady=10)
        
        # Table Header
        tbl_hdr = ctk.CTkFrame(self.left_frame, fg_color="#1a1a1a")
        tbl_hdr.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="ew")
        tbl_hdr.grid_columnconfigure((0,1,2,3), weight=1)
        
        cols = ["Code", "Product Name", "Price (Rs.)", "Stock Qty"]
        for c_idx, col_name in enumerate(cols):
            ctk.CTkLabel(tbl_hdr, text=col_name, font=("Arial", 13, "bold"), text_color="#eaab06").grid(row=0, column=c_idx, pady=5)
            
        # Table Rows Container
        self.stock_table = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.stock_table.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        
        # Right Side: Alerts & Manager CRUD Panels
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Low Stock Warnings
        self.setup_low_stock_panel()
        
        # Manager Operations Frame (Only populated if user is Manager)
        if pa.emp_role == "Manager":
            self.setup_manager_ops()
        else:
            no_access = ctk.CTkLabel(self.right_frame, text="Stock write controls restricted to managers.", font=("Arial", 13, "italic"), text_color="grey")
            no_access.pack(pady=30)
            
        self.load_inventory()

    def setup_low_stock_panel(self):
        self.low_stock_card = ctk.CTkFrame(self.right_frame)
        self.low_stock_card.pack(fill="x", padx=15, pady=15)
        
        title = ctk.CTkLabel(self.low_stock_card, text="Low Stock Alerts (< 20 Units)", font=("Arial", 14, "bold"), text_color="red")
        title.pack(pady=10)
        
        self.alerts_container = ctk.CTkFrame(self.low_stock_card, fg_color="transparent")
        self.alerts_container.pack(fill="x", padx=15, pady=10)

    def setup_manager_ops(self):
        self.ops_card = ctk.CTkFrame(self.right_frame)
        self.ops_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        title = ctk.CTkLabel(self.ops_card, text="Manager Operations", font=("Arial", 14, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Form inputs
        lbl_code = ctk.CTkLabel(self.ops_card, text="Item Code:")
        lbl_code.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ent_code = ctk.CTkEntry(self.ops_card, width=150, placeholder_text="e.g. 107")
        self.ent_code.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        lbl_name = ctk.CTkLabel(self.ops_card, text="Item Name:")
        lbl_name.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ent_name = ctk.CTkEntry(self.ops_card, width=150, placeholder_text="e.g. ORANGE")
        self.ent_name.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        lbl_price = ctk.CTkLabel(self.ops_card, text="Price (Rs.):")
        lbl_price.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.ent_price = ctk.CTkEntry(self.ops_card, width=150, placeholder_text="e.g. 90")
        self.ent_price.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        lbl_stock = ctk.CTkLabel(self.ops_card, text="Stock:")
        lbl_stock.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.ent_stock = ctk.CTkEntry(self.ops_card, width=150, placeholder_text="e.g. 100")
        self.ent_stock.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Control Buttons
        btn_frame = ctk.CTkFrame(self.ops_card, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        btn_add = ctk.CTkButton(btn_frame, text="Add Item", width=90, fg_color="#2ecc71", text_color="white", hover_color="#27ae60", font=("Arial", 12, "bold"), command=self.add_item)
        btn_add.grid(row=0, column=0, padx=5)
        
        btn_edit = ctk.CTkButton(btn_frame, text="Update Price/Stock", width=120, fg_color="#3498db", text_color="white", hover_color="#2980b9", font=("Arial", 12, "bold"), command=self.update_item)
        btn_edit.grid(row=0, column=1, padx=5)
        
        btn_del = ctk.CTkButton(btn_frame, text="Delete Item", width=90, fg_color="#e74c3c", text_color="white", hover_color="#c0392b", font=("Arial", 12, "bold"), command=self.delete_item)
        btn_del.grid(row=0, column=2, padx=5)

    def load_inventory(self):
        # Clear table
        for widget in self.stock_table.winfo_children():
            widget.destroy()
            
        # Clear alerts
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
            
        try:
            items = db_adapter.execute_query("SELECT item_code, item_name, price, available_stock FROM STOCK ORDER BY item_code ASC", fetch="all")
            
            low_stock_list = []
            
            for row in items:
                code, name, price, stock = row
                
                # Render Row
                row_frame = ctk.CTkFrame(self.stock_table, height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.grid_columnconfigure((0,1,2,3), weight=1)
                
                # Clicking a row in manager mode auto-populates fields
                if pa.emp_role == "Manager":
                    btn = ctk.CTkButton(row_frame, text="", fg_color="transparent", hover_color=("#eaab06", "#3a3a3a"), height=30, command=lambda c=code, n=name, p=price, s=stock: self.select_item(c, n, p, s))
                    btn.place(x=0, y=0, relwidth=1, relheight=1)
                    
                ctk.CTkLabel(row_frame, text=str(code), font=("Arial", 13)).grid(row=0, column=0, pady=5)
                ctk.CTkLabel(row_frame, text=name, font=("Arial", 13)).grid(row=0, column=1, pady=5)
                ctk.CTkLabel(row_frame, text=f"Rs. {price}", font=("Arial", 13)).grid(row=0, column=2, pady=5)
                
                stock_color = "red" if stock < 20 else "white"
                ctk.CTkLabel(row_frame, text=str(stock), font=("Arial", 13, "bold"), text_color=stock_color).grid(row=0, column=3, pady=5)
                
                if stock < 20:
                    low_stock_list.append((code, name, stock))
                    
            # Populate alerts panel
            if low_stock_list:
                for code, name, stock in low_stock_list:
                    alert_row = ctk.CTkFrame(self.alerts_container, fg_color="transparent")
                    alert_row.pack(fill="x", pady=2)
                    
                    lbl_alert = ctk.CTkLabel(alert_row, text=f"{name} (Qty: {stock})", text_color="red", font=("Arial", 13, "bold"))
                    lbl_alert.pack(side="left", padx=10)
                    
                    btn_restock = ctk.CTkButton(alert_row, text="Restock (+50)", width=100, height=22, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 11, "bold"), command=lambda c=code: self.quick_restock(c))
                    btn_restock.pack(side="right", padx=10)
            else:
                ctk.CTkLabel(self.alerts_container, text="All products are well stocked!", text_color="green", font=("Arial", 13, "italic")).pack(pady=10)
                
        except Exception as e:
            print(f"Error loading inventory: {e}")

    def select_item(self, code, name, price, stock):
        self.ent_code.delete(0, 'end')
        self.ent_code.insert(0, str(code))
        self.ent_name.delete(0, 'end')
        self.ent_name.insert(0, name)
        self.ent_price.delete(0, 'end')
        self.ent_price.insert(0, str(price))
        self.ent_stock.delete(0, 'end')
        self.ent_stock.insert(0, str(stock))

    def add_item(self):
        code = self.ent_code.get().strip()
        name = self.ent_name.get().strip().upper()
        price = self.ent_price.get().strip()
        stock = self.ent_stock.get().strip()
        
        if not all([code, name, price, stock]):
            pymsgbox.alert("All fields are required to add an item!", "ERROR")
            return
            
        if not code.isdigit() or not price.isdigit() or not stock.isdigit():
            pymsgbox.alert("Code, Price, and Stock must be integers!", "ERROR")
            return
            
        try:
            db_adapter.execute_query(
                "INSERT INTO STOCK VALUES (?, ?, ?, ?)",
                (int(code), name, int(price), int(stock)),
                commit=True,
                fetch="none"
            )
            pymsgbox.alert(f"Product '{name}' added successfully!", "SUCCESS")
            self.clear_form()
            self.load_inventory()
        except Exception as e:
            pymsgbox.alert(f"Failed to add product. Code or Name may already exist!", "ERROR")
            print(e)

    def update_item(self):
        code = self.ent_code.get().strip()
        price = self.ent_price.get().strip()
        stock = self.ent_stock.get().strip()
        
        if not code or not price or not stock:
            pymsgbox.alert("Item Code, Price, and Stock are required for updates!", "ERROR")
            return
            
        if not code.isdigit() or not price.isdigit() or not stock.isdigit():
            pymsgbox.alert("Fields must contain valid integers!", "ERROR")
            return
            
        try:
            db_adapter.execute_query(
                "UPDATE STOCK SET PRICE = ?, AVAILABLE_STOCK = ? WHERE ITEM_CODE = ?",
                (int(price), int(stock), int(code)),
                commit=True,
                fetch="none"
            )
            pymsgbox.alert("Product updated successfully!", "SUCCESS")
            self.clear_form()
            self.load_inventory()
        except Exception as e:
            pymsgbox.alert(f"Failed to update product: {e}", "ERROR")

    def delete_item(self):
        code = self.ent_code.get().strip()
        
        if not code:
            pymsgbox.alert("Enter Item Code of product to delete!", "ERROR")
            return
            
        if not code.isdigit():
            return
            
        confirm = pymsgbox.confirm(f"Are you sure you want to delete item code {code}?", "CONFIRM DELETE")
        if confirm != 'OK':
            return
            
        try:
            db_adapter.execute_query(
                "DELETE FROM STOCK WHERE ITEM_CODE = ?",
                (int(code),),
                commit=True,
                fetch="none"
            )
            pymsgbox.alert("Product deleted successfully!", "SUCCESS")
            self.clear_form()
            self.load_inventory()
        except Exception as e:
            pymsgbox.alert(f"Failed to delete product: {e}", "ERROR")

    def quick_restock(self, code):
        try:
            db_adapter.execute_query(
                "UPDATE STOCK SET AVAILABLE_STOCK = AVAILABLE_STOCK + 50 WHERE ITEM_CODE = ?",
                (code,),
                commit=True,
                fetch="none"
            )
            self.load_inventory()
        except Exception as e:
            pymsgbox.alert(f"Restock failed: {e}", "ERROR")

    def clear_form(self):
        self.ent_code.delete(0, 'end')
        self.ent_name.delete(0, 'end')
        self.ent_price.delete(0, 'end')
        self.ent_stock.delete(0, 'end')
