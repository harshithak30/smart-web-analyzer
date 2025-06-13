from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = 'secret'

# -------------------- DB Configuration --------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# Create DB tables
with app.app_context():
    db.create_all()

# -------------------- Home --------------------
@app.route('/')
def home():
    if 'username' in session:
        return render_template('url_input.html')
    return redirect(url_for('login'))

# -------------------- Features Page --------------------
@app.route('/features')
def features():
    return render_template('features.html')

# -------------------- Pricing Page --------------------
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# -------------------- Contact Page --------------------
@app.route('/contact')
def contact():
    return render_template('contact.html')

# -------------------- Documentation Page --------------------
@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

# -------------------- Register --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validation
        if not username or not password:
            return render_template('register.html', error='Username and password are required!')
        
        if len(username) < 3:
            return render_template('register.html', error='Username must be at least 3 characters long!')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long!')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists!')
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='Registration failed. Please try again.')
    
    return render_template('register.html')

# -------------------- Login --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required!')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for('home'))
        
        return render_template('login.html', error='Invalid username or password.')
    
    return render_template('login.html')

# -------------------- Logout --------------------
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

# -------------------- Webpage Content Extraction --------------------
def extract_webpage_content(url):
    """
    Extract content from a webpage including title, description, and text content.
    """
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length
        if len(content) > 5000:
            content = content[:5000] + "..."
        
        # Extract additional metadata
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords_text = keywords.get('content', '') if keywords else ''
        
        # Extract headings for structure analysis
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip()
                })
        
        return {
            'title': title_text,
            'description': description,
            'keywords': keywords_text,
            'content': content,
            'url': url,
            'headings': headings[:10],  # Limit to first 10 headings
            'word_count': len(content.split()),
            'status': 'success'
        }
        
    except requests.exceptions.Timeout:
        return create_error_response(url, 'Request timeout - the webpage took too long to respond.')
    except requests.exceptions.ConnectionError:
        return create_error_response(url, 'Connection error - unable to reach the webpage.')
    except requests.exceptions.HTTPError as e:
        return create_error_response(url, f'HTTP error {e.response.status_code} - webpage not accessible.')
    except Exception as e:
        print(f"Error extracting webpage content: {e}")
        return create_error_response(url, 'Could not extract content from this webpage.')

def create_error_response(url, error_message):
    """Create a standardized error response for webpage extraction."""
    return {
        'title': 'External webpage',
        'description': 'Could not extract content',
        'keywords': '',
        'content': f'Viewing: {url}\n\nError: {error_message}',
        'url': url,
        'headings': [],
        'word_count': 0,
        'status': 'error'
    }

# -------------------- Chat --------------------
API_KEY = "AIzaSyCKtkY2b5j08igbYUoRI60-YJk-otVhtsU"
MODEL = "gemini-1.5-flash"

@app.route('/start', methods=['POST'])
def start():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    url = request.form.get('url', '').strip()
    if not url:
        return redirect(url_for('home'))
    
    # Extract webpage content
    webpage_info = extract_webpage_content(url)
    
    # Store in session
    session['url'] = url
    session['webpage_info'] = webpage_info
    
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    url = session.get('url')
    webpage_info = session.get('webpage_info')
    
    if not url or not webpage_info:
        return redirect(url_for('home'))
    
    return render_template('chat.html', 
                         url=url, 
                         webpage_info=webpage_info,
                         username=session.get('username'))

@app.route('/chat', methods=['POST'])
def get_reply():
    if 'username' not in session:
        return jsonify({"reply": "Session expired. Please log in again.", "error": True})

    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"reply": "Invalid request format.", "error": True})
        
        message = data['message'].strip()
        if not message:
            return jsonify({"reply": "Please enter a message.", "error": True})
        
        webpage_info = session.get('webpage_info', {})
        
        if not webpage_info:
            return jsonify({"reply": "No webpage information available. Please analyze a webpage first.", "error": True})

        # Enhanced context prompt with better structure
        context_prompt = f"""
You are an AI assistant specialized in webpage analysis. You have analyzed the following webpage:

**Webpage Information:**
- Title: {webpage_info.get('title', 'N/A')}
- URL: {webpage_info.get('url', 'N/A')}
- Description: {webpage_info.get('description', 'N/A')}
- Keywords: {webpage_info.get('keywords', 'N/A')}
- Word Count: {webpage_info.get('word_count', 0)}
- Status: {webpage_info.get('status', 'unknown')}

**Content Structure:**
{format_headings(webpage_info.get('headings', []))}

**Main Content:**
{webpage_info.get('content', 'No content available')}

**User Question:** {message}

Please provide a helpful, accurate, and detailed response based on the webpage content above. If the question is about SEO, performance, content quality, or technical aspects, provide specific insights and recommendations.
"""

        # Make API request to Gemini
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}",
            json={
                "contents": [{"parts": [{"text": context_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                reply = data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": reply, "error": False})
            else:
                return jsonify({"reply": "Sorry, I couldn't generate a response. Please try again.", "error": True})
        else:
            print(f"Gemini API Error: {response.status_code} - {response.text}")
            return jsonify({"reply": "Sorry, I encountered an API error. Please try again later.", "error": True})
            
    except requests.exceptions.Timeout:
        return jsonify({"reply": "Request timeout. Please try again.", "error": True})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"reply": "Sorry, I encountered an unexpected error. Please try again.", "error": True})

def format_headings(headings):
    """Format headings for better context in the prompt."""
    if not headings:
        return "No headings found."
    
    formatted = []
    for heading in headings:
        level_indicator = "#" * heading['level']
        formatted.append(f"{level_indicator} {heading['text']}")
    
    return "\n".join(formatted)

@app.route('/new-chat')
def new_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Clear webpage-specific session data but keep user session
    session.pop('url', None)
    session.pop('webpage_info', None)
    return redirect(url_for('home'))

# -------------------- API Routes (for future API access) --------------------
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for webpage analysis."""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        webpage_info = extract_webpage_content(url)
        
        return jsonify({
            "status": "success",
            "data": webpage_info
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Error Handlers --------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# -------------------- Health Check --------------------
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Chat AI Web Analyzer is running"})

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)