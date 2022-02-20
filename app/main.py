from sqlite3 import Cursor
from telnetlib import STATUS
from time import sleep
from typing import Optional, List
from urllib import response
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import timeit
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='password', cursor_factory=RealDictCursor)
        cursor= conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to teh database failed.")
        print(f"Error: {error}")
        sleep(2)

my_posts = [{"title":"title of first post", "content": "content of post 1", "id": 1}, {"title":"favourite foods", "content":"i like pizza!", "id":2}]

def find_posts(id):
    for post in my_posts:
        if post["id"]==id:
            return post


def find_index_posts(id):
    for i,post in enumerate(my_posts):
        if post["id"]==id:
            return i

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}