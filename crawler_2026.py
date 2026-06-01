import requests
import pymysql
import configparser

luckyUrl    = "https://www.dhlottery.co.kr/lt645/result"
lucky_api   = "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do"
pensionUrl  = "https://www.dhlottery.co.kr/pt720/result"
pension_api = "https://www.dhlottery.co.kr/pt720/selectPstPt720WnList.do"


lucky_query       = "INSERT INTO sweetycooki.TB_LUCKY (round, numbers, insert_date) VALUES (%s, %s, now())"
pension_query     = "INSERT INTO sweetycooki.TB_PENSION (round, winNumbers, bonusNumbers, insert_date) VALUES (%s, %s, %s, SYSDATE())"
lucky_last_round  = "SELECT round FROM sweetycooki.TB_LUCKY ORDER BY seq DESC LIMIT 1"
pension_last_round= "SELECT round FROM sweetycooki.TB_PENSION ORDER BY seq DESC LIMIT 1"

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (HTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

def get_config() :
  global parser

  parser = configparser.ConfigParser()
  #parser.read('./config.ini')
  parser.read('https://github.com/sweetycookie/luckyCrawler/blob/main/')
  parser.read('config.ini')

def db_conn() :
  global conn
  global cursor

  try:
    conn = pymysql.connect(host     = parser['db_config']['hostname'], #parser.get('db_config', 'hostname'),
                           user     = parser['db_config']['username'], #parser.get('db_config', 'username'),
                           password = parser['db_config']['password'], #parser.get('db_config', 'password'),
                           database = parser['db_config']['database'], #parser.get('db_config', 'database'),
                           port     = int(parser['db_config']['port']), #parser.getint('db_config', 'port'),
                           charset  ='utf8')
  except pymysql.err.MySQLError as e :
    print(f"DB 연결 오류 :: {e}")
  cursor = conn.cursor()

def db_close() :
  conn.commit()
  cursor.close()
  conn.close()

def job_lucky_new() :
  print("########## job_lucky start ##########")
  get_data = requests.get(lucky_api, headers=headers)
  org_data = get_data.json()
  process_1_data = org_data.get("data")
  process_2_data = process_1_data.get("list")
  ## print(">> process_2_data :: ", process_2_data[0])

  ## 저장되어있는 회차 가져오기
  cursor.execute(lucky_last_round)
  get_data = cursor.fetchone()
  old_last_round = get_data[0]

  ## 새로운 회차 가져오기2
  item = process_2_data[0]
  new_round = str(item.get("ltEpsd")) + "회"
  number_list = str(item.get("tm1WnNo")) + ","
  number_list += str(item.get("tm2WnNo")) + ","
  number_list += str(item.get("tm3WnNo")) + ","
  number_list += str(item.get("tm4WnNo")) + ","
  number_list += str(item.get("tm5WnNo")) + ","
  number_list += str(item.get("tm6WnNo")) + ","
  number_list += str(item.get("bnsWnNo"))

  ## 처리
  if new_round != old_last_round :
    lucky_values  = (new_round, number_list)
    cursor.execute(lucky_query, lucky_values,)

    print(">> title :: ", new_round)
    print(">> luckyNumbers :: ", number_list)
  else :
    print(">> new_round :: ", new_round)
    print(">> old_last_round :: ", old_last_round)
    print(">> 회차가 같음")

  print("########## job_lucky end ##########")

def job_pension_new() :
  print("########## job_pension start ##########")
  get_data = requests.get(pension_api, headers=headers)
  org_data = get_data.json()
  process_1_data = org_data.get("data")
  process_2_data = process_1_data.get("result")

  ## 저장되어있는 회차 가져오기
  cursor.execute(pension_last_round)
  get_data = cursor.fetchone()
  old_last_round = get_data[0]

  ## 새로운 회차 가져오기
  item = process_2_data[0]
  win_rnk = str(item.get("wnRnkVl"))
  bns_rnk = str(item.get("bnsRnkVl"))

  new_round = str(item.get("psltEpsd")) + "회"
  win_numbers = str(item.get("wnBndNo")) + ","
  win_numbers += win_rnk[0] + ","
  win_numbers += win_rnk[1] + ","
  win_numbers += win_rnk[2] + ","
  win_numbers += win_rnk[3] + ","
  win_numbers += win_rnk[4] + ","
  win_numbers += win_rnk[5]

  bonus_numbers = "각,"
  bonus_numbers += bns_rnk[0] + ","
  bonus_numbers += bns_rnk[1] + ","
  bonus_numbers += bns_rnk[2] + ","
  bonus_numbers += bns_rnk[3] + ","
  bonus_numbers += bns_rnk[4] + ","
  bonus_numbers += bns_rnk[5]

  ## 처리
  if new_round != old_last_round :
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

def step_process() :
  get_config()
  db_conn()
  job_lucky_new()
  job_pension_new()
  db_close()

step_process()
