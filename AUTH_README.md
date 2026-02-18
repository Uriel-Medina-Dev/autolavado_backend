# Sistema de Autenticación - Autolavado Backend

## Descripción

Se ha implementado un sistema de autenticación JWT (JSON Web Tokens) que protege las rutas de tu API FastAPI.

## Rutas Públicas (sin protección)

Las siguientes rutas NO requieren token de autenticación:

- `POST /auth/login` - Login de usuario
- `GET /rol/` - Ver todos los roles
- `POST /users/` - Crear nuevo usuario

## Rutas Protegidas (requieren token)

Todas las demás rutas requieren un token JWT válido:

- **Users**: `GET /users/`, `GET /users/{id}`, `PUT /users/{id}`, `DELETE /users/{id}`
- **Vehicles**: `GET /vehicles/`, `GET /vehicles/{id}`, `POST /vehicles/`, `PUT /vehicles/{id}`, `DELETE /vehicles/{id}`
- **Services**: `GET /services/`, `GET /services/{id}`, `POST /services/`, `PUT /services/{id}`, `DELETE /services/{id}`
- **Vehicle Services**: `GET /vehicle_services/`, `GET /vehicle_services/{id}`, `POST /vehicle_services/`, `PUT /vehicle_services/{id}`, `DELETE /vehicle_services/{id}`
- **Auth**: `GET /auth/me` - Obtener datos del usuario actual

## Cómo usar

### 1. Crear un usuario (público)

```bash
POST /users/
Content-Type: application/json

{
  "rol_Id": 1,
  "user_name": "Juan",
  "user_1lastname": "Pérez",
  "user_2lastname": "García",
  "user": "juan_perez",
  "user_password": "tu_contraseña_segura",
  "user_address": "Calle Principal 123",
  "user_phone": "1234567890",
  "status": true,
  "creation_date": "2024-02-18T00:00:00",
  "modification_date": "2024-02-18T00:00:00"
}
```

### 2. Hacer login (público)

```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

user=juan_perez&password=tu_contraseña_segura
```

O con JSON:

```bash
POST /auth/login
Content-Type: application/json

{
  "user": "juan_perez",
  "password": "tu_contraseña_segura"
}
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1
}
```

### 3. Usar el token en rutas protegidas

Incluye el token en el header `Authorization`:

```bash
GET /users/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Características de seguridad

- **Hash de contraseñas**: Las contraseñas se almacenan con hash bcrypt, nunca en texto plano
- **JWT Tokens**: Los tokens expiran después de 30 minutos
- **Bearer Authentication**: Usa el estándar HTTP Bearer para autenticación

## Configuración importante

### Cambiar la clave secreta (IMPORTANTE en producción)

En [core/security.py](core/security.py), actualiza la variable `SECRET_KEY`:

```python
SECRET_KEY = "tu-clave-secreta-muy-segura-cambiar-en-produccion"
```

**En producción, usa una clave segura y única.**

### Cambiar el tiempo de expiración del token

En [core/security.py](core/security.py), modifica `ACCESS_TOKEN_EXPIRE_MINUTES`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Cambiar a minutos deseados
```

## Validar token activo

```bash
GET /auth/me
Authorization: Bearer tu_token_aqui
```

**Respuesta:**

```json
{
  "id": 1,
  "username": "juan_perez",
  "name": "Juan",
  "email": "juan_perez",
  "rol_id": 1
}
```

## Error: Token inválido o expirado

Si recibes error 401 Unauthorized:

```json
{
  "detail": "Token inválido o expirado"
}
```

Necesitas:
1. Hacer login nuevamente para obtener un token válido
2. Verificar que incluyes el token completo en el header Authorization
3. Verificar que el token no haya expirado (30 minutos por defecto)

## Notas

- El formato correcto del header es: `Authorization: Bearer [token]`
- No olvides el espacio entre "Bearer" y el token
- Los tokens son sensibles a mayúsculas/minúsculas
- Las contraseñas se almacenan de forma segura con bcrypt
