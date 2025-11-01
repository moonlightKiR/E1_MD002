from typing import Optional, Union
from pydantic import BaseModel

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