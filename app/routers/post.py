from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s)  RETURNING * """, 
    #                 (post.title, post.content, post.published,))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post= models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # new_post = cursor.fetchone()
    #new_post = find_posts(id)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404,detail=f"post with id {id} was not found.")
        # reponse.status_code=status.HTTP_404_NOT_FOUND
        # return {"message":f"post with id {id} was not found."}
    #new_post = {k:v for (k,v) in enumerate(my_posts).items() if v==id}
    #print(id)
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
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


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
def update_post(id : int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
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
