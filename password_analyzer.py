import re
from typing import List, Dict, Any, Union
from collections import Counter
# Importamos User y sus submodelos desde models.py
from models import User


# ==== VALIDACIÓN DE CONTRASEÑAS ====

def validar_password(pwd: Union[str, int]) -> bool:
    """Valida una contraseña según criterios de seguridad."""
    # Convertir a string para la validación
    pwd_str = str(pwd)

    reglas = [
        len(pwd_str) >= 8,  # longitud mínima
        re.search(r'[A-Z]', pwd_str),  # al menos una mayúscula
        re.search(r'[a-z]', pwd_str),  # al menos una minúscula
        re.search(r'\d', pwd_str),  # al menos un número
        re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd_str)  # al menos un símbolo
    ]
    return all(reglas)


def analizar_contraseñas(users: List[User]) -> Dict[str, Any]:
    """
    Analiza las contraseñas de los usuarios.
    Retorna estadísticas por edad, género y país.
    """
    usuarios_invalidos = []

    for user in users:
        if not validar_password(user.login.password):
            usuarios_invalidos.append(user)

    total_invalidos = len(usuarios_invalidos)
    total_usuarios = len(users)

    """Agrupar por edad, género y país"""
    conteo = {}
    for u in usuarios_invalidos:
        age = u.dob.age if u.dob.age is not None else 'N/A'
        country = u.location.country if u.location.country else 'N/A'

        key = (age, u.gender, country)
        conteo[key] = conteo.get(key, 0) + 1

    """Ordenar por cantidad descendente"""
    conteo_ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)

    """Retorna los datos por si se quieren mostrar en Flask"""
    return {
        "total_invalidos": total_invalidos,
        "total_usuarios": total_usuarios,
        "detalle": conteo_ordenado
    }