# password_analyzer.py

import re
from typing import List, Dict, Any, Union
from collections import Counter
# Importamos User y sus submodelos desde models.py
from models import User

# =============================================================
# CONSTANTES PARA CATEGORIZACIÓN
# =============================================================
NIVELES_SEGURIDAD = {
    "NIVEL_0_DEBIL": 0,  # Menos de 8 caracteres o 0-1 condiciones cumplidas
    "NIVEL_1_BAJO": 2,  # Al menos 2 condiciones cumplidas
    "NIVEL_2_MEDIO": 3,  # Al menos 3 condiciones cumplidas
    "NIVEL_3_SEGURO": 5  # Todas las 5 condiciones cumplidas (Longitud + 4 reglas)
}


# ==== VALIDACIÓN Y CATEGORIZACIÓN DE CONTRASEÑAS ====

def obtener_reglas_cumplidas(pwd: Union[str, int]) -> List[bool]:
    """Evalúa las reglas de seguridad y retorna una lista de True/False."""
    pwd_str = str(pwd)

    # Reglas a evaluar (5 en total)
    reglas = [
        len(pwd_str) >= 8,  # 1. Longitud mínima (8)
        bool(re.search(r'[A-Z]', pwd_str)),  # 2. Al menos una mayúscula (CORRECCIÓN: Conversión a bool)
        bool(re.search(r'[a-z]', pwd_str)),  # 3. Al menos una minúscula (CORRECCIÓN: Conversión a bool)
        bool(re.search(r'\d', pwd_str)),  # 4. Al menos un número (CORRECCIÓN: Conversión a bool)
        bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd_str))  # 5. Al menos un símbolo (CORRECCIÓN: Conversión a bool)
    ]
    return reglas


def validar_password(pwd: Union[str, int]) -> bool:
    """Valida una contraseña si CUMPLE TODAS las reglas (NIVEL_3_SEGURO)."""
    reglas_cumplidas = obtener_reglas_cumplidas(pwd)
    return all(reglas_cumplidas)


def categorizar_nivel_seguridad(pwd: Union[str, int]) -> str:
    """
    Asigna un nivel de seguridad basado en la cantidad de reglas cumplidas.
    """
    reglas_cumplidas = obtener_reglas_cumplidas(pwd)
    # ✅ FIX: sum() ahora funciona correctamente porque reglas_cumplidas solo contiene True/False
    conteo_reglas = sum(reglas_cumplidas)

    # Si no cumple la longitud mínima, se considera débil (NIVEL 0)
    if not reglas_cumplidas[0] or conteo_reglas < NIVELES_SEGURIDAD["NIVEL_1_BAJO"]:
        return "NIVEL 0: Débil"

    # Categorización basada en el número de reglas (contando la longitud)
    if conteo_reglas == NIVELES_SEGURIDAD["NIVEL_3_SEGURO"]:
        return "NIVEL 3: Seguro"
    elif conteo_reglas >= NIVELES_SEGURIDAD["NIVEL_2_MEDIO"]:
        return "NIVEL 2: Medio"
    elif conteo_reglas >= NIVELES_SEGURIDAD["NIVEL_1_BAJO"]:
        return "NIVEL 1: Bajo"

    return "NIVEL 0: Débil"


def analizar_contraseñas(users: List[User]) -> Dict[str, Any]:
    """
    Analiza las contraseñas de los usuarios y retorna estadísticas detalladas
    por nivel de seguridad, edad, género y país.
    """
    # Usaremos dos estructuras de conteo
    conteo_invalidos_detalle = {}  # Agrupación por (nivel, edad, género, país) para el top 5
    conteo_por_nivel = Counter()  # Conteo simple de usuarios por nivel de seguridad

    total_usuarios = len(users)

    for user in users:
        password = user.login.password
        nivel = categorizar_nivel_seguridad(password)

        # 1. Conteo por nivel (Todos los usuarios)
        conteo_por_nivel[nivel] += 1

        # 2. Conteo detallado solo para niveles 0, 1 y 2 (considerados "inseguros")
        if nivel != "NIVEL 3: Seguro":
            age = user.dob.age if user.dob.age is not None else 'N/A'
            country = user.location.country if user.location.country else 'N/A'

            # Agregamos el nivel de seguridad a la clave para el análisis detallado
            key = (nivel, age, user.gender, country)
            conteo_invalidos_detalle[key] = conteo_invalidos_detalle.get(key, 0) + 1

    total_inseguros = sum(conteo_por_nivel[nivel] for nivel in conteo_por_nivel if nivel != "NIVEL 3: Seguro")

    """Ordenar el detalle por cantidad descendente"""
    conteo_ordenado = sorted(conteo_invalidos_detalle.items(), key=lambda x: x[1], reverse=True)

    """Retorna los datos por si se quieren mostrar en Flask"""
    return {
        "total_inseguros": total_inseguros,
        "total_usuarios": total_usuarios,
        "detalle_niveles": dict(conteo_por_nivel),  # {NIVEL_3: count, NIVEL_1: count, ...}
        "detalle_top_grupos": conteo_ordenado
    }
