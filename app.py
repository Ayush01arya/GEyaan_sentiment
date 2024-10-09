from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)

# Use more specific CORS settings for security and functionality
cors = CORS(app, resources={r"/sentiment": {"origins": "*"}})


@app.route("/")
def start():
    return "<h1><b><center>Ayush Arya API</center></b></h1>"


# Sentiment analysis function
@app.route('/sentiment', methods=['POST', 'OPTIONS'])
def sentiment_analysis():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'CORS preflight passed'}), 200

    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Perform sentiment analysis
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Classify sentiment
    mood = classify_sentiment(polarity)
    context = analyze_context(text, polarity)

    # Suggest actions
    suggestion = generate_suggestion(mood)

    return jsonify({
        'mood': mood,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'context': context,
        'suggestion': suggestion
    })


# Helper functions
def classify_sentiment(polarity):
    if polarity > 0.75:
        return "Very Positive"
    elif 0.25 < polarity <= 0.75:
        return "Positive"
    elif 0.05 < polarity <= 0.25:
        return "Slightly Positive"
    elif -0.05 <= polarity <= 0.05:
        return "Neutral"
    elif -0.25 <= polarity < -0.05:
        return "Slightly Negative"
    elif -0.75 <= polarity < -0.25:
        return "Negative"
    else:
        return "Very Negative"


def analyze_context(text, polarity):
    keywords_help = ['help', 'support', 'assist', 'issue', 'problem']
    keywords_satisfaction = ['happy', 'satisfied', 'great', 'love']
    keywords_dissatisfaction = ['disappointed', 'frustrated', 'angry', 'poor']

    lower_text = text.lower()
    if any(word in lower_text for word in keywords_satisfaction):
        return 'Satisfaction'
    elif any(word in lower_text for word in keywords_dissatisfaction):
        return 'Dissatisfaction'
    elif any(word in lower_text for word in keywords_help):
        return 'Request for Help'
    else:
        return 'General Feedback'


def generate_suggestion(mood):
    if mood in ['Negative', 'Very Negative']:
        return 'Consider escalating this issue or providing immediate assistance.'
    elif mood == 'Slightly Negative':
        return 'Ensure the issue is addressed properly to prevent further dissatisfaction.'
    elif mood == 'Slightly Positive':
        return 'Acknowledge the positive sentiment but check if additional help is needed.'
    else:
        return 'Thank the customer for their feedback and offer continued support.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
