# Chat AI Web Analyzer

Chat AI Web Analyzer is a full-stack Flask web application that allows users to analyze and interact with websites using AI. It includes user authentication, a live webpage preview, and a contextual chat interface powered by Gemini that responds specifically to content from the analyzed webpage.

## 🔥 Features

- 🔐 User Signup & Login Authentication
- 🌐 Enter any valid URL and view the webpage inside an iframe
- 🤖 Chat interface powered by Gemini, trained to answer questions **only** about the entered website
- 🧠 Backend uses **Selenium** to fetch full HTML content of the webpage for private analysis
- 🧭 Navigation bar with multiple pages:
  - **Home** – URL Input and Analyzer
  - **Features** – Key highlights of the analyzer
  - **Pricing** – Subscription plans (static demo)
  - **Contact** – Random contact info
  - **Documentation** – Full documentation with light/dark theme toggle

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Flask
- Selenium
- Chrome WebDriver
- OpenAI Gemini API (or mock integration)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/chat-ai-web-analyzer.git
cd chat-ai-web-analyzer
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
pip install -r requirements.txt
python app.py
chat-ai-web-analyzer/

├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── url_input.html
│   ├── chat.html
│   ├── features.html
│   ├── pricing.html
│   ├── contact.html
│   └── documentation.html
├── app.py
└── README.md
