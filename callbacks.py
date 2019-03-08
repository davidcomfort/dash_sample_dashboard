from dash.dependencies import Input, Output
from app import app
import plotly.graph_objs as go
from plotly import tools

from datetime import datetime as dt
from datetime import date, timedelta
from datetime import datetime

import numpy as np
import pandas as pd

import io
import xlsxwriter
import flask
from flask import send_file

from components import formatter_currency, formatter_currency_with_cents, formatter_percent, formatter_percent_2_digits, formatter_number
from components import update_first_datatable, update_first_download, update_second_datatable, update_graph


pd.options.mode.chained_assignment = None

# Read in Travel Report Data
df = pd.read_csv('data/performance_analytics_cost_and_ga_metrics.csv')

df.rename(columns={
 'Travel Product': 'Placement type', 
  'Spend - This Year': 'Spend TY', 
  'Spend - Last Year': 'Spend LY', 
  'Sessions - This Year': 'Sessions - TY',
  'Sessions - Last Year': 'Sessions - LY',
  'Bookings - This Year': 'Bookings - TY',
  'Bookings - Last Year': 'Bookings - LY',
  'Revenue - This Year': 'Revenue - TY',
  'Revenue - Last Year': 'Revenue - LY',
  }, inplace=True)

df['Date'] = pd.to_datetime(df['Date'])
current_year = df['Year'].max()
current_week = df[df['Year'] == current_year]['Week'].max()

now = datetime.now()
datestamp = now.strftime("%Y%m%d")

columns = ['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']

columns_complete = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)', \
                        'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', \
                        'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)']

columns_condensed = ['Placement type', 'Spend TY', 'Spend PoP (%)', 'Spend YoY (%)', 'Sessions - TY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY',  'Bookings PoP (%)', 'Bookings YoY (%)',]

conditional_columns = ['Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional', 
'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional', 'Bookings_PoP_percent_conditional', 'Bookings_YoY_percent_conditional',
'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional', 'Revenue_YoY_percent_conditional',]

dt_columns_total = ['Placement type', 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)', \
                        'Sessions - TY', 'Sessions - LP', 'Sessions - LY', 'Sessions PoP (%)', 'Sessions YoY (%)', \
                        'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', \
                        'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)',
                        'Spend_PoP_abs_conditional', 'Spend_PoP_percent_conditional', 'Spend_YoY_percent_conditional',
'Sessions_PoP_percent_conditional', 'Sessions_YoY_percent_conditional', 
'Bookings_PoP_abs_conditional', 'Bookings_YoY_abs_conditional', 'Bookings_PoP_percent_conditional', 'Bookings_YoY_percent_conditional',
'Revenue_PoP_abs_conditional', 'Revenue_YoY_abs_conditional', 'Revenue_PoP_percent_conditional', 'Revenue_YoY_percent_conditional',]

######################## Birst Category Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-birst-category', 'children'),
	[Input('my-date-picker-range-birst-category', 'start_date'),
	 Input('my-date-picker-range-birst-category', 'end_date')])
def update_output(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-birst-category', 'data'),
	[Input('my-date-picker-range-birst-category', 'start_date'),
	 Input('my-date-picker-range-birst-category', 'end_date')])
def update_data_1(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, None, 'Birst Category')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-birst-category', 'columns'),
    [Input('radio-button-birst-category', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-birst-category', 'href'),
    [Input('my-date-picker-range-birst-category', 'start_date'),
	 Input('my-date-picker-range-birst-category', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/birst-category/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/birst-category/urlToDownload") 
def download_excel_birst_category():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_birst_category_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, None, 'Birst Category')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-birst-category-2', 'data'),
	[Input('my-date-picker-range-birst-category', 'start_date'),
	 Input('my-date-picker-range-birst-category', 'end_date')])
def update_data_2(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, None, 'Birst Category')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('birst-category', 'figure'),
   [Input('datatable-birst-category', "selected_rows"),
   Input('my-date-picker-range-birst-category', 'end_date')])
def update_birst_category(selected_rows, end_date):
	travel_product = []
	travel_product_list = sorted(df['Birst Category'].unique().tolist())
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Birst Category'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

######################## GA Category Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-ga-category', 'children'),
	[Input('my-date-picker-range-ga-category', 'start_date'),
	 Input('my-date-picker-range-ga-category', 'end_date')])
def update_output(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-ga-category', 'data'),
	[Input('my-date-picker-range-ga-category', 'start_date'),
	 Input('my-date-picker-range-ga-category', 'end_date')])
