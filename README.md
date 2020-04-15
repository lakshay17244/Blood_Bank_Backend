# Blood_Bank_Backend

To get started,

1) Install requirements.txt by

    pip install -r requirements.txt

2) Run CreateTables.sql in your SQL Workbench

3) Run Populate.py to populate data

4) Open app.py and replace the following with your own Workbench Credentials

    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'dbms_123'
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_DB'] = 'ConnectGroup'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

5) Open CMD, run flask server by typing

    flask run
