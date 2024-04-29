import requests
import json
import boto3

url = "https://www.fih.hockey/default.aspx?methodtype=3&client=8696669363&sport=5&league=0&timezone=0530&language=en&gamestate=4"

payload = ""
headers = {
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'cookie': '_ga=GA1.1.1996902381.1714371701; ASP.NET_SessionId=5yo2dxmebmnqjzwdzammyfj5; _ga_H0WVV33TCY=GS1.1.1714371701.1.1.1714372718.0.0.0',
  'priority': 'u=1, i',
  'referer': 'https://www.fih.hockey/schedule-fixtures-results',
  'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

response = requests.request("GET", url, headers=headers, data=payload)

results = response.json()

# Create a list to hold the results
matches = []

result_items = results['matches']

for result_item in result_items:
    match_info = {}
    match_info['tour_name'] = result_item['tour_name']
    match_info['match_date'] = result_item['match_date']
    match_info['sport'] = result_item['sport']
    match_info['event_status'] = result_item['event_status']
    team_names = [team['name'] for team in result_item['participants']]
    match_info['team_names'] = team_names
    match_info['winning_margin'] = result_item.get('winning_margin', None)
    matches.append(match_info)

# Write the list of dictionaries into a JSON file with new lines for each match
#with open('output.json', 'w') as f:
#    for match in matches:
#        json.dump(match, f)
#        f.write('\n')

matches_json = json.dumps(matches)


s3 = boto3.client('s3')
s3.put_object(Bucket='your-bucket-name', Key='match_statistics.json', Body=matches_json)

print("Data written to match_statistics.json in S3 bucket successfully.")