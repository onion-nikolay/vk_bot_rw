import sqlite3
from os.path import join as pjoin


def read_sql_script(script_name):
    with open(pjoin('sql', script_name+'.sql')) as f:
        return ''.join(f.readlines())


def db_read(db, script_name, **params):
    sql_command = read_sql_script(script_name)
    if len(params) > 0:
        sql_command = sql_command.format(**params)
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute(sql_command)
    return cursor.fetchall()


def db_write(db, script_name, **params):
    sql_command = read_sql_script(script_name)
    if len(params) > 0:
        sql_command = sql_command.format(**params)
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute(sql_command)
    connection.commit()
    connection.close()
