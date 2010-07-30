"""A utility module to fetch the appropriate chunks of data from sqlite"""
# todo: kill this module, stick methods somewhere that makes more sense

import sqlite3
import datetime
import os
from os.path import split, getsize, join, isfile
from shutil import copytree, rmtree

import wx

sns_to_ids = {}
ACCTS = [['AIM', 'cyenatwork'], ['AIM', 'thensheburns'],
         ['GTalk','christineyen@gmail.com']]
CURRENT_ACCT = ACCTS[0]
path = os.path.join('/Users', 'cyen', 'Library', 'Application Support',
                    'Adium 2.0', 'Users', 'Default', 'LogsBackup',
                    '.'.join(CURRENT_ACCT))
db_path = os.path.join('/Users', 'cyen', 'Library', 'Preferences', 'lumos',
                       'Local Store', 'db', '.'.join(CURRENT_ACCT)+'.db')
acct_logs = os.listdir(path)

def get_user_id(conn, screen_name):
    if screen_name in sns_to_ids: return sns_to_ids[screen_name]

    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE screenname = ? LIMIT 1',
                (screen_name,))
    row = cur.fetchone()
    if row is None:
        cur.execute('INSERT INTO users (screenname) VALUES (?)', (screen_name,))
        cur.execute('SELECT id FROM users WHERE screenname = ? LIMIT 1',
                    (screen_name,))
        row = cur.fetchone()
    sns_to_ids[screen_name] = row[0]
    return row[0]

def get_connection():
    if not os.path.exists(db_path):
        db_parent = os.path.dirname(db_path)
        if not os.path.exists(db_parent):
            os.makedirs(db_parent)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    setup_db(conn)
    update_from_logs(conn)
    return conn

def setup_db(conn):
    conn.executescript('''create table if not exists users
                       (id integer primary key, screenname text);''')
    conn.executescript('''create table if not exists conversations
                       (id integer primary key, user_id integer,
                       buddy_id integer, size integer, initiated boolean,
                       msgs_user integer, msgs_buddy integer,
                       start_time float, end_time float, timestamp float,
                       file_path string);''')
    conn.executescript('''create unique index if not exists user_start_time
                       on conversations(buddy_id, start_time, end_time);''')

def update_database(callback):
    # todo: EARLY RETURN! find a way to check need for this
    conn = get_connection()
    convert_new_format()
    update_from_logs(conn)
    conn.close()
    wx.CallAfter(callback)

def convert_new_format():
    """ Converts old *****.chatlog file to *****.chatlog/*****.xml format,
        removes .DS_Store fields """
    print '''Backing up your logs...''' + path
    return False # todo re-allow

    try:
        copytree(path, path+'.bk')
        print '''Converting chatlog structures...'''
        for username in acct_logs:
            if username == '.DS_Store': continue
            for dir_entry in os.listdir(join(path, username)):
                chatlog = join(path, username, dir_entry)
                if dir_entry == '.DS_Store': os.remove(chatlog); continue
                if isfile(chatlog):
                    dir, fn = split(chatlog)
                    os.rename(chatlog, chatlog+'2')
                    os.renames(chatlog+'2',
                               join(dir, fn, fn.rsplit('.',1)[0]+'.xml'))
        rmtree(path+'.bk')
    except OSError:
        print 'Backup already exists. Did the process not finish last time?'

def update_from_logs(conn):
    for username in acct_logs:
        if username[0] == '.': continue
        cur = conn.cursor()
        cur.execute('''select max(timestamp) from conversations inner join
                    users on users.id = conversations.buddy_id where
                    users.screenname = ? limit 1''', (username,))
        ts = cur.fetchone()
        if ts is None:
            last_file_ts = 0
        else:
            last_file_ts = ts[0]

        if last_file_ts >= os.stat(join(path, username)).st_mtime:
            continue
        print 'updating db for '+username

        for root, dirs, files in os.walk(join(path, username)):
            if not files: continue # empty dir
            for name in files:
                if name.find('.swp') > -1: continue
                if last_file_ts >= os.stat(join(root, name)).st_mtime:
                    continue
                buddy_log_entry.create(conn, CURRENT_ACCT[-1],
                                       username, join(root, name))
