from fastapi import APIRouter, HTTPException,Depends,status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(
    prefix= "/group"
)

@router.post("/create_group/{adminID}/{groupName}/{groupDescription}")
def create_group(adminID: int, groupName: str, groupDescription: str, db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("INSERT INTO groupTable(groupName,groupDescription, adminID) values(%s,%s,%s)", (groupName,groupDescription,adminID))
        db.commit()
        return {"result":"Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 생성에 실패했습니다."
        )


@router.get("/get_user_groups")
def get_user_groups(userID: int,db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute("SELECT groupID FROM groupTable WHERE adminID = %s", (userID,))
        groups = db.fetchall()
        db.commit()
        group_list = []
        for group in groups:
            group_id = group[0]
            db.execute("SELECT * FROM groupTable WHERE groupID = %s", (group_id,))
            group = db.fetchall()
            db.commit()

            if group:
                group_obj = Group(
                    groupID = group[0][0],
                    groupName = group[0][1],
                    groupDescription = group[0][2],
                    role = "admin"
                )
                group_list.append(group_obj)
        db.execute("SELECT groupID FROM groupMemberTable WHERE memberID = %s", (userID,))
        groups = db.fetchall()
        db.commit()
        for group in groups:
            group_id = group[0]
            db.execute("SELECT * FROM groupTable WHERE groupID = %s", (group_id,))
            group = db.fetchall()
            db.commit()

            if group:
                group_obj = Group(
                    groupID = group[0][0],
                    groupName = group[0][1],
                    groupDescription = group[0][2],
                    role = "member"
                )
                group_list.append(group_obj)

        return group_list
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 생성에 실패했습니다."
        )