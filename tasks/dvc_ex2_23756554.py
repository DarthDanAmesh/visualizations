# Activate the proper environment
# Import necessary dependencies

import pandas as pd
from bokeh.plotting import figure 
from bokeh.io import output_file, save
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, GroupFilter, \
    HoverTool, LinearAxis, NumeralTickFormatter, Range1d, RangeTool

# Task 1: Prepare the Data

# The weekly stock data of META, AAPL, GOOGL, MSFT, AMZN (MAGMA) from 1/1/2019 to 27/12/2022
stock_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM1scE44za7xyuheW_FrUkdSdOKipDgDOWa_03ixmJCWK_ReSqhjzax66nNHyDKARXWIXgFI_EW9X/pub?gid=1661368486&single=true&output=csv'
stock = pd.read_csv(stock_url)

## 1.1: Convert the data type of time columns to datetime using "to_datetime()"

# Column 'Date' in stock
stock['Date'] =  pd.to_datetime(stock['Date'], format="%m/%d/%Y")

# Task 2: Create A Candlestick Chart From the Stock Data

# https://docs.bokeh.org/en/latest/docs/user_guide/topics/timeseries.html#candlestick-chart

## 2.1 Create the data source and set the basic properties of the figure

# Use ColumnDataSource to create the data source
# The dataframe is not directly used as source here
# because you'll use CDSView filter later
# which works with ColumnDataSource


TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

source = ColumnDataSource(stock)

p = figure(
    width=1200, 
    height=300, 
    title='META',
    # Specify the x range to be (min date, max date)
    # so that you can refer to this range in other plots
     x_range=(stock['Date'].min(), stock['Date'].max()),
    # Set the x axis to show date time
    x_axis_type='datetime',
    # Put the x axis to be at the top of the plot
    x_axis_location = 'above',
    background_fill_color='#fbfbfb',
    tools=TOOLS,
    toolbar_location='right'
)

p.xgrid.grid_line_color='#e5e5e5'
p.ygrid.grid_line_alpha=0.5
p.xaxis.major_label_text_font_size = '12px'
p.yaxis.axis_label = 'Stock Price in USD'
p.yaxis.formatter = NumeralTickFormatter(format="0.0")

## 2.2: Manually set the y axis range 

# Make it larger than the (min, max) range of the data
# e.g. (min * 0.9, max * 1.1)
# https://docs.bokeh.org/en/latest/docs/reference/models/ranges.html

p.y_range.start = stock['Low'].min() * 0.9
p.y_range.end = stock['High'].max() * 1.1

## 2.3: Use CDSView to create two filters on the stock data

# 'inc' keeps the data where the close price is higher than the open price
# 'dec' does the opposite of 'inc' 
# https://docs.bokeh.org/en/latest/docs/user_guide/basic/data.html#filtering-data

inc = stock['Close'] > stock['Open']
dec = stock['Close'] < stock['Open']

filter = GroupFilter(column_name="Symbol", group="META")

inc_view = CDSView(filter=BooleanFilter(inc) & filter)
dec_view = CDSView(filter=BooleanFilter(dec) & filter)

## 2.4: Draw the glyphs in the candlesticks

# A candlestick consists of a segment and a vbar

# Set the width of the vbar
# Note that the unit of datetime axis is milliseconds
# while the interval of the stock data is week

# set width, 7 days in milliseconds
w = 7 * 24 * 60 * 60 * 1000

# Draw the segement and the vbar
# inc vbars are green, dec vbars are red

p.segment('Date', 'High', 'Date', 'Low', color='grey', source=source, view=inc_view)
p.vbar('Date', w, 'Open', 'Close', fill_color="green", line_color="#49a3a3", line_width=0.2, source=source, view=inc_view)

p.segment('Date', 'High', 'Date', 'Low', color='grey', source=source, view=dec_view)
p.vbar('Date', w, 'Open', 'Close', fill_color="red", line_color="#49a3a3", line_width=0.2, source=source, view=dec_view)

## 2.5: Add volume bars in the candlestick chart

# Note that volume data is different from stock price data in unit and scale
# You'll create a twin y axis for volume on the right side of the chart
# https://docs.bokeh.org/en/latest/docs/user_guide/basic/axes.html
# https://docs.bokeh.org/en/latest/docs/reference/models/axes.html#bokeh.models.LinearAxis

y_volume = stock['Volume']
p.extra_y_ranges['volume'] = Range1d(start=stock['Volume'].min(), end=stock['Volume'].max())

y_volume_axis = LinearAxis(
    y_range_name='volume',
    axis_label= 'Volume',
    # Set the format of this y axis to display large number in short form
    # e.g. 1,000,000 : 1m
    formatter = NumeralTickFormatter(format=" 0 a")
)

p.add_layout(y_volume_axis, 'right')

stock_volume = p.vbar(
    'Date', 0.5, 'Volume', fill_color='grey', line_color='grey', source=source, y_range_name='volume'
)

## 2.6: Add a hover tool for the candlesticks

# https://stackoverflow.com/questions/61175554/how-to-get-bokeh-hovertool-working-for-candlesticks-chart
hover_stock = HoverTool()
hover_stock.tooltips=[
    ('Date', '@Date{%Y-%m-%d}'),
    ('Open', '@Open{0.00}'),
    ('Close', '@Close{0.00}'),
    ('High', '@High{0.00}'),
    ('Low', '@Low{0.00}'),
    ('Volume', '@Volume{0 }')
]

hover_stock.formatters={
    '@Date': 'datetime',
}

# This hover tool only shows tooltips on the vbars in the candlesticks, thus you need to specify the renderers
hover_stock.renderers = p.renderers

p.add_tools(hover_stock)

p.output_backend = 'svg'

# Task 3: Add a Range Selection Plot

# Add a plot with a range tool to select and zoom 
# a region in the candlestick chart
# https://docs.bokeh.org/en/latest/docs/user_guide/topics/timeseries.html#range-tool

# fliter data for the 'META' stock
meta_stock = stock[stock['Symbol'] == 'META']

# ColumnDataSource using 'Date' and 'Adj Close' 
source_meta = ColumnDataSource(data=dict(date=meta_stock['Date'], close=meta_stock['Adj Close']))

select = figure(
    height=130, width=1200,
    y_range=p.y_range, 
    x_axis_type ='datetime',
    y_axis_type =None,
    tools=TOOLS, toolbar_location=None, title=None,
    background_fill_color='#efefef'
)

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = 'navy'
range_tool.overlay.fill_alpha = 0.2

select.line(
    'date', 'close', source=source_meta
)

select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = 'auto'
select.output_backend = 'svg'

# Put the candlestick chart and the range plot in a column 
# with responsive sizing in width
# https://docs.bokeh.org/en/latest/docs/user_guide/basic/layouts.html
_p = column(
   p, select,
    sizing_mode = 'stretch_width'
)

# Example output
output_file('dvc_ex2.html')
save(_p)