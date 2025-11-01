# main.py

import requests
from typing import List, Dict, Any
from flask import Flask
from collections import Counter
import sys

# Importamos las dependencias
from models import User
from data_cleaner import clean_and_deduplicate_users
from password_analyzer import analizar_contraseñas

# Importamos las funciones JSON
from file_handler import load_users_from_json, save_users_to_json

# =================================================================
# CONSTANTE GLOBAL DE CONFIGURACIÓN
# Modifica este valor para cambiar la cantidad de usuarios descargados
# =================================================================
USER_AMOUNT: int = 2000  # Cantidad predeterminada de usuarios a descargar y analizar
# =================================================================


# ==== FUNCIONES ETL ====
def fetch_users(amount: int) -> List[User]:
    """
    Obtiene una lista de usuarios desde la API randomuser.me.
    """
    params: Dict[str, Any] = {"results": amount}

    response = requests.get("https://randomuser.me/api/", params=params)
    response.raise_for_status()

    data: Dict[str, Any] = response.json()
    users_json: List[Dict[str, Any]] = data["results"]

    return [User.model_validate(user) for user in users_json]


# Nota: La función load_users_from_json se ha movido a file_handler.py


def count_users_by_nationality(users_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Cuenta cuántos usuarios hay de cada nacionalidad.
    """
    nationalities = [user["nat"] for user in users_data]
    return dict(Counter(nationalities))


def main(amount: int = USER_AMOUNT) -> None:
    """Descarga, limpia, guarda y analiza usuarios."""
    print("--- 1. Obtención de Datos ---")

    users_original: List[User] = fetch_users(amount=amount)
    total_original = len(users_original)
    print(f"Descargando {amount} usuarios...")

    # --- 2. Limpieza y Deduplicación (Lógica en data_cleaner.py) ---
    print("\n--- 2. Limpieza de Datos ---")
    users_data_cleaned_and_unique = clean_and_deduplicate_users(users_original)

    total_unique = len(users_data_cleaned_and_unique)
    eliminados = total_original - total_unique

    print(f" - Total registros originales: {total_original}")
    print(f" - Registros eliminados (nulos/duplicados): {eliminados}")
    print(f" - Registros finales (limpios y únicos): {total_unique}\n")

    # --- 3. Guardado en JSON (Usando file_handler.py) ---
    save_users_to_json(users_data_cleaned_and_unique)  # 💥 Aquí usamos la nueva función

    # --- 4. Análisis de Contraseñas ---
    print("\n--- 4. Análisis de Contraseñas ---")
    users_to_analyze = [User.model_validate(u) for u in users_data_cleaned_and_unique]

    stats = analizar_contraseñas(users_to_analyze)

    print(f" Total_Usuarios analizados: {stats['total_usuarios']}")
    print(f" Num_Contraseñas_Inválidas: {stats['total_invalidos']}\n")
    print("Grupos más frecuentes con contraseñas inválidas:")
    for (edad, genero, pais), count in stats["detalle"][:5]:
        print(f" - {count} usuarios | {genero.capitalize()} de {pais}, edad {edad}")


# ==== FLASK ====

app = Flask(__name__)
@app.route('/')
def show_stats():
    """Muestra estadísticas generales de usuarios y validación de contraseñas."""
    # 💥 Aquí usamos la nueva función de carga
    users_data = load_users_from_json()

    if not users_data:
        return "No se encontraron datos de usuarios.", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    total_users = len(users_data)
    result = "==========================================\n"
    result += "ESTADÍSTICAS GENERALES DE USUARIOS\n"
    result += "==========================================\n"
    result += f"Total de usuarios únicos: {total_users}\n\n"

    # 1. Estadísticas por país
    nationalities_data = count_users_by_nationality(users_data)
    result += "Usuarios por nacionalidad:\n"
    for nationality, count in sorted(nationalities_data.items(), key=lambda x: x[1], reverse=True):
        result += f" - {nationality}: {count} usuarios\n"

    # 2. Análisis de contraseñas
    users = [User.model_validate(u) for u in users_data]
    stats = analizar_contraseñas(users)

    result += "\n\n==========================================\n"
    result += "VALIDACIÓN DE CONTRASEÑAS\n"
    result += "==========================================\n"
    result += f"Total de usuarios analizados: {stats['total_usuarios']}\n"
    result += f"Contraseñas inválidas: {stats['total_invalidos']}\n\n"
    result += "Top 5 grupos con contraseñas inválidas:\n"

    for (edad, genero, pais), count in stats["detalle"][:5]:
        result += f" - {count} usuarios | {genero.capitalize()} de {pais}, edad {edad}\n"

    # 3. Retornar texto consolidado
    return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def start_web_app():
    """Inicia la aplicación web."""
    print("\nIniciando aplicación web...")
    print("Abre tu navegador y ve a: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":

    main(amount=USER_AMOUNT)
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        start_web_app()