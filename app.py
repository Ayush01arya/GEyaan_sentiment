from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)

# Allow all origins or specify certain domains to allow CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def start():
    return "<h><b><center>Ayush Arya API</center></b></h1>"

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

@app.route('/sentiment', methods=['POST'])
def sentiment_analysis():
    try:
        data = request.json
        text = data.get('text')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        mood = classify_sentiment(polarity)
        context = analyze_context(text, polarity)

        if mood in ['Negative', 'Very Negative']:
            suggestion = 'Consider escalating this issue or providing immediate assistance.'
        elif mood == 'Slightly Negative':
            suggestion = 'Ensure the issue is addressed properly to prevent further dissatisfaction.'
        elif mood == 'Slightly Positive':
            suggestion = 'Acknowledge the positive sentiment but check if additional help is needed.'
        else:
            suggestion = 'Thank the customer for their feedback and offer continued support.'

        return jsonify({
            'mood': mood,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'context': context,
            'suggestion': suggestion
        })
    except Exception as e:
        return jsonify({'error': 'Something went wrong', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
