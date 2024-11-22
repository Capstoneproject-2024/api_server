from fastapi import FastAPI
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager



class MySQLConnection:
    def __init__(self):
        load_dotenv()
        self.host = os.environ.get("host")
        self.user = os.environ.get("user")
        self.password = os.environ.get("password")
        self.database = os.environ.get("database")
        self.connection = None
        self.cursor = None
        
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("MySQL에 성공적으로 연결되었습니다.")
        except Error as e:
            print(f"연결 오류: {e}")
            self.connection = None
            self.cursor = None
            
    def commit(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.commit()
                print("변경 사항이 커밋되었습니다.")
            except Error as e:
                print(f"커밋 오류: {e}")
        else:
            print("MySQL 연결이 되지 않았습니다. 커밋할 수 없습니다.")

    def start_transaction(self):
        if self.connection and self.connection.is_connected():
            self.connection.start_transaction()
            print("트랜잭션이 시작되었습니다.")
        else:
            print("MySQL 연결이 되지 않았습니다.")

    def rollback(self):
        if self.connection and self.connection.is_connected():
            self.connection.rollback()
            print("트랜잭션이 롤백되었습니다.")
        else:
            print("MySQL 연결이 되지 않았습니다.")

    def execute(self, query, params=None):
        if self.cursor:
            try:
                self.cursor.execute(query, params)
                print(f"쿼리 실행됨: {query}")
            except Error as e:
                print(f"쿼리 실행 오류: {e}")
                raise e
        else:
            print("커서가 초기화되지 않았습니다.")

    def fetchall(self):
        if self.cursor:
            return self.cursor.fetchall()
        else:
            print("커서가 초기화되지 않았습니다.")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL 연결이 종료되었습니다.")
        else:
            print("연결이 되어 있지 않습니다.")


mysql_connection = None

# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

def get_mysql_connection() -> MySQLConnection:
    global mysql_connection
    if not mysql_connection:
        mysql_connection = MySQLConnection()
        mysql_connection.connect()
    return mysql_connection

def start():
    global mysql_connection
    mysql_connection = MySQLConnection()
    mysql_connection.connect()
    print("service is started.")
    
def shutdown():
    global mysql_connection
    # MySQL 연결 종료
    if mysql_connection:
        mysql_connection.close()
        print("Service stopped, MySQL connection closed.")  


@asynccontextmanager
async def lifespan(app: FastAPI):
    # When service starts.
    start()
    
    yield
    
    # When service is stopped.
    shutdown()