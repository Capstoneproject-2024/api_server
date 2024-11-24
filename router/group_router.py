from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(prefix="/group")


@router.post("/create_group/{adminID}/{groupName}/{groupDescription}")
def create_group(
    adminID: int,
    groupName: str,
    groupDescription: str,
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        db.execute(
            "INSERT INTO groupTable(groupName,groupDescription, adminID) values(%s,%s,%s)",
            (groupName, groupDescription, adminID),
        )
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="그룹 생성에 실패했습니다."
        )


@router.get("/get_user_groups")
def get_user_groups(userID: int, db: MySQLConnection = Depends(get_mysql_connection)):
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
                    groupID=group[0][0],
                    groupName=group[0][1],
                    groupDescription=group[0][2],
                    role="admin",
                )
                group_list.append(group_obj)
        db.execute(
            "SELECT groupID FROM groupMemberTable WHERE memberID = %s", (userID,)
        )
        groups = db.fetchall()
        db.commit()
        for group in groups:
            group_id = group[0]
            db.execute("SELECT * FROM groupTable WHERE groupID = %s", (group_id,))
            group = db.fetchall()
            db.commit()

            if group:
                group_obj = Group(
                    groupID=group[0][0],
                    groupName=group[0][1],
                    groupDescription=group[0][2],
                    role="member",
                )
                group_list.append(group_obj)

        return group_list
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="그룹 생성에 실패했습니다."
        )


@router.delete("/delete_group")
def delete_group(groupID: int, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(f"DELETE FROM groupTable WHERE groupID = {groupID}")
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 삭제에 실패했습니다.",
        )


# member 관련
@router.get("/get_members")
def get_members(groupID: int, db: MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT u.*
FROM groupMemberTable gm
JOIN userTable u ON gm.memberID = u.ID
WHERE gm.groupID = {groupID};
"""
        )
        members = db.fetchall()
        db.commit()
        return [
            User(id=mem[0], nickname=mem[1], email=mem[2], uid=mem[3])
            for mem in members
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버 가져오는데 실패했습니다.",
        )


@router.post("/create_member")
def create_member(
    groupMember: GroupMember, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"INSERT INTO groupMemberTable(groupID, memberID) VALUES({groupMember.groupID},{groupMember.memberID})"
        )
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버 생성에 실패했습니다.",
        )


@router.delete("/delete_member")
def delete_member(
    deleteMemberID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(f"DELETE FROM groupMemberTable WHERE memberID = {deleteMemberID}")
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버 삭제에 실패했습니다.",
        )


@router.get("/get_searched_nonMember_friends")
def get_searched_nonMember_friends(
    groupID: int,
    userID: int,
    email: str,
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT u.*
FROM userTable u
WHERE u.ID IN (
    SELECT f.followeeID
    FROM followerTable f
    WHERE f.followerID = {userID}
    AND f.followeeID NOT IN (
        SELECT gm.memberID
        FROM groupMemberTable gm
        WHERE gm.groupID = {groupID}
    )
);
"""
        )
        members = db.fetchall()
        db.commit()
        return [
            User(id=mem[0], nickname=mem[1], email=mem[2], uid=mem[3])
            for mem in members
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버 가져오는데 실패했습니다.",
        )
