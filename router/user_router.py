from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection


router = APIRouter(prefix="/user")


@router.post("/create_user")
def create_user(user: UserInput, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(
            "INSERT INTO userTable (nickname, email, uid) VALUES (%s,%s, %s)",
            (user.nickname, user.email, user.uid),
        )
        db.fetchall()
        db.commit()
        db.execute("SELECT * FROM userTable WHERE email = %s", (user.email,))
        new_user = db.fetchall()
        db.commit()
        return User(
            id=new_user[0][0],
            nickname=new_user[0][1],
            email=new_user[0][2],
            uid=new_user[0][3],
        )

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 생성에 실패했습니다.",
        )


@router.get("/get_user")
def get_user(id: int, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT * FROM userTable WHERE id = %s", (id,))
        user = db.fetchall()
        db.commit()
        return User(
            id=user[0][0],
            nickname=user[0][1],
            email=user[0][2],
            uid=user[0][3],
        )

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 사용자입니다.",
        )
    

@router.post("/update_user")
def update_user(id:str,nickname : str,db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(
            f"""
            UPDATE userTable
            SET 
            nickname = {nickname}
            
            WHERE ID = {id}
            """
        )
        db.fetchall()
        db.commit()
        db.execute("SELECT * FROM userTable WHERE ID = %s", (id))
        new_user = db.fetchall()
        db.commit()
        return User(
            id=new_user[0][0],
            nickname=new_user[0][1],
            email=new_user[0][2],
            uid=new_user[0][3],
        )

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 생성에 실패했습니다.",
        )
    



@router.get("/get_user_email")
def get_user_email(email: str, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT * FROM userTable WHERE email = %s", (email,))
        user = db.fetchall()
        db.commit()
        return User(
            id=user[0][0],
            nickname=user[0][1],
            email=user[0][2],
            uid=user[0][3],
        )

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 사용자입니다.",
        )


@router.delete("/delete_user")
def delete_user(userID: int, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(
            "DELETE FROM followRequestTable WHERE userID = $s",
            (userID),
        )
        db.fetchall()
        db.commit()
        return {"result": "Success"}

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 삭제에 실패했습니다.",
        )
