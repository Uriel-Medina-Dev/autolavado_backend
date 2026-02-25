from fastapi import HTTPException, Request, status, Depends
from core.security import verify_token  # La función que decodifica el token y lo valida

def verify_token_header(request: Request):
    authorization: str = request.headers.get("Authorization")
    
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    token_type, token = authorization.split()

    if token_type.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    return payload