-- =====================================================================
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

-- usuários de login (senha com hash)
INSERT INTO usuario (id, nome, login, senha_hash) VALUES (1, 'Ana Souza', 'ana', 'scrypt:32768:8:1$F4uP6MlQvWEMf1dC$e9c439e1cf4a0346ddbc8945e77dff8805d290e14df2b7072e2964179c0aa5ae4d00d986b84f3b6b66cd6fa92fca668c90926ef89a98127f7f7d776630c66481');
INSERT INTO usuario (id, nome, login, senha_hash) VALUES (2, 'Carlos Lima', 'carlos', 'scrypt:32768:8:1$SAEjffZTjvF5zzjr$9a4f1fbe12d788bf685dc3fecacb2fe2ca96e73517630cbee8e8fe547edc80ecc0474a737278f43ba7a3e655938c8c200881ef30d9d1c4b3c84eac2955298cdf');
INSERT INTO usuario (id, nome, login, senha_hash) VALUES (3, 'Juliana Melo', 'juliana', 'scrypt:32768:8:1$HwjZfgzeW8rwULXn$03cf3cf642d876947de4992103797899d35abe2db27978e16f1eaaa5785ca1a9b1f05abf004fdd890d5bb41c1ce7785795ce733455457900428e98c992ac1ec0');

-- barbeiros (CPF e senha criptografados)
INSERT INTO barbeiro (id, nome, telefone, cpf_criptografado, senha_criptografada) VALUES (1, 'Rafael Costa', '(11) 98888-1111', 'gAAAAABq8cEXNbgSY98pQV_dqH5-L6aUdTTzPad8dSa3eoyJiios6pcDdXpVIjQnwpvZJDyaSw9w-Z6HHjH4f5uomio0ReLq4A==', 'gAAAAABq8cEXin_D4Pj_9_rnLCvzjA7fiQY1hlMrZ7pUn8YfATrRpDHihiA544YJZUeh4Aww0KTII2qpp235VXepSCMJFrF9Wg==');
INSERT INTO barbeiro (id, nome, telefone, cpf_criptografado, senha_criptografada) VALUES (2, 'Bruno Alves', '(11) 98888-2222', 'gAAAAABq8cEXVdaTYF_HPvVtF-VzOhtu1g1NM66eags7pUA6aotg0T_FJdUBBDDal3BEjieVUpo7K9Pfyfe0an2jzxdQmQCA_Q==', 'gAAAAABq8cEXd8HNUls0TGoNBNYqWs0HrxAODa3R8p6QZRUjnmcyWfZISBovTRasTP8XdBvcFwc35-Hfq1gL04s069bKSZcULg==');
INSERT INTO barbeiro (id, nome, telefone, cpf_criptografado, senha_criptografada) VALUES (3, 'Diego Nunes', '(11) 98888-3333', 'gAAAAABq8cEXFYtK6omQRVFdxtfZhRS3Fx6-A7K-AauHkDBpDZhD31sE36um2SVASchKsPXLV1Pe7oA3wep9Bt7bOKxU5TUaYQ==', 'gAAAAABq8cEX2sVUGB9WwMaB7Bhi_2fjKz-P-_D_-8puR0BQPcBTG36dVEzHpdvMb68Q2M8T_Q8nXQIZCInigblvvdnN-CoHcw==');

-- clientes (CPF criptografado)
INSERT INTO cliente (id, nome, telefone, email, cpf_criptografado) VALUES (1, 'Marcos Pereira', '(11) 97777-1111', 'marcos@email.com', 'gAAAAABq8cEXdEkYjAnv2QNsWCkxJNpuUXxrQG_g3wvCTVsCtO__kRTZY3vRP5S5b_H68n7RMRaqftJXpds8PMfFPo9pZ12O7w==');
INSERT INTO cliente (id, nome, telefone, email, cpf_criptografado) VALUES (2, 'Lucas Ferreira', '(11) 97777-2222', 'lucas@email.com', 'gAAAAABq8cEXXpcPjo4WuH1BYjtE9Datlb0CQMORi9bHMzZ1MZCWUTHKiUNIDzZtanXVPsz9BbpqUnABVYmkPWCpArvOpXZHAA==');
INSERT INTO cliente (id, nome, telefone, email, cpf_criptografado) VALUES (3, 'Pedro Oliveira', '(11) 97777-3333', NULL, 'gAAAAABq8cEXIFmhdzdHJ1pEIN6h6nRNJOoru9wqsTX5iSNrDjugLTQ_x9sVwo_SZwCTk1tGcjRQfZTYXzF1AH57wMJOq_OzRQ==');

-- serviços
INSERT INTO servico (id, nome, preco, duracao_min) VALUES (1, 'Corte masculino', 45.00, 30);
INSERT INTO servico (id, nome, preco, duracao_min) VALUES (2, 'Barba completa', 35.00, 20);
INSERT INTO servico (id, nome, preco, duracao_min) VALUES (3, 'Corte + barba', 70.00, 50);

-- agendamentos
INSERT INTO agendamento (id, cliente_id, barbeiro_id, servico_id, data, hora, status) VALUES (1, 1, 1, 3, '2026-11-10', '09:00', 'marcado');
INSERT INTO agendamento (id, cliente_id, barbeiro_id, servico_id, data, hora, status) VALUES (2, 2, 2, 1, '2026-11-10', '10:00', 'marcado');
INSERT INTO agendamento (id, cliente_id, barbeiro_id, servico_id, data, hora, status) VALUES (3, 3, 3, 2, '2026-11-11', '14:30', 'marcado');
