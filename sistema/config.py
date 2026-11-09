"""Configurações do sistema. Mexeu aqui, mexeu no dono da barbearia (ou só no seu sono)."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# chave de criptografia DEMO. Em produção isso vai pra variável de ambiente,
# nunca fica no código. Mas é simulado, então deixa quieto mesmo.
CHAVE_DEMO = "uqto25BdOKQRNS9hSQ4EnN_K3RLYmLGKrtvIoCCbf08="


class Config:
    SECRET_KEY = os.environ.get("SAEP_SECRET", "troca-isso-depois-por-favor")
    CHAVE_CRIPTO = os.environ.get("SAEP_CHAVE", CHAVE_DEMO)
    DB_PATH = os.environ.get("SAEP_DB", os.path.join(BASE_DIR, "..", "saep.db"))
    # sessão expira em 30 min de inatividade (o gestor pediu, então toma)
    SESSION_MINUTOS = 30
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
