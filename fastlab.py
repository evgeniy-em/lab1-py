from fastapi import FastAPI

app = FastAPI()


def sum_two_args(x, y):
    return x + y


@app.get("/")
def read_root():
    return {"Hello": "world"}
