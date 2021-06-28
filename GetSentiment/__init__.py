import logging
import json
import azure.functions as func
from typing import List
from typing import Dict
from collections import Counter
from collections import namedtuple

class point(dict):
    def __init__(self,word: str ,count : str):
        dict.__init__(self, text=word, value = count)

def stem(word:str) -> str :
    if "'" in word:
        return word.split("'")[0]
    return word
def extractTokens(facts : List[str]) -> Dict[str,int]:
    long_fact = ' '.join(facts)
    # filter punctuation
    punctuation ='.,")('
    long_fact = ''.join([f for f in long_fact if f not in punctuation])
    # tokenization
    tokens = long_fact.split(' ')
    # filter stop words
    stop_words = set(['the', 'is', 'from', 'with', 'a', \
        'on', 'm' , 'ft', 'about', 'other' ,'at', 'and', 'an' , 'of', 'that', 'its'])
    tokens = [t for t in tokens if not t.lower() in stop_words]
    # stemming 
    tokens = [stem(t) for t in tokens]
    # return
    return Counter(tokens)

    
def main(req: func.HttpRequest, factsData : func.DocumentList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info('getting data for facts')
    tokens = extractTokens([f["details"] for f in factsData])
    logging.info(tokens)
    # Word = namedtuple("Word", "text value")
    tokens = [point(key,val) for key,val in tokens.items()]
    topic = req.params.get('topic')
    if not topic:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            topic = req_body.get('topic')

    if topic:
        payload = json.dumps(
            {'topic' : topic, 
            "version": 1, 
            'headers': dict(req.headers),
            'tokens': tokens
            })
        return func.HttpResponse(payload)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a topic  in the query string or in the request body for a personalized response.",
             status_code=200
        )
