
---

## 🛠️ Prerequisites

To run this project, you need:

- **Python 3.10+**
- **pip** (Python’s package manager)

---

## 🐍 Setting Up Your Environment

Before running the project, you should set up a virtual environment (this keeps your project dependencies isolated).

Run these commands:

For **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
For Linux/Mac:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate
Once the virtual environment is activated, install all required libraries:

bash
Copy
Edit
pip install -r requirements.txt
⚙️ Configuration (Setting up .env file)
Create a file called .env in the root folder (same place as app1.py). This file will contain all your secret settings and API keys.

Example .env file (you can customize it for your needs):

ini
Copy
Edit
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///your_database.db
WHATSAPP_API_KEY=your_whatsapp_api_key_here
DEBUG=True
Never commit your .env file to GitHub!

🚀 Running the Web Application
To start the web application, run:

bash
Copy
Edit
python app1.py
The application will typically run on:

arduino
Copy
Edit
http://localhost:5000
You can open this in your browser to view the web app.

💬 Running the WhatsApp Bot
To run the WhatsApp bot (which is a separate script), run:

bash
Copy
Edit
python whatsapp_bot.py
Make sure your .env file has the necessary WhatsApp API key and any other bot settings.

👥 Contributing
Want to contribute? Follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature-name).
Make your changes.
Commit and push (git commit -m "Add your feature" and git push origin your-branch-name).
Open a Pull Request.

