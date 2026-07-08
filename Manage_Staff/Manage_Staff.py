import customtkinter as ctk
import db_adapter
import Login.Login as pa
import pymsgbox

class ManageStaffFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout (Left: Staff Table, Right: Form Editor)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(self, text="STAFF USER MANAGEMENT", font=("Arial", 22, "bold"), text_color="#eaab06")
        title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Left Side: Staff List
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        
        tbl_title = ctk.CTkLabel(self.left_frame, text="Active Employees", font=("Arial", 16, "bold"))
        tbl_title.grid(row=0, column=0, pady=10)
        
        # Table Header
        tbl_hdr = ctk.CTkFrame(self.left_frame, fg_color="#1a1a1a")
        # Offset right padding to account for the scrollbar width on the list below
        tbl_hdr.grid(row=1, column=0, padx=(15, 32), pady=(0, 5), sticky="ew")
        tbl_hdr.grid_columnconfigure((0,1,2), weight=1)
        
        cols = ["Username", "Full Name", "Role"]
        for c_idx, col_name in enumerate(cols):
            ctk.CTkLabel(tbl_hdr, text=col_name, font=("Arial", 13, "bold"), text_color="#eaab06", anchor="center").grid(row=0, column=c_idx, pady=5, sticky="ew")
            
        # Scrollable list
        self.staff_scroll = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.staff_scroll.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        
        # Right Side: Editor Card
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(1, weight=1)
        
        self.setup_editor()
        self.load_staff()

    def setup_editor(self):
        editor_title = ctk.CTkLabel(self.right_frame, text="Staff Register & Editor", font=("Arial", 16, "bold"), text_color="#eaab06")
        editor_title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Form inputs
        lbl_user = ctk.CTkLabel(self.right_frame, text="Username:")
        lbl_user.grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.ent_user = ctk.CTkEntry(self.right_frame, width=180, placeholder_text="e.g. jsmith")
        self.ent_user.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        
        lbl_name = ctk.CTkLabel(self.right_frame, text="Full Name:")
        lbl_name.grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.ent_name = ctk.CTkEntry(self.right_frame, width=180, placeholder_text="e.g. John Smith")
        self.ent_name.grid(row=2, column=1, padx=15, pady=8, sticky="w")
        
        lbl_pass = ctk.CTkLabel(self.right_frame, text="Password:")
        lbl_pass.grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.ent_pass = ctk.CTkEntry(self.right_frame, width=180, placeholder_text="Password", show="*")
        self.ent_pass.grid(row=3, column=1, padx=15, pady=8, sticky="w")
        
        lbl_role = ctk.CTkLabel(self.right_frame, text="System Role:")
        lbl_role.grid(row=4, column=0, padx=15, pady=8, sticky="e")
        self.ent_role = ctk.CTkComboBox(self.right_frame, width=180, values=["Cashier", "Manager"])
        self.ent_role.grid(row=4, column=1, padx=15, pady=8, sticky="w")
        
        # Feedback msg
        self.feedback_lbl = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 12, "bold"))
        self.feedback_lbl.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        self.add_btn = ctk.CTkButton(btn_frame, text="Add Staff", width=90, fg_color="#2ecc71", text_color="white", hover_color="#27ae60", font=("Arial", 12, "bold"), command=self.add_staff)
        self.add_btn.grid(row=0, column=0, padx=5)
        
        self.update_btn = ctk.CTkButton(btn_frame, text="Save Changes", width=110, fg_color="#3498db", text_color="white", hover_color="#2980b9", font=("Arial", 12, "bold"), state="disabled", command=self.update_staff)
        self.update_btn.grid(row=0, column=1, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="Delete Staff", width=90, fg_color="#e74c3c", text_color="white", hover_color="#c0392b", font=("Arial", 12, "bold"), state="disabled", command=self.delete_staff)
        self.delete_btn.grid(row=0, column=2, padx=5)
        
        self.clear_btn = ctk.CTkButton(btn_frame, text="Clear", width=60, fg_color="#cfcfcf", text_color="black", hover_color="#b5b5b5", font=("Arial", 12, "bold"), command=self.clear_form)
        self.clear_btn.grid(row=0, column=3, padx=5)

    def load_staff(self):
        # Clear list
        for widget in self.staff_scroll.winfo_children():
            widget.destroy()
            
        try:
            users = db_adapter.execute_query("SELECT username, name, role FROM EMPLOYEES ORDER BY username ASC", fetch="all")
            
            for row in users:
                row_frame = ctk.CTkFrame(self.staff_scroll, height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.grid_columnconfigure((0,1,2), weight=1)
                
                username, name, role = row
                
                btn = ctk.CTkButton(
                    row_frame,
                    text="",
                    fg_color="transparent",
                    hover_color=("#eaab06", "#3a3a3a"),
                    height=30,
                    command=lambda u=username, n=name, r=role: self.select_staff(u, n, r)
                )
                btn.place(x=0, y=0, relwidth=1, relheight=1)
                
                ctk.CTkLabel(row_frame, text=username, font=("Arial", 12), anchor="center").grid(row=0, column=0, pady=5, sticky="ew")
                ctk.CTkLabel(row_frame, text=name, font=("Arial", 12), anchor="center").grid(row=0, column=1, pady=5, sticky="ew")
                ctk.CTkLabel(row_frame, text=role, font=("Arial", 12), anchor="center").grid(row=0, column=2, pady=5, sticky="ew")
                
        except Exception as e:
            print(f"Error loading staff: {e}")

    def select_staff(self, username, name, role):
        self.ent_user.delete(0, 'end')
        self.ent_user.insert(0, username)
        self.ent_user.configure(state="disabled") # Cannot rename username PK
        
        self.ent_name.delete(0, 'end')
        self.ent_name.insert(0, name)
        
        self.ent_pass.delete(0, 'end')
        self.ent_pass.configure(placeholder_text="Enter new pass to update")
        
        self.ent_role.set(role)
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")
        
        # Prevent deleting oneself
        if username == pa.emp_username:
            self.delete_btn.configure(state="disabled")
        else:
            self.delete_btn.configure(state="normal")
            
        self.feedback_lbl.configure(text="")

    def clear_form(self):
        self.ent_user.configure(state="normal")
        self.ent_user.delete(0, 'end')
        self.ent_user.configure(placeholder_text="e.g. jsmith")
        
        self.ent_name.delete(0, 'end')
        self.ent_name.configure(placeholder_text="e.g. John Smith")
        
        self.ent_pass.delete(0, 'end')
        self.ent_pass.configure(placeholder_text="Password")
        
        self.ent_role.set("Cashier")
        
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
        self.feedback_lbl.configure(text="")

    def add_staff(self):
        username = self.ent_user.get().strip()
        name = self.ent_name.get().strip()
        password = self.ent_pass.get().strip()
        role = self.ent_role.get()
        
        if not all([username, name, password, role]):
            self.feedback_lbl.configure(text="All fields are required to register staff!", text_color="red")
            return
            
        try:
            pass_hash = db_adapter.hash_password(password)
            db_adapter.execute_query(
                "INSERT INTO EMPLOYEES VALUES (?, ?, ?, ?)",
                (username, pass_hash, name, role),
                commit=True,
                fetch="none"
            )
            self.feedback_lbl.configure(text=f"Staff '{username}' added successfully!", text_color="green")
            self.clear_form()
            self.load_staff()
        except Exception as e:
            self.feedback_lbl.configure(text="Username already exists!", text_color="red")
            print(e)

    def update_staff(self):
        username = self.ent_user.get().strip()
        name = self.ent_name.get().strip()
        password = self.ent_pass.get().strip()
        role = self.ent_role.get()
        
        if not username or not name or not role:
            self.feedback_lbl.configure(text="Name and Role are required!", text_color="red")
            return
            
        try:
            if password:
                # Update with new password
                pass_hash = db_adapter.hash_password(password)
                db_adapter.execute_query(
                    "UPDATE EMPLOYEES SET name = ?, password_hash = ?, role = ? WHERE username = ?",
                    (name, pass_hash, role, username),
                    commit=True,
                    fetch="none"
                )
            else:
                # Update without changing password
                db_adapter.execute_query(
                    "UPDATE EMPLOYEES SET name = ?, role = ? WHERE username = ?",
                    (name, role, username),
                    commit=True,
                    fetch="none"
                )
            self.feedback_lbl.configure(text="Staff details updated successfully!", text_color="green")
            self.clear_form()
            self.load_staff()
        except Exception as e:
            self.feedback_lbl.configure(text="Update failed!", text_color="red")
            print(e)

    def delete_staff(self):
        username = self.ent_user.get().strip()
        if not username:
            return
            
        if username == pa.emp_username:
            pymsgbox.alert("You cannot delete your own logged-in manager account!", "ERROR")
            return
            
        confirm = pymsgbox.confirm(f"Are you sure you want to delete employee '{username}'?", "CONFIRM STAFF DELETE")
        if confirm != 'OK':
            return
            
        try:
            db_adapter.execute_query("DELETE FROM EMPLOYEES WHERE username = ?", (username,), commit=True, fetch="none")
            self.feedback_lbl.configure(text="Staff deleted successfully!", text_color="green")
            self.clear_form()
            self.load_staff()
        except Exception as e:
            self.feedback_lbl.configure(text="Deletion failed!", text_color="red")
            print(e)
