from datetime import datetime
from matplotlib import dates

import wx

import lumos.events
import lumos.view.plotter

class QuantityPlotter(lumos.view.plotter.Plotter):
    # ViewType
    BYTES = 0
    MSGS = 1
    CONVERSATIONS = 2

    def __init__(self, parent, application):
        self.view_type = self.view_types().items()[0][1]
        self.app = application

        lumos.view.plotter.Plotter.__init__(
            self, parent, "Quantity of logs accumulated over time")

        options = lumos.view.plotter.Options(self,
            label='cumulative:',
            view_types=self.view_types().keys(),
            event_class=lumos.events.QuantitySettingsEvent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 14, wx.EXPAND)
        self.sizer.Add(options, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Bind(lumos.events.EVT_QUANTITY_SETTINGS, self.on_settings_change)


    def draw(self, buddy_sns=[], ble_entries=[]):
        ''' Draws a plot based on the size of conversations. '''
        axes = self.figure.gca()
        for ble_list in ble_entries:
            if len(ble_list) == 0: continue
            x, y = self.data_by_type(ble_list)

            axes.plot_date(dates.date2num(x), y,
                linestyle='-',
                marker='o', markeredgewidth=0,
                color=self.color_for_sn(ble_list[0].buddy_sn))
        axes.get_xaxis().set_major_formatter(lumos.view.plotter.FORMATTER)
        self.figure.legend(axes.get_lines(), buddy_sns, 'upper left',
            prop={'size': 'small'})
        self.figure.canvas.draw()

    def data_by_type(self, ble_list):
        ''' Returns lists  of x and y coordinates based on the current view_type.

            @param ble_list A list of BuddyLogEntrys for a given user.
            '''
        x = []; y = []
        for i, e in enumerate(ble_list):
            x.append(datetime.fromtimestamp(e.start_time))
            if self.view_type == QuantityPlotter.BYTES:
                y.append(e.size)
            elif self.view_type == QuantityPlotter.MSGS:
                y.append(e.cumu_msgs_ct)
            elif self.view_type == QuantityPlotter.CONVERSATIONS:
                y.append(i)

        # add a point to connect it to the x axis
        x.insert(0, x[0])
        y.insert(0, 0)

        if self.app.debug: self.print_debug_info(ble_list, x, y)

        return x, y

    def view_types(self):
        ''' Used to map the label text to a ViewType. '''
        return {
            'bytes': QuantityPlotter.BYTES,
            'msgs': QuantityPlotter.MSGS,
            'conversations': QuantityPlotter.CONVERSATIONS
        }

