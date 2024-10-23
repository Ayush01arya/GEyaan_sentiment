from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import random
import requests

app = Flask(__name__)

# Use more specific CORS settings for security and functionality
cors = CORS(app, resources={r"/send_otp": {"origins": "*"},r"/verify_otp": {"origins": "*"}, r"/sentiment": {"origins": "*"}})  # Allow all origins for both routes



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
otp_storage = {}

otp_storage = {}

def send_otp(mobile_number, otp):
    """
    This function sends an OTP using the Fast2SMS API.
    Replace this placeholder implementation with the actual code that calls the Fast2SMS API.
    """
    try:
        # Your implementation to send OTP through Fast2SMS
        # Make the API call to send OTP here
        return True  # Return True if OTP sent successfully
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False

@app.route('/send_otp', methods=['POST'])
def send_otp_api():
    data = request.json
    mobile_number = data.get('mobile_number')

    if not mobile_number:
        return jsonify({"message": "Mobile number is required"}), 400

    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)

    # Send the OTP using the send_otp function
    success = send_otp(mobile_number, otp)

    if success:
        # Store the OTP with a timestamp (set to expire in 5 minutes)
        otp_storage[mobile_number] = {
            'otp': otp,
            'expiry_time': time.time() + 300  # OTP expires in 300 seconds (5 minutes)
        }
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"message": "Failed to send OTP"}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp_api():
    data = request.json
    mobile_number = data.get('mobile_number')
    otp = data.get('otp')

    if not mobile_number or not otp:
        return jsonify({"message": "Mobile number and OTP are required"}), 400

    # Check if the OTP for the given mobile number exists and hasn't expired
    stored_otp_data = otp_storage.get(mobile_number)
    if stored_otp_data:
        stored_otp = stored_otp_data['otp']
        expiry_time = stored_otp_data['expiry_time']

        if time.time() > expiry_time:
            return jsonify({"success": False, "message": "OTP has expired"}), 400

        if stored_otp == int(otp):
            # OTP verified successfully
            del otp_storage[mobile_number]  # Optionally, remove the OTP after successful verification
            return jsonify({"success": True, "message": "OTP verified successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid OTP"}), 400
    else:
        return jsonify({"success": False, "message": "No OTP found for this number"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
