import requests
import json
from typing import Optional, List, Dict, Any, Union
from flask import Flask
from collections import Counter
from pydantic import BaseModel
import re

# ==== MODELOS (Pydantic) ====

class Street(BaseModel):
    number: int
    name: str

class Coordinates(BaseModel):
    latitude: str
    longitude: str

class Timezone(BaseModel):
    offset: str
    description: str

class Location(BaseModel):
    street: Street
    city: str
    state: str
    country: str
    postcode: Union[int, str]
    coordinates: Coordinates
    timezone: Timezone

class Name(BaseModel):
    title: str
    first: str
    last: str

class Login(BaseModel):
    uuid: str
    username: str
    password: Union[int, str]
    salt: str
    md5: str
    sha1: str
    sha256: str

class DOB(BaseModel):
    date: str
    age: int

class Registered(BaseModel):
    date: str
    age: int

class ID(BaseModel):
    name: str
    value: Optional[str]

class Picture(BaseModel):
    large: str
    medium: str
    thumbnail: str

class User(BaseModel):
    gender: str
    name: Name
    location: Location
    email: str
    login: Login
    dob: DOB
    registered: Registered
    phone: str
    cell: str
    id: ID
    picture: Picture
    nat: str


# ==== VALIDACIÓN DE CONTRASEÑAS ====

def validar_password(pwd: str) -> bool:
    """Valida una contraseña según criterios de seguridad."""
    if not isinstance(pwd, str):
        return False
    reglas = [
        len(pwd) >= 8,                          # longitud mínima
        re.search(r'[A-Z]', pwd),               # al menos una mayúscula
        re.search(r'[a-z]', pwd),               # al menos una minúscula
        re.search(r'\d', pwd),                  # al menos un número
        re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd)  # al menos un símbolo
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

    print(f"\n Total_Usuarios: {total_usuarios}")
    print(f"\n Num_Contraseñas_Invalidad: {total_invalidos}\n")

   """Agrupar por edad, género y país"""
    conteo = {}
    for u in usuarios_invalidos:
        key = (u.dob.age, u.gender, u.location.country)
        conteo[key] = conteo.get(key, 0) + 1

    """Ordenar por cantidad descendente"""
    conteo_ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)

    print("Grupos más frecuentes con contraseñas inválidas:")
    for (edad, genero, pais), count in conteo_ordenado[:5]:
        print(f" - {count} usuarios | {genero.capitalize()} de {pais}, edad {edad}")

    """Retorna los datos por si se quieren mostrar en Flask"""
    return {
        "total_invalidos": total_invalidos,
        "total_usuarios": total_usuarios,
        "detalle": conteo_ordenado
    }

def fetch_users(amount: int = 2000) -> List[User]:
    """Obtiene usuarios desde la API randomuser.me"""
    params: Dict[str, Any] = {"results": amount}
    response = requests.get("https://randomuser.me/api/", params=params)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    return [User.model_validate(u) for u in data["results"]]


def load_users_from_json(filename: str = "users.json") -> List[Dict[str, Any]]:
    """Carga usuarios desde un archivo JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        return []


def count_users_by_nationality(users_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Cuenta cuántos usuarios hay de cada nacionalidad."""
    nationalities = [user["nat"] for user in users_data]
    return dict(Counter(nationalities))


def main() -> None:
    """Descarga, guarda usuarios y valida contraseñas."""
    users: List[User] = fetch_users(amount=200)
    users_data = [user.model_dump() for user in users]

    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users_data, file, ensure_ascii=False, indent=2)

    print(f"Se han guardado {len(users)} usuarios en 'users.json'")

    """Analizar contraseñas"""
    analizar_contraseñas(users)


# ==== FLASK ====

app = Flask(__name__)

@app.route('/')
def show_stats():
    """Muestra estadísticas generales de usuarios y validación de contraseñas."""
    users_data = load_users_from_json()
    if not users_data:
        return "No se encontraron datos de usuarios.", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # 1. Estadísticas por país
    nationalities_data = count_users_by_nationality(users_data)
    total_users = len(users_data)

    result = "==========================================\n"
    result += "ESTADÍSTICAS GENERALES DE USUARIOS\n"
    result += "==========================================\n"
    result += f"Total de usuarios: {total_users}\n\n"
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
    print("Iniciando aplicación web...")
    print("Abre tu navegador y ve a: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    import sys
    main()
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        start_web_app()
