from database import get_connection
from models import Usuario

def criar_usuario(nome, email, idade):
    usuario = Usuario(nome, email, idade)
    valido, msg = usuario.validar()
    if not valido:
        return False, msg
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, idade) VALUES (?, ?, ?)",
                       (nome, email, idade))
        conn.commit()
        conn.close()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar: {e}"

def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    conn.close()
    return data

def atualizar_usuario(id_usuario, nome=None, email=None, idade=None):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []
    if nome:
        campos.append("nome=?")
        valores.append(nome)
    if email:
        campos.append("email=?")
        valores.append(email)
    if idade:
        campos.append("idade=?")
        valores.append(idade)
    valores.append(id_usuario)
    try:
        cursor.execute(f"UPDATE usuarios SET {', '.join(campos)} WHERE id=?", valores)
        conn.commit()
        conn.close()
        return True, "Usuário atualizado!"
    except Exception as e:
        return False, f"Erro ao atualizar: {e}"

def remover_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (id_usuario,))
    conn.commit()
    conn.close()
    return True, "Usuário removido!"
