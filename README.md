# Popbots UNIVERSAL REST API  

# 1. To deploy:

## 1.1 Deploying given the database has been configured
- Create a python3 venv (see online tutorials) recommended name popbots_venv
- Activate the venv by doing: 
    > source "venv_name"/bin/activate
- install all the required packages by navigating into the popbots-refactor folder and running 
    > pip3 install -r requirements.txt

- Several environment variables are mandatory in order for the code to communicate with slack, telegram and the Postgres database (Contact the Administrator to obtain a file with all the neccessary env variables). Once you have the file:

    1. Copy all the environment variables in the ~/.bash_profile (they look like export VARNAME="something"), the bash_profile might not exist, just create it. 
        > sudo nano ~/.bash_profile 
    
    2. Source the newly created env variables 
        > source ~/.bash_profile 

## 1.2 Deploying the Postgres Database on your local machine (not mandatory)

- Install Postgres on your machine
- Create a Database user and password 
- Create a database with a corresponding name and password
- Edit the .ini file (in models/core/database.ini) and complete all fiels accordingly (if you are working on your local machine, host will be localhost) 
- Create the tables with the file models/core/create_tables.py
- I recommend using DBEAVER to view and monitor database (https://dbeaver.io/download/)

# 1.3 Running the code/telegram/slack sockets

If you are just testing you can just run the python or telegram script like so:
- Activate the venv by doing: 
    > source "venv_name"/bin/activate
- Run the code
    > python3 telegram_socket.py
    or
    > python3 slack_socket.py

In deployment we will use PM2 as a process manager, for logs and also restarting the APP in case it crashes

- For installation (see instructions here : https://blog.pm2.io/2018-09-19/Manage-Python-Processes/)



# REST API structure

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