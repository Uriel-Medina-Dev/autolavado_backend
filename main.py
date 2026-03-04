from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import config.db
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos para que se registren en metadata
import models.model_rols
import models.model_user
import models.model_service
import models.model_vehicle
import models.model_vehicles_services

# Importar routers
from routes.routes_auth import router as auth_router
from routes.routes_rol import rol
from routes.routes_services import router as services_router
from routes.routes_user import router as users_router
from routes.routes_vehicle import router as vehicles_router
from routes.routes_vehicles_services import router as vehicle_services_router

# Configuración
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000").split(",")

app = FastAPI(
    title="Sistema de control de autolavado",
    description="Sistema de creación y almacenamiento de información y ventas en un autolavado",
    version="1.0.0",
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# Configurar CORS - IMPORTANTE para Swagger
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Manejador de excepciones personalizado para mejor debugging
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "timestamp": str(datetime.now())
        },
    )

# Crear todas las tablas registradas por los modelos
try:
    print("📦 Creando/verificando tablas en la base de datos...")
    config.db.Base.metadata.create_all(bind=config.db.engine)
    print("✅ Tablas creadas/verificadas exitosamente")
except Exception as e:
    print(f"❌ Error creando tablas: {e}")
    print("⚠️ La aplicación continuará pero puede haber problemas con la BD")

# Incluir routers - El orden puede ser importante
app.include_router(auth_router)  # Primero autenticación
app.include_router(rol)          # Luego roles
app.include_router(users_router) # Usuarios
app.include_router(services_router)
app.include_router(vehicles_router)
app.include_router(vehicle_services_router)

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "API Autolavado",
        "version": "1.0.0",
        "environment": "development" if DEBUG else "production",
        "docs": "/docs" if DEBUG else "Documentación no disponible en producción",
        "endpoints": {
            "auth": "/auth (login, me)",
            "roles": "/rol (CRUD de roles)",
            "users": "/users (CRUD de usuarios)",
            "services": "/services (CRUD de servicios)",
            "vehicles": "/vehicles (CRUD de vehículos)",
            "vehicle_services": "/vehicle_services (asignaciones)"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor y la BD"""
    db_status = "disconnected"
    db_error = None
    
    try:
        # Verificar conexión a BD
        db = config.db.SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    
    return {
        "status": "healthy",
        "timestamp": str(datetime.now()),
        "database": {
            "status": db_status,
            "error": db_error
        },
        "debug_mode": DEBUG
    }

# Middleware opcional para logging de requests (útil para debugging)
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para loggear requests (solo en debug)"""
    if DEBUG:
        print(f"\n🔍 Request: {request.method} {request.url.path}")
        
        # Log headers (ocultando el token completo)
        auth_header = request.headers.get("authorization")
        if auth_header:
            masked = auth_header[:20] + "..." if len(auth_header) > 20 else auth_header
            print(f"   Auth: {masked}")
    
    response = await call_next(request)
    
    if DEBUG:
        print(f"✅ Response: {response.status_code}")
    
    return response

# Evento de startup
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("🚀 Iniciando API de Autolavado")
    print(f"📌 Modo: {'DESARROLLO' if DEBUG else 'PRODUCCIÓN'}")
    print(f"📌 Documentación: http://localhost:8000/docs")
    print("="*50 + "\n")

# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("\n" + "="*50)
    print("👋 Apagando API de Autolavado")
    print("="*50 + "\n")