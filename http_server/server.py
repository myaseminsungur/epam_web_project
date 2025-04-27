from flask import Flask, render_template, request, jsonify
import requests


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Get form data

    base_currency = request.form.get('base_currency')
    target_currency = request.form.get('target_currency')
    date = request.form.get('date')
    
    # Prepare JSON data
    json_data = {
        'base_currency': base_currency,
        'target_currency': target_currency,
        'date': date
    }

    # Send request to Django application
    try:
        response = requests.post(
            'http://localhost:8000/currency_converter/api/convert/',
            json=json_data
        )
        if response.ok:
            return render_template('result.html', result=response.json())
        else:
            return render_template('result.html', error=response.json().get('error', 'Unknown error'))
    except Exception as e:
        return render_template('result.html', error=str(e))

if __name__ == '__main__':
    print('Starting Flask server on port 8001...')
    app.run(host='0.0.0.0', port=8001, debug=True) 