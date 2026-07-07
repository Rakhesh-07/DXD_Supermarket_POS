import customtkinter as ctk
import time
import os
import db_adapter
import Login.Login as pa
import pymsgbox

class POSFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout (Left: POS terminal, Right: Cart Details)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # State variables
        self.cart = [] # List of dicts: {'code', 'name', 'price', 'qty', 'total'}
        self.total_amount = 0
        self.discount = 0
        self.final_amount = 0
        self.member_details = None # Stores member dict if found
        self.customer_name = ""
        self.customer_phone = ""
        
        # Left Panel (Inputs and Checkout)
        self.left_panel = ctk.CTkFrame(self, corner_radius=15)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.grid_columnconfigure(1, weight=1)
        
        # Right Panel (Cart Summary)
        self.right_panel = ctk.CTkFrame(self, corner_radius=15)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)
        
        self.setup_left_panel()
        self.setup_right_panel()
        self.load_stock_items()

    def load_stock_items(self):
        try:
            items = db_adapter.execute_query("SELECT item_name FROM STOCK WHERE available_stock > 0", fetch="all")
            self.stock_list = [row[0] for row in items]
            self.item_select.configure(values=self.stock_list)
        except Exception as e:
            self.stock_list = []
            print(f"Error loading stock items: {e}")

    def setup_left_panel(self):
        title = ctk.CTkLabel(self.left_panel, text="BILLING TERMINAL", font=("Arial", 20, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Item Select
        lbl1 = ctk.CTkLabel(self.left_panel, text="Select Item:", font=("Arial", 14, "bold"))
        lbl1.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        
        self.item_select = ctk.CTkComboBox(self.left_panel, width=220, font=("Arial", 14))
        self.item_select.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Quantity
        lbl2 = ctk.CTkLabel(self.left_panel, text="Quantity:", font=("Arial", 14, "bold"))
        lbl2.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        
        self.qty_entry = ctk.CTkEntry(self.left_panel, width=220, font=("Arial", 14), placeholder_text="Enter Qty")
        self.qty_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Cart Buttons
        btn_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        add_btn = ctk.CTkButton(btn_frame, text="Add to Cart", width=120, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 13, "bold"), command=self.add_to_cart)
        add_btn.grid(row=0, column=0, padx=10)
        
        undo_btn = ctk.CTkButton(btn_frame, text="Undo Last", width=120, fg_color="#cfcfcf", text_color="black", hover_color="#b5b5b5", font=("Arial", 13, "bold"), command=self.undo_last)
        undo_btn.grid(row=0, column=1, padx=10)
        
        # Checkout Divider
        divider = ctk.CTkFrame(self.left_panel, height=2, fg_color="#3a3a3a")
        divider.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=15)
        
        # Customer Phone (for membership lookup)
        lbl_ph = ctk.CTkLabel(self.left_panel, text="Customer Phone:", font=("Arial", 14, "bold"))
        lbl_ph.grid(row=5, column=0, padx=20, pady=10, sticky="e")
        
        self.phone_entry = ctk.CTkEntry(self.left_panel, width=220, font=("Arial", 14), placeholder_text="10-digit Phone")
        self.phone_entry.grid(row=5, column=1, padx=20, pady=10, sticky="w")
        self.phone_entry.bind("<Return>", lambda e: self.check_membership())
        
        # Customer Name
        lbl_name = ctk.CTkLabel(self.left_panel, text="Customer Name:", font=("Arial", 14, "bold"))
        lbl_name.grid(row=6, column=0, padx=20, pady=10, sticky="e")
        
        self.name_entry = ctk.CTkEntry(self.left_panel, width=220, font=("Arial", 14), placeholder_text="Guest Name")
        self.name_entry.grid(row=6, column=1, padx=20, pady=10, sticky="w")
        
        # Amount Paid
        lbl_paid = ctk.CTkLabel(self.left_panel, text="Amount Paid:", font=("Arial", 14, "bold"))
        lbl_paid.grid(row=7, column=0, padx=20, pady=10, sticky="e")
        
        self.paid_entry = ctk.CTkEntry(self.left_panel, width=220, font=("Arial", 14), placeholder_text="Received Cash")
        self.paid_entry.grid(row=7, column=1, padx=20, pady=10, sticky="w")
        self.paid_entry.bind("<Return>", lambda e: self.calculate_change())
        
        # Feedback/Change message
        self.checkout_feedback = ctk.CTkLabel(self.left_panel, text="", font=("Arial", 13, "bold"))
        self.checkout_feedback.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Final Checkout Button
        self.checkout_btn = ctk.CTkButton(self.left_panel, text="Complete & Print Bill", width=250, height=40, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 15, "bold"), command=self.complete_checkout)
        self.checkout_btn.grid(row=9, column=0, columnspan=2, pady=15)

    def setup_right_panel(self):
        title = ctk.CTkLabel(self.right_panel, text="CART SUMMARY", font=("Arial", 20, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, pady=20)
        
        # Table Header
        header_frame = ctk.CTkFrame(self.right_panel, fg_color="#1a1a1a")
        header_frame.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="ew")
        header_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        cols = ["Code", "Item Name", "Price", "Qty", "Total"]
        for c_idx, col_name in enumerate(cols):
            lbl = ctk.CTkLabel(header_frame, text=col_name, font=("Arial", 13, "bold"), text_color="#eaab06")
            lbl.grid(row=0, column=c_idx, pady=5)
            
        # Scrollable Cart Container
        self.cart_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.cart_scroll.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.right_panel.grid_rowconfigure(2, weight=1)
        
        # Footer (Total sums)
        self.footer_frame = ctk.CTkFrame(self.right_panel, height=120, fg_color=("#eaab06", "#202020"))
        self.footer_frame.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_tot = ctk.CTkLabel(self.footer_frame, text="Subtotal: Rs. 0", font=("Arial", 14, "bold"))
        self.lbl_tot.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.lbl_disc = ctk.CTkLabel(self.footer_frame, text="Discount: Rs. 0 (0%)", font=("Arial", 14, "bold"))
        self.lbl_disc.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_final = ctk.CTkLabel(self.footer_frame, text="Final Due: Rs. 0", font=("Arial", 18, "bold"), text_color="#2ecc71")
        self.lbl_final.grid(row=2, column=0, padx=20, pady=10, sticky="w")

    def add_to_cart(self):
        item_name = self.item_select.get()
        qty_str = self.qty_entry.get().strip()
        
        if not item_name or not qty_str:
            self.checkout_feedback.configure(text="Please select item and quantity!", text_color="red")
            return
            
        if not qty_str.isdigit():
            self.checkout_feedback.configure(text="Quantity must be an integer!", text_color="red")
            return
            
        qty = int(qty_str)
        if qty <= 0:
            self.checkout_feedback.configure(text="Quantity must be positive!", text_color="red")
            return
            
        # Check database for price and stock
        try:
            item_info = db_adapter.execute_query(
                "SELECT item_code, price, available_stock FROM STOCK WHERE item_name = ?",
                (item_name,),
                fetch="one"
            )
            
            if not item_info:
                self.checkout_feedback.configure(text="Product not found!", text_color="red")
                return
                
            item_code, price, stock = item_info
            
            # Check if cart already has this item
            cart_qty = sum(cart_item['qty'] for cart_item in self.cart if cart_item['name'] == item_name)
            
            if cart_qty + qty > stock:
                self.checkout_feedback.configure(text=f"Insufficient Stock! Only {stock} left.", text_color="red")
                return
                
            # Add or update cart
            item_exists = False
            for cart_item in self.cart:
                if cart_item['name'] == item_name:
                    cart_item['qty'] += qty
                    cart_item['total'] = cart_item['qty'] * price
                    item_exists = True
                    break
                    
            if not item_exists:
                self.cart.append({
                    'code': item_code,
                    'name': item_name,
                    'price': price,
                    'qty': qty,
                    'total': price * qty
                })
                
            self.checkout_feedback.configure(text="Added to cart!", text_color="green")
            self.qty_entry.delete(0, 'end')
            self.update_cart_display()
            
        except Exception as e:
            self.checkout_feedback.configure(text="Database error!", text_color="red")
            print(f"Add to cart database error: {e}")

    def undo_last(self):
        if self.cart:
            removed = self.cart.pop()
            self.checkout_feedback.configure(text=f"Removed {removed['name']} from cart.", text_color="green")
            self.update_cart_display()
        else:
            self.checkout_feedback.configure(text="Cart is empty!", text_color="red")

    def update_cart_display(self):
        # Clear current scrollable area
        for widget in self.cart_scroll.winfo_children():
            widget.destroy()
            
        self.total_amount = 0
        
        # Populate items
        for r_idx, item in enumerate(self.cart):
            row_frame = ctk.CTkFrame(self.cart_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
            
            ctk.CTkLabel(row_frame, text=str(item['code']), font=("Arial", 13)).grid(row=0, column=0)
            ctk.CTkLabel(row_frame, text=item['name'], font=("Arial", 13)).grid(row=0, column=1)
            ctk.CTkLabel(row_frame, text=f"Rs. {item['price']}", font=("Arial", 13)).grid(row=0, column=2)
            ctk.CTkLabel(row_frame, text=str(item['qty']), font=("Arial", 13)).grid(row=0, column=3)
            ctk.CTkLabel(row_frame, text=f"Rs. {item['total']}", font=("Arial", 13, "bold"), text_color="#eaab06").grid(row=0, column=4)
            
            self.total_amount += item['total']
            
        self.recalculate_bill_totals()

    def check_membership(self):
        phone_str = self.phone_entry.get().strip()
        if not phone_str:
            return
            
        if not phone_str.isdigit() or len(phone_str) != 10:
            self.checkout_feedback.configure(text="Phone number must be 10 digits!", text_color="red")
            return
            
        try:
            member = db_adapter.execute_query(
                "SELECT mem_name, exp_date FROM MEMBERSHIP WHERE phone_number = ?",
                (int(phone_str),),
                fetch="one"
            )
            
            if member:
                mem_name, exp_date = member
                # Check expiry
                current_date_str = time.strftime("%Y-%m-%d")
                if exp_date >= current_date_str:
                    self.member_details = {'name': mem_name, 'phone': phone_str}
                    self.customer_name = mem_name
                    self.customer_phone = phone_str
                    self.name_entry.delete(0, 'end')
                    self.name_entry.insert(0, mem_name)
                    self.name_entry.configure(state="disabled")
                    self.checkout_feedback.configure(text=f"Welcome Member: {mem_name} (2% Discount Applied)", text_color="green")
                else:
                    self.checkout_feedback.configure(text="Membership has expired!", text_color="red")
                    self.member_details = None
                    self.name_entry.configure(state="normal")
            else:
                self.checkout_feedback.configure(text="Non-member phone number. Checking out as Guest.", text_color="orange")
                self.member_details = None
                self.name_entry.configure(state="normal")
                self.customer_phone = phone_str
                
            self.recalculate_bill_totals()
            
        except Exception as e:
            self.checkout_feedback.configure(text="Membership check failed!", text_color="red")
            print(f"Membership check database error: {e}")

    def recalculate_bill_totals(self):
        # Calculate discount
        if self.member_details:
            self.discount = int(self.total_amount * 0.02)
        else:
            self.discount = 0
            
        self.final_amount = self.total_amount - self.discount
        
        # Update display labels
        self.lbl_tot.configure(text=f"Subtotal: Rs. {self.total_amount}")
        self.lbl_disc.configure(text=f"Discount: Rs. {self.discount} " + ("(2%)" if self.member_details else "(0%)"))
        self.lbl_final.configure(text=f"Final Due: Rs. {self.final_amount}")

    def calculate_change(self):
        paid_str = self.paid_entry.get().strip()
        if not paid_str:
            return
            
        if not paid_str.isdigit():
            self.checkout_feedback.configure(text="Invalid amount paid!", text_color="red")
            return
            
        paid = int(paid_str)
        if paid < self.final_amount:
            self.checkout_feedback.configure(text=f"Insufficient amount paid! Need Rs. {self.final_amount}", text_color="red")
            return
            
        change = paid - self.final_amount
        self.checkout_feedback.configure(text=f"Change to return: Rs. {change}", text_color="green")

    def complete_checkout(self):
        if not self.cart:
            self.checkout_feedback.configure(text="Cart is empty!", text_color="red")
            return
            
        self.customer_name = self.name_entry.get().strip().upper()
        self.customer_phone = self.phone_entry.get().strip()
        
        if not self.customer_name:
            self.checkout_feedback.configure(text="Please specify customer name!", text_color="red")
            return
            
        paid_str = self.paid_entry.get().strip()
        if not paid_str or not paid_str.isdigit():
            self.checkout_feedback.configure(text="Please enter valid cash paid!", text_color="red")
            return
            
        paid = int(paid_str)
        if paid < self.final_amount:
            self.checkout_feedback.configure(text=f"Amount paid must cover Final Due!", text_color="red")
            return
            
        change = paid - self.final_amount
        
        # Register Transaction in Database
        try:
            # 1. Insert into BILLS
            current_date_str = time.strftime("%Y-%m-%d")
            db_adapter.execute_query(
                "INSERT INTO BILLS (cashier_username, customer_phone, customer_name, bill_date, total_amount, discount_amount, final_amount, amount_paid, amount_returned) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (pa.emp_username, self.customer_phone, self.customer_name, current_date_str, self.total_amount, self.discount, self.final_amount, paid, change),
                commit=True,
                fetch="none"
            )
            
            # Get newly created bill_id
            # Query changes depending on sqlite vs mysql
            last_id_res = db_adapter.execute_query("SELECT last_insert_rowid()" if "sqlite" in str(type(db_adapter.get_connection()[0])).lower() else "SELECT LAST_INSERT_ID()", fetch="one")
            bill_id = last_id_res[0]
            
            # 2. Insert items and deduct stock
            for item in self.cart:
                db_adapter.execute_query(
                    "INSERT INTO BILL_ITEMS (bill_id, item_code, item_name, quantity, price_at_sale) VALUES (?, ?, ?, ?, ?)",
                    (bill_id, item['code'], item['name'], item['qty'], item['price']),
                    commit=True,
                    fetch="none"
                )
                
                # Deduct Stock
                db_adapter.execute_query(
                    "UPDATE STOCK SET AVAILABLE_STOCK = AVAILABLE_STOCK - ? WHERE item_code = ?",
                    (item['qty'], item['code']),
                    commit=True,
                    fetch="none"
                )
                
            # 3. Print Receipt File
            self.generate_receipt_file(bill_id, current_date_str, paid, change)
            
            # Clear Form and show success dialog
            pymsgbox.alert(f"Transaction Success!\nBill ID: {bill_id}\nReturned Change: Rs. {change}\nReceipt printed successfully.", "SUCCESS")
            
            # Reset Cart
            self.cart = []
            self.total_amount = 0
            self.discount = 0
            self.final_amount = 0
            self.member_details = None
            self.customer_name = ""
            self.customer_phone = ""
            self.name_entry.configure(state="normal")
            self.name_entry.delete(0, 'end')
            self.phone_entry.delete(0, 'end')
            self.paid_entry.delete(0, 'end')
            self.checkout_feedback.configure(text="")
            self.update_cart_display()
            self.load_stock_items()
            
        except Exception as e:
            self.checkout_feedback.configure(text="Checkout failed!", text_color="red")
            print(f"Checkout Transaction error: {e}")

    def generate_receipt_file(self, bill_id, bill_date, paid, change):
        os.makedirs("receipts", exist_ok=True)
        receipt_path = f"receipts/receipt_{bill_id}.txt"
        
        receipt_content = [
            "="*40,
            "         DXD SUPERMARKET          ",
            "       Point of Sale Receipt      ",
            "="*40,
            f"Bill ID:    {bill_id}",
            f"Date:       {bill_date}",
            f"Cashier:    {pa.emp_name}",
            f"Customer:   {self.customer_name}",
            f"Phone:      {self.customer_phone or 'N/A'}",
            "-"*40,
            f"{'Item Name':<20} {'Qty':<5} {'Price':<6} {'Total':<7}",
            "-"*40
        ]
        
        for item in self.cart:
            name_trunc = item['name'][:18]
            receipt_content.append(f"{name_trunc:<20} {item['qty']:<5} {item['price']:<6} {item['total']:<7}")
            
        receipt_content.extend([
            "-"*40,
            f"Subtotal:                      Rs. {self.total_amount}",
            f"Discount:                      Rs. {self.discount}",
            f"Final Due:                     Rs. {self.final_amount}",
            "-"*40,
            f"Cash Received:                 Rs. {paid}",
            f"Change Returned:               Rs. {change}",
            "="*40,
            "      Thank you for shopping!     ",
            "="*40
        ])
        
        with open(receipt_path, "w") as f:
            f.write("\n".join(receipt_content))
