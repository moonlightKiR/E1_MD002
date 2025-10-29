import requests
import json
from typing import Optional, List, Dict, Any, Union
from flask import Flask
from collections import Counter
from pydantic import BaseModel


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
    # randomuser puede devolver postcode como int o str
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
    password: str
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


# ==== FUNCIÓN PRINCIPAL ====

def fetch_users(amount: int = 2000) -> List[User]:
    """
    Obtiene una lista de usuarios desde la API randomuser.me.

    Args:
        amount (int): Número de usuarios a solicitar (por defecto 2000).
        nationality (Optional[str]): Código de país (por ejemplo, "ES" o "US").

    Returns:
        List[User]: Lista de instancias de la clase User.
    """
    params: Dict[str, Any] = {"results": amount}

    response = requests.get("https://randomuser.me/api/", params=params)
    response.raise_for_status()  # lanza excepción si hay error HTTP

    data: Dict[str, Any] = response.json()
    users_json: List[Dict[str, Any]] = data["results"]

    return [User.model_validate(user) for user in users_json]


def load_users_from_json(filename: str = "users.json") -> List[Dict[str, Any]]:
    """
    Carga usuarios desde un archivo JSON.
    
    Args:
        filename (str): Nombre del archivo JSON.
        
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con datos de usuarios.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        return []


def count_users_by_nationality(users_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Cuenta cuántos usuarios hay de cada nacionalidad.
    
    Args:
        users_data (List[Dict[str, Any]]): Lista de datos de usuarios.
        
    Returns:
        Dict[str, int]: Diccionario con nacionalidad como clave y cantidad como valor.
    """
    nationalities = [user["nat"] for user in users_data]
    return dict(Counter(nationalities))


def main() -> None:
    """Obtiene usuarios y los guarda en un archivo JSON."""
    users: List[User] = fetch_users(amount=2000)
    
    # Convertir los objetos User a diccionarios para poder serializar a JSON
    users_data = [user.model_dump() for user in users]
    
    # Guardar en archivo JSON
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users_data, file, ensure_ascii=False, indent=2)
    
    print(f"Se han guardado {len(users)} usuarios en el archivo 'users.json'")


# ==== APLICACIÓN WEB ====

app = Flask(__name__)


@app.route('/')
def show_stats():
    """Muestra las estadísticas de usuarios por nacionalidad en texto plano."""
    users_data = load_users_from_json()
    
    if not users_data:
        return "No se encontraron datos de usuarios.", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    nationalities_data = count_users_by_nationality(users_data)
    total_users = len(users_data)
    
    # Ordenar nacionalidades por cantidad (mayor a menor)
    nationalities_data = dict(sorted(nationalities_data.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True))
    
    # Crear texto plano
    result = f"ESTADÍSTICAS DE USUARIOS POR NACIONALIDAD\n"
    result += f"==========================================\n\n"
    result += f"Total de usuarios: {total_users}\n\n"
    result += f"Distribución por nacionalidades:\n"
    result += f"--------------------------------\n"
    
    for nationality, count in nationalities_data.items():
        result += f"{nationality}: {count} usuarios\n"
    
    return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def start_web_app():
    """Inicia la aplicación web."""
    print("Iniciando aplicación web...")
    print("Abre tu navegador y ve a: http://localhost:8080")
    print("Presiona Ctrl+C para detener el servidor")
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    import sys
    main()
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        start_web_app()
