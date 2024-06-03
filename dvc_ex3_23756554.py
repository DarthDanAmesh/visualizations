# ====================================================================
# Goal: Build an interactive visualization app with Bokeh server

# Task 1: Dimension Reduction
# Task 2: Visualization
# Task 3: Interaction
# ====================================================================

# How to use Bokeh server to build application:
# https://docs.bokeh.org/en/latest/docs/user_guide/server/app.html

# To see the interactive visualization app,
# pleae run this script in the terminal with the command: 
#   bokeh serve --show YOURFILENAME.py/ipynb
# It will be opened in the browser: http://localhost:5006/YOURFILENAME.
# To stop the app, press ctrl+c in the terminal

# Setting up:
# This script runs with bokeh version 3.3.4
# For the dimension reduction and clustering tasks,
# please install sciket-learn: 
# https://scikit-learn.org/stable/install.html

# import packages for processing data
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_object_dtype
# import packages for principal component analysis and clustering
from sklearn.decomposition import PCA
# import packages for Multidimensional scaling
from sklearn.manifold import MDS
from sklearn.preprocessing import MinMaxScaler
from sklearn import cluster
from sklearn.impute import SimpleImputer
# import packages for visualization
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool, LassoSelectTool, Select
from bokeh.palettes import TolRainbow, Muted, d3
from bokeh.transform import factor_cmap

# ====================================================================
# Task 1: Dimension Reduction and Clustering
# ====================================================================

# Read the raw data and inspect the rows and columns.
# There are 5 categorical columns (Country, Industry, Company, Symbol, Recommendation)
# and 102 numerical columns (i.e. features).

data_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQFGt2FAUh_Fb7XAtYasA95ut8X_4a6sqizwcF-QFHdxULsPCf0kXhqn3wJdxNE2Ogf-f1qwyeOIySw/pub?gid=1323235&single=true&output=csv'
data = pd.read_csv(data_url)
num_data = data.iloc[:, 5:] ###answer

## Found 95 numerical colums, and 5 categorical columns
#print(num_data.shape)

# use MinMaxScaler to scale the features
data_scaled = MinMaxScaler().fit_transform(num_data)

# use SimpleImputer to fill in the missing values with the mean value
imp = SimpleImputer(strategy='mean') ###answer

data_imp = imp.fit_transform(data_scaled)
#print(np.isnan(data_imp).any())

## 1.1 Divide all data points into 2 groups according to the 102 numerical columns and assign a label to each point.
# You can choose how many groups to divide into here.
# Reference:
# https://scikit-learn.org/stable/modules/clustering.html#clustering
# https://github.com/bokeh/bokeh/tree/branch-3.4/examples/server/app/clustering


# sets the random seed to 0 so that the result is reproducible
np.random.seed(0)
# use MiniBatchKMeans to perform the clustering
model = cluster.MiniBatchKMeans(n_clusters=2, n_init=2)
model.fit(data_imp)
# append the cluster labels to the dataframe
h_pred = model.labels_.astype(str)
data['H_Cluster'] = h_pred ###answer


## 1.2 Dimension reduction and Clustering
# Apply dimension reduction to the original data, then apply the same clustering function.
# So that the difference of clustering results can be inspected.

# You'll project the 102 numeric features to 2 dimensions using PCA.
# Reference:
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
pca = PCA(n_components=2)
data_pca = pca.fit_transform(data_imp)

#print(np.isnan(data_pca).any())

# append the 2 principal components to the dataframe
data['PCA 1'] = data_pca[:,0]  ###answer
data['PCA 2'] = data_pca[:,1]  ###answer
# divide the data points into 2 groups according to the 2 dimensions produced by PCA
model.fit(data_pca)
# append the cluster labels to the dataframe
P_pred = model.labels_.astype(str)
data['P_Cluster'] = P_pred   ###answer

#You'll project the 102 numeric features to 2 dimensions using MDS
# Reference:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.MDS.html#sklearn.manifold.MDS

mds = MDS(n_components=2)
data_mds = mds.fit_transform(data_imp)  ###answer
# append the 2 principal components to the dataframe
data['MDS 1'] = data_mds[:,0]   ###answer
data['MDS 2'] = data_mds[:,1]  ###answer

