from flask import Flask, request, jsonify
from economy import fetch_currency_offers
from typing import Optional

app = Flask(__name__)

@app.route('/api/currency/offers', methods=['GET'])
def get_currency_offers():
    """GET /api/currency/offers - pobiera oferty walutowe"""
    try:
        currency_id = request.args.get('currency_id')
        if not currency_id:
            return jsonify({
                "code": 400,
                "description": "Missing required parameter: currency_id"
            }), 400
        
        try:
            currency_id = int(currency_id)
        except ValueError:
            return jsonify({
                "code": 400,
                "description": "Invalid currency_id: must be an integer"
            }), 400
        
        transaction = request.args.get('transaction')
        if transaction and transaction.upper() not in ['BUY', 'SELL']:
            return jsonify({
                "code": 400,
                "description": "Invalid transaction: must be BUY or SELL"
            }), 400
        
        page = request.args.get('page', 1)
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        offers = fetch_currency_offers(
            currency_id=currency_id,
            transaction=transaction,
            page=page
        )
        
        return jsonify({
            "code": 200,
            "description": "Success",
            "data": offers
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "description": f"Internal server error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
