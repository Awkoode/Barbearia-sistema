# SAEP Barbearia — Documentação de software (Anexo 1)

Documento escrito já meio sem energia, mas com todas as informações que o enunciado pede.

## 1. Visão geral

Sistema web para gestão de atendimentos de uma rede de barbearias: cadastro de clientes, barbeiros e serviços, e agendamento de horários com barbeiro responsável. Os dados sensíveis (CPF e senha de barbeiro) ficam criptografados no banco, e o login expira após 30 minutos de inatividade.

## 2. Tecnologias

| Camada     | Tecnologia                                    |
|------------|-----------------------------------------------|
| Backend    | Python 3 + Flask 3.1                          |
| Banco      | SQLite (script `saep_db.sql`)                 |
| Criptografia dos dados | `cryptography` (Fernet)           |
| Senha de login | hash com `werkzeug.security` (PBKDF2)     |
| Frontend   | HTML + CSS renderizados pelo Jinja2 (sem JS)  |

## 3. Requisitos funcionais

| ID    | Requisito                                                                                   |
|-------|---------------------------------------------------------------------------------------------|
| RF01  | Login com usuário e senha; mensagem de erro quando usuário ou senha forem inválidos          |
| RF02  | Sessão com expiração de 30 minutos de inatividade                                           |
| RF03  | Painel principal com nome do usuário logado, navegação e botão de logout                    |
| RF04  | Cadastro de clientes (nome, telefone, CPF, e-mail opcional)                                 |
| RF05  | Busca de clientes por nome; a listagem é atualizada mostrando só os correspondentes         |
| RF06  | Cadastro de barbeiros (nome, telefone, CPF, senha)                                          |
| RF07  | Cadastro de serviços/cortes (nome, preço, duração)                                          |
| RF08  | Agendamento obrigatoriamente vinculado a um cliente, um serviço e um barbeiro cadastrado   |
| RF09  | Não permitir dois agendamentos para o mesmo barbeiro no mesmo dia e horário                 |
| RF10  | Listagem de agendamentos ordenada por data e hora, com cliente, serviço e barbeiro          |

## 4. Requisitos não funcionais e regras de negócio

- **RNF01 — Segurança:** CPF e senha de barbeiro cifrados com Fernet antes de ir para o banco. Senha de usuário de login guardada apenas como hash (não reversível).
- **RNF02 — LGPD:** na tela, o CPF aparece mascarado (`***.456.789-**`).
- **RNF03 — Integridade:** chaves primárias e estrangeiras definidas no script; `UNIQUE (barbeiro_id, data, hora)` impede choque de horário também no banco.
- **RNF04 — Massa de dados:** todas as cinco tabelas têm ao menos três registros no script.

## 5. Modelo de dados

O diagrama Entidade-Relacionamento está em `docs/der.png` (fonte em `docs/der.mmd`).

Tabelas: `usuario`, `barbeiro`, `cliente`, `servico`, `agendamento`.

## 6. Como rodar

```bash
# 1) dependências
pip install -r sistema/requirements.txt

# 2) banco (cria as tabelas e popula)
sqlite3 saep.db < saep_db.sql
#   sem sqlite3 no sistema? então:
python -c "import sqlite3; c=sqlite3.connect('saep.db'); c.executescript(open('saep_db.sql',encoding='utf-8').read()); c.commit()"

# 3) servidor
cd sistema
python app.py
# abre http://127.0.0.1:5000
```

Logins de teste: `ana / ana123`, `carlos / carlos123`, `juliana / juliana123`.

Variáveis de ambiente opcionais: `SAEP_SECRET` (chave da sessão), `SAEP_CHAVE` (chave Fernet), `SAEP_DB` (caminho do banco).

## 7. Observações

- A chave Fernet que está no `config.py` é **demo**. Em produção ela sai do código e vai para variável de ambiente, e não pode ser perdida (senão os CPFs cadastrados viram lixo).
- O script `saep_db.sql` foi gerado por `scripts/gerar_seed.py`, que reaproveita o mesmo código de criptografia do sistema.
