import argparse
import os
import sys
import psycopg2 # Python library for database connection
from psycopg2 import OperationalError, errorcodes, errors
import logging
import json


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger



def debug(*args):
    if os.getenv('CHECK_PSQL_TABLES', True):
        print(*args)


def get_users(db_conn):
    logger.info('Executing get_users Function')
    db_cursor = db_conn.cursor()
    db_cursor.execute("""SELECT usename AS role_name
    FROM pg_catalog.pg_user;""" )
    users = db_cursor.fetchall()
    logger.info('########## The available users in db : ' + str(users))
    return users

def check_table_for_user(db_conn,userName):
    logger.info('Executing check_table_for_user Function')
    db_cursor = db_conn.cursor()
    db_cursor.execute("SELECT tablename FROM pg_tables t WHERE t.tableowner = '{user}' and t.schemaname = 'public';".format(user=userName))
    all_tables = db_cursor.fetchall()
    logger.info("Avalaible tables for the user {user} : ".format(user=userName) + str(all_tables))
    for tables in all_tables:
        logger.info("Check the table : "+tables[0])
        try:
            logger.info('######## Selecting rows from table {table} for the User {user} from database {database}'.format(table=tables[0],user=userName,database=db_name))
            db_cursor.execute('SELECT * from \"{table}\" limit 20'.format(table=tables[0]))
            logger.info("The number of Rows available in the TABLE {table} : ".format(table=tables[0]) + str(db_cursor.rowcount))
            row = db_cursor.fetchone()

            while row is not None:
                #print(row)
                row = db_cursor.fetchone()
        except Exception as err:
            error_logger.error ('Exception occured while reading the TABLE {table} for the User {user} from the database {database}'.format(table=tables[0],user=userName,database=db_name))
            print_psycopg2_exception(err)
            db_conn.rollback()


def print_psycopg2_exception(err):
    logger.info(' ******** Exception Found , Please check error.log file for detailed information ***********')
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    error_logger.error ("\npsycopg2 ERROR:" + str(err) + "on line number:" + str(line_num))
    error_logger.error ("psycopg2 traceback: " + str(traceback) + "-- type:" +  str(err_type))

    # psycopg2 extensions.Diagnostics object attribute
    error_logger.error ("\nextensions.Diagnostics: " + str(err.diag))

    # print the pgcode and pgerror exceptions
    error_logger.error ("pgerror:" + str(err.pgerror))
    error_logger.error ("pgcode:" + str(err.pgcode) + "\n")

def check_postgres_tables(un,pw,hn,db_name):
    logger.info('Executing check_postgres_tables Function')
    db_conn = psycopg2.connect(database = db_name, user = un, password=pw, host=hn)
    #db_conn.autocommit = True
    #db_cursor = db_conn.cursor()
    users = get_users(db_conn)
    for user in users:
        check_table_for_user(db_conn,user[0])
    
    if db_conn is not None:
        db_conn.close()
        logger.info('<<<<<<< Execution Completed >>>>>>>>')


if __name__ == '__main__':
    logger = setup_logger('first_logger', 'debug.log')
    error_logger = setup_logger('error_logger', 'error.log')
    
    with open('postgres_config.json', 'r') as f:
        postgres_db_details = json.load(f)
        
    print("Execution Started ...Please don't terminate the execution")
    logger.info('<<<<<<<<<<< Starting the Execution >>>>>>>>>>>')
    
    parser = argparse.ArgumentParser(
        description='Find rows in a table that have corrupted TOAST values.'
    )
    parser.add_argument('--psql-server', required=True)
    args = parser.parse_args()
    global db_name
    if (args.psql_server) == "etp_perf_psql":
        hn = postgres_db_details['etp_perf_psql']['hostname']
        un = postgres_db_details['etp_perf_psql']['username']
        pw = postgres_db_details['etp_perf_psql']['password']
        for db in postgres_db_details['etp_perf_psql']['db_list']:
            logger.info("<<<<<<<<<<<< Connecting to Data base : {database} >>>>>>>>>>>>>>".format(database=db))
            print("Validating the Database: " + db)
            db_name = db
            check_postgres_tables(un,pw,hn,db)
    
    
