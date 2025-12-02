import re

class Usuario:
    def __init__(self, nome, email, idade):
        self.nome = nome
        self.email = email
        self.idade = idade

    def validar(self):
        if len(self.nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, self.email):
            return False, "E-mail inválido."

        if not isinstance(self.idade, int) or self.idade <= 0:
            return False, "Idade deve ser maior que zero."

        return True, "Dados válidos."
