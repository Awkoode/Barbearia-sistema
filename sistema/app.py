"""SAEP Barbearia — app principal.

Escrito de madrugada, então os comentários estão com cara de quem já não aguenta mais.
A lógica tá toda aqui, sem framework de frescura além do Flask.
"""
import functools
import re
from datetime import timedelta

import psycopg
from psycopg.rows import dict_row
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from config import Config
from crypto import cifrar, decifrar, mascarar_cpf

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(minutes=Config.SESSION_MINUTOS)


# ---------------------------------------------------------------- banco

def get_db():
    # uma conexão por requisição. Se abrir duas eu me perco no meio do caminho.
    if "db" not in g:
        g.db = psycopg.connect(Config.DATABASE_URL, row_factory=dict_row)
    return g.db


@app.teardown_appcontext
def fecha_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


# ---------------------------------------------------------------- login

def login_obrigatorio(view):
    @functools.wraps(view)
    def envoltorio(*args, **kwargs):
        # sem sessão viva, sem entrada. Simples assim, mesmo que eu queira dormir.
        if "usuario_id" not in session:
            flash("Sua sessão acabou ou você nem entrou ainda. Faz login de novo.", "erro")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return envoltorio


@app.route("/")
def raiz():
    return redirect(url_for("painel") if "usuario_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_digitado = request.form.get("login", "").strip()
        senha = request.form.get("senha", "")

        usuario = get_db().execute(
            "SELECT id, nome, senha_hash FROM usuario WHERE login = %s", (login_digitado,)
        ).fetchone()

        # mensagem genérica de propósito: não dizer se foi o usuário ou a senha que errou
        if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
            flash("Usuário ou senha inválidos. Confere aí e tenta de novo.", "erro")
            return render_template("login.html"), 401

        session.clear()
        session.permanent = True  # aqui começa o relógio dos 30 min
        session["usuario_id"] = usuario["id"]
        session["nome"] = usuario["nome"]
        return redirect(url_for("painel"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Saiu. Agora pode ir dormir, que eu também vou.", "ok")
    return redirect(url_for("login"))


# ---------------------------------------------------------------- painel

@app.route("/painel")
@login_obrigatorio
def painel():
    db = get_db()
    contagens = {
        "clientes": db.execute("SELECT COUNT(*) FROM cliente").fetchone()["count"],
        "barbeiros": db.execute("SELECT COUNT(*) FROM barbeiro WHERE ativo = 1").fetchone()["count"],
        "servicos": db.execute("SELECT COUNT(*) FROM servico").fetchone()["count"],
        "agendamentos": db.execute("SELECT COUNT(*) FROM agendamento").fetchone()["count"],
    }
    return render_template("painel.html", contagens=contagens)


# ---------------------------------------------------------------- clientes

@app.route("/clientes", methods=["GET", "POST"])
@login_obrigatorio
def clientes():
    db = get_db()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        cpf = somente_digitos(request.form.get("cpf", ""))

        if not nome or len(cpf) != 11:
            flash("Nome e CPF com 11 números são obrigatórios. Sem isso eu não cadastro.", "erro")
        else:
            db.execute(
                "INSERT INTO cliente (nome, telefone, cpf_criptografado) VALUES (%s, %s, %s)",
                (nome, telefone, cifrar(cpf)),
            )
            db.commit()
            flash("Cliente cadastrado. Mais um pra conta.", "ok")
        return redirect(url_for("clientes"))

    # busca: só filtra o nome, o CPF tá criptografado e não dá pra fazer LIKE nele
    busca = request.args.get("busca", "").strip()
    linhas = db.execute(
        "SELECT id, nome, telefone, cpf_criptografado FROM cliente WHERE nome ILIKE %s ORDER BY nome",
        (f"%{busca}%",),
    ).fetchall()

    lista = [
        {
            "id": l["id"],
            "nome": l["nome"],
            "telefone": l["telefone"],
            "cpf": mascarar_cpf(decifrar(l["cpf_criptografado"])),
        }
        for l in linhas
    ]
    return render_template("clientes.html", clientes=lista, busca=busca)


# ---------------------------------------------------------------- barbeiros

@app.route("/barbeiros", methods=["GET", "POST"])
@login_obrigatorio
def barbeiros():
    db = get_db()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        cpf = somente_digitos(request.form.get("cpf", ""))
        senha = request.form.get("senha", "")

        if not nome or len(cpf) != 11 or len(senha) < 6:
            flash("Nome, CPF com 11 números e senha com 6+ caracteres. Tudo obrigatório.", "erro")
        else:
            db.execute(
                "INSERT INTO barbeiro (nome, telefone, cpf_criptografado, senha_criptografada) "
                "VALUES (%s, %s, %s, %s)",
                (nome, telefone, cifrar(cpf), cifrar(senha)),
            )
            db.commit()
            flash("Barbeiro cadastrado. Tesoura nova na área.", "ok")
        return redirect(url_for("barbeiros"))

    linhas = db.execute(
        "SELECT id, nome, telefone, cpf_criptografado FROM barbeiro WHERE ativo = 1 ORDER BY nome"
    ).fetchall()
    lista = [
        {
            "id": l["id"],
            "nome": l["nome"],
            "telefone": l["telefone"],
            "cpf": mascarar_cpf(decifrar(l["cpf_criptografado"])),
        }
        for l in linhas
    ]
    return render_template("barbeiros.html", barbeiros=lista)


# ---------------------------------------------------------------- serviços

@app.route("/servicos", methods=["GET", "POST"])
@login_obrigatorio
def servicos():
    db = get_db()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        try:
            preco = float(request.form.get("preco", "").replace(",", "."))
            duracao = int(request.form.get("duracao", ""))
        except ValueError:
            flash("Preço e duração têm que ser número. Não é hora de escrever poema.", "erro")
            return redirect(url_for("servicos"))

        if not nome or preco < 0 or duracao <= 0:
            flash("Nome obrigatório, preço não negativo e duração maior que zero.", "erro")
        else:
            db.execute(
                "INSERT INTO servico (nome, preco, duracao_min) VALUES (%s, %s, %s)",
                (nome, preco, duracao),
            )
            db.commit()
            flash("Serviço cadastrado. Agora tem mais uma coisa pra cobrar.", "ok")
        return redirect(url_for("servicos"))

    lista = db.execute("SELECT id, nome, preco, duracao_min FROM servico ORDER BY nome").fetchall()
    return render_template("servicos.html", servicos=lista)


# ---------------------------------------------------------------- agendamentos

@app.route("/agendamentos", methods=["GET", "POST"])
@login_obrigatorio
def agendamentos():
    db = get_db()

    if request.method == "POST":
        # barbeiro é obrigatório. Serviço sem barbeiro não existe nessa barbearia.
        try:
            cliente_id = int(request.form["cliente_id"])
            barbeiro_id = int(request.form["barbeiro_id"])
            servico_id = int(request.form["servico_id"])
        except (KeyError, ValueError):
            flash("Escolhe cliente, barbeiro e serviço. Os três, por favor.", "erro")
            return redirect(url_for("agendamentos"))

        data = request.form.get("data", "")
        hora = request.form.get("hora", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data) or not re.fullmatch(r"\d{2}:\d{2}", hora):
            flash("Data ou hora em formato estranho. Usa o calendário e o relógio.", "erro")
            return redirect(url_for("agendamentos"))

        # choque de horário era o problema principal da barbearia, então isso aqui não pode falhar
        conflito = db.execute(
            "SELECT 1 FROM agendamento WHERE barbeiro_id = %s AND data = %s AND hora = %s",
            (barbeiro_id, data, hora),
        ).fetchone()
        if conflito:
            flash("Esse barbeiro já tem horário nesse dia e nessa hora. Escolhe outro.", "erro")
            return redirect(url_for("agendamentos"))

        try:
            db.execute(
                "INSERT INTO agendamento (cliente_id, barbeiro_id, servico_id, data, hora) "
                "VALUES (%s, %s, %s, %s, %s)",
                (cliente_id, barbeiro_id, servico_id, data, hora),
            )
            db.commit()
            flash("Agendamento marcado. Agora é torcer pro cliente aparecer.", "ok")
        except psycopg.IntegrityError:
            db.rollback()  # no Postgres a transação fica abortada depois de erro
            flash("Cliente, barbeiro ou serviço não existe mais. Recarrega a página.", "erro")
        return redirect(url_for("agendamentos"))

    # listagem ordenada por dia e horário, com dados completos (pedido do enunciado)
    lista = db.execute(
        """
        SELECT a.id, a.data, a.hora, a.status,
               c.nome AS cliente, s.nome AS servico, s.preco, s.duracao_min,
               b.nome AS barbeiro
          FROM agendamento a
          JOIN cliente c ON c.id = a.cliente_id
          JOIN servico s ON s.id = a.servico_id
          JOIN barbeiro b ON b.id = a.barbeiro_id
         ORDER BY a.data, a.hora
        """
    ).fetchall()

    clientes_lista = db.execute("SELECT id, nome FROM cliente ORDER BY nome").fetchall()
    barbeiros_lista = db.execute(
        "SELECT id, nome FROM barbeiro WHERE ativo = 1 ORDER BY nome"
    ).fetchall()
    servicos_lista = db.execute("SELECT id, nome FROM servico ORDER BY nome").fetchall()

    return render_template(
        "agendamentos.html",
        agendamentos=lista,
        clientes=clientes_lista,
        barbeiros=barbeiros_lista,
        servicos=servicos_lista,
    )


if __name__ == "__main__":
    app.run(debug=True)
