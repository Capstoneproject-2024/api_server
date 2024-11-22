from MySQLConnection import MySQLConnection

if __name__ == "__main__":
    # MySQL 연결 객체 생성
    db = MySQLConnection()
    # MySQL 연결
    db.connect()

    # 트랜잭션 시작
    db.start_transaction()

    try:
        # 쿼리 실행
        db.execute("SELECT count(*) FROM testDB.bookTable")
        # db.execute("INSERT INTO users (username, email) VALUES (%s, %s)", ("user2", "user2@example.com"))
        result = db.fetchall()
        if result:
            print(f"Book Table Row Count: {result[0][0]}")  # 첫 번째 값에 접근
        else:
            print("No data found.")
        # 트랜잭션 커밋
        db.commit()
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()

    # 연결 종료
    db.close()
