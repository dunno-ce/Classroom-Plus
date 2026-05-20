What’s in the ZIP (and what’s missing)
Included: Django source, requirements.txt, templates, migrations.

Not included (by design):
Missing	Effect
.env
No API keys — AI chat won’t work until they add one
db.sqlite3
Empty database — no notes, recordings, or tests until they add data
media/
No uploaded files

They create their own Virtualenv

Step-by-step setup
1. Prerequisites
Python 3.9+ (3.10 or 3.11 is fine)
pip
A Groq API key if they want the AI chatbot (console.groq.com)
2. Unzip and open the project
After unzip, the folder is usually something like Classroom-Plus-main. They should cd into the folder that contains manage.py.

3. Create and activate a virtual environment
macOS / Linux:
python3 -m venv venv
source venv/bin/activate
Windows:
python -m venv venv
venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt
That installs Django 4.2 and packages such as groq, python-dotenv, etc.

5. Create a .env file
In the same folder as manage.py, create .env:

GROQ_API_KEY=their_groq_api_key_here 
Important: The app’s chatbot uses Groq, not Gemini. settings.py defines GEMINI_*, but chat/views.py only calls Groq. Without GROQ_API_KEY, the site loads but AI chat returns an error.

6. Set up the database
python manage.py migrate
That creates a new db.sqlite3 with empty tables. They start with no notes, recordings, or tests.

7. (Optional) Django admin user
python manage.py createsuperuser
Then they can use http://127.0.0.1:8000/admin/.

8. Run the server
python manage.py runserver
Open http://127.0.0.1:8000/ in a browser.

What works vs what needs extra setup
Feature	Works after basic setup?
Home page, subject pages
Yes
Upload notes / recordings / tests
Yes (files go into media/, created on upload)
AI classroom assistant
Only if GROQ_API_KEY is set in .env
Your existing class content
No — they’d need your DB + media/ separately

Common issues
ModuleNotFoundError: django — venv not activated or pip install not run.
AI shows “Unavailable” — missing or wrong GROQ_API_KEY in .env (restart server after editing .env).
Port in use — python manage.py runserver 8001
Wrong folder — run commands where manage.py lives.


