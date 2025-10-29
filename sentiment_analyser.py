from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

sentiment_task = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

def get_sentiment_score(text: str) -> float:
        sentence = str(text)
        sentence = sentence[:513]
        model_output = sentiment_task(sentence)
        label = model_output[0]["label"]
        score = model_output[0]["score"]
        if label == "NEGATIVE" or label == "NEUTRAL":
            return -score
        elif label == "POSITIVE":
            return score
        else:
            return 0.0
