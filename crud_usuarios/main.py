import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_user(name, email, age):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, age, created_at) VALUES (?, ?, ?, ?)",
        (name, email, age, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

def update_user(user_id, name, email, age):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=?, email=?, age=? WHERE id=?",
                (name, email, age, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows


class HamburgerIcon(tk.Canvas):
    def __init__(self, master, size=32, line_color="#00f2ff", **kwargs):
        super().__init__(master, width=size, height=size, bg=master.cget("bg"), highlightthickness=0, **kwargs)
        self.size = size
        self.line_color = line_color
        s = size
        pad = 8
        w = s - 2 * pad
        # coords for three lines
        self.lines = []
        y_positions = [pad, s//2, s - pad]
        for y in y_positions:
            self.lines.append(self.create_line(pad, y, pad + w, y, width=3, fill=self.line_color, capstyle=tk.ROUND))
        self.is_open = False
        self.pulse_dir = 1
        self._pulse_step = 0
        self.after(80, self._pulse)

       
        self.bind("<Button-1>", self.toggle)

    def _pulse(self):
       
        hexcol = self.line_color.lstrip("#")
        r = int(hexcol[0:2], 16)
        g = int(hexcol[2:4], 16)
        b = int(hexcol[4:6], 16)
        
        delta = (self._pulse_step - 10)  # -10..+10
        g2 = max(0, min(255, g + delta*1))
        color = f"#{r:02x}{g2:02x}{b:02x}"
        for ln in self.lines:
            self.itemconfigure(ln, fill=color)
        self._pulse_step += self.pulse_dir
        if self._pulse_step >= 20 or self._pulse_step <= 0:
            self.pulse_dir *= -1
        self.after(80, self._pulse)

    def toggle(self, _=None):
       
        if not self.is_open:
            
            coords = self.coords(self.lines[0])  # returns [x1,y1,x2,y2]
            s = self.size; pad = 8
            self._animate_to([(pad, pad, s-pad, s-pad),
                              (pad, s//2, s-pad, s//2),  # middle will fade
                              (pad, s-pad, s-pad, pad)])
            # fade middle line
            self.itemconfigure(self.lines[1], state="hidden")
            self.is_open = True
        else:
            # back to hamburger
            s = self.size; pad = 8; w = s - 2*pad
            self._animate_to([(pad, pad, pad + w, pad),
                              (pad, s//2, pad + w, s//2),
                              (pad, s-pad, pad + w, s-pad)])
            self.itemconfigure(self.lines[1], state="normal")
            self.is_open = False

    def _animate_to(self, target_coords, steps=6):
        
        start = [self.coords(ln) for ln in self.lines]
        steps_list = []
        for i in range(len(self.lines)):
            s = start[i]
            t = target_coords[i]
            dx1 = (t[0] - s[0]) / steps
            dy1 = (t[1] - s[1]) / steps
            dx2 = (t[2] - s[2]) / steps
            dy2 = (t[3] - s[3]) / steps
            steps_list.append((dx1, dy1, dx2, dy2))
        def step_animation(step=0):
            if step >= steps:
                
                for i, ln in enumerate(self.lines):
                    self.coords(ln, *target_coords[i])
                return
            for i, ln in enumerate(self.lines):
                s = self.coords(ln)
                dx1, dy1, dx2, dy2 = steps_list[i]
                new = (s[0] + dx1, s[1] + dy1, s[2] + dx2, s[3] + dy2)
                self.coords(ln, *new)
            self.after(30, lambda: step_animation(step+1))
        step_animation(0)

# animação do botão
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def rgb_to_hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(int(r),int(g),int(b))

def animate_color(button, start_color, end_color, steps=10, delay=15):
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)
    dif = [(end[i]-start[i])/steps for i in range(3)]
    cur = list(start)
    step = 0
    def do_step():
        nonlocal step
        if step>steps: 
            return
        cur[0]+=dif[0]; cur[1]+=dif[1]; cur[2]+=dif[2]
        try:
            button.configure(fg_color=rgb_to_hex(*cur))
        except Exception:
            pass
        step+=1
        if step<=steps:
            button.after(delay, do_step)
    do_step()

def animate_scale(button, grow=4):
    
    try:
        
        if not hasattr(button, "_orig_padx"):
            button._orig_padx = int(button.cget("padx")) if button.cget("padx") else 8
            button._orig_pady = int(button.cget("pady")) if button.cget("pady") else 4
        button.configure(padx=button._orig_padx+grow, pady=button._orig_pady+grow)
    except Exception:
        pass

def reset_scale(button):
    try:
        if hasattr(button, "_orig_padx"):
            button.configure(padx=button._orig_padx, pady=button._orig_pady)
    except Exception:
        pass

def add_button_animation(button, normal="#1f6aa5", hover="#2c88d6"):
    def on_enter(e):
        animate_color(button, normal, hover)
        animate_scale(button, grow=4)
    def on_leave(e):
        animate_color(button, hover, normal)
        reset_scale(button)
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


# matplotlib

def open_dashboard():
    dash = ctk.CTkToplevel()
    dash.title("Dashboard")
    dash.geometry("900x600")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT age, created_at FROM users")
    rows = cur.fetchall()
    conn.close()

    ages = [r[0] for r in rows if r[0] is not None]
    dates_raw = [r[1] for r in rows if r[1]]
    dates = []
    for d in dates_raw:
        try:
            dates.append(datetime.strptime(d,"%Y-%m-%d"))
        except:
            pass

    avg = sum(ages)/len(ages) if ages else 0
    ctk.CTkLabel(dash, text=f"Média de idade: {avg:.1f}", font=("Arial",18)).pack(pady=8)

    # pie
    faixa_0_17 = len([a for a in ages if a <= 17])
    faixa_18_30 = len([a for a in ages if 18 <= a <= 30])
    faixa_31_50 = len([a for a in ages if 31 <= a <= 50])
    faixa_51_mais = len([a for a in ages if a >= 51])
    labels = ["0-17","18-30","31-50","51+"]
    values = [faixa_0_17,faixa_18_30,faixa_31_50,faixa_51_mais]

    fig1, ax1 = plt.subplots(figsize=(4,4))
    ax1.pie(values, labels=labels, autopct="%1.1f%%")
    ax1.set_title("Faixa Etária")
    FigureCanvasTkAgg(fig1, master=dash).get_tk_widget().pack()

    if dates:
        dates.sort()
        counts = list(range(1,len(dates)+1))
        fig2, ax2 = plt.subplots(figsize=(6,4))
        ax2.plot(dates, counts, marker="o")
        ax2.set_title("Cadastros ao longo do tempo")
        fig2.autofmt_xdate()
        FigureCanvasTkAgg(fig2, master=dash).get_tk_widget().pack()


# Interface principal (CTk)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("CRUD Moderno - Animado")
app.geometry("900x600")


sidebar = ctk.CTkFrame(app, width=0, corner_radius=0)
sidebar.pack(side="left", fill="y")


hamb = HamburgerIcon(app, size=36, line_color="#00f2ff")
hamb.place(x=12, y=12)


menu_title = ctk.CTkLabel(sidebar, text="Menu", font=("Arial",18))
menu_title.pack(pady=18)

btn_cadastrar = ctk.CTkButton(sidebar, text="Cadastrar", command=lambda: None)
btn_cadastrar.pack(fill="x", padx=12, pady=6)
add_button_animation(btn_cadastrar)

btn_listar = ctk.CTkButton(sidebar, text="Listar", command=lambda: load_users())
btn_listar.pack(fill="x", padx=12, pady=6)
add_button_animation(btn_listar)

btn_dash = ctk.CTkButton(sidebar, text="Dashboard", command=open_dashboard)
btn_dash.pack(fill="x", padx=12, pady=6)
add_button_animation(btn_dash)

# Tema
ctk.CTkLabel(sidebar, text="Tema").pack(pady=8)
theme_menu = ctk.CTkOptionMenu(sidebar, values=["Dark","Light","System"], command=lambda v: ctk.set_appearance_mode(v.lower()))
theme_menu.pack(padx=12, pady=6)


menu_width = 0
menu_expanded = False
def expand_menu():
    global menu_width, menu_expanded
    if menu_width < 220:
        menu_width += 20
        sidebar.configure(width=menu_width)
        sidebar.after(12, expand_menu)
    else:
        menu_expanded = True

def collapse_menu():
    global menu_width, menu_expanded
    if menu_width > 0:
        menu_width -= 20
        sidebar.configure(width=menu_width)
        sidebar.after(12, collapse_menu)
    else:
        menu_expanded = False

def toggle_menu():
    global menu_expanded
    if not menu_expanded:
        expand_menu()
    else:
        collapse_menu()
    
    hamb.toggle()


hamb.bind("<Button-1>", lambda e: toggle_menu())


main_frame = ctk.CTkFrame(app)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

entry_name = ctk.CTkEntry(main_frame, placeholder_text="Nome")
entry_email = ctk.CTkEntry(main_frame, placeholder_text="Email")
entry_age = ctk.CTkEntry(main_frame, placeholder_text="Idade")
entry_name.pack(pady=6, fill="x")
entry_email.pack(pady=6, fill="x")
entry_age.pack(pady=6, fill="x")

btn_add = ctk.CTkButton(main_frame, text="Cadastrar", command=lambda: add_user())
btn_add.pack(pady=8)
add_button_animation(btn_add)

btn_cancel = ctk.CTkButton(main_frame, text="Cancelar edição", fg_color="gray", command=lambda: clear_editing_state())
btn_cancel.pack_forget()
add_button_animation(btn_cancel, normal="#555555", hover="#777777")

btn_delete = ctk.CTkButton(main_frame, text="Excluir último", fg_color="red", command=lambda: delete_last())
btn_delete.pack(pady=6)
add_button_animation(btn_delete, normal="#8b0000", hover="#b30000")

table_frame = ctk.CTkFrame(main_frame)
table_frame.pack(pady=10, fill="both", expand=True)

# editar

editing_user_id = None

def add_user():
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    age = entry_age.get().strip()
    if not name or not email or not age or not age.isdigit():
        messagebox.showerror("Erro", "Preencha corretamente os campos.")
        return
    insert_user(name,email,int(age))
    load_users()
    clear_editing_state()

def start_edit(user):
    global editing_user_id
    editing_user_id = user[0]
    entry_name.delete(0,"end"); entry_email.delete(0,"end"); entry_age.delete(0,"end")
    entry_name.insert(0,user[1]); entry_email.insert(0,user[2]); entry_age.insert(0,str(user[3]))
    btn_add.configure(text="Salvar", command=save_edit)
    btn_cancel.pack(pady=6)

def save_edit():
    global editing_user_id
    name = entry_name.get().strip(); email = entry_email.get().strip(); age = entry_age.get().strip()
    if not editing_user_id:
        messagebox.showerror("Erro","Nenhum usuário selecionado.")
        return
    if not name or not email or not age.isdigit():
        messagebox.showerror("Erro","Dados inválidos.")
        return
    update_user(editing_user_id, name, email, int(age))
    clear_editing_state()
    load_users()

def clear_editing_state():
    global editing_user_id
    editing_user_id = None
    entry_name.delete(0,"end"); entry_email.delete(0,"end"); entry_age.delete(0,"end")
    btn_add.configure(text="Cadastrar", command=add_user)
    try: btn_cancel.pack_forget()
    except: pass

def delete_last():
    users = get_users()
    if not users: return
    delete_user(users[-1][0]); load_users()

def load_users():
    for w in table_frame.winfo_children(): w.destroy()
    users = get_users()
    for user in users:
       
        row = ctk.CTkButton(table_frame, text=f"{user[0]} | {user[1]} | {user[2]} | {user[3]}",
                            fg_color="transparent", hover_color="#222", anchor="w",
                            command=lambda u=user: start_edit(u))
        row.pack(fill="x", pady=2, padx=4)


init_db()
load_users()
app.mainloop()
