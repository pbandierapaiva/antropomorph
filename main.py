from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
        return {"Hello": "World"}


@app.get("/antro")
def read_root():
        return {"ANTRO": "World"}
