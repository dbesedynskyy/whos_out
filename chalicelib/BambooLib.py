import json
import requests
import datetime

class BambooTimeOff():
    def __init__(self, json_data):
        self.id = json_data['employeeId']
        self.name = json_data['name']
        self.start_date = json_data['start']
        self.end_date = json_data['end']
class BambooHoliday():
    def __init__(self, json_data):
        self.id = json_data['id']
        self.name = json_data['name']
        self.start_date = json_data['start']
        self.end_date = json_data['end']

class Bamboo:
    def __init__(self, org, key):
        self.org = org
        self.key = key
        self.base_uri = "https://{0}:x@api.bamboohr.com/api/gateway.php/{1}/v1/".format(self.key, self.org)
        self.today = datetime.datetime.today()

    def get_whosout(self, days = 0):
        start_date = self.today.strftime('%Y-%m-%d')
        end_date = (self.today + datetime.timedelta(days=days)).strftime('%Y-%m-%d')

        return self.get_whosout_range(start_date, end_date)

    def get_whosout_range(self, start_date = None, end_date = None):
        request_uri = self.base_uri + "time_off/whos_out/?"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        if not start_date:
            start_date = self.today.strftime('%Y-%m-%d')
        if not end_date:
            end_date = start_date


        request_uri = self.base_uri + "time_off/whos_out/?start={0}&end={1}".format(start_date, end_date)
        print(request_uri)
        response = requests.get(request_uri, headers=headers)

        data = []
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))

        print(data)
        result = {}
        holidays = []
        for json_toff in data:
            # holidays are also returned from api
            if json_toff['type'] == 'holiday':
                holiday = BambooHoliday(json_toff)
                holidays.append(holiday)
            elif 'employeeId' not in json_toff:
                continue
            else:
                time_off = BambooTimeOff(json_toff)

                if time_off.id in result:
                    result[time_off.id].start_date = min(result[time_off.id].start_date, time_off.start_date)
                    result[time_off.id].end_date = max(result[time_off.id].end_date, time_off.end_date)
                else:
                    result[time_off.id] = time_off

        return (list(result.values()), holidays)
    
    def filter_today_vacations(self, data):
        today = self.today.strftime('%Y-%m-%d')
        today_vacations = list(filter(lambda x: x.start_date <= today, data))

        return today_vacations

    def filter_future_vacations(self, data):
        today = self.today.strftime('%Y-%m-%d')
        future_vacations = list(filter(lambda x: x.start_date > today, data))

        return future_vacations