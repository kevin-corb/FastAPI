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

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool =  True
# #     rating: Optional[int] = None
# #     id: int = randrange(1,999)


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


@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}

@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s)  RETURNING * """, 
    #                 (post.title, post.content, post.published,))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post= models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # new_post = cursor.fetchone()
    #new_post = find_posts(id)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404,
                            detail=f"post with id {id} was not found.")
        # reponse.status_code=status.HTTP_404_NOT_FOUND
        # return {"message":f"post with id {id} was not found."}
    #new_post = {k:v for (k,v) in enumerate(my_posts).items() if v==id}
    #print(id)
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db)):
    # #index = find_index_posts(id)
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(id,))
    # index = cursor.fetchone()
    # if index == None:
    #     raise HTTPException(status_code=404,
    #                         detail=f"post with id {id} was not found.")
    # #my_posts.pop(index)
    # conn.commit()
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found.")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
def update_post(id : int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    #                 (post.title, post.content, post.published, id,))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with id {id} was not found.")
    
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    # post_dict=post.dict()
    # post_dict['id'] = id
    # my_posts[index]=post_dict
    return post_query.first()
    #Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserReturn)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pw = utils.hash(user.password)
    user.password = hashed_pw
    new_user= models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserReturn)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=404,
                            detail=f"User with id {id} was not found.")
    return user