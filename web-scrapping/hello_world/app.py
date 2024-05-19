import json
import requests
import boto3
import os
from collections import defaultdict
from gensim import corpora
from gensim import models
from gensim import similarities


def lambda_handler(event, context):
    bucket_name = os.environ.get('SCRAPY_S3_BUCKET')
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

    # Convert the list of dictionaries to JSON string
    matches_json = json.dumps(matches)

    # Write the JSON data directly to S3
    s3 = boto3.client('s3')
    s3.put_object(Bucket=f"{bucket_name}", Key='match.json', Body=matches_json)

    return {
        'statusCode': 200,
        'body': json.dumps('Data written to match.json in S3 bucket successfully.')
    }

def gensim_query(event,context):
    body = json.loads(event['body'])
    input_prompt = body['prompt']
   
    bucket_name = os.environ.get('SCRAPY_S3_BUCKET')
    FILE_TO_READ = 'match.json'
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=FILE_TO_READ)
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    
    for match in data:
        match['team_names'] = ' '.join(match['team_names'])
    texts = []
    for item in data:
      split_data = " ".join(str(v) for v in item.values())
      tokens = split_data.lower().split()
      texts.append(tokens)

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=5)
    vec_bow = dictionary.doc2bow(input_prompt.lower().split())
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space

    num_features = len(dictionary)
    index = similarities.MatrixSimilarity(lsi[corpus],num_features=num_features)
    sims = index[vec_lsi] 
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    results = []
    for doc_position, doc_score in sims:
        results.append(data[doc_position])
    """
    def format_results(results):
        formatted_matches = []

        for match in results:
            formatted_match = {
                "Match": match["Match"],
                "Date": match["Date"],
                "Status": match["Status"],
                "Score": match["Score"],
                "match_details": match["match_details"]
            }

            formatted_matches.append(formatted_match)

        return formatted_matches

    formatted_results = format_results(results)
    """
    return {
        'statusCode': 200,
        'body': json.dumps(results.json)
    }