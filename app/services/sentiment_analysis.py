import requests
import os


def analyze_sentiment(text):
    url = "https://api.meaningcloud.com/sentiment-2.1"
    payload = {
        'key': os.getenv('MEANING_CLOUD_API_KEY'),
        'txt': text,
        'lang': 'en'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return simplify_sentiment(response.json())
    else:
        return None


def simplify_sentiment(sentiment_response):
    """
    Simplifies the sentiment analysis response to include only meaningful values.

    :param sentiment_response: The full sentiment analysis response from MeaningCloud.
    :return: A simplified dictionary with selected sentiment values.
    """
    simplified = {
        'overall_sentiment': sentiment_response.get('score_tag'),
        'agreement': sentiment_response.get('agreement'),
        'subjectivity': sentiment_response.get('subjectivity'),
        'confidence': int(sentiment_response.get('confidence', 0)),
        'irony': sentiment_response.get('irony'),
        'sentence_sentiments': [
            {
                'text': sentence.get('text'),
                'sentiment': sentence.get('score_tag'),
                'confidence': int(sentence.get('confidence', 0))
            } for sentence in sentiment_response.get('sentence_list', [])
        ],
        'concepts': [
            {
                'form': concept.get('form'),
                'type': concept.get('type'),
                'sentiment': concept.get('score_tag')
            } for concept in sentiment_response.get('sentimented_concept_list', [])
        ]
    }

    return simplified
