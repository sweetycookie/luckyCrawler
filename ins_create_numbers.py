import pymysql
import configparser

#Query
lucky_ins_query = "INSERT INTO sweetycooki.TB_CREATE_LUCKY_NUMS (round, numbers, insert_date) VALUES (%s, %s, now())"
#Init setting
parser = configparser.ConfigParser()
parser.read('./config.ini')

def db_conn() :
    global conn
    global cursor

    try:
        conn = pymysql.connect(host     = parser.get('db_config', 'hostname'),
                               user     = parser.get('db_config', 'username'),
                               password = parser.get('db_config', 'password'),
                               db       = parser.get('db_config', 'database'),
                               port     = parser.getint('db_config', 'port'),
                               charset  ='utf8')
    except pymysql.err.MySQLError as e :
        print(f"DB 연결 오류 :: {e}")
    cursor = conn.cursor()

def db_close() :
    conn.commit()
    cursor.close()
    conn.close()

def input_values() :
    global is_end
    is_end = True

    while is_end :
        in_round = input("회차를 입력하세요(ex; 1111) : ")
        in_nums = input("생성번호를 입력하세요(ex; 1,2,3,4,5,6) : ")

        print(">> 입력된 회차 :: ", in_round)
        print(">> 입력된 번호 :: ", in_nums)

        lucky_values  = (in_round, in_nums)
        cursor.execute(lucky_ins_query, lucky_values,)

        is_yn = input("종료하시겠습니까?(예; Y, 아니요; N) : ")

        if is_yn == "Y" :
            is_end = True
        elif is_yn == "y" :
            is_end = True
        else :
            is_end = False
#process
db_conn()
print("##### 데이터 입력 시작 #####")
input_values()
print("##### 데이터 입력 종료 #####")
db_close()