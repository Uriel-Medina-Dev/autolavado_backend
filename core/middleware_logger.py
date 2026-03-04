from fastapi import Request
import time

async def log_requests(request: Request, call_next):
    """Middleware para loggear requests y headers"""
    
    print(f"\n🔍 Request: {request.method} {request.url.path}")
    print("Headers:")
    for name, value in request.headers.items():
        if name.lower() == "authorization":
            # Mostrar solo parte del token por seguridad
            value_preview = value[:20] + "..." if len(value) > 20 else value
            print(f"  {name}: {value_preview}")
        else:
            print(f"  {name}: {value}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"✅ Response status: {response.status_code} (took {process_time:.3f}s)")
    return response