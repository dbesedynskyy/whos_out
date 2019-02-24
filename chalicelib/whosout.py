import json
import requests
import datetime

def run():

    AUTH_TOKEN = ''
    start_date = datetime.datetime.today().strftime('%Y-%m-%d')
    end_date = start_date

    api_org = ''
    api_url = "https://" + AUTH_TOKEN + ":x@api.bamboohr.com/api/gateway.php/" + api_org + "/v1/time_off/whos_out/?start=" + start_date + '&end=' + end_date

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

    slack_message = ''
    for e in data:
        slack_message += e['name'] + '\n'
        print(e['name'], '\t\t (', e['end'], ')')

    # post to slack
    webhook_url = ''
    slack_data = {
        'text': slack_message,
        "username": "whos out",
        "icon_emoji": ":hb:"
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )


