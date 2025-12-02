import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Animação do botão

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))

def animate_color(button, start_color, end_color, steps=20, delay=10):
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    diff = [(end[i] - start[i]) / steps for i in range(3)]
    current = list(start)
    step = 0

    def do_step():
        nonlocal step
        if step >= steps:
            return
        current[0] += diff[0]
        current[1] += diff[1]
        current[2] += diff[2]

        button.configure(fg_color=rgb_to_hex(*current))
        button.after(delay, do_step)
        step += 1

    do_step()

def animate_scale(button, grow_size=6):
    try:
        orig_padx = button._orig_padx
        orig_pady = button._orig_pady
    except:
        button._orig_padx = button.cget("padx")
        button._orig_pady = button.cget("pady")
        orig_padx = button._orig_padx
        orig_pady = button._orig_pady

    button.configure(padx=orig_padx + grow_size, pady=orig_pady + grow_size)

def reset_scale(button):
    try:
        button.configure(padx=button._orig_padx, pady=button._orig_pady)
    except:
        pass

def add_button_animation(button, normal="#1f6aa5", hover="#2c88d6"):
    def on_enter(event):
        animate_color(button, normal, hover)
        animate_scale(button)

    def on_leave(event):
        animate_color(button, hover, normal)
        reset_scale(button)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


# banco de dados

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
    cur.execute(
        "UPDATE users SET name=?, email=?, age=? WHERE id=?",
        (name, email, age, user_id)
    )
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


# dashboard

def open_dashboard():
    dash = ctk.CTkToplevel()
    dash.title("Dashboard")
    dash.geometry("900x600")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT age, created_at FROM users")
    rows = cur.fetchall()
    conn.close()

    ages = [r[0] for r in rows]
    dates_raw = [r[1] for r in rows]

    # Converter datas
    dates = []
    for d in dates_raw:
        try:
            dates.append(datetime.strptime(d, "%Y-%m-%d"))
        except:
            continue

    avg = sum(ages) / len(ages) if ages else 0
    ctk.CTkLabel(dash, text=f"Média de idade: {avg:.1f}", font=("Arial", 22)).pack(pady=10)

    # Gráfico pizza
    faixa_0_17 = len([a for a in ages if a <= 17])
    faixa_18_30 = len([a for a in ages if 18 <= a <= 30])
    faixa_31_50 = len([a for a in ages if 31 <= a <= 50])
    faixa_51_mais = len([a for a in ages if a >= 51])

    labels = ["0-17", "18-30", "31-50", "51+"]
    values = [faixa_0_17, faixa_18_30, faixa_31_50, faixa_51_mais]

    fig1, ax1 = plt.subplots(figsize=(4, 4))
    ax1.pie(values, labels=labels, autopct="%1.1f%%")
    ax1.set_title("Faixa Etária")
    FigureCanvasTkAgg(fig1, master=dash).get_tk_widget().pack()

    # Linha evolução
    if dates:
        dates.sort()
        counts = list(range(1, len(dates) + 1))

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(dates, counts, marker="o")
        ax2.set_title("Cadastros ao longo do tempo")
        fig2.autofmt_xdate()
        FigureCanvasTkAgg(fig2, master=dash).get_tk_widget().pack()


# funçoes da interface

editing_user_id = None

def add_user():
    name = entry_name.get()
    email = entry_email.get()
    age = entry_age.get()

    if not name or not email or not age:
        messagebox.showerror("Erro", "Preencha tudo!")
        return

    if not age.isdigit():
        messagebox.showerror("Erro", "Idade inválida!")
        return

    insert_user(name, email, int(age))
    load_users()

    entry_name.delete(0, "end")
    entry_email.delete(0, "end")
    entry_age.delete(0, "end")

def start_edit(user):
    global editing_user_id
    editing_user_id = user[0]

    entry_name.delete(0, "end")
    entry_email.delete(0, "end")
    entry_age.delete(0, "end")

    entry_name.insert(0, user[1])
    entry_email.insert(0, user[2])
    entry_age.insert(0, user[3])

    btn_add.configure(text="Salvar", command=save_edit)
    btn_cancel_edit.pack(pady=5)

def save_edit():
    global editing_user_id

    name = entry_name.get()
    email = entry_email.get()
    age = entry_age.get()

    update_user(editing_user_id, name, email, int(age))
    clear_editing_state()
    load_users()

