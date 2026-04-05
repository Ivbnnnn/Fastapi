from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

app = FastAPI()
security = HTTPBasic()

LOGIN = "ivan"
PASSWORD = "ivan"

@app.get("/login")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if credentials.username == LOGIN and credentials.password == PASSWORD:
        return {"message": "You got my secret, welcome"}
    else:        
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": 'Basic realm="Login Required"'}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)