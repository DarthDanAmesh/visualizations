# Activate the bokeh environment
# You may refer to:
# bokeh tutorial 00 - Introduction and Setup - Getting set up

# Import dependencies
import pandas as pd
from bokeh.plotting import figure 
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, NumeralTickFormatter
from bokeh.transform import factor_cmap
import numpy as np

# Task 1: Prepare the Data

## 1.1: Use pandas to read a csv file into a dataframe from a link

# You may refer to:
# https://pythoninoffice.com/how-to-read-google-sheet-into-pandas/

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQdNgN-88U31tk1yQytaJdmoLrxuFn1LnbwTubwCd8se2aHh8656xLLHzxHSoiaXMUu8rIcu6gMj5Oq/pub?gid=1242961990&single=true&output=csv'
MAGMA_financials = pd.read_csv(url)

## 1.2: Inspect the columns in the dataframe

# 'Symbol': 
# The stock ticker symbols of five companies
# META, AAPL, GOOGL, MSFT, AMZN 
# You may refer to https://pandas.pydata.org/docs/reference/api/pandas.unique.html
# In order to correspond companies to the right net income values, you have to sort the symbols.

# 'Quarter Ended': 
# The time when the companies filed their quarterly financial statements to SEC
# from 2019Q1 to 2022Q4

# 'Net Income':
# The column you need to visualize

symbols = list(MAGMA_financials['Symbol'])


# use the below for ploting the bar graph
symbols_unique = MAGMA_financials['Symbol'].unique().tolist()

## 1.3: Create a nested categorical coordinate

# To see the trend, you'll use 'Quarter Ended' in the x axis
# Each item has 16 quarters' data, and each quarter has a subset of items
# To make the x axis clear and readable, 
# you'll create a nested (hierarchical) categorical coordinate as x
# Namely, it will group the bars in nested levels of (year, quarter, item)
# e.g. x = [ ('2019', 'Q1', 'item 1'),  ('2019', 'Q1', 'item 2'), ...]

# You may refer to:
# bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts

years = ['2019', '2020', '2021', '2022']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
x = []
y = []

for _, row in MAGMA_financials.iterrows():
    quarter_ended = row['Quarter Ended']
    year, quarter = quarter_ended[:4], quarter_ended[4:]
    symbol = row['Symbol']
    net_income = row['Net Income']
    x.append((year, quarter, symbol))
    y.append(net_income)

# using list comprehension and pandas methods
x = [(row['Quarter Ended'][:4], row['Quarter Ended'][4:], row['Symbol'])
     for _, row in MAGMA_financials.iterrows()]
y = MAGMA_financials['Net Income'].tolist()

## 1.4: Use ColumnDataSource to generate data sources

# You may refer to:
# bokeh tutorial 03 - Data Sources and Transformations - Creating with Python Dicts

# To relate x to the right y, you have to reorder the value in column 'Net Income'
df = MAGMA_financials.sort_values(by = ['Symbol', 'Quarter Ended'])

# Flatten the 'Net Income' data to a 1d list as y
    # corresponding to the nested categorical coordinate of x axis
    # You may refer to:
    # https://www.datasciencelearner.com/flatten-dataframe-in-pandas-methods/
# y = list(...)
y = list(np.array(df['Net Income']).reshape(-1))



#print("Printing x")
#print(len(x))

#print("Printing y")
#print(len(y))

#print("Printing not x and y")
#print(len(symbols))

x_label =  'Symbol-Quarter'
source = ColumnDataSource(data = dict(x=x, y=y, label=symbols))



# Task 2: Draw the Bar Chart

## 2.1: Configure the settings of the figure 

# Set the width and hight of the figure
# You'll add a hover tool later, for now set the tools to empty

p = figure(
    # Use FactorRange to create the x_range
    # You may refer to:
    # bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts
    x_range=FactorRange(factors=x),
    height = 200,
    width = 700,
    tools = '',
    title='Net Income', 
    
)
 # Set the x grid line 
p.xgrid.grid_line_color = None

# Pad the x range 
p.x_range.range_padding = 0.12

# You'll use the legend group to show the item names of the bars
# So hide the default labels and ticks on x axis
# You may refer to:
# bokeh tutorial 02 - Styling and Theming - Axes

# Set the x major text font size to hide the labels on x axis
p.xaxis.major_label_text_font_size = '0.8pt'

# Set the x major tick line color 
p.xaxis.major_tick_line_color = None

# Set the y axis label to 'millions USD'
p.yaxis.axis_label = 'millions USD'

# Use NumeralTickFormatter to a comma as the thousand separator
p.yaxis.formatter = NumeralTickFormatter(format="0,0")

## 2.2: Configure the bar glyphs
p.vbar(
        x='x', top='y', width=1, 
        source=source,
        # Use the column 'label' in the data source as the legend group
        legend_group='label',
        line_color='gray',
         # Use factor_cmap to assign colors to bars accroding to their item names
            # You may refer to:
            # bokeh tutorial 07 - Bar and Categorical Data Plots - Grouped Bar Charts
        fill_color=factor_cmap(
           'label', palette=['royalblue', 'blue', 'green', 'yellow', 'pink'], 
            factors=symbols_unique, start = 2, end = 3
        )
      )


## 2.3: Add a hover tool

    # When you hover over a bar, the tooltip will show (year, quarter, item: value)
    # Note that (year, quarter, item) is the nested categorical coordinate in x
    # and data is the value in y
    # The (label, value) tuple in the tooltip can be ('', 'value1 : value2') 
    # You may refer to:
    # https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
    # You can also format tooltips, e.g. add a comma as thousand separator to the value:
    # https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#formatting-tooltip-fields

p.add_tools(HoverTool(tooltips=[
    ("Year-Quarter", "@x"),
    ("Symbol", "@label"), 
    ("Net Income", "@y{0,0} millions USD")
]))

## 2.4: Add a legend

    # Set the legend label and glyph sizes
    # You may refer to:
    # https://stackoverflow.com/questions/29130098/how-do-you-change-size-of-labels-in-the-bokeh-legend-in-python
    
p.legend.label_text_font_size = '10pt'
p.legend.label_height = 18
p.legend.glyph_height = 15
p.legend.glyph_width = 23
# Set the legend orientation and location
p.legend.orientation = "horizontal"
p.legend.location = "top_left"
# Set the output_backend to preserve the resolution when zooming in
p.output_backend = "svg"


## 2.5: Save the bar chart to a html file with the filename 'dvc_ex1.html'

# You may refer to:
# bokeh tutorial 10 - Exporting and Embedding - Saving to an HTML File
output_file("dvc_ex1.html")
save(p)