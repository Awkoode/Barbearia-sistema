# SAEP Barbearia

Sistema web de gestão e agendamento para barbearia. Login, painel, clientes com busca, barbeiros, serviços e agendamentos sem choque de horário.

Documentação completa em [`docs/documentacao.md`](docs/documentacao.md). DER em [`docs/der.png`](docs/der.png).

## Rodar rápido

```bash
pip install -r sistema/requirements.txt
sqlite3 saep.db < saep_db.sql
cd sistema && python app.py
```

Login de teste: `ana` / `ana123`.

## Estrutura

```
saep_db.sql          criação + população do banco
docs/                documentação e DER
sistema/             código-fonte (app.py, crypto.py, config.py, templates/, static/)
scripts/gerar_seed.py  gera o saep_db.sql com os dados já criptografados
```

Se você mexer nos dados de teste, rode `python scripts/gerar_seed.py` de novo e recrie o banco. Sim, é chato. Eu sei.