def update_data_1(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, None, 'GA Category')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-ga-category', 'columns'),
    [Input('radio-button-ga-category', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-ga-category', 'href'),
    [Input('my-date-picker-range-ga-category', 'start_date'),
	 Input('my-date-picker-range-ga-category', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/ga-category/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/ga-category/urlToDownload") 
def download_excel_ga_category():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_ga_category_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, None, 'GA Category')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-ga-category-2', 'data'),
	[Input('my-date-picker-range-ga-category', 'start_date'),
	 Input('my-date-picker-range-ga-category', 'end_date')])
def update_data_2(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, None, 'GA Category')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('ga-category', 'figure'),
   [Input('datatable-ga-category', "selected_rows"),
   Input('my-date-picker-range-ga-category', 'end_date')])
def update_ga_category(selected_rows, end_date):
	travel_product = []
	travel_product_list = sorted(df['GA Category'].unique().tolist())
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['GA Category'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

######################## Paid Search Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-paid-search', 'children'),
	[Input('my-date-picker-range-paid-search', 'start_date'),
	 Input('my-date-picker-range-paid-search', 'end_date')])
def update_output(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-paid-search', 'data'),
	[Input('my-date-picker-range-paid-search', 'start_date'),
	 Input('my-date-picker-range-paid-search', 'end_date')])
def update_data_1(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, 'Paid Search', 'Placement type')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-paid-search', 'columns'),
    [Input('radio-button-paid-search', 'value')])
def update_columns(value):
    if value == 'Complete':
    	column_set=[{"name": i, "id": i, 'deletable': True} for i in columns_complete] + [{"name": j, "id": j, 'hidden': 'True'} for j in conditional_columns]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-paid-search-1', 'href'),
    [Input('my-date-picker-range-paid-search', 'start_date'),
	 Input('my-date-picker-range-paid-search', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/paid-search/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/paid-search/urlToDownload") 
def download_excel_1():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_paid_search_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, 'Paid Search', 'Placement type')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-paid-search-2', 'data'),
	[Input('my-date-picker-range-paid-search', 'start_date'),
	 Input('my-date-picker-range-paid-search', 'end_date')])
def update_data_2(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, 'Paid Search', 'Placement type')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('paid-search', 'figure'),
   [Input('datatable-paid-search', "selected_rows"),
   Input('my-date-picker-range-paid-search', 'end_date')])
def update_paid_search(selected_rows, end_date):
	travel_product = []
	travel_product_list = df[(df['Category'] == 'Paid Search')]['Placement type'].unique().tolist()
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Placement type'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig


######################## Display Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-display', 'children'),
	[Input('my-date-picker-range-display', 'start_date'),
	 Input('my-date-picker-range-display', 'end_date')])
