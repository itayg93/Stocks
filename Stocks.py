import wx
import wx.adv
import wx.grid as gridlib
import pandas as pd
from pandas_datareader import data
import bs4 as bs
import pickle
import requests
import datetime

import Constants


class Stocks(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.InititalUI()

    def InititalUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # dates
        date_hbox = wx.BoxSizer(wx.HORIZONTAL)
        # from
        from_label = wx.StaticText(panel, -1, Constants.FROM_LABEL)
        date_hbox.Add(from_label, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        self.from_value = wx.adv.DatePickerCtrl(
            panel, 1, size=(120, 30))
        date_hbox.Add(self.from_value, 1, wx.EXPAND |
                      wx.ALIGN_LEFT | wx.ALL, 5)
        # till
        till_label = wx.StaticText(panel, -1, Constants.TILL_LABEL)
        date_hbox.Add(till_label, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        self.till_value = wx.adv.DatePickerCtrl(
            panel, 1, size=(120, 30))
        date_hbox.Add(self.till_value, 1, wx.EXPAND |
                      wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(date_hbox)
        # filters
        filters_hbox = wx.BoxSizer(wx.HORIZONTAL)
        market_cap_label = wx.StaticText(panel, -1, Constants.MARKET_CAP_LABEL)
        filters_hbox.Add(market_cap_label, 1, wx.EXPAND |
                         wx.ALIGN_LEFT | wx.ALL, 5)
        self.market_cap_text = wx.TextCtrl(panel, size=(30, 30))
        filters_hbox.Add(self.market_cap_text, 1, wx.EXPAND |
                         wx.ALIGN_LEFT | wx.ALL, 5)
        options = [Constants.M_LABEL, Constants.B_LABEL]
        self.options_combo = wx.ComboBox(
            panel, choices=options, style=wx.CB_READONLY)
        self.options_combo.Bind(wx.EVT_COMBOBOX, self.OnAmountSelect)
        filters_hbox.Add(self.options_combo, 1, wx.EXPAND |
                         wx.ALIGN_LEFT | wx.ALL, 5)
        percentage_label = wx.StaticText(panel, -1, Constants.PERCENTAGE_LABEL)
        filters_hbox.Add(percentage_label, 1, wx.EXPAND |
                         wx.ALIGN_LEFT | wx.ALL, 5)
        self.percentage_slider = wx.Slider(
            panel, value=60, minValue=60, maxValue=100, style=wx.SL_HORIZONTAL)
        self.percentage_slider.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        filters_hbox.Add(self.percentage_slider, 1,
                         wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        self.percentage_value = wx.StaticText(
            panel, label=Constants.DEFAULT_PERCENATGE)
        filters_hbox.Add(self.percentage_value, 1, wx.EXPAND |
                         wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(filters_hbox)
        # button
        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        analyze_btn = wx.Button(panel, wx.ID_ANY,
                                Constants.ANALYZE_LABEL, size=(90, 30))
        self.Bind(wx.EVT_BUTTON, self.OnAnalyze)
        button_hbox.Add(analyze_btn, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(button_hbox)
        # grid
        self.grid = gridlib.Grid(panel)
        self.grid.CreateGrid(100, 3)
        self.grid.SetColLabelValue(0, Constants.TICKER_LABEL)
        self.grid.SetColLabelValue(1, Constants.DIRECTION_LABEL)
        self.grid.SetColLabelValue(2, Constants.PERCENTAGE_LABEL)
        vbox.Add(self.grid, 1, wx.EXPAND, 5)
        # set sizer
        panel.SetSizer(vbox)
        # status bar
        self.status_bar = self.CreateStatusBar()

    def OnAmountSelect(self, event):
        self.amount_selection = event.GetString()

    def OnSliderScroll(self, event):
        value = event.GetEventObject().GetValue()
        self.percentage_value.SetLabel(str(value))

    def OnAnalyze(self, event):
        # initial tickers name
        with open("NasdaqTickers.pickle", "rb") as f:
            self.tickers_name = pickle.load(f)
        # extract dates
        start = self.from_value.GetValue()
        end = self.till_value.GetValue()
        self.from_date = datetime.datetime(int(start.GetYear()), int(
            start.GetMonth() + 1), int(start.GetDay()))
        self.till_date = datetime.datetime(
            int(end.GetYear()), int(end.GetMonth() + 1), int(end.GetDay()))
        # calculate market cap
        if self.amount_selection == Constants.M_LABEL:
            self.market_cap = int(
                self.market_cap_text.GetValue())*1000000
        elif self.amount_selection == Constants.B_LABEL:
            self.market_cap = int(
                self.market_cap_text.GetValue())*1000000000
        # extract percentage
        self.percentage = float(self.percentage_value.GetLabel())
        self.FetchTickersData()
        self.CalculateTickerRates()
        self.CalculateTickerPercentage()

    def FetchTickersData(self):
        self.tickers_data = []
        for ticker in self.tickers_name:
            current_ticker = ''.join(filter(str.isalnum, ticker))
            self.status_bar.SetStatusText(
                Constants.STATUS_BAR_LOADING_MESSAGE + current_ticker)
            try:
                # find ticker market cap value
                current_ticker_market_cap = data.get_quote_yahoo(
                    current_ticker)['marketCap'][0]
                # check if the value is bigger/equal to user market cap input
                if current_ticker_market_cap >= self.market_cap:
                    # fetch all ticker data
                    current_ticker_data = data.get_data_yahoo(
                        current_ticker, self.from_date, self.till_date)
                    # create a dictionary icluding the name, open and close rates
                    self.tickers_data.append(self.TickerAsDictionary(
                        current_ticker, current_ticker_data[Constants.OPEN_LABEL], current_ticker_data[Constants.CLOSE_LABEL]))
            except Exception as e:
                # wx.MessageBox(
                #    Constants.ERROR_MESSAGE,
                #    Constants.ERROR,
                #    wx.OK | wx.ICON_ERROR)
                print(str(e))
        self.status_bar.SetStatusText(Constants.DONE_LABEL)

    def TickerAsDictionary(self, ticker, open_rates, close_rates):
        ticker_dictionary = {
            Constants.TICKER_NAME: ticker,
            Constants.OPEN_RATES: open_rates,
            Constants.CLOSE_RATES: close_rates,
            Constants.UP_COUNTER: 0,
            Constants.DOWN_COUNTER: 0,
            Constants.DONT_COUNT: 0,
            Constants.TOTAL_AMOUNT: 0
        }
        return ticker_dictionary

    def CalculateTickerRates(self):
        for ticker in self.tickers_data:
            period = len(ticker.get(Constants.OPEN_RATES))
            day = 0
            while day < period:
                # check the percentage calculation
                # up
                if ticker.get(Constants.CLOSE_RATES)[day] > ticker.get(Constants.OPEN_RATES)[day]:
                    value = (ticker.get(Constants.CLOSE_RATES)[
                        day]-ticker.get(Constants.OPEN_RATES)[day]) * 100
                    value /= ticker.get(Constants.OPEN_RATES)[day]
                    # up will count only if the stock went up by 0.5% or above
                    if value > 0.5:
                        ticker[Constants.UP_COUNTER] += 1
                    else:
                        ticker[Constants.DONT_COUNT] += 1
                # down
                elif ticker.get(Constants.OPEN_RATES)[day] > ticker.get(Constants.CLOSE_RATES)[day]:
                    ticker[Constants.DOWN_COUNTER] += 1
                day += 1
            ticker[Constants.TOTAL_AMOUNT] = period - \
                ticker.get(Constants.DONT_COUNT)

    def CalculateTickerPercentage(self):
        row_index = 0
        for ticker in self.tickers_data:
            period = len(ticker.get(Constants.OPEN_RATES))
            ticker[Constants.UP_COUNTER] /= ticker.get(Constants.TOTAL_AMOUNT)
            ticker[Constants.UP_COUNTER] *= 100
            ticker[Constants.DOWN_COUNTER] /= ticker.get(
                Constants.TOTAL_AMOUNT)
            ticker[Constants.DOWN_COUNTER] *= 100
            if ticker[Constants.UP_COUNTER] >= self.percentage or ticker[Constants.DOWN_COUNTER] >= self.percentage:
                if ticker[Constants.UP_COUNTER] > ticker[Constants.DOWN_COUNTER]:
                    self.InsertTickerDataIntoGrid(row_index, ticker.get(Constants.TICKER_NAME), Constants.UP_LABEL,
                                                  str(round(ticker.get(Constants.UP_COUNTER), 2))+"%")
                elif ticker[Constants.DOWN_COUNTER] > ticker[Constants.UP_COUNTER]:
                    self.InsertTickerDataIntoGrid(row_index, ticker.get(Constants.TICKER_NAME), Constants.DOWN_LABEL,
                                                  str(round(ticker.get(Constants.DOWN_COUNTER), 2))+"%")
                row_index += 1

    def InsertTickerDataIntoGrid(self, row, ticker, direction, percentage):
        self.grid.SetCellValue(row, 0, ticker)
        self.grid.SetCellValue(row, 1, direction)
        self.grid.SetCellValue(row, 2, percentage)


def main():
    app = wx.App()
    stocks = Stocks().Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
