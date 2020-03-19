1. To deploy:

- Create a python venv
- Activate the venv by doing 
> source venv_name/bin/activate
- install all the required packages by navigating into the popbots-refactor folder and running 
> pip3 install -r requirements.txt




```
popbots-refactor

├─ .gitignore
├─ .spyproject
│  ├─ codestyle.ini
│  ├─ encoding.ini
│  ├─ vcs.ini
│  └─ workspace.ini
├─ __pycache__
│  ├─ main.cpython-37.pyc
│  ├─ message.cpython-37.pyc
│  └─ utils.cpython-37.pyc
├─ controllers
│  ├─ __pycache__
│  │  ├─ main.cpython-37.pyc
│  │  └─ message.cpython-37.pyc
│  ├─ main.py
│  └─ message.py
├─ credentials
│  ├─ client_secret.json
│  ├─ credential.json
│  └─ credentials.json
├─ deprecated_scripts
│  ├─ bot_management.py
│  ├─ database_poc
│  │  ├─ bots_management.py
│  │  ├─ database.sqlite3
│  │  ├─ database_creation.py
│  │  ├─ database_operations.py
│  │  └─ main.py
│  ├─ messages_tree
│  │  ├─ csv_cleaner.py
│  │  ├─ example_data.csv
│  │  ├─ example_index.html
│  │  ├─ index.html
│  │  ├─ messages.csv
│  │  ├─ sample_messages.csv
│  │  ├─ tree_messages.csv
│  │  └─ tree_sample_messages.csv
│  ├─ populate_database.py
│  └─ populate_database_csv.py
├─ exceptions
│  ├─ __pycache__
│  │  └─ badinput.cpython-37.pyc
│  ├─ badinput.py
│  └─ userNotCreated.py
├─ img
│  ├─ checkin.png
│  ├─ chill.png
│  ├─ doom.png
│  ├─ dunno.png
│  ├─ glass.png
│  ├─ onboarding.png
│  ├─ sherlock.png
│  ├─ sirs.png
│  └─ treat.png
├─ models
│  ├─ __init__.py
│  ├─ __pycache__
│  │  ├─ __init__.cpython-37.pyc
│  │  ├─ conversation.cpython-37.pyc
│  │  ├─ database_operations.cpython-37.pyc
│  │  └─ user.cpython-37.pyc
│  ├─ connect.py
│  ├─ conversation.py
│  ├─ core
│  │  ├─ __pycache__
│  │  │  ├─ __init__.cpython-37.pyc
│  │  │  ├─ config.cpython-37.pyc
│  │  │  ├─ live_google_sheet.cpython-37.pyc
│  │  │  ├─ pushModels.cpython-37.pyc
│  │  │  ├─ sql_alchemy_core.cpython-37.pyc
│  │  │  └─ sqlalchemy_config.cpython-37.pyc
│  │  ├─ config.py
│  │  ├─ database.ini
│  │  ├─ database_localhost.ini
│  │  ├─ live_google_sheet.py
│  │  ├─ pushModels.py
│  │  └─ sqlalchemy_config.py
│  ├─ create_tables.py
│  ├─ database_operations.py
│  └─ user.py
├─ pip-install.sh
├─ populate_database_live.py
├─ readme.md
├─ requirements.txt
├─ slack_socket.py
├─ telegram_socket.py
├─ telegrame
│  ├─ __pycache__
│  │  └─ utils.cpython-37.pyc
│  ├─ token.txt
│  └─ utils.py
└─ utils.py

```