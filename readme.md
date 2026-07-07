# Professional Supermarket POS & Inventory Management System

A production-grade, secure desktop Point of Sale (POS) and inventory control terminal built using **CustomTkinter** and **SQLite** (with dual support for MySQL).

---

## Key Upgrades & Industry Features

1. **Modern Single-Window UI**:
   - Built using `customtkinter` with an elegant, responsive dark/light themed sidebar layout.
   - Replaced multi-window popping and laggy destructions with dynamic frame-swapping.
2. **Relational Database Storage**:
   - Retired the insecure binary pickling file `bill_details.dat`.
   - Implemented relational SQLite database schema mapping `EMPLOYEES`, `STOCK`, `MEMBERSHIP`, `BILLS`, and `BILL_ITEMS`.
3. **Staff Roles & Security**:
   - Employees login safely. Passwords are saved and verified using **SHA-256 encryption hashes** (no plain text logs).
   - Cashiers get access to POS billing, memberships, and stock checker.
   - Managers get access to stock CRUD (add/edit/delete) and the Sales Analytics Dashboard.
4. **Point of Sale Billing Terminal**:
   - Live scrollable cart table.
   - Membership discount verification (checks dates and applies a 2% discount automatically).
   - Cash received calculation and change-returned prompt.
   - Automatically writes to the local `receipts/` directory as formatted text invoices.
5. **Interactive Memberships Portal**:
   - Divided into two distinct tabs using `ctk.CTkTabview`:
     * **Create Membership**: The registration form for new customers.
     * **View / Edit Memberships**: Search member profiles by name, ID, or phone; update contact details; delete accounts; or extend memberships (+1 Year) with a single click.
6. **Manager Analytics**:
   - Interactive charts drawn using `matplotlib` visualizing weekly sales revenue and statistics.

---

## Getting Started

### 1. Installation
Install the project dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Initialization
Verify or seed the database:
```bash
python db_setup.py
```
This automatically constructs the databases and seeds sample products and the default staff accounts:
- **Manager**: `dxd` (password: `ryomen`)
- **Cashier**: `rocky2003` (password: `vrv07`)

### 3. Launching the App
Run the launcher:
```bash
python main.py
```