# divide the data points into 2 groups according to the 2 dimensions produced by MDS
model.fit(data_mds)
# append the cluster labels to the dataframe
M_pred = model.labels_.astype(str)
data['M_Cluster'] = M_pred   ###answer

# ====================================================================
# Task 2: Visualization
# ====================================================================

# The visualization includes 3 parts:
# 1) A main plot that shows the data points by the 2 dimensions.

# 2) A subplot that shows the statistics of a selected feature.
#    If the feature is numerical, the subplot will be a histogram.
#    If the feature is categorical, the subplot will be a bar chart.

# 3) Two selection widgets,
#    one to select the dimension reduction method to apply in the main plot,
#    one to select the feature to show in the subplot.

## 2.1 Define a function to plot the dimensions you get after reduction.

# dr_selected is the selected method to apply in the color map

def plot_dr(df,dr_selected):
    
    c = dr_selected
    p = figure(
        title=f'Dimension reduction method {c}', 
        tools='hover, pan, wheel_zoom, lasso_select, reset',
        tooltips=[('', '@Symbol')],
        toolbar_location='below', 
        width=500,
        height=450        
    )
   # create a discete color mapper (factor_cmap) for cluster result
    # Reference: https://docs.bokeh.org/en/latest/docs/reference/transform.html#bokeh.transform.factor_cmap
        # use a palette from bokeh:
        # https://docs.bokeh.org/en/latest/docs/reference/palettes.html#d3-palettes
        # the result is binary, you'll need to explicitly make a list of colors
    l = np.unique(data['H_Cluster'].astype(str))    
    palette = ['#FF5733', '#33FF57']  ###answer
    mapper = factor_cmap(
        'H_Cluster', 
        palette=palette, 
        factors=l
    )
    # draw circles to represent the companies.
    # Reference:
    # https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/circle.html#bokeh.models.Circle

    
    r = p.circle(
        # use the 2 components as x and y
        x=c + ' 1', ###answer
        y=c + ' 2', ###answer
        size=8,
        # apply the color map on the glyphs
        fill_color= mapper, ###answer
        alpha=0.4, 
        line_color=None,
        legend_field='H_Cluster', ###answer
        source=df
    )    

    p.background_fill_color = "#fafafa"
    p.xaxis.axis_label = 'Dimension 1'
    p.yaxis.axis_label = 'Dimension 2'
 
    # Put the legend to the left of the plot
    p.add_layout(p.legend[0], 'left')
    # set the 'continuous' property of the lasso select tool to False
    # so that the computation will happen after (not during) the selection
    # https://docs.bokeh.org/en/latest/docs/reference/models/tools.html#bokeh.models.LassoSelectTool
    p.select(LassoSelectTool).continuous = False    ###answer
    p.output_backend = 'svg'
    
    return p

## 2.2.1 Define a function to draw the histogram for a numeric feature.

# The histogram has two sets of bins:
# set 1 shows the histogram of all the points in the main plot
# set 2 shows the histogram of the points selected by the lasso selection tool in the main plot
# Example:
# https://docs.bokeh.org/en/latest/docs/examples/topics/stats/histogram.html#index-0
# https://github.com/bokeh/bokeh/blob/branch-3.5/examples/server/app/selection_histogram.py

