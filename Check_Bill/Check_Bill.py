import customtkinter as ctk
import time
import os
import db_adapter
import pymsgbox

class CheckBillFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(self, text="BILL TRANSACTION EXPLORER", font=("Arial", 22, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Left Side: Search & Table List
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        
        # Search panel
        search_panel = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        search_panel.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        lbl_date = ctk.CTkLabel(search_panel, text="Date (YYYY-MM-DD):", font=("Arial", 13, "bold"))
        lbl_date.grid(row=0, column=0, padx=(0, 10))
        self.search_date = ctk.CTkEntry(search_panel, placeholder_text="YYYY-MM-DD", width=120)
        self.search_date.grid(row=0, column=1, padx=(0, 20))
        
        lbl_id = ctk.CTkLabel(search_panel, text="Bill ID:", font=("Arial", 13, "bold"))
        lbl_id.grid(row=0, column=2, padx=(0, 10))
        self.search_id = ctk.CTkEntry(search_panel, placeholder_text="ID", width=80)
        self.search_id.grid(row=0, column=3, padx=(0, 20))
        
        search_btn = ctk.CTkButton(search_panel, text="Find Bills", width=100, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 13, "bold"), command=self.load_bills)
        search_btn.grid(row=0, column=4)
        
        # Table list header
        tbl_header = ctk.CTkFrame(self.left_frame, fg_color="#1a1a1a")
        tbl_header.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="ew")
        tbl_header.grid_columnconfigure((0,1,2,3), weight=1)
        
        headers = ["ID", "Customer Name", "Date", "Final Amount"]
        for c_idx, h_text in enumerate(headers):
            ctk.CTkLabel(tbl_header, text=h_text, font=("Arial", 13, "bold"), text_color="#eaab06").grid(row=0, column=c_idx, pady=5)
            
        # Table rows container
        self.list_container = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.list_container.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        
        # Right Side: Active Bill Inspector
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)
        
        self.setup_inspector()
        self.load_bills()

    def setup_inspector(self):
        ins_title = ctk.CTkLabel(self.right_frame, text="TRANSACTION DETAILS", font=("Arial", 16, "bold"), text_color="#eaab06")
        ins_title.grid(row=0, column=0, pady=15)
        
        self.meta_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.meta_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        self.meta_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Detail items container
        self.items_container = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        self.items_container.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        
        # Footer Action Panel
        self.action_panel = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.action_panel.grid(row=3, column=0, pady=15, sticky="ew")
        self.action_panel.grid_columnconfigure((0, 1), weight=1)
        
        self.reprint_btn = ctk.CTkButton(self.action_panel, text="Re-Export Receipt", fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 13, "bold"), state="disabled", command=self.reprint_bill)
        self.reprint_btn.grid(row=0, column=0, padx=10, pady=5)
        
        self.selected_bill_id = None

    def load_bills(self):
        # Clear list
        for widget in self.list_container.winfo_children():
            widget.destroy()
            
        date_q = self.search_date.get().strip()
        id_q = self.search_id.get().strip()
        
        query = "SELECT bill_id, customer_name, bill_date, final_amount FROM BILLS WHERE 1=1"
        params = []
        
        if date_q:
            query += " AND bill_date = ?"
            params.append(date_q)
        if id_q:
            query += " AND bill_id = ?"
            params.append(int(id_q) if id_q.isdigit() else -1)
            
        query += " ORDER BY bill_id DESC"
        
        try:
            results = db_adapter.execute_query(query, tuple(params) if params else None, fetch="all")
            
            for row in results:
                row_frame = ctk.CTkFrame(self.list_container, height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.grid_columnconfigure((0,1,2,3), weight=1)
                
                b_id, c_name, b_date, f_amt = row
                
                # We use buttons for rows so they are clickable
                btn = ctk.CTkButton(
                    row_frame,
                    text=" ",
                    fg_color="transparent",
                    hover_color=("#eaab06", "#3a3a3a"),
                    height=30,
                    command=lambda i=b_id: self.inspect_bill(i)
                )
                btn.place(x=0, y=0, relwidth=1, relheight=1)
                
                # Block interactions but render text
                ctk.CTkLabel(row_frame, text=str(b_id), font=("Arial", 13)).grid(row=0, column=0, pady=5)
                ctk.CTkLabel(row_frame, text=c_name, font=("Arial", 13)).grid(row=0, column=1, pady=5)
                ctk.CTkLabel(row_frame, text=str(b_date), font=("Arial", 13)).grid(row=0, column=2, pady=5)
                ctk.CTkLabel(row_frame, text=f"Rs. {f_amt}", font=("Arial", 13, "bold"), text_color="#eaab06").grid(row=0, column=3, pady=5)
                
        except Exception as e:
            print(f"Error loading bills: {e}")

    def inspect_bill(self, bill_id):
        self.selected_bill_id = bill_id
        self.reprint_btn.configure(state="normal")
        
        # Clear inspector views
        for widget in self.meta_frame.winfo_children():
            widget.destroy()
        for widget in self.items_container.winfo_children():
            widget.destroy()
            
        try:
            # 1. Fetch metadata
            meta = db_adapter.execute_query(
                "SELECT bill_date, customer_name, customer_phone, cashier_username, total_amount, discount_amount, final_amount FROM BILLS WHERE bill_id = ?",
                (bill_id,),
                fetch="one"
            )
            
            if meta:
                b_date, c_name, c_phone, cashier, total, discount, final = meta
                
                details_text_l = (
                    f"Bill ID: {bill_id}\n"
                    f"Date: {b_date}\n"
                    f"Cashier: {cashier}"
                )
                details_text_r = (
                    f"Customer: {c_name}\n"
                    f"Phone: {c_phone or 'N/A'}\n"
                    f"Final Due: Rs. {final} (Disc: Rs. {discount})"
                )
                
                ctk.CTkLabel(self.meta_frame, text=details_text_l, font=("Arial", 13), justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.meta_frame, text=details_text_r, font=("Arial", 13), justify="left").grid(row=0, column=1, padx=10, pady=5, sticky="w")
                
            # 2. Fetch items
            items = db_adapter.execute_query(
                "SELECT item_name, quantity, price_at_sale FROM BILL_ITEMS WHERE bill_id = ?",
                (bill_id,),
                fetch="all"
            )
            
            # Header in inspector
            row_hdr = ctk.CTkFrame(self.items_container, fg_color="#1a1a1a")
            row_hdr.pack(fill="x", pady=2)
            row_hdr.grid_columnconfigure((0,1,2,3), weight=1)
            ctk.CTkLabel(row_hdr, text="Item Name", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=0)
            ctk.CTkLabel(row_hdr, text="Price", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=1)
            ctk.CTkLabel(row_hdr, text="Qty", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=2)
            ctk.CTkLabel(row_hdr, text="Total", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=3)
            
            for row in items:
                name, qty, price = row
                row_frame = ctk.CTkFrame(self.items_container, fg_color="transparent")
                row_frame.pack(fill="x", pady=1)
                row_frame.grid_columnconfigure((0,1,2,3), weight=1)
                
                ctk.CTkLabel(row_frame, text=name, font=("Arial", 12)).grid(row=0, column=0)
                ctk.CTkLabel(row_frame, text=f"Rs. {price}", font=("Arial", 12)).grid(row=0, column=1)
                ctk.CTkLabel(row_frame, text=str(qty), font=("Arial", 12)).grid(row=0, column=2)
                ctk.CTkLabel(row_frame, text=f"Rs. {price*qty}", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=3)
                
        except Exception as e:
            print(f"Error inspecting bill: {e}")

    def reprint_bill(self):
        if not self.selected_bill_id:
            return
            
        try:
            # Recreate text receipt file
            meta = db_adapter.execute_query(
                "SELECT bill_date, customer_name, customer_phone, cashier_username, total_amount, discount_amount, final_amount, amount_paid, amount_returned FROM BILLS WHERE bill_id = ?",
                (self.selected_bill_id,),
                fetch="one"
            )
            items = db_adapter.execute_query(
                "SELECT item_name, quantity, price_at_sale FROM BILL_ITEMS WHERE bill_id = ?",
                (self.selected_bill_id,),
                fetch="all"
            )
            
            if meta:
                b_date, c_name, c_phone, cashier, total, discount, final, paid, change = meta
                
                os.makedirs("receipts", exist_ok=True)
                receipt_path = f"receipts/receipt_{self.selected_bill_id}.txt"
                
                receipt_content = [
                    "="*40,
                    "         DXD SUPERMARKET          ",
                    "       Point of Sale Receipt      ",
                    "           (DUPLICATE)            ",
                    "="*40,
                    f"Bill ID:    {self.selected_bill_id}",
                    f"Date:       {b_date}",
                    f"Cashier:    {cashier}",
                    f"Customer:   {c_name}",
                    f"Phone:      {c_phone or 'N/A'}",
                    "-"*40,
                    f"{'Item Name':<20} {'Qty':<5} {'Price':<6} {'Total':<7}",
                    "-"*40
                ]
                
                for name, qty, price in items:
                    name_trunc = name[:18]
                    receipt_content.append(f"{name_trunc:<20} {qty:<5} {price:<6} {price*qty:<7}")
                    
                receipt_content.extend([
                    "-"*40,
                    f"Subtotal:                      Rs. {total}",
                    f"Discount:                      Rs. {discount}",
                    f"Final Due:                     Rs. {final}",
                    "-"*40,
                    f"Cash Received:                 Rs. {paid}",
                    f"Change Returned:               Rs. {change}",
                    "="*40,
                    "      Thank you for shopping!     ",
                    "="*40
                ])
                
                with open(receipt_path, "w") as f:
                    f.write("\n".join(receipt_content))
                    
                pymsgbox.alert(f"Duplicate receipt successfully printed to {receipt_path}", "SUCCESS")
                
        except Exception as e:
            pymsgbox.alert(f"Receipt reprint failed: {e}", "ERROR")
