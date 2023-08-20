import base64
import io

from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

app = FastAPI()


def sum_two_args(x, y):
    return x + y


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/process-image", response_class=HTMLResponse)
async def process_image(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.post("/process-image", response_class=HTMLResponse)
async def process_image(request: Request, image: UploadFile, direction: str = Form()):

    content = await image.read()

    user_image = Image.open(io.BytesIO(content))

    if direction == "horizontal":
        width = user_image.width * 2
        height = user_image.height
        duplicate_x = user_image.width
        duplicate_y = 0
    else:
        width = user_image.width
        height = user_image.height * 2
        duplicate_x = 0
        duplicate_y = user_image.height

    result = Image.new('RGB', (width, height))

    result.paste(user_image, (0, 0))
    result.paste(user_image, (duplicate_x, duplicate_y))

    temp = io.BytesIO();

    result.save(temp, format="jpeg")

    image_src = base64.b64encode(temp.getvalue()).decode()

    return templates.TemplateResponse("main.html",
                                      {"request": request, "direction": direction, "filename": image.filename, "image_src": image_src})

