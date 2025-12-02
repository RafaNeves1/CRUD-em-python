import tkinter as tk
from tkinter import messagebox
from database import create_tables
from user_service import criar_usuario, listar_usuarios, atualizar_usuario, remover_usuario

create_tables()

class CRUDGui:
    def __init__(self, root):
        self.root = root
        self.root.title("CRUD de Usuários - GUI")
        self.root.geometry("600x400")
        self.selected_id = None

        # Frame formulário
        form_frame = tk.Frame(root, padx=10, pady=10)
        form_frame.pack(fill="x")

        tk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="w")
        self.nome_entry = tk.Entry(form_frame)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w")
        self.email_entry = tk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(form_frame, text="Idade:").grid(row=2, column=0, sticky="w")
        self.idade_entry = tk.Entry(form_frame)
        self.idade_entry.grid(row=2, column=1, sticky="ew", padx=5)

        form_frame.columnconfigure(1, weight=1)

        # Frame botões
        btn_frame = tk.Frame(root, padx=10, pady=5)
        btn_frame.pack(fill="x")

        self.add_btn = tk.Button(btn_frame, text="Cadastrar", command=self.add_user)
        self.add_btn.pack(side="left", padx=5)

        self.update_btn = tk.Button(btn_frame, text="Atualizar", command=self.update_user)
        self.update_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(btn_frame, text="Remover", command=self.delete_user)
        self.delete_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Limpar campos", command=self.clear_fields)
        self.clear_btn.pack(side="left", padx=5)

        # Frame listagem
        list_frame = tk.Frame(root, padx=10, pady=5)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        users = listar_usuarios()
        for u in users:
            display = f"{u[0]} | {u[1]} | {u[2]} | {u[3]}"
            self.listbox.insert(tk.END, display)

    def add_user(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        idade_text = self.idade_entry.get().strip()
        if not nome or not email or not idade_text:
            messagebox.showwarning("Dados incompletos", "Preencha todos os campos.")
            return
        try:
            idade = int(idade_text)
        except ValueError:
            messagebox.showerror("Idade inválida", "Idade deve ser um número inteiro.")
            return
        ok, msg = criar_usuario(nome, email, idade)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.clear_fields()
            self.refresh_list()
        else:
            messagebox.showerror("Erro", msg)

    def update_user(self):
        if self.selected_id is None:
            messagebox.showwarning("Seleção", "Selecione um usuário na lista para atualizar.")
            return
        nome = self.nome_entry.get().strip() or None
        email = self.email_entry.get().strip() or None
        idade_text = self.idade_entry.get().strip()
        idade = None
        if idade_text:
            try:
                idade = int(idade_text)
            except ValueError:
                messagebox.showerror("Idade inválida", "Idade deve ser um número inteiro.")
                return
        ok, msg = atualizar_usuario(self.selected_id, nome, email, idade)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.clear_fields()
            self.refresh_list()
        else:
            messagebox.showerror("Erro", msg)

    def delete_user(self):
        if self.selected_id is None:
            messagebox.showwarning("Seleção", "Selecione um usuário na lista para remover.")
            return
        if messagebox.askyesno("Confirmação", "Deseja remover o usuário selecionado?"):
            ok, msg = remover_usuario(self.selected_id)
            if ok:
                messagebox.showinfo("Removido", msg)
                self.clear_fields()
                self.refresh_list()
            else:
                messagebox.showerror("Erro", msg)

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        text = self.listbox.get(sel[0])
        # formato: "id | nome | email | idade"
        parts = [p.strip() for p in text.split("|")]
        try:
            self.selected_id = int(parts[0])
        except Exception:
            self.selected_id = None
        self.nome_entry.delete(0, tk.END)
        self.nome_entry.insert(0, parts[1])
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, parts[2])
        self.idade_entry.delete(0, tk.END)
        self.idade_entry.insert(0, parts[3])

    def clear_fields(self):
        self.selected_id = None
        self.nome_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.idade_entry.delete(0, tk.END)
        self.listbox.selection_clear(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDGui(root)
    root.mainloop()
