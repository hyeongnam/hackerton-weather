import datetime
import pytz
import urllib.request
import json
import pymysql.cursors
from decouple import config

# connection = pymysql.connect(host='localhost',
#                              user='root',
#                              password='oracle',
#                              db='weather',
#                              charset='utf8',
#                              cursorclass=pymysql.cursors.DictCursor)


def get_api_date():
    standard_time = [2, 5, 8, 11, 14, 17, 20, 23]
    time_now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%H')
    check_time = int(time_now) - 1
    day_calibrate = 0
    while not check_time in standard_time:
        check_time -= 1
        if check_time < 2:
            day_calibrate = 1
            check_time = 23
    if check_time < 1000:
        check_time = '0' + str(check_time)
    date_now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%Y%m%d')
    date_day = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%m%d')
    check_date = int(date_now) - day_calibrate
    return (str(check_date), (str(check_time) + '00'))


def get_weather_data():
    api_date, api_time = get_api_date()
    url = "http://newsky2.kma.go.kr/service/SecndSrtpdFrcstInfoService2/ForecastSpaceData?"
    key = f"serviceKey={config('SERVICE_KEY')}"
    date = "&base_date=" + api_date
    time = "&base_time=" + api_time
    nx = "&nx=97"
    ny = "&ny=76"
    numOfRows = "&numOfRows=100"
    type = "&_type=json"
    api_url = url + key + date + time + nx + ny + numOfRows + type
    print(api_url)
    data = urllib.request.urlopen(api_url).read().decode('utf8')
    data_json = json.loads(data)

    parsed_json = data_json['response']['body']['items']['item']
    # 현재기준 날씨 추출
    target_date = parsed_json[0]['fcstDate']  # get date and time
    target_time = parsed_json[0]['fcstTime']
    date_calibrate = target_date  # date of TMX, TMN
    if target_time > '1300':
        if str(target_date)[4:] == 1231:
            pass
        else:
            date_calibrate = str(int(target_date) + 1)

    passing_data = {}
    for one_parsed in parsed_json:
        if one_parsed['fcstDate'] == target_date and one_parsed['fcstTime'] == target_time:  # get today's data
            passing_data[one_parsed['category']] = one_parsed['fcstValue']

        if one_parsed['fcstDate'] == date_calibrate and (
                one_parsed['category'] == 'TMX' or one_parsed['category'] == 'TMN'):  # TMX, TMN at calibrated day
            passing_data[one_parsed['category']] = one_parsed['fcstValue']

    return passing_data


if __name__ == '__main__':
    print(get_weather_data())
    # try:
    #     with connection.cursor() as cursor:
    #         sql = "INSERT INTO WEATHER (name,price,yst,updn) VALUES (%s,%s,%s,%s)"
    #         cursor.execute(sql,(name, price, yst, updn))
    #     connection.commit()
    # finally:
    #     connection.close()