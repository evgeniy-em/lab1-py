from fastapi import FastAPI
import uvicorn

app = FastAPI()


def sum_two_args(x, y):
    return x + y


@app.get("/")
def read_root():
    return {"Hello": "world"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
