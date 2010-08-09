import matplotlib
matplotlib.use('WxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

# set matplotlib rc settings
matplotlib.rc('font', size=10.0)

import wx

import lumos.buddy_log_entry
import lumos.util

class Plotter(wx.Panel):

    def __init__(self, parent, application):
        wx.Panel.__init__(self, parent)
        self.app = application

        self.figure = matplotlib.figure.Figure(dpi=None, figsize=(2,2))
        self.figure.set_facecolor('white')
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)

        self.draw_blank()
        self.current_buddy_sn_list = []

    def fetch_log_entries_by_buddy(self, buddy_sns):
        ''' For each buddy_sn passed in via buddy_sns, return a list of
            BuddyLogEntrys.

            @param buddy_sns A list of strings representing buddy screen names.
            @return a list of lists, holding individual BuddyLogEntrys.
            '''
        user_id = lumos.util.get_user_id(self.app.conn, lumos.util.get_current_sn())

        all_entries = []
        for buddy_sn in buddy_sns:
            buddy_id = lumos.util.get_user_id(self.app.conn, buddy_sn)
            entries = lumos.buddy_log_entry.get_cumu_logs_for_user(
                self.app.conn, user_id, buddy_id, buddy_sn)
            all_entries.append(entries)

        return all_entries

    def update(self, buddy_sns):
        ''' The general 'update' logic for a plotter. Subclasses override
            draw() in order to provide unique behavior.

            @param buddy_sns A list of strings representing buddy screen names.
            '''
        if len(buddy_sns) == 0: return self.draw_blank()
        self.current_buddy_sn_list = buddy_sns

        # todo: decide how we feel about the view looking stuff up in the db
        # todo: consider moving some of this elsewhere, triggered by events
        ble_entries = self.fetch_log_entries_by_buddy(buddy_sns)

        self.figure.clear()
        self.figure.gca().clear()
        self.draw(buddy_sns=buddy_sns, ble_entries=ble_entries)

    def draw(self, buddy_sns=[], ble_entries=[]):
        ''' Override to define plotter-specific drawing behavior.'''
        pass # abstract

    def draw_blank(self):
        self.figure.clear()
        self.figure.text(0.05, 0.375, DRAW_BLANK_TEXT, fontsize=11, color='#333333')

    def get_min_max_for_axis(self, axis, data):
        idx = 0 if axis == 'x' else 1
        axis_data = [elt[idx] for elt in data]
        return [min(axis_data), max(axis_data)]

    def color_for_sn(self, buddy_sn):
        hsh = hash(buddy_sn)
        def norm(num):
            return num / 256.0
        return norm(hsh % 256), norm(hsh / 256 % 256), norm(hsh / 256 / 256 % 256)

    def print_debug_info(self, ble_list, x, y):
        print '%d chats w/ %s' % (len(ble_list), ble_list[0].buddy_sn)
        print 'x: ' + str(x)
        print 'y: ' + str(y)

DRAW_BLANK_TEXT= '''You have not selected any conversations to graph.\n
Please click on one or more buddy screen names on the left\n
to see results graphed in this space. '''