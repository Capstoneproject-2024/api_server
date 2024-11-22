from fastapi import APIRouter, HTTPException,Depends,status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(
    prefix= "/friend"
)

@router.post("/create_followerRequest")
def create_followerRequest(followRequest:FollowerRequest, db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("INSERT INTO followRequestTable(senderID, receiverID) values(%s,%s)", (followRequest.senderID,followRequest.receiverID))
        db.commit()
        return {"result":"Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="친구 요청에 실패했습니다."
        )


@router.get("/get_request_sender")
def get_request_sender(receiverID:int, db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT * FROM followRequestTable WHERE receiverID = %s", (receiverID,))
        
        users = db.fetchall()
        db.commit()
        user_list = []
        for user in users:
            user_id = user[0]  
            db.execute("SELECT * FROM userTable WHERE id = %s", (user_id,))
            
            user_data = db.fetchall()
            db.commit()

            if user_data:
                user_obj = User(
                    id=user_data[0][0],        # id
                    nickname=user_data[0][1],  # nickname
                    email=user_data[0][2],     # email
                    uid=user_data[0][3]        # uid
                )
                user_list.append(user_obj)


        return user_list
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="친구 요청에 실패했습니다."
        )