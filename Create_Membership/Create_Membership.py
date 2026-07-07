import customtkinter as ctk
import time
import pymsgbox
import db_adapter

class CreateMembershipFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create Tabview
        self.tabview = ctk.CTkTabview(self, width=900, height=600, corner_radius=15, border_width=1, border_color="#eaab06")
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Add tabs
        self.tabview.add("Create Membership")
        self.tabview.add("View / Edit Memberships")
        
        self.setup_create_tab()
        self.setup_view_edit_tab()
        
    def setup_create_tab(self):
        tab = self.tabview.tab("Create Membership")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        
        # Next Member ID Preview
        self.cno = self.get_next_member_id()
        self.id_lbl = ctk.CTkLabel(tab, text=f"New Member ID: {self.cno}", font=("Arial", 16, "bold"), text_color="#eaab06")
        self.id_lbl.grid(row=0, column=0, columnspan=2, pady=(20, 20))
        
        # Form Fields
        self.create_field(tab, "Customer Name:", 1, "name")
        self.create_field(tab, "Phone Number:", 2, "phone")
        self.create_field(tab, "Address Line 1:", 3, "addr1")
        self.create_field(tab, "Address Line 2:", 4, "addr2")
        self.create_field(tab, "Address Line 3:", 5, "addr3")
        
        # Feedback label
        self.feedback_lbl = ctk.CTkLabel(tab, text="", font=("Arial", 13, "bold"))
        self.feedback_lbl.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Buttons
        self.register_btn = ctk.CTkButton(tab, text="Register Information", width=180, height=35, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 14, "bold"), command=self.confirm_registration)
        self.register_btn.grid(row=7, column=0, pady=20, padx=(20, 10), sticky="e")
        
        self.clear_btn = ctk.CTkButton(tab, text="Clear Form", width=180, height=35, fg_color="#cfcfcf", text_color="black", hover_color="#b5b5b5", font=("Arial", 14, "bold"), command=self.clear_form)
        self.clear_btn.grid(row=7, column=1, pady=20, padx=(10, 20), sticky="w")
        
    def setup_view_edit_tab(self):
        tab = self.tabview.tab("View / Edit Memberships")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Left Panel: Members list and search
        left_pane = ctk.CTkFrame(tab)
        left_pane.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        left_pane.grid_columnconfigure(0, weight=1)
        left_pane.grid_rowconfigure(2, weight=1)
        
        search_frame = ctk.CTkFrame(left_pane, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Name/Phone/ID", width=180)
        self.search_entry.grid(row=0, column=0, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.load_members())
        
        search_btn = ctk.CTkButton(search_frame, text="Search", width=80, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 12, "bold"), command=self.load_members)
        search_btn.grid(row=0, column=1)
        
        # Table Header
        tbl_hdr = ctk.CTkFrame(left_pane, fg_color="#1a1a1a")
        tbl_hdr.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        tbl_hdr.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(tbl_hdr, text="ID", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=0, pady=2)
        ctk.CTkLabel(tbl_hdr, text="Name", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=1, pady=2)
        ctk.CTkLabel(tbl_hdr, text="Phone", font=("Arial", 12, "bold"), text_color="#eaab06").grid(row=0, column=2, pady=2)
        
        # Scrollable Members List
        self.members_scroll = ctk.CTkScrollableFrame(left_pane, fg_color="transparent")
        self.members_scroll.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        # Right Panel: Member Editor
        self.right_pane = ctk.CTkFrame(tab)
        self.right_pane.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.right_pane.grid_columnconfigure(1, weight=1)
        
        editor_title = ctk.CTkLabel(self.right_pane, text="MEMBER DETAILS & EDIT", font=("Arial", 16, "bold"), text_color="#eaab06")
        editor_title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Edit Form Fields
        lbl_eid = ctk.CTkLabel(self.right_pane, text="Member ID:")
        lbl_eid.grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.edit_id_entry = ctk.CTkEntry(self.right_pane, width=180, state="disabled")
        self.edit_id_entry.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        
        lbl_ename = ctk.CTkLabel(self.right_pane, text="Name:")
        lbl_ename.grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.edit_name_entry = ctk.CTkEntry(self.right_pane, width=180)
        self.edit_name_entry.grid(row=2, column=1, padx=15, pady=8, sticky="w")
        
        lbl_ephone = ctk.CTkLabel(self.right_pane, text="Phone:")
        lbl_ephone.grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.edit_phone_entry = ctk.CTkEntry(self.right_pane, width=180)
        self.edit_phone_entry.grid(row=3, column=1, padx=15, pady=8, sticky="w")
        
        lbl_eexp = ctk.CTkLabel(self.right_pane, text="Expiry Date:")
        lbl_eexp.grid(row=4, column=0, padx=15, pady=8, sticky="e")
        self.edit_exp_entry = ctk.CTkEntry(self.right_pane, width=180)
        self.edit_exp_entry.grid(row=4, column=1, padx=15, pady=8, sticky="w")
        
        lbl_eaddr = ctk.CTkLabel(self.right_pane, text="Address:")
        lbl_eaddr.grid(row=5, column=0, padx=15, pady=8, sticky="e")
        self.edit_addr_entry = ctk.CTkEntry(self.right_pane, width=180)
        self.edit_addr_entry.grid(row=5, column=1, padx=15, pady=8, sticky="w")
        
        self.edit_feedback = ctk.CTkLabel(self.right_pane, text="", font=("Arial", 12, "bold"))
        self.edit_feedback.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self.right_pane, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.update_btn = ctk.CTkButton(btn_frame, text="Save Changes", width=110, fg_color="#3498db", hover_color="#2980b9", text_color="white", font=("Arial", 12, "bold"), state="disabled", command=self.update_member)
        self.update_btn.grid(row=0, column=0, padx=4)
        
        self.renew_btn = ctk.CTkButton(btn_frame, text="Renew (+1 Yr)", width=110, fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=("Arial", 12, "bold"), state="disabled", command=self.renew_member)
        self.renew_btn.grid(row=0, column=1, padx=4)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="Delete", width=80, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=("Arial", 12, "bold"), state="disabled", command=self.delete_member)
        self.delete_btn.grid(row=0, column=2, padx=4)
        
        self.load_members()
        
    def get_next_member_id(self):
        try:
            result = db_adapter.execute_query("SELECT mem_id FROM MEMBERSHIP ORDER BY mem_id DESC LIMIT 1", fetch="one")
            if result:
                return int(result[0]) + 1
        except Exception as e:
            print(f"Error fetching member ID: {e}")
        return 1001
        
    def create_field(self, parent, label_text, row_idx, attr_name):
        lbl = ctk.CTkLabel(parent, text=label_text, font=("Arial", 14, "bold"), anchor="e")
        lbl.grid(row=row_idx, column=0, padx=(100, 20), pady=10, sticky="e")
        
        entry = ctk.CTkEntry(parent, width=220, font=("Arial", 14))
        entry.grid(row=row_idx, column=1, padx=(20, 100), pady=10, sticky="w")
        
        setattr(self, f"{attr_name}_entry", entry)
        
    def clear_form(self):
        self.name_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.addr1_entry.delete(0, 'end')
        self.addr2_entry.delete(0, 'end')
        self.addr3_entry.delete(0, 'end')
        self.feedback_lbl.configure(text="")
        
    def confirm_registration(self):
        name = self.name_entry.get().strip().upper()
        phone = self.phone_entry.get().strip()
        addr1 = self.addr1_entry.get().strip().upper()
        addr2 = self.addr2_entry.get().strip().upper()
        addr3 = self.addr3_entry.get().strip().upper()
        
        if not all([name, phone, addr1, addr2, addr3]):
            self.feedback_lbl.configure(text="Please fill in all fields!", text_color="red")
            return
            
        if not phone.isdigit() or len(phone) != 10:
            self.feedback_lbl.configure(text="Phone Number must be exactly 10 digits!", text_color="red")
            return
            
        # Top-level confirmation popup
        top = ctk.CTkToplevel(self)
        top.title("Confirm Registration")
        top.geometry("450x300")
        top.transient(self)
        top.grab_set()
        
        title = ctk.CTkLabel(top, text="Confirm Customer Details", font=("Arial", 16, "bold"), text_color="#eaab06")
        title.pack(pady=15)
        
        details = (
            f"ID: {self.cno}\n"
            f"Name: {name}\n"
            f"Phone: {phone}\n"
            f"Address: {addr1}, {addr2}, {addr3}"
        )
        details_lbl = ctk.CTkLabel(top, text=details, font=("Arial", 13), justify="left")
        details_lbl.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def save():
            try:
                # Add one year for membership expiry
                localtime = time.localtime(time.time())
                month = f"0{localtime[1]}" if localtime[1] < 10 else str(localtime[1])
                day = f"0{localtime[2]}" if localtime[2] < 10 else str(localtime[2])
                exp_date = f"{localtime[0]+1}-{month}-{day}"
                
                address = f"{addr1}, {addr2}, {addr3}"
                
                db_adapter.execute_query(
                    "INSERT INTO MEMBERSHIP VALUES (?, ?, ?, ?, ?)",
                    (self.cno, name, int(phone), exp_date, address),
                    commit=True,
                    fetch="none"
                )
                
                self.feedback_lbl.configure(text="Membership Created Successfully!", text_color="green")
                self.clear_form()
                
                # Refresh cno and view table list
                self.cno = self.get_next_member_id()
                self.id_lbl.configure(text=f"New Member ID: {self.cno}")
                self.load_members()
                top.destroy()
                
            except Exception as e:
                self.feedback_lbl.configure(text="Error: Phone Number already registered!", text_color="red")
                print(f"Registration save error: {e}")
                top.destroy()
                
        confirm_btn = ctk.CTkButton(btn_frame, text="Confirm", fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 13, "bold"), command=save)
        confirm_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="#cfcfcf", text_color="black", hover_color="#b5b5b5", font=("Arial", 13, "bold"), command=top.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)

    # VIEW & EDIT TAB CONTROLS
    def load_members(self):
        # Clear list
        for widget in self.members_scroll.winfo_children():
            widget.destroy()
            
        search_q = self.search_entry.get().strip()
        
        query = "SELECT mem_id, mem_name, phone_number, exp_date, address FROM MEMBERSHIP WHERE 1=1"
        params = []
        
        if search_q:
            if search_q.isdigit():
                query += " AND (phone_number LIKE ? OR mem_id = ?)"
                params.extend([f"%{search_q}%", int(search_q)])
            else:
                query += " AND mem_name LIKE ?"
                params.append(f"%{search_q.upper()}%")
                
        query += " ORDER BY mem_id DESC"
        
        try:
            results = db_adapter.execute_query(query, tuple(params) if params else None, fetch="all")
            
            for row in results:
                row_frame = ctk.CTkFrame(self.members_scroll, height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.grid_columnconfigure((0, 1, 2), weight=1)
                
                m_id, name, phone, exp, addr = row
                
                # Clicking a row selects it
                btn = ctk.CTkButton(
                    row_frame,
                    text="",
                    fg_color="transparent",
                    hover_color=("#eaab06", "#3a3a3a"),
                    height=30,
                    command=lambda r=row: self.select_member(r)
                )
                btn.place(x=0, y=0, relwidth=1, relheight=1)
                
                ctk.CTkLabel(row_frame, text=str(m_id), font=("Arial", 12)).grid(row=0, column=0, pady=5)
                ctk.CTkLabel(row_frame, text=name, font=("Arial", 12)).grid(row=0, column=1, pady=5)
                ctk.CTkLabel(row_frame, text=str(phone), font=("Arial", 12)).grid(row=0, column=2, pady=5)
                
        except Exception as e:
            print(f"Error loading members: {e}")
            
    def select_member(self, row):
        m_id, name, phone, exp, addr = row
        
        # Unlock fields
        self.edit_id_entry.configure(state="normal")
        self.edit_id_entry.delete(0, 'end')
        self.edit_id_entry.insert(0, str(m_id))
        self.edit_id_entry.configure(state="disabled")
        
        self.edit_name_entry.delete(0, 'end')
        self.edit_name_entry.insert(0, name)
        
        self.edit_phone_entry.delete(0, 'end')
        self.edit_phone_entry.insert(0, str(phone))
        
        self.edit_exp_entry.delete(0, 'end')
        self.edit_exp_entry.insert(0, str(exp))
        
        self.edit_addr_entry.delete(0, 'end')
        self.edit_addr_entry.insert(0, addr)
        
        # Enable action buttons
        self.update_btn.configure(state="normal")
        self.renew_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        self.edit_feedback.configure(text="")
        
    def update_member(self):
        m_id = self.edit_id_entry.get().strip()
        name = self.edit_name_entry.get().strip().upper()
        phone = self.edit_phone_entry.get().strip()
        exp = self.edit_exp_entry.get().strip()
        addr = self.edit_addr_entry.get().strip().upper()
        
        if not all([m_id, name, phone, exp, addr]):
            self.edit_feedback.configure(text="All fields are required!", text_color="red")
            return
            
        if not phone.isdigit() or len(phone) != 10:
            self.edit_feedback.configure(text="Phone Number must be exactly 10 digits!", text_color="red")
            return
            
        try:
            db_adapter.execute_query(
                "UPDATE MEMBERSHIP SET mem_name = ?, phone_number = ?, exp_date = ?, address = ? WHERE mem_id = ?",
                (name, int(phone), exp, addr, int(m_id)),
                commit=True,
                fetch="none"
            )
            self.edit_feedback.configure(text="Member updated successfully!", text_color="green")
            self.load_members()
        except Exception as e:
            self.edit_feedback.configure(text="Update failed! Phone may be duplicate.", text_color="red")
            print(f"Update member error: {e}")
            
    def renew_member(self):
        m_id = self.edit_id_entry.get().strip()
        exp = self.edit_exp_entry.get().strip()
        
        if not m_id or not exp:
            return
            
        # Parse current expiry year and add 1 year
        try:
            parts = exp.split("-")
            if len(parts) == 3:
                new_year = int(parts[0]) + 1
                new_exp = f"{new_year}-{parts[1]}-{parts[2]}"
                
                db_adapter.execute_query(
                    "UPDATE MEMBERSHIP SET exp_date = ? WHERE mem_id = ?",
                    (new_exp, int(m_id)),
                    commit=True,
                    fetch="none"
                )
                self.edit_exp_entry.delete(0, 'end')
                self.edit_exp_entry.insert(0, new_exp)
                self.edit_feedback.configure(text=f"Membership extended to {new_exp}!", text_color="green")
                self.load_members()
            else:
                self.edit_feedback.configure(text="Invalid Expiry Date format!", text_color="red")
        except Exception as e:
            self.edit_feedback.configure(text="Renewal failed!", text_color="red")
            print(f"Renewal error: {e}")
            
    def delete_member(self):
        m_id = self.edit_id_entry.get().strip()
        if not m_id:
            return
            
        confirm = pymsgbox.confirm(f"Are you sure you want to delete member ID {m_id}?", "CONFIRM MEMBER DELETE")
        if confirm != 'OK':
            return
            
        try:
            db_adapter.execute_query(
                "DELETE FROM MEMBERSHIP WHERE mem_id = ?",
                (int(m_id),),
                commit=True,
                fetch="none"
            )
            self.edit_feedback.configure(text="Member deleted successfully!", text_color="green")
            
            # Clear editor fields
            self.edit_id_entry.configure(state="normal")
            self.edit_id_entry.delete(0, 'end')
            self.edit_id_entry.configure(state="disabled")
            self.edit_name_entry.delete(0, 'end')
            self.edit_phone_entry.delete(0, 'end')
            self.edit_exp_entry.delete(0, 'end')
            self.edit_addr_entry.delete(0, 'end')
            
            self.update_btn.configure(state="disabled")
            self.renew_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            
            self.load_members()
        except Exception as e:
            self.edit_feedback.configure(text="Deletion failed!", text_color="red")
            print(f"Delete member error: {e}")
