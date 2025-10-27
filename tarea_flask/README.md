# Tarea Flask 

## Endpoints

`GET /juguetes`
- Se puede filtrar con:
  - `?categoria=Carros`
  - `?marca=LEGO`

## Obtener un juguete por ID
`GET /juguetes/2`

## Agregar un juguete
`POST /juguetes`
## Ejemplo JSON:
```json
{
  "nombre": "Balón de Baloncesto",
  "categoria": "Deportes",
  "precio": 120.000,
  "marca": "Wilson"
} 