from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(prefix="/friend")


@router.post("/create_followerRequest")
def create_followerRequest(
    followRequest: FollowerRequest, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            "INSERT INTO followRequestTable(senderID, receiverID) values(%s,%s)",
            (followRequest.senderID, followRequest.receiverID),
        )
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="친구 요청에 실패했습니다."
        )


@router.get("/get_users_by_email")
def get_users_by_email(email: str, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(f"SELECT * FROM userTable WHERE email LIKE '%{email}%'")
        users = db.fetchall()
        db.commit()
        return [
            User(id=user[0], nickname=user[1], email=user[2], uid=user[3])
            for user in users
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일로 유저리스트 검색이 실패했습니다.",
        )


@router.get("/get_request_sender")
def get_request_sender(
    receiverID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            "SELECT * FROM followRequestTable WHERE receiverID = %s", (receiverID,)
        )

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
                    id=user_data[0][0],  # id
                    nickname=user_data[0][1],  # nickname
                    email=user_data[0][2],  # email
                    uid=user_data[0][3],  # uid
                )
                user_list.append(user_obj)

        return user_list
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="친구 요청에 실패했습니다."
        )


def createFriend(follower: Follower, db: MySQLConnection):

    try:
        db.execute(
            "insert into followerTable(followerID, followeeID) values(%s, %s)",
            (follower.followerID, follower.followeeID),
        )

        return {"result": "Success"}
    except Exception as e:

        raise e


def createReverseFriend(follower: Follower, db: MySQLConnection):
    try:
        db.execute(
            "insert into followerTable(followerID, followeeID) values(%s, %s)",
            (follower.followerID, follower.followeeID),
        )

        return {"result": "Success"}
    except Exception as e:
        raise e


def deleteFriendRequest(senderID: int, receiverID: int, db: MySQLConnection):
    try:
        db.execute(
            "DELETE FROM followRequestTable WHERE senderID = %s AND receiverID = %s",
            (senderID, receiverID),
        )

        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        raise e


@router.post("/create_friend_and_autoDelete")
def create_friend_and_autoDelete(
    follower: Follower, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        dbResponseCreate = createFriend(follower=follower, db=db)
        dbResponseCreateReverse = createReverseFriend(
            follower=Follower(
                followerID=follower.followeeID, followeeID=follower.followerID
            ),
            db=db,
        )
        dbResponseDelete = deleteFriendRequest(
            senderID=follower.followeeID, receiverID=follower.followerID, db=db
        )
        db.commit()
        return dbResponseDelete
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="친구 요청 삭제에 실패했습니다.",
        )


@router.delete("/delete_friend_request")
async def delete_friend_request(
    senderID: int, receiverID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        dbResponse = deleteFriendRequest(
            senderID=senderID, receiverID=receiverID, db=db
        )
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="친구 요청 삭제에 실패했습니다.",
        )
    return dbResponse
