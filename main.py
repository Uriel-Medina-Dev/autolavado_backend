from fastapi import FastAPI
import config.db

# importar modelos para que se registren en metadata
import models.model_rols
import models.model_user
import models.model_service
import models.model_vehicle
import models.model_vehicles_services

from routes.routes_rol import rol
from routes.routes_services import router as services_router
from routes.routes_user import router as users_router
from routes.routes_vehicle import router as vehicles_router
from routes.routes_vehicles_services import router as vehicle_services_router

app = FastAPI(
    title="Sistema de control de autolavado",
    description="Sistema de creacion y almacenamiento de información y ventas en un autolavado"
)

# Crear todas las tablas registradas por los modelos
config.db.Base.metadata.create_all(bind=config.db.engine)

app.include_router(rol)
app.include_router(services_router)
app.include_router(users_router)
app.include_router(vehicles_router)
app.include_router(vehicle_services_router)