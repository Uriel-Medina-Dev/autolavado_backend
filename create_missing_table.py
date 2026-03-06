# crear archivo recreate_tables.py
from config.db import engine, Base
import models.model_vehicles_services  # Asegurar que se importe
import models.model_rols
import models.model_user
import models.model_service
import models.model_vehicle
import models.model_producto
import models.model_cajero

print("🗑️ Eliminando todas las tablas...")
Base.metadata.drop_all(bind=engine)
print("✅ Tablas eliminadas")

print("🏗️ Creando todas las tablas nuevamente...")
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas exitosamente")
print("\n📋 Tablas que deberían existir:")
print("   - tbc_rols")
print("   - tbb_user")
print("   - tbc_servicios")
print("   - tbb_vehicles")
print("   - tbd_vehicles_services  👈 ESTA ES LA QUE FALTABA")
print("   - tbc_productos")
print("   - tbb_cajeros")