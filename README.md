# psql_health_check
Steps to Execute the Script.
1. Clone the repo to your machine and update postgres_config.json with hostname , Username, password and DB list details.(Better to user Super user credentials which has access to all the DB)
2. Before executing the script make sure you have connectivity between your local machine and Postgres VM.
3. Install required Python packges before executing the script "pip install -r requirements.txt"
4. Run the Python script python3 psql_health_check.py --psql-server 'psql_server_1'
5. This script will create 2 log files debug.log and error.log. All Errors/Exception will be updated in error.log

