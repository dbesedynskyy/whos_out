import logging
import datetime
import requests
import json

from chalice import Chalice
from chalicelib import BambooLib
from chalicelib import ConfigLib
from chalicelib import QuoteLib

# Global configuration
config = ConfigLib.ConfigHelper()

def _getNextBusinessDay(start_day, HOLIDAYS):
    ONE_DAY = datetime.timedelta(days=1)
    temp_day = start_day
    next_day = temp_day + ONE_DAY
    while next_day.weekday() in [5,6] or next_day in HOLIDAYS:
        next_day += ONE_DAY
    temp_day = next_day
    return temp_day

def _getVacationText(vacation, holiday_list):
    start_date = datetime.datetime.strptime(vacation.start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(vacation.end_date, '%Y-%m-%d')
    return_date = _getNextBusinessDay(end_date, holiday_list)
    n_days = (return_date - start_date).days

    start_date_text = start_date.strftime('%A %B %-d')
    return_date_text   = return_date.strftime('%A %B %-d')
    return ":desert_island: *{0}* is out for {1} day(s) on {2} (back {3})".format(vacation.name, n_days, start_date_text, return_date_text)

def _getSlackMessage(team_name, vacations):
    n_vacations = len(vacations)
    if n_vacations == 0:
        slack_message = '*Team {0} has no vacations scheduled in next 14 days*'.format(team_name)
    else:
        slack_message = 'The following people have *booked time off in the next 14 days:*'.format(team_name)
    return slack_message

def _getDailyQuote(quote_config):
    return QuoteLib.QuoteHelper.getQuote()

def _postSlack(team_name, team_channel, team_vacations, holiday_dates, daily_quote):
    vacation_text = []
    slack_message = _getSlackMessage(team_name, team_vacations)
    
    for v in team_vacations:
        vacation_text.append(_getVacationText(v, holiday_dates))

    slack_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": slack_message
            }
        }
    ]
    if len(team_vacations) > 0:
        slack_blocks.append({
            "type": "divider"
        })
        slack_blocks.append({
            "type": "section",
            "text" : {
                "type": "mrkdwn",
                "text": "\n".join(vacation_text)
            }
        })
    if daily_quote:
        slack_blocks.append({
            "type": "divider"
        })
        slack_blocks.append({
            "type": "section",
            "text" : {
                "type": "mrkdwn",
                "text": ">>> _{0}_".format(daily_quote["quote"])
            }
        })
        slack_blocks.append({
		    "type": "context",
		    "elements": [
			    {
				    "type": "mrkdwn",
				    "text": "*Author:* {0}".format(daily_quote["author"])
			    }
		    ]
        })

    slack_data = {
        'text': slack_message,
        "username": "whos out",
        "icon_emoji": ":hb:",
        "channel": team_channel,
        "blocks": slack_blocks
    }
    print("Posting slack message for {0}: {1}".format(team_name, slack_data))
    slack_hook = config.getSlackHook()
    response = requests.post(
        slack_hook, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

def _getVacationSortKey(vacation):
    return vacation.start_date

def PostTeamVacations(team, vacation_list, holiday_list):
    team_vacations = set()
    holiday_dates = set()

    for holiday in holiday_list:
        holiday_dates.add(datetime.datetime.strptime(holiday.start_date, '%Y-%m-%d'))
    
    print('Processing team {0}'.format(team['name']))
    for vacation in vacation_list:
        if vacation.name in team['members']:
            team_vacations.add(vacation)
    
    print('Getting daily quote')
    daily_quote = None
    if(team['daily_quote']):
        daily_quote = _getDailyQuote(team['daily_quote'])

    # TODO: separate slack related routines 
    team_vacations = sorted(team_vacations, key=_getVacationSortKey)
    _postSlack(team["name"], team["channel"], team_vacations, holiday_dates, daily_quote)

# Load configuration
#app = Chalice(app_name='whosout')
#@app.schedule('cron(0 12 ? * MON-FRI *)')
def run_schedule(event):

    teams = config.getTeams()
    days = config.getDays()
    
    bambooOrg = config.getBambooOrg()
    bambooKey = config.getBambooKey()

    # Get vacations
    bambooClient = BambooLib.Bamboo(bambooOrg, bambooKey)
    result = bambooClient.get_whosout(days)
    # Post vacation information for each team
    for team in teams:
        PostTeamVacations(team, result[0], result[1])

run_schedule(None)

#print("test")
#import json
#import random

#with open('./chalicelib/quotes.json') as json_file:
#    json_data = json.load(json_file)
#    count = len(json_data["data"])
    
#    index = random.randint(0, count)
#    print(index, ": ", json_data["data"][index])    
#    with open('./chalicelib/quotes.jsonl', 'w') as outfile:
#        for entry in json_data["data"]:
#            json.dump(entry, outfile)
#            outfile.write('\n')