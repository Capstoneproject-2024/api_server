from fastapi import APIRouter, HTTPException,Depends,status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection


router = APIRouter(
    prefix= "/book"
)

@router.get("/search_by_name")
def search_by_name(bookName:str = "", db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT ID, name, author, publisher, year, image, ISBN FROM bookTable WHERE name LIKE %s", ("%"+bookName+"%",))
        books = db.fetchall()
        db.commit()
        return[ BookWihtoutDesc(
            id=item[0],
            name=item[1],
            author=item[2],
            publisher=item[3],
            year=item[4],
            image=item[5],
            ISBN=item[6],
            )
            for item in books
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="도서 검색이 실패했습니다."
        )

@router.get("/search_by_id/{id}")
def search_book_by_id(id:int, db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT * FROM bookTable WHERE id = %s",(id,))
        book = db.fetchall()
        db.commit()
        return Book(
            id=book[0][0],
            name=book[0][1],
            author=book[0][2],
            publisher=book[0][3],
            year=book[0][4],
            desc=book[0][5],
            image=book[0][6],
            ISBN=book[0][7],
        )
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="도서가 존재하지 않습니다."
        )
    
