import sqlite3
import os
from os.path import split, getsize, join, isfile
from shutil import copytree, rmtree
import datetime
from buddy_log_entry import *
from buddy_summary import *
from buddy_list import BuddyListCtrl

import wx
import sys
import wx.lib.plot as plot

class Lumos(wx.App):
  ACCTS = [['AIM', 'cyenatwork'], ['AIM', 'thensheburns'], ['GTalk','christineyen@gmail.com'], ['GTalk', 'temp']]
  CURRENT_ACCT = ACCTS[1]
  path = os.path.join('/Users', 'cyen', 'Library', 'Application Support', 'Adium 2.0', 'Users', 'Default', 'LogsBackup', '.'.join(CURRENT_ACCT))
  db_path = os.path.join('/Users', 'cyen', 'Library', 'Preferences', 'lumos', 'Local Store', 'db', '.'.join(CURRENT_ACCT)+'.db')
  acct_logs = os.listdir(path)

  def OnInit(self):
    self.conn = self.one_time_setup()
    user_id = get_user_id(self.conn, self.CURRENT_ACCT[-1])
    all = get_all_buddy_summaries(self.conn, user_id)

    frame = wx.Frame(None, -1, 'simpleeeee', None, wx.Size(780, 540))
    frame.CreateStatusBar()

    box = wx.BoxSizer(wx.HORIZONTAL)
    # list nonsense
    lst = BuddyListCtrl(frame, [(bs.buddy_sn, str(bs.size), bs.start_time.ctime()) for bs in all])
    box.Add(lst, 2, wx.EXPAND | wx.ALL, 3)
    # graphing nonsense
    data = [(1,2), (2,3), (3, 5), (4, 5), (5, 8), (6, 10)]
    data2 = [(1, 4), (2, 0), (3, 10), (4, 5), (5, 7), (6, 2)]
    client = plot.PlotCanvas(frame)
    line = plot.PolyLine(data, legend='blue', colour='midnight blue', width=1)
    line2 = plot.PolyLine(data2, legend='green', colour='green', width=1)
    gc = plot.PlotGraphics([line, line2], 'Line', 'X axiss', 'Y axis')
    client.SetEnableLegend(True)
    client.SetFontSizeLegend(10)
    client.Draw(gc, xAxis=(0, 8), yAxis=(0, 15))

    box.Add(client, 3, wx.EXPAND)

    frame.SetSizer(box)

    frame.Center()
    frame.Show()
    return True

  def one_time_setup(self):
    if os.path.exists(self.db_path):
      conn = sqlite3.connect(self.db_path)
      conn.row_factory = sqlite3.Row
      self.update_from_logs(conn)
      return conn

    db_parent = os.path.dirname(self.db_path)
    if not os.path.exists(db_parent):
      os.mkdirs(db_parent)
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    self.setup_db(conn)
    self.convert_new_format() # todo: EARLY RETURN! find a way to check need for this
    self.update_from_logs(conn)
    return conn
 
  def setup_db(self, conn):
    conn.executescript('''create table if not exists users
      (id integer primary key, screenname text);''')
    conn.executescript('''create table if not exists conversations
      (id integer primary key, user_id integer, buddy_id integer,
      size integer, initiated boolean, msgs_user integer, msgs_buddy integer,
      start_time float, end_time float, timestamp float, file_path string);''')
    conn.executescript('''create unique index if not exists user_start_time
      on conversations(buddy_id, start_time, end_time);''')

  def convert_new_format(self):
    """ Converts old *****.chatlog file to *****.chatlog/*****.xml format,
        removes .DS_Store fields """
    print '''Backing up your logs...''' + self.path
    return


    try:
      copytree(self.path, self.path+'.bk')
      print '''Converting chatlog structures...'''
      for username in self.acct_logs:
        if username == '.DS_Store': continue
        for dir_entry in os.listdir(join(self.path, username)):
          chatlog = join(self.path, username, dir_entry)
          if dir_entry == '.DS_Store': os.remove(chatlog); continue
          if isfile(chatlog):
            dir, fn = split(chatlog)
            os.rename(chatlog, chatlog+'2')
            os.renames(chatlog+'2', join(dir, fn, fn.rsplit('.',1)[0]+'.xml'))
      rmtree(self.path+'.bk')
    except OSError:
      print 'Backup already exists. Did the process not finish last time?'

  def update_from_logs(self, conn):
    for username in self.acct_logs:
      if username[0] == '.': continue
      cur = conn.cursor()
      cur.execute('''select max(timestamp)
        from conversations inner join users on users.id = conversations.buddy_id
        where users.screenname = ? limit 1''', (username,))
      ts = cur.fetchone()
      if ts is None:
        last_file_ts = 0
      else:
        last_file_ts = ts[0]

      if last_file_ts >= os.stat(join(self.path, username)).st_mtime: continue
      print 'updating db for '+username

      for root, dirs, files in os.walk(join(self.path, username)):
        if not files: continue # empty dir
        for name in files:
          if name.find('.swp') > -1: continue
          if last_file_ts >= os.stat(join(root, name)).st_mtime: continue
          create_buddy_log_entry(conn, self.CURRENT_ACCT[-1], username, join(root, name))

if __name__ == '__main__':
  l = Lumos(redirect=False)
  l.MainLoop()
