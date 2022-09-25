# author:冯重阳
# @File：fastapi_part.py
from select import select

from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse
from news_xmly import *

app = FastAPI()
template = Jinja2Templates("../pages")
list_finish = ["Jan","Fcy"]
result_list = []
@app.get("/")
def user(req : Request):
    return template.TemplateResponse("index.html",context={"request":req,"name_list":list_finish,"result_list":result_list})

@app.post("/select")
def find(number=Form(None)):
    global result_list
    result_list = db_coporate.selectinfo(db_coporate,number)
    return RedirectResponse("/",status_code=302)

@app.post("/user")
def spider(number_tot=Form(None)):
    """爬取数据"""
    name_list = download_news(number_tot)
    global list_finish
    list_finish = name_list + list_finish
    return RedirectResponse("/", status_code=302)

