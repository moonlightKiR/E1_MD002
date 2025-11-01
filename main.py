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
USER_AMOUNT: int = 20  # Cantidad predeterminada de usuarios a descargar y analizar


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
    print("he hecho el fetch_users")
    return [User.model_validate(user) for user in users_json]


def count_users_by_nationality(users_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Cuenta cuántos usuarios hay de cada nacionalidad.
    """
    nationalities = [user["nat"] for user in users_data]
    return dict(Counter(nationalities))


def main(amount: int = USER_AMOUNT) -> None:
    """Descarga, limpia, guarda y analiza usuarios (Modo Consola)."""
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
    save_users_to_json(users_data_cleaned_and_unique)

    # --- 4. Análisis de Contraseñas (Actualizado para niveles) ---
    print("\n--- 4. Análisis de Contraseñas ---")
    users_to_analyze = [User.model_validate(u) for u in users_data_cleaned_and_unique]

    stats = analizar_contraseñas(users_to_analyze)

    total_inseguros = stats['total_inseguros']
    total_usuarios = stats['total_usuarios']

    print(f" Total_Usuarios analizados: {total_usuarios}")
    print(f" Total Contraseñas Inseguras (Nivel 0-2): {total_inseguros}\n")

    print("Distribución por Nivel de Seguridad:")
    # Ordenar los niveles de menor a mayor
    niveles_ordenados = sorted(stats['detalle_niveles'].items())
    for nivel, count in niveles_ordenados:
        print(f" - {nivel:<13}: {count} usuarios")

    print("\nTop 5 grupos con contraseñas INSEGURAS (Nivel 0, 1 o 2):")
    # El detalle ahora viene como (Nivel, Edad, Género, País)
    for (nivel, edad, genero, pais), count in stats["detalle_top_grupos"][:5]:
        print(f" - {count} usuarios | Nivel: {nivel}, {genero.capitalize()} de {pais}, edad {edad}")


# ==== FLASK (Web App Logic) ====

app = Flask(__name__)


@app.route('/')
def show_stats():
    """Muestra estadísticas generales de usuarios y validación de contraseñas (Modo Web)."""
    users_data = load_users_from_json()

    if not users_data:
        return "No se encontraron datos de usuarios. Ejecute 'python main.py' primero.", 200, {
            'Content-Type': 'text/plain; charset=utf-8'}

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

    # 2. Análisis de contraseñas (Nuevos Resultados)
    users = [User.model_validate(u) for u in users_data]
    stats = analizar_contraseñas(users)

    total_inseguros = stats['total_inseguros']
    total_usuarios = stats['total_usuarios']

    result += "\n\n==========================================\n"
    result += "VALIDACIÓN DE CONTRASEÑAS POR NIVEL\n"
    result += "==========================================\n"
    result += f"Total de usuarios analizados: {total_usuarios}\n"
    result += f"Total Contraseñas Inseguras (Nivel 0-2): {total_inseguros}\n\n"

    result += "Distribución por Nivel de Seguridad:\n"
    # Ordenar los niveles de menor a mayor
    niveles_ordenados = sorted(stats['detalle_niveles'].items())
    for nivel, count in niveles_ordenados:
        result += f" - {nivel:<13}: {count} usuarios\n"

    result += "\nTop 5 grupos con contraseñas INSEGURAS:\n"
    # El detalle ahora viene como (Nivel, Edad, Género, País)
    for (nivel, edad, genero, pais), count in stats["detalle_top_grupos"][:5]:
        result += f" - {count} usuarios | Nivel: {nivel}, {genero.capitalize()} de {pais}, edad {edad}\n"

    # 3. Retornar texto consolidado
    return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def start_web_app():
    """Inicia la aplicación web."""
    print("\nIniciando aplicación web...")
    print("Abre tu navegador y ve a: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":

    # ⬅️ Bloque de ejecución original restaurado
    main(amount=USER_AMOUNT)
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        start_web_app()
