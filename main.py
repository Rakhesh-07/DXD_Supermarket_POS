import customtkinter as ctk
import time
from PIL import Image
import db_adapter
import Login.Login as pa

# Import our custom frames from modules
from Create_Membership.Create_Membership import CreateMembershipFrame
from Bill_Customer.Bill_Customer import POSFrame
from Check_Bill.Check_Bill import CheckBillFrame
from Check_Stock.Check_Stock import CheckStockFrame

# If manager, we can use matplotlib to draw a dashboard chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SupermarketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("DXD Supermarket - Management POS System")
        
        # Query exact display information from OS
        import ctypes
        try:
            self.w = ctypes.windll.user32.GetSystemMetrics(0)
            self.h = ctypes.windll.user32.GetSystemMetrics(1)
        except Exception:
            self.w = self.winfo_screenwidth()
            self.h = self.winfo_screenheight()
            
        self.geometry(f"{self.w}x{self.h}+0+0")
        
        # Configure layout (1 column for sidebar, 1 for content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create Sidebar
        self.create_sidebar()
        
        # Create Content Container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Dictionary to store frames
        self.frames = {}
        
        # Bind Escape to exit and close process
        self.bind("<Escape>", lambda e: self.on_closing())
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize and show Dashboard Frame
        self.show_frame("Dashboard")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#eaab06", "#202020"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Push logout button to the bottom
        
        # App Title in Sidebar
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DXD POS", font=("Arial", 24, "bold"), text_color=("#1e1e1e", "#eaab06"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Navigation Buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "Dashboard"),
            ("Billing / POS", "POS"),
            ("Inventory", "Inventory"),
            ("Create Membership", "Membership"),
            ("Bill History", "History")
        ]
        
        for idx, (label, target) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=label,
                font=("Arial", 14, "bold"),
                fg_color="transparent",
                text_color=("#1e1e1e", "#ffffff"),
                hover_color=("#d39a04", "#2c2c2c"),
                anchor="w",
                height=40,
                command=lambda t=target: self.show_frame(t)
            )
            btn.grid(row=idx+1, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[target] = btn
            
        # Logout Button at the bottom
        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Logout",
            font=("Arial", 14, "bold"),
            fg_color="#c21807",
            hover_color="#9e1205",
            text_color="white",
            height=40,
            command=self.logout
        )
        self.logout_btn.grid(row=8, column=0, padx=15, pady=20, sticky="ew")

    def show_frame(self, page_name):
        # Remove current frame if exists
        for frame in self.content_container.winfo_children():
            frame.grid_forget()
            frame.destroy() # Completely destroy the old frame to release resources
            
        # Lazy load and build active frame
        if page_name == "Dashboard":
            frame = DashboardFrame(self.content_container, self)
        elif page_name == "POS":
            frame = POSFrame(self.content_container, self)
        elif page_name == "Inventory":
            frame = CheckStockFrame(self.content_container, self)
        elif page_name == "Membership":
            frame = CreateMembershipFrame(self.content_container, self)
        elif page_name == "History":
            frame = CheckBillFrame(self.content_container, self)
            
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Highlight active sidebar button
        for target, btn in self.nav_buttons.items():
            if target == page_name:
                btn.configure(fg_color=("#c89205", "#3a3a3a"))
            else:
                btn.configure(fg_color="transparent")

    def logout(self):
        self.on_closing()

    def on_closing(self):
        import sys
        try:
            self.quit()
            self.destroy()
        except Exception:
            pass
        sys.exit(0)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top Panel
        top_panel = ctk.CTkFrame(self, height=80, fg_color=("#eaab06", "#202020"))
        top_panel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        top_panel.grid_columnconfigure(1, weight=1)
        
        welcome_lbl = ctk.CTkLabel(top_panel, text=f"Welcome back, {pa.emp_name} ({pa.emp_role})", font=("Arial", 18, "bold"), text_color=("#1e1e1e", "#ffffff"))
        welcome_lbl.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        current_date = time.strftime("%A, %d %B %Y")
        date_lbl = ctk.CTkLabel(top_panel, text=current_date, font=("Arial", 14), text_color=("#1e1e1e", "#aaaaaa"))
        date_lbl.grid(row=0, column=2, padx=20, pady=20, sticky="e")
        
        # Left Dashboard Side: Statistics Cards
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        
        # Fetch stats from DB
        try:
            total_sales = db_adapter.execute_query("SELECT SUM(final_amount) FROM BILLS", fetch="one")[0] or 0
            total_bills = db_adapter.execute_query("SELECT COUNT(*) FROM BILLS", fetch="one")[0] or 0
            total_items = db_adapter.execute_query("SELECT COUNT(*) FROM STOCK", fetch="one")[0] or 0
            total_members = db_adapter.execute_query("SELECT COUNT(*) FROM MEMBERSHIP", fetch="one")[0] or 0
        except Exception:
            total_sales = 0
            total_bills = 0
            total_items = 0
            total_members = 0
            
        self.create_card(stats_frame, "Total Revenue", f"Rs. {total_sales}", 0, 0, "#2ecc71")
        self.create_card(stats_frame, "Total Transactions", str(total_bills), 0, 1, "#3498db")
        self.create_card(stats_frame, "Active Inventory Items", str(total_items), 1, 0, "#f1c40f")
        self.create_card(stats_frame, "Registered Members", str(total_members), 1, 1, "#9b59b6")
        
        # Right Dashboard Side: Manager Sales Charts (only visible to Managers)
        chart_frame = ctk.CTkFrame(self, corner_radius=15)
        chart_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(1, weight=1)
        
        chart_title = ctk.CTkLabel(chart_frame, text="Sales Analysis (Last 7 Days)", font=("Arial", 16, "bold"))
        chart_title.grid(row=0, column=0, pady=15)
        
        if pa.emp_role == "Manager":
            self.draw_sales_chart(chart_frame)
        else:
            no_access_lbl = ctk.CTkLabel(chart_frame, text="Analytics are restricted to managers.", font=("Arial", 14, "italic"), text_color="grey")
            no_access_lbl.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

    def create_card(self, parent, title, val, r, c, accent_color):
        card = ctk.CTkFrame(parent)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        # Accent indicator
        accent = ctk.CTkFrame(card, height=4, fg_color=accent_color)
        accent.grid(row=0, column=0, sticky="ew")
        
        title_lbl = ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color="grey")
        title_lbl.grid(row=1, column=0, pady=(20, 10))
        
        val_lbl = ctk.CTkLabel(card, text=val, font=("Arial", 24, "bold"), text_color=accent_color)
        val_lbl.grid(row=2, column=0, pady=(0, 20))

    def draw_sales_chart(self, parent):
        # Fetch Sales details from DB grouped by date
        try:
            sales_data = db_adapter.execute_query(
                "SELECT bill_date, SUM(final_amount) FROM BILLS GROUP BY bill_date ORDER BY bill_date DESC LIMIT 7",
                fetch="all"
            )
        except Exception:
            sales_data = []
            
        dates = []
        revenues = []
        
        if sales_data:
            # Reverse order so they print chronologically left to right
            for row in reversed(sales_data):
                dates.append(row[0])
                revenues.append(row[1])
        else:
            dates = ["No Data"]
            revenues = [0]
            
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor='#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        ax.bar(dates, revenues, color='#eaab06', width=0.4)
        
        # Set chart styles
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.yaxis.grid(True, color='grey', linestyle='--', alpha=0.3)
        ax.set_ylabel("Revenue (Rs.)", color='white', fontsize=10)
        
        plt.tight_layout()
        
        # Render chart in Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

if __name__ == "__main__":
    if pa.v == 1:
        app = SupermarketApp()
        app.mainloop()