def draw_hist(col, points_selected):
    # get the corresponding rows in the dataframe for the selected points
    s = data.loc[points_selected]  ###answer
    
    # compute the tops and edges of the bins in the histogram
    # for all the points and the selected points respectively
    
    top, edges = np.histogram(data[col], bins=10)   ###answer
    top_s, _ = np.histogram(s[col], bins=edges)      ###answer
    

    # create a data source for both sets of bins
    source = ColumnDataSource(data=dict(
        left=edges[:-1],
        right=edges[1:],
        top=top,
        top_s=top_s,
    ))  ###answer

    ph = figure(
        width=400,
        height=300, 
        min_border=20,  
        y_range = (0, 1.1*top.max()),
        y_axis_location="right", 
        title=f'Histogram of {col}',
        tools='pan, wheel_zoom, reset', 
        toolbar_location='below', 
    )
    
    ph.xaxis.axis_label = f'{col}'
    ph.yaxis.axis_label = 'Counts'
    ph.xgrid.grid_line_color = None
    ph.background_fill_color = "#fafafa"
    # draw the bins of all points
    h_a = ph.quad(
        bottom=0, 
        left='left',      ###answer
        right='right',    ###answer 
        top='top',        ###answer
        source=source,
        legend_label='all',
        color="white", 
        line_color="silver"
    )
    # draw the bins of selected points
    h_s = ph.quad(
        bottom=0, 
        left='left', 
        right='right',    ###answer 
        top='top_s', 
        source=source,
        legend_label='selected',
        color='silver', 
        line_color=None, 
        alpha=0.5, 
    )
    ph.legend.orientation = "horizontal"
    ph.legend.location = "top_right"
    # add a hover tool that shows the values of 
    # the range (left and right edges) of a bin,
    # the counts of all points in the bin,
    # the counts of selected points in the bin.
    hover = HoverTool()
    hover.tooltips=[
        ('range', '@left - @right'), ###answer 
        ('all', '@top'),   ###answer
        ('selected', '@top_s')  ###answer
    ]
    # to avoid overlap, apply the hover tool only on the bins of all points
    hover.renderers = [h_a]       
    ph.add_tools(hover)     

    return ph

## 2.2.2 Define a function to draw a bar chart for a categorical feature.

# The bar chart has two sets of bars:
# set 1 shows the bars of all the points in the main plot
# set 2 shows the bars of the points selected by the lasso selection tool in the mian plot

def draw_bar_chart(col, points_selected):
    # get the corresponding rows in the dataframe for the selected points
    s = data.loc[points_selected, col]  ###answer 
    # count the number in the categories
    # for all the points and the selected points respectively
    dis = data[col].value_counts()
    dis_s = s.value_counts()
    cat = dis.index.values
    count = dis.values
    # note that if the selected points do not have a certain category
    # the corresponding count should be zero
    count_s = []
    for c in cat:
        if c in dis_s:
            count_s.append(dis_s[c])
        else:
            count_s.append(0)
     ###answer

 
    # create a data source for both sets of bars
    source = ColumnDataSource(data=dict(
        cat=cat, 
        count=count,
        count_s=count_s,
        color=TolRainbow[5]
    ))

    pb = figure(
        x_range=cat, 
        y_range=(0, count.max()*1.1),
        y_axis_location="right",  
        width=400,
        height=300, 
        min_border=20, 
        title=f'Distribution of {col}',
        tools='pan, wheel_zoom, reset',
        toolbar_location='below', 
    )
    pb.background_fill_color = "#fafafa"
    pb.xaxis.axis_label = f'{col}'
    pb.yaxis.axis_label = 'Counts'
    # draw the bars of all points
    bar_all = pb.vbar(
        x='cat',    ###answer
        top='count',   ###answer
        width=0.6, 
        color='white',
        line_color="silver",
        legend_label='all',
        source=source
    )
    # draw the bars of selected points
    bar_selected = pb.vbar(
        x='cat', 
        top='count_s', 
        width=0.6, 
        color='color',
        alpha=0.4,
        legend_label='selected',
        source=source
    )

    pb.xgrid.grid_line_color = None
    pb.xaxis.major_label_orientation = np.pi/2
    pb.legend.orientation = "horizontal"
    pb.legend.location = "top_right"
    # add a hover tool that shows the values of 
    # the category of a bar,
    # the counts of all points in the bar,
    # the counts of selected points in the bar,
    hover = HoverTool()
    hover.tooltips=[
            ('category', '@cat'),  ###answer
            ('all', '@count'),       ###answer
            ('selected', '@count_s')  ###answer
        ]
    hover.renderers = [bar_all, bar_selected]        
    pb.add_tools(hover)      
    pb.output_backend = 'svg'
        
    return pb

# Define a function to draw the subplot 
# according to the data type of the selected feature
# and the indices of the selected points in the dimension reduction plot

def draw_subplot(ft_selected, points_selected):
    cs = ft_selected
    rs = points_selected
    if is_numeric_dtype(data[cs]):
        sub_p = draw_hist(cs, rs)
    elif is_object_dtype(data[cs]):
        sub_p = draw_bar_chart(cs, rs)
    return sub_p

