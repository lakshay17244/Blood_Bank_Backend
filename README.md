# Blood_Bank_Backend

### Getting Started

The Blood_Bank_Backend is based on with Python with flask server coupled with MySQL server. 

### Installing

1. Install requirements.txt

```
pip install -r requirements.txt
pip install mysql-connector-python
```

2. Run CreateTables.sql in your SQL Workbench

3. Run Populate.py to populate data

4. Open app.py and configure the following with your own Workbench Credentials

```
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dbms_123'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'ConnectGroup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
```

5. Run flask server

For CMD, type -
```bash
python app.py
```
For Anaconda/Linux type - 
```
flask run
```
### Contributors

| [![Lakshay Sharma](https://github.com/lakshay17244.png?size=100)](https://github.com/lakshay17244) | [![Jay Rawal](https://github.com/jayr1305.png?size=100)](https://github.com/jayr1305) |
| --- | --- |
| [Lakshay Sharma](https://github.com/lakshay17244) | [Jay Rawal](https://github.com/jayr1305) |
