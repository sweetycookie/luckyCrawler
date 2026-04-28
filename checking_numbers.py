import pymysql
import configparser

parser = configparser.ConfigParser()
parser.read('./config.ini')

lucky_list_query = "select TL.round, TL.numbers from sweetycooki.TB_LUCKY TL order by TL.round"

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

def check_main() :
    cursor.execute(lucky_list_query)
    get_data_list = cursor.fetchall()

    for oldNumber in get_data_list :
        if oldNumber :
            print(">> oldNumber_round :: ", oldNumber[0])
            print(">> oldNumber_nums :: ", oldNumber[1])
            old_numbers = oldNumber[1].split(',')
            old_numbers.pop()
            #print(">> old_numbers :: ", old_numbers)

            #for num in old_numbers :
            #    print(f">> {oldNumber[0]}_num :: ", num)
        else :
            print(">> oldNumber :: null")

db_conn()
check_main()
db_close()