# Plotting
# 2.3 Initialize the two widgets
# Select a initial method for the dimension reduction plot
dr_selected = 'PCA'
# Add two columns to copy the dimensions you get after dimension reduction.
# It will be updated when you choose a different method
data['D1'] = data['PCA 1']
data['D2'] = data['PCA 2']
# create a ColumnDataSource to update the data when select a new method
df = ColumnDataSource(data=data)
# Select a initial feature for the subplot
ft_selected = 'Mean Recommendation'
# The initial indices of selected points is an empty list
points_selected = []

# Create the initial PCA plot and the subplot
p_dr = plot_dr(df, dr_selected)
p_sub = draw_subplot(ft_selected, points_selected)

# ====================================================================
# Task 3: Interaction
# ====================================================================

# 3.1 Add two Select widgets

# To select the dimension reduction method for the color map and the features of the subplot respectively
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#select

select_col_dr = Select(
    title='Select a dimension reduction method:', 
    value=dr_selected,
    options=[
       'PCA', 'MDS'       ###answer
    ],
    width=200,
    margin=(20, 10, 10, 20)
)

select_col_sub = Select(
    title='Select a feature to show in the subplot:', 
    value=ft_selected, 
    options=list(data.columns[5:]), ###answer options = [ ... ]
    width=200,
    margin=(10, 10, 10, 20)
)

# arrange the plots and widgets in a layout
layout = row(
    column(
      p_dr, 
      width=500, 
    ), 
    column(
      select_col_dr, 
      select_col_sub, 
      p_sub,
      width=350,
    ), 
)

# 3.2 Define the callback functions for the selection widgets

# Python callbacks:
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/python_callbacks.html#python-callbacks
# Example:
# https://github.com/bokeh/bokeh/tree/branch-3.5/examples/server/app/crossfilter
# https://stackoverflow.com/questions/38982276/how-to-refresh-bokeh-document

# Callback function of the Select widget for the dimension reduction plot:
# when you select a new method, it will be adapted to the data, and a new plot will be drawn to replace the previous one in the layout
# the new plot will keep the previous selection of points by the lasso selection tool 
# Reference:
# https://hub.ovh2.mybinder.org/user/bokeh-tutorial-6xc7neyx/notebooks/notebooks/11_widgets_interactivity.ipynb
# (Please note that replacing the whole plot will cause a warning, which is harmless.)
# Reference:
# https://discourse.bokeh.org/t/bug-with-deserializationerror-when-changing-content-layout-in-bokeh-3-1-1/10566/3
def update_dr_col(attrname, old, new):
    global dr_selected
    dr_selected = new       ###answer
    df.data['D1'] = data[dr_selected + ' 1']
    df.data['D2'] = data[dr_selected + ' 2']
    layout.children[0].children[0] = plot_dr(df, new)
    
# Callback function of the Select widget for the subplot:
# when you select a new feature
# a new subplot of this feature will be drawn to replace the previous one in the layout
# the new subplot will keep the previous selection of points by the lasso selection tool 

def update_sub_col(attrname, old, new):
    
    global ft_selected
    ft_selected = new       ###answer
    layout.children[1].children[2] = draw_subplot(new, points_selected)  ###answer

select_col_dr.on_change('value', update_dr_col)       ###answer
select_col_sub.on_change('value', update_sub_col)      ###answer

## 3.3 Define the callback functions for the lasso selection tool in the main plot

# when you select some points with the lasso selection tool,
# a new subplot will be drawn to replace the previous one in the layout
# with the new selection of points reflected in the bins/bars of the selected points
# Example:
# https://github.com/bokeh/bokeh/blob/branch-3.5/examples/server/app/selection_histogram.py

def lasso_update(attr, old, new):
   
    global points_selected
    points_selected = new
    layout.children[1].children[2] = draw_subplot(ft_selected, points_selected)    ###answer

p_dr.renderers[0].data_source.selected.on_change('indices', lasso_update)     ###answer

curdoc().add_root(layout)
curdoc().title = 'Dimension Reduction'