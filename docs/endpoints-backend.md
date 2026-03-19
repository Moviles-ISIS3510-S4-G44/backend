# Endpoints del Backend (API actual)

Este documento resume los endpoints HTTP expuestos actualmente por el backend y su propósito funcional.

## Base de la API

- URL base local (ejemplo): `http://localhost:8000`

---

## Salud del servicio

### `GET /health`

Verifica si el servicio está en ejecución.

- **Qué hace:** retorna el estado general del backend.
- **Respuesta esperada (200):**

```json
{
  "status": "healthy",
  "service": "backend"
}
```

---

## Usuarios

### `GET /users/profile/{user_id}`

Obtiene el perfil público de un usuario por su identificador.

- **Qué hace:** consulta la información de perfil del usuario.
- **Parámetros de ruta:**
  - `user_id` (int): id del usuario.
- **Respuestas comunes:**
  - `200`: perfil encontrado.
  - `404`: usuario no encontrado.

---

## Categorías

### `POST /categories`

Crea una nueva categoría.

- **Qué hace:** registra una categoría para clasificar publicaciones.
- **Body esperado:** datos de creación de categoría (`CategoryCreateRequest`).
- **Respuestas comunes:**
  - `200`: categoría creada.

### `GET /categories`

Lista todas las categorías existentes.

- **Qué hace:** retorna el catálogo de categorías disponibles.
- **Respuestas comunes:**
  - `200`: lista de categorías.

### `GET /categories/{category_id}`

Obtiene una categoría por su identificador.

- **Qué hace:** retorna los datos de una categoría específica.
- **Parámetros de ruta:**
  - `category_id` (int): id de la categoría.
- **Respuestas comunes:**
  - `200`: categoría encontrada.
  - `404`: categoría no encontrada.

---

## Publicaciones (Listings)

### `POST /listings`

Crea una nueva publicación en el marketplace.

- **Qué hace:** crea un listing asociado a un vendedor y a una categoría.
- **Body esperado:** datos de creación de publicación (`ListingCreateRequest`).
- **Validaciones asociadas:**
  - el vendedor (`seller_id`) debe existir.
  - la categoría (`category_id`) debe existir.
- **Respuestas comunes:**
  - `200`: publicación creada.
  - `404`: vendedor no encontrado o categoría no encontrada.

### `GET /listings`

Lista todas las publicaciones.

- **Qué hace:** retorna las publicaciones disponibles.
- **Respuestas comunes:**
  - `200`: lista de publicaciones.

### `GET /listings/{listing_id}`

Obtiene una publicación por su identificador.

- **Qué hace:** retorna el detalle de una publicación específica.
- **Parámetros de ruta:**
  - `listing_id` (int): id de la publicación.
- **Respuestas comunes:**
  - `200`: publicación encontrada.
  - `404`: publicación no encontrada.

---

## Endpoints automáticos de FastAPI

Además de los endpoints funcionales anteriores, FastAPI expone por defecto:

- `GET /docs`: documentación Swagger UI.
- `GET /redoc`: documentación ReDoc.
- `GET /openapi.json`: especificación OpenAPI en JSON.
