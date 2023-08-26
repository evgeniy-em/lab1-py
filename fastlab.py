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
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

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
    url = 'https://www.google.com/recaptcha/api/siteverify'
    private_recaptcha = '6Lf-fr4nAAAAANuXY_U4-JtYXtKZ3lXEYMdMqY88'
    params = urlencode({
        'secret': private_recaptcha,
        'response': token,
    })

    data = urlopen(url, params.encode('utf-8')).read()
    result = json.loads(data)
    # check google captcha
    success = result.get('success', None)

    if not success:
        return templates.TemplateResponse("main.html", {"request": request, "sitekey": sitekey, "error": "Captcha failed"})

    content = await image.read()

    user_image = Image.open(io.BytesIO(content))

    # calculate width and height of the result image
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

    # create result image
    result = Image.new('RGB', (width, height))

    # paste original image
    result.paste(user_image, (0, 0))
    # duplicate original image
    result.paste(user_image, (duplicate_x, duplicate_y))

    # create buffer for the result image
    result_buffer = io.BytesIO()

    # save the result image to the buffer
    result.save(result_buffer, format="jpeg")

    # resize images to simplify drawing color graphs
    user_image.thumbnail(size=(100, 100))
    result.thumbnail(size=(100, 100))

    # create figure for graphs
    figure = plt.figure(figsize=(15, 10))

    # draw graphs for the original image
    draw_graphs(user_image, figure, 1, "original image")

    # draw graphs for the result image
    draw_graphs(result, figure, 2, "result image")

    # create buffer for the image with graphs
    graphs_buffer = io.BytesIO()

    # save graphs to the buffer
    plt.savefig(graphs_buffer, format="jpg")

    # get source for the result image in base64
    image_src = base64.b64encode(result_buffer.getvalue()).decode()

    # get source for the image with graphs in base64
    graphs_src = base64.b64encode(graphs_buffer.getvalue()).decode()

    return templates.TemplateResponse("main.html",
                                      {"request": request, "direction": direction, "filename": image.filename, "image_src": image_src, "graphs_src": graphs_src, "sitekey": sitekey})


# Function for adding RGB graphs to figure
def draw_graphs(image: Image, figure: Figure, row: int, title: str):
    # total rows in the figure
    rows = 2
    # total columns in the figure
    columns = 3

    image_array = np.array(image)

    red, green, blue = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]

    # index of the first subplot in the row
    subplot_starting_index = (row - 1) * 3 + 1

    # add graph for red color
    red_subplot = figure.add_subplot(rows, columns, subplot_starting_index, title=f'red in the {title}', ylim=[0, 255])
    red_subplot.plot(red.flatten(), color="red")

    # add graph for green color
    green_subplot = figure.add_subplot(rows, columns, subplot_starting_index + 1, title=f'green in the {title}', ylim=[0, 255])
    green_subplot.plot(green.flatten(), color="green")

    # add graph for blue color
    blue_subplot = figure.add_subplot(rows, columns, subplot_starting_index + 2, title=f'blue in the {title}', ylim=[0, 255])
    blue_subplot.plot(blue.flatten(), color="blue")
