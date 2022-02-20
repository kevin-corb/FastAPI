from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# SECRET_KEY - OPENSSL RAND -HEX 32
# Algorithm
# TTL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = '36e6e93d2b4599465047c4be25e261fa753735d8f9bcbb29fd3331b8e6e8b221'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) 

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,[ALGORITHM])
        id: str =payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could ot validate credentials.",
    headers={"WWW-Authenicate":"Bearer"})

    token = verify_access_token(token, credentials_exception)

    user =db.query(models.User).filter(models.User.id==token.id).first()

    return user
