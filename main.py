from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import config.db
import os
from dotenv import load_dotenv

# Importar modelos (para que se creen las tablas)
import models.model_rols
import models.model_user
import models.model_service
import models.model_vehicle
import models.model_vehicles_services
import models.model_producto
import models.model_cajero  # 👈 NUEVO

# Importar routers
from routes.routes_auth import router as auth_router
from routes.routes_rol import rol
from routes.routes_services import router as services_router
from routes.routes_user import router as users_router
from routes.routes_vehicle import router as vehicles_router
from routes.routes_vehicles_services import router as vehicle_services_router
from routes.routes_productos import router as productos_router
from routes.routes_cajeros import router as cajeros_router  # 👈 NUEVO

# Configuración
load_dotenv()
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000").split(",")

app = FastAPI(
    title="Sistema de control de autolavado",
    description="Sistema de creación y almacenamiento de información y ventas en un autolavado",
    version="1.0.0",
    debug=DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas
try:
    print("📦 Creando/verificando tablas...")
    config.db.Base.metadata.create_all(bind=config.db.engine)
    print("✅ Tablas listas")
except Exception as e:
    print(f"❌ Error: {e}")

# Incluir routers
app.include_router(auth_router)
app.include_router(rol)
app.include_router(users_router)
app.include_router(services_router)
app.include_router(vehicles_router)
app.include_router(vehicle_services_router)
app.include_router(productos_router)
app.include_router(cajeros_router)  # 👈 NUEVO

@app.get("/")
async def root():
    return {
        "message": "API Autolavado",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "roles": "/rol",
            "users": "/users",
            "services": "/services",
            "vehicles": "/vehicles",
            "vehicle_services": "/vehicle_services",
            "productos": "/productos",
            "cajeros": "/cajeros"  # 👈 NUEVO
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(datetime.now())}