def update_output_display(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix


# Callback and update first data table
@app.callback(Output('datatable-display', 'data'),
	[Input('my-date-picker-range-display', 'start_date'),
	 Input('my-date-picker-range-display', 'end_date')])
def update_data_1_display(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, 'Display', 'Placement type')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-display', 'columns'),
    [Input('radio-button-display', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-display-1', 'href'),
    [Input('my-date-picker-range-display', 'start_date'),
	 Input('my-date-picker-range-display', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/display/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/display/urlToDownload") 
def download_excel_display_1():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_display_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, 'Display', 'Placement type')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-display-2', 'data'),
	[Input('my-date-picker-range-display', 'start_date'),
	 Input('my-date-picker-range-display', 'end_date')])
def update_data_2_display(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, 'Display', 'Placement type')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('display', 'figure'),
   [Input('datatable-display', "selected_rows"),
   Input('my-date-picker-range-display', 'end_date')])
def update_display(selected_rows, end_date):
	travel_product = []
	travel_product_list = df[(df['Category'] == 'Display')]['Placement type'].unique().tolist()
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Placement type'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

######################## Publishing Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-publishing', 'children'),
	[Input('my-date-picker-range-publishing', 'start_date'),
	 Input('my-date-picker-range-publishing', 'end_date')])
def update_output_publishing(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-publishing', 'data'),
	[Input('my-date-picker-range-publishing', 'start_date'),
	 Input('my-date-picker-range-publishing', 'end_date')])
def update_data_1_publishing(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, 'Publishing', 'Placement type')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-publishing', 'columns'),
    [Input('radio-button-publishing', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-publishing-1', 'href'),
    [Input('my-date-picker-range-publishing', 'start_date'),
	 Input('my-date-picker-range-publishing', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/publishing/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/publishing/urlToDownload") 
def download_excel_publishing_1():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_publishing_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, 'Publishing', 'Placement type')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-publishing-2', 'data'),
	[Input('my-date-picker-range-publishing', 'start_date'),
	 Input('my-date-picker-range-publishing', 'end_date')])
def update_data_2_publishing(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, 'Publishing', 'Placement type')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('publishing', 'figure'),
   [Input('datatable-publishing', "selected_rows"),
   Input('my-date-picker-range-publishing', 'end_date')])
def update_publishing(selected_rows, end_date):
	travel_product = []
	travel_product_list = df[(df['Category'] == 'Publishing')]['Placement type'].unique().tolist()
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Placement type'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

######################## Metasearch Callbacks ######################## 

#### Date Picker Callback
@app.callback(Output('output-container-date-picker-range-metasearch', 'children'),
	[Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_output_metasearch(start_date, end_date):
	string_prefix = 'You have selected '
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%B %d, %Y')
		string_prefix = string_prefix + 'a Start Date of ' + start_date_string + ' | '
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%B %d, %Y')
		days_selected = (end_date - start_date).days
		prior_start_date = start_date - timedelta(days_selected + 1)
		prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
		prior_end_date = end_date - timedelta(days_selected + 1)
		prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
		string_prefix = string_prefix + 'End Date of ' + end_date_string + ', for a total of ' + str(days_selected + 1) + ' Days. The prior period Start Date was ' + \
		prior_start_date_string + ' | End Date: ' + prior_end_date_string + '.'
	if len(string_prefix) == len('You have selected: '):
		return 'Select a date to see it displayed here'
	else:
		return string_prefix

# Callback and update first data table
@app.callback(Output('datatable-metasearch', 'data'),
	[Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_data_1_metasearch(start_date, end_date):
	data_1 = update_first_datatable(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
	return data_1

# Callback and update data table columns
@app.callback(Output('datatable-metasearch', 'columns'),
    [Input('radio-button-metasearch', 'value')])
def update_columns(value):
    if value == 'Complete':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_complete]
    elif value == 'Condensed':
        column_set=[{"name": i, "id": i, "deletable": True} for i in columns_condensed]
    return column_set

# Callback for excel download
@app.callback(
    Output('download-link-metasearch-1', 'href'),
    [Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])   
def update_link(start_date, end_date):
	return '/cc-travel-report/metasearch/urlToDownload?value={}/{}'.format(dt.strptime(start_date,'%Y-%m-%d').strftime('%Y-%m-%d'),dt.strptime(end_date,'%Y-%m-%d').strftime('%Y-%m-%d'))
@app.server.route("/cc-travel-report/metasearch/urlToDownload") 
def download_excel_metasearch_1():
    value = flask.request.args.get('value')
    #here is where I split the value
    value = value.split('/')
    start_date = value[0]
    end_date = value[1]

    filename = datestamp + '_metasearch_' + start_date + '_to_' + end_date + '.xlsx'
	# Dummy Dataframe
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    download_1 = update_first_download(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
    download_1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    # df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

# Callback and update second data table
@app.callback(
	Output('datatable-metasearch-2', 'data'),
	[Input('my-date-picker-range-metasearch', 'start_date'),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_data_2_metasearch(start_date, end_date):
	data_2 = update_second_datatable(start_date, end_date, 'Metasearch and Travel Ads', 'Placement type')
	return data_2

# Callback for the Graphs
@app.callback(
   Output('metasearch', 'figure'),
   [Input('datatable-metasearch', "selected_rows"),
	 Input('my-date-picker-range-metasearch', 'end_date')])
def update_metasearch(selected_rows, end_date):
	travel_product = []
	travel_product_list = df[(df['Category'] == 'Metasearch and Travel Ads')]['Placement type'].unique().tolist()
	for i in selected_rows:
		travel_product.append(travel_product_list[i])
		# Filter by specific product
	filtered_df = df[(df['Placement type'].isin(travel_product))].groupby(['Year', 'Week']).sum()[['Spend TY', 'Spend LY', 'Sessions - TY', 'Sessions - LY', 'Bookings - TY', 'Bookings - LY', 'Revenue - TY', 'Revenue - LY']].reset_index()
	fig = update_graph(filtered_df, end_date)
	return fig