def clear_editing_state():
    global editing_user_id
    editing_user_id = None

    entry_name.delete(0, "end")
    entry_email.delete(0, "end")
    entry_age.delete(0, "end")

    btn_add.configure(text="Cadastrar", command=add_user)
    btn_cancel_edit.pack_forget()

def delete_last():
    users = get_users()
    if not users:
        return
    delete_user(users[-1][0])
    load_users()

def load_users():
    for w in table_frame.winfo_children():
        w.destroy()

    users = get_users()

    for user in users:
        text = f"{user[0]} | {user[1]} | {user[2]} | {user[3]}"
        row = ctk.CTkButton(
            table_frame,
            text=text,
            fg_color="transparent",
            hover_color="#333",
            anchor="w",
            command=lambda u=user: start_edit(u)
        )
        row.pack(fill="x", pady=2)


# menu hamburguer e animação

menu_width = 0
menu_expanded = False

def toggle_menu():
    global menu_width, menu_expanded

    if not menu_expanded:
        expand_menu()
    else:
        collapse_menu()

def expand_menu():
    global menu_width, menu_expanded
    if menu_width < 200:
        menu_width += 20
        sidebar.configure(width=menu_width)
        sidebar.after(10, expand_menu)
    else:
        menu_expanded = True

def collapse_menu():
    global menu_width, menu_expanded
    if menu_width > 0:
        menu_width -= 20
        sidebar.configure(width=menu_width)
        sidebar.after(10, collapse_menu)
    else:
        menu_expanded = False


# app Principal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("CRUD Moderno")
app.geometry("900x600")

# Sidebar
sidebar = ctk.CTkFrame(app, width=0, corner_radius=0)
sidebar.pack(side="left", fill="y")

btn_hamburguer = ctk.CTkButton(app, text="☰", width=50, command=toggle_menu)
btn_hamburguer.place(x=10, y=10)
add_button_animation(btn_hamburguer, "#1f1f1f", "#333333")

# Conteúdo menu
menu_title = ctk.CTkLabel(sidebar, text="Menu", font=("Arial", 20))
menu_title.pack(pady=20)

btn_cadastrar = ctk.CTkButton(sidebar, text="Cadastrar")
btn_cadastrar.pack(fill="x", pady=5)
add_button_animation(btn_cadastrar)

btn_listar = ctk.CTkButton(sidebar, text="Listar", command=load_users)
btn_listar.pack(fill="x", pady=5)
add_button_animation(btn_listar)

btn_dashboard = ctk.CTkButton(sidebar, text="Dashboard", command=open_dashboard)
btn_dashboard.pack(fill="x", pady=5)
add_button_animation(btn_dashboard)

ctk.CTkLabel(sidebar, text="Tema").pack(pady=10)
theme_switch = ctk.CTkOptionMenu(
    sidebar,
    values=["Dark", "Light", "System"],
    command=lambda opt: ctk.set_appearance_mode(opt.lower())
)
theme_switch.pack(pady=5)


# tela principal

main_frame = ctk.CTkFrame(app)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

entry_name = ctk.CTkEntry(main_frame, placeholder_text="Nome")
entry_email = ctk.CTkEntry(main_frame, placeholder_text="Email")
entry_age = ctk.CTkEntry(main_frame, placeholder_text="Idade")

entry_name.pack(pady=5, fill="x")
entry_email.pack(pady=5, fill="x")
entry_age.pack(pady=5, fill="x")

btn_add = ctk.CTkButton(main_frame, text="Cadastrar", command=add_user)
btn_add.pack(pady=5)
add_button_animation(btn_add)

btn_cancel_edit = ctk.CTkButton(main_frame, text="Cancelar edição", fg_color="gray", command=clear_editing_state)
btn_cancel_edit.pack_forget()
add_button_animation(btn_cancel_edit, "#555555", "#777777")

btn_delete = ctk.CTkButton(main_frame, text="Excluir último", fg_color="red", command=delete_last)
btn_delete.pack(pady=5)
add_button_animation(btn_delete, "#8b0000", "#b30000")

table_frame = ctk.CTkFrame(main_frame)
table_frame.pack(pady=10, fill="both", expand=True)

# Inicializar
init_db()
load_users()
app.mainloop()