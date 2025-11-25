import requests
from bs4 import BeautifulSoup
import pymysql

luckyUrl    = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
pensionUrl  = "https://www.dhlottery.co.kr/gameResult.do?method=win720"

lucky_query       = "INSERT INTO sweetycooki.TB_LUCKY (round, numbers, insert_date) VALUES (%s, %s, now())"
pension_query     = "INSERT INTO sweetycooki.TB_PENSION (round, winNumbers, bonusNumbers, insert_date) VALUES (%s, %s, %s, SYSDATE())"
lucky_last_round  = "SELECT round FROM sweetycooki.TB_LUCKY ORDER BY seq DESC LIMIT 1"
pension_last_round= "SELECT round FROM sweetycooki.TB_PENSION ORDER BY seq DESC LIMIT 1"

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (HTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

def db_conn() :
  global conn
  global cursor
  db_host   = 'sweetycooki.mycafe24.com'
  #db_host   = 'localhost'
  db_user   = 'sweetycooki'
  db_pw     = 'Cafe240110'
  db_dbname = 'sweetycooki'

  try:
    conn = pymysql.connect(host     = db_host,
                           user     = db_user,
                           password = db_pw,
                           db       = db_dbname,
                           port     = 3306,
                           charset  ='utf8')
  except pymysql.err.MySQLError as e :
    print(f"DB 연결 오류 :: {e}")
  cursor = conn.cursor()

def db_close() :
  conn.commit()
  cursor.close()
  conn.close()


def job_lucky() :
  print("########## job_lucky start ##########")
  lucky_data = requests.get(luckyUrl, headers=headers)
  lucky_soup = BeautifulSoup(lucky_data.text, 'html.parser')

  number_list = ""

  ## 저장되어있는 회차 가져오기
  cursor.execute(lucky_last_round)
  get_data = cursor.fetchone()
  old_last_round = get_data[0]

  new_round = lucky_soup.select_one('.win_result h4 > strong').text

  if new_round != old_last_round :
    for content in lucky_soup.select('.win_result') :
      for num in content.select('span.ball_645') :
        number_list += num.text + ","

    if number_list.endswith(','):
      number_list = number_list[:-1]

    lucky_values  = (new_round, number_list)
    cursor.execute(lucky_query, lucky_values,)

    print(">> title :: ", new_round)
    print(">> luckyNumbers :: ", number_list)
  else :
    print(">> new_round :: ", new_round)
    print(">> old_last_round :: ", old_last_round)
    print(">> 회차가 같음")

  print("########## job_lucky end ##########")


def job_pension() :
  print("########## job_pension start ##########")
  pension_data = requests.get(pensionUrl, headers=headers)
  pension_soup = BeautifulSoup(pension_data.text, 'html.parser')

  win_numbers = ""
  bonus_numbers = ""

  ## 저장되어있는 회차 가져오기
  cursor.execute(pension_last_round)
  get_data = cursor.fetchone()
  old_last_round = get_data[0]

  new_round = pension_soup.select_one('#after720 h4 > strong').text

  if new_round != old_last_round :
    for content in pension_soup.select('#after720') :
      count = 0
      for nums in content.select('.win720_num') :
        for eachNum in nums.select(".num") :
            if eachNum is not None :
              count += 1
              if count < 8 :
                win_numbers += eachNum.text + ","
              else :
                bonus_numbers += eachNum.text + ","
            else :
              break

    if win_numbers.endswith(','):
      win_numbers = win_numbers[:-1]

    if bonus_numbers.endswith(','):
      bonus_numbers = bonus_numbers[:-1]

    pension_values  = (new_round, win_numbers, bonus_numbers)
    cursor.execute(pension_query, pension_values,)

    print(">> new_round :: ", new_round)
    print(">> winNumbers :: ", win_numbers)
    print(">> bonusNumbers :: ", bonus_numbers)
  else :
    print(">> new_round :: ", new_round)
    print(">> old_last_round :: ", old_last_round)
    print(">> 회차가 같음")

  print("########## job_pension end ##########")

db_conn()
job_lucky()
job_pension()
db_close()
