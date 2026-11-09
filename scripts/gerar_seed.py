"""Gera o saep_db.sql (criação das tabelas + massa de dados).

Por que um gerador? Porque CPF e senha de barbeiro precisam estar CRIPTOGRAFADOS
dentro do SQL, e o jeito mais honesto de fazer isso é usar o mesmo código do sistema.
Rode na raiz do projeto:  python scripts/gerar_seed.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "sistema"))

from werkzeug.security import generate_password_hash  # noqa: E402

from crypto import cifrar  # noqa: E402


def sql_str(valor):
    if valor is None:
        return "NULL"
    return "'" + str(valor).replace("'", "''") + "'"


USUARIOS = [
    (1, "Ana Souza", "ana", "ana123"),
    (2, "Carlos Lima", "carlos", "carlos123"),
    (3, "Juliana Melo", "juliana", "juliana123"),
]

BARBEIROS = [
    (1, "Rafael Costa", "(11) 98888-1111", "12345678901", "rafa123"),
    (2, "Bruno Alves", "(11) 98888-2222", "98765432100", "bruno123"),
    (3, "Diego Nunes", "(11) 98888-3333", "11122233344", "diego123"),
]

CLIENTES = [
    (1, "Marcos Pereira", "(11) 97777-1111", "55566677788", "marcos@email.com"),
    (2, "Lucas Ferreira", "(11) 97777-2222", "22233344455", "lucas@email.com"),
    (3, "Pedro Oliveira", "(11) 97777-3333", "66677788899", None),
]

SERVICOS = [
    (1, "Corte masculino", 45.00, 30),
    (2, "Barba completa", 35.00, 20),
    (3, "Corte + barba", 70.00, 50),
]

AGENDAMENTOS = [
    (1, 1, 1, 3, "2026-11-10", "09:00", "marcado"),
    (2, 2, 2, 1, "2026-11-10", "10:00", "marcado"),
    (3, 3, 3, 2, "2026-11-11", "14:30", "marcado"),
]

CABECALHO = """-- =====================================================================
-- SAEP Barbearia - script de criação e população do banco
-- Banco: SQLite  (gerado por scripts/gerar_seed.py)
-- Uso:   sqlite3 saep.db < saep_db.sql
-- Logins de teste: ana/ana123, carlos/carlos123, juliana/juliana123
-- CPF e senha de barbeiro estão criptografados (Fernet). Chave demo no config.py.
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS agendamento;
DROP TABLE IF EXISTS servico;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS barbeiro;
DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    login       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL           -- hash, nunca senha em texto puro
);

CREATE TABLE barbeiro (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                  TEXT    NOT NULL,
    telefone              TEXT,
    cpf_criptografado     TEXT    NOT NULL,  -- LGPD
    senha_criptografada   TEXT    NOT NULL,  -- LGPD
    ativo                 INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE cliente (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                  TEXT    NOT NULL,
    telefone              TEXT,
    email                 TEXT,
    cpf_criptografado     TEXT    NOT NULL   -- LGPD
);

CREATE TABLE servico (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL,
    preco         REAL    NOT NULL CHECK (preco >= 0),
    duracao_min   INTEGER NOT NULL CHECK (duracao_min > 0)
);

CREATE TABLE agendamento (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id    INTEGER NOT NULL REFERENCES cliente(id),
    barbeiro_id   INTEGER NOT NULL REFERENCES barbeiro(id),
    servico_id    INTEGER NOT NULL REFERENCES servico(id),
    data          TEXT    NOT NULL,           -- AAAA-MM-DD
    hora          TEXT    NOT NULL,           -- HH:MM
    status        TEXT    NOT NULL DEFAULT 'marcado',
    UNIQUE (barbeiro_id, data, hora)          -- um barbeiro, um horário
);

-- ---------------------------------------------------------------- massa de dados
"""


def gerar():
    linhas = [CABECALHO]

    linhas.append("-- usuários de login (senha com hash)")
    for id_, nome, login, senha in USUARIOS:
        h = generate_password_hash(senha)
        linhas.append(
            f"INSERT INTO usuario (id, nome, login, senha_hash) VALUES "
            f"({id_}, {sql_str(nome)}, {sql_str(login)}, {sql_str(h)});"
        )

    linhas.append("\n-- barbeiros (CPF e senha criptografados)")
    for id_, nome, tel, cpf, senha in BARBEIROS:
        linhas.append(
            f"INSERT INTO barbeiro (id, nome, telefone, cpf_criptografado, senha_criptografada) VALUES "
            f"({id_}, {sql_str(nome)}, {sql_str(tel)}, {sql_str(cifrar(cpf))}, {sql_str(cifrar(senha))});"
        )

    linhas.append("\n-- clientes (CPF criptografado)")
    for id_, nome, tel, cpf, email in CLIENTES:
        linhas.append(
            f"INSERT INTO cliente (id, nome, telefone, email, cpf_criptografado) VALUES "
            f"({id_}, {sql_str(nome)}, {sql_str(tel)}, {sql_str(email)}, {sql_str(cifrar(cpf))});"
        )

    linhas.append("\n-- serviços")
    for id_, nome, preco, dur in SERVICOS:
        linhas.append(
            f"INSERT INTO servico (id, nome, preco, duracao_min) VALUES "
            f"({id_}, {sql_str(nome)}, {preco:.2f}, {dur});"
        )

    linhas.append("\n-- agendamentos")
    for id_, cli, barb, serv, data, hora, status in AGENDAMENTOS:
        linhas.append(
            f"INSERT INTO agendamento (id, cliente_id, barbeiro_id, servico_id, data, hora, status) VALUES "
            f"({id_}, {cli}, {barb}, {serv}, {sql_str(data)}, {sql_str(hora)}, {sql_str(status)});"
        )

    destino = os.path.join(RAIZ, "saep_db.sql")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("gerado:", destino)


if __name__ == "__main__":
    gerar()
