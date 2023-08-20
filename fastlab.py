import base64
import io
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import FastAPI, Form, Request, UploadFile, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

app = FastAPI()

sitekey = "6Lf-fr4nAAAAAD4ym_ggSgZC1GsAdxQs8l2-K1QP"


def sum_two_args(x, y):
    return x + y


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "sitekey": sitekey})


@app.post("/", response_class=HTMLResponse)
async def process_image(request: Request, image: UploadFile, direction: str = Form(), token: str = Body(alias="g-recaptcha-response", default="")):
    print(token)

    url = 'https://www.google.com/recaptcha/api/siteverify'
    private_recaptcha = '6Lf-fr4nAAAAANuXY_U4-JtYXtKZ3lXEYMdMqY88'
    params = urlencode({
        'secret': private_recaptcha,
        'response': token,
    })

    data = urlopen(url, params.encode('utf-8')).read()
    result = json.loads(data)
    success = result.get('success', None)

    if not success:
        return templates.TemplateResponse("main.html", {"request": request, "sitekey": sitekey, "error": "Captcha failed"})

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
                                      {"request": request, "direction": direction, "filename": image.filename, "image_src": image_src, "sitekey": sitekey})

