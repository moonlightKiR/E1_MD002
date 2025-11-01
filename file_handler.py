import json
from typing import List, Dict, Any

def load_users_from_json(filename: str = "~/users.json") -> List[Dict[str, Any]]:
    """
    Carga usuarios desde un archivo JSON.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        return []

def save_users_to_json(users_data: List[Dict[str, Any]], filename: str = "~/users.json") -> None:
    """
    Guarda una lista de diccionarios de usuarios en un archivo JSON.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=2)
        print(f"Datos guardados en '{filename}' ({len(users_data)} registros).")
    except Exception as e:
        print(f"Error al guardar datos en {filename}: {e}")