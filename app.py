from flask import Flask, render_template, request, jsonify
from database import init_database, get_all_faqs, log_chat, log_unmatched_query, get_chat_stats, add_faq
from chatbot_engine import ChatbotEngine

app = Flask(__name__)

# Initialize database and chatbot engine
init_database()
faqs = get_all_faqs()
chatbot = ChatbotEngine(faqs)

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    stats = get_chat_stats()
    return render_template('admin.html', stats=stats)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        user_message = request.json.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            })
        
        # Get response from chatbot
        result = chatbot.get_response(user_message)
        
        # Log the interaction
        log_chat(user_message, result['answer'], result['confidence'])
        
        # Log unmatched queries
        if not result['success']:
            log_unmatched_query(user_message)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'confidence': round(result['confidence'] * 100, 2),
            'matched_question': result['matched_question']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = get_chat_stats()
    return jsonify(stats)

@app.route('/api/add_faq', methods=['POST'])
def api_add_faq():
    """API endpoint to add new FAQ"""
    try:
        data = request.json
        add_faq(
            data['question'],
            data['answer'],
            data['category'],
            data['keywords']
        )
        
        # Reload chatbot engine with new data
        global chatbot
        faqs = get_all_faqs()
        chatbot = ChatbotEngine(faqs)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)