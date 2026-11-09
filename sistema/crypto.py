"""Criptografia dos dados sensíveis (CPF e senha de barbeiro) — LGPD e essas coisas.

Usa Fernet (cryptography). Ele é simétrico, então dá pra descriptografar.
Pra senha de login de usuário a gente usa hash (werkzeug), que é de mão única.
Ou seja: não tem como 'desfazer' a senha. Só comparar.
"""
from cryptography.fernet import Fernet

from config import Config


def _fernet():
    # cria o objeto toda vez, custa quase nada e eu não tô a fim de cache agora
    return Fernet(Config.CHAVE_CRIPTO.encode())


def cifrar(texto: str) -> str:
    return _fernet().encrypt(texto.encode("utf-8")).decode("ascii")


def decifrar(token: str) -> str:
    return _fernet().decrypt(token.encode("ascii")).decode("utf-8")


def mascarar_cpf(cpf: str) -> str:
    # mostra só o miolo, porque ninguém precisa ver o CPF inteiro na tela da recepção
    if len(cpf) != 11:
        return "CPF inválido guardado aqui, alguém mexeu errado"
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"
