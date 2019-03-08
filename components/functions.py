from datetime import datetime as dt
from datetime import date, timedelta
from datetime import datetime
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import pandas as pd

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


# Define Formatters
def formatter_currency(x):
	return "${:,.0f}".format(x) if x >= 0 else "(${:,.0f})".format(abs(x))

def formatter_currency_with_cents(x):
	return "${:,.2f}".format(x) if x >= 0 else "(${:,.2f})".format(abs(x))

def formatter_percent(x):
	return "{:,.1f}%".format(x) if x >= 0 else "({:,.1f}%)".format(abs(x))

def formatter_percent_2_digits(x):
	return "{:,.2f}%".format(x) if x >= 0 else "({:,.2f}%)".format(abs(x))

def formatter_number(x):
	return "{:,.0f}".format(x) if x >= 0 else "({:,.0f})".format(abs(x))


# First Data Table Update Function
def update_first_datatable(start_date, end_date, category, aggregation):
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%Y-%m-%d')
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%Y-%m-%d')
	days_selected = (end_date - start_date).days

	prior_start_date = start_date - timedelta(days_selected + 1)
	prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%d')
	prior_end_date = end_date - timedelta(days_selected + 1)
	prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%d')

	if aggregation == 'Placement type':
		df1 = df[(df['Category'] == category)].groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
	elif aggregation == 'GA Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'GA Category':'Placement type'}, inplace=True)
	elif aggregation == 'Birst Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'Birst Category':'Placement type'}, inplace=True)

	# Calculate Differences on-the-fly
	df_by_date_combined['Spend PoP (%)'] = np.nan
	df_by_date_combined['Spend YoY (%)'] = np.nan
	df_by_date_combined['Sessions PoP (%)'] = np.nan
	df_by_date_combined['Sessions YoY (%)'] = np.nan
	df_by_date_combined['Bookings PoP (%)'] = np.nan
	df_by_date_combined['Bookings YoY (%)'] = np.nan
	df_by_date_combined['Revenue PoP (%)'] = np.nan
	df_by_date_combined['Revenue YoY (%)'] = np.nan

	df_by_date_combined['Spend_PoP_abs_conditional'] = df_by_date_combined['Spend PoP (Abs)'] = ((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend - LP']))
	# Formatter
	df_by_date_combined['Spend PoP (Abs)'] = df_by_date_combined['Spend PoP (Abs)'].apply(formatter_currency)

	df_by_date_combined['Spend_PoP_percent_conditional'] = df_by_date_combined['Spend PoP (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend - LP'] != 0),\
		(((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend - LP'])/df_by_date_combined['Spend - LP']) * 100), df_by_date_combined['Spend PoP (%)'])
	# Formatter
	df_by_date_combined['Spend PoP (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend - LP'] != 0),\
		df_by_date_combined['Spend PoP (%)'].apply(formatter_percent), df_by_date_combined['Spend PoP (%)'])

	df_by_date_combined['Spend_YoY_percent_conditional'] = df_by_date_combined['Spend YoY (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend LY'] != 0),\
		((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend LY'])/df_by_date_combined['Spend LY']) * 100, df_by_date_combined['Spend YoY (%)'])
	# Formatter
	df_by_date_combined['Spend YoY (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend LY'] != 0),\
		df_by_date_combined['Spend YoY (%)'].apply(formatter_percent), df_by_date_combined['Spend YoY (%)'])


	df_by_date_combined['Sessions_PoP_percent_conditional'] = df_by_date_combined['Sessions PoP (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LP'] != 0),\
		((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LP'])/df_by_date_combined['Sessions - LP']) * 100, df_by_date_combined['Sessions PoP (%)'])
	# Formatter
	df_by_date_combined['Sessions PoP (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LP'] != 0),\
		df_by_date_combined['Sessions PoP (%)'].apply(formatter_percent), df_by_date_combined['Sessions PoP (%)'])

	df_by_date_combined['Sessions_YoY_percent_conditional'] = df_by_date_combined['Sessions YoY (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LY'] != 0),\
		((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LY'])/df_by_date_combined['Sessions - LY']) * 100, df_by_date_combined['Sessions YoY (%)'])
	# Formatter
	df_by_date_combined['Sessions YoY (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LY'] != 0),\
		df_by_date_combined['Sessions YoY (%)'].apply(formatter_percent), df_by_date_combined['Sessions YoY (%)'])


	df_by_date_combined['Bookings_PoP_abs_conditional'] = df_by_date_combined['Bookings PoP (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LP'])
	# Formatter
	df_by_date_combined['Bookings PoP (Abs)'] = df_by_date_combined['Bookings PoP (Abs)'].apply(formatter_number)

	df_by_date_combined['Bookings_YoY_abs_conditional'] = df_by_date_combined['Bookings YoY (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LY'])
	# Formatter
	df_by_date_combined['Bookings YoY (Abs)'] = df_by_date_combined['Bookings YoY (Abs)'].apply(formatter_number)

	df_by_date_combined['Bookings_PoP_percent_conditional'] = df_by_date_combined['Bookings PoP (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LP'] != 0),\
		(df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LP'])/df_by_date_combined['Bookings - LP'] * 100, df_by_date_combined['Bookings PoP (%)'])
	# Formatter
	df_by_date_combined['Bookings PoP (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LP'] != 0),\
		df_by_date_combined['Bookings PoP (%)'].apply(formatter_percent), df_by_date_combined['Bookings PoP (%)'])

	df_by_date_combined['Bookings_YoY_percent_conditional'] = df_by_date_combined['Bookings YoY (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LY'] != 0),\
		(df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LY'])/df_by_date_combined['Bookings - LY'] * 100, df_by_date_combined['Bookings YoY (%)'])
	# Formatter
	df_by_date_combined['Bookings YoY (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LY'] != 0),\
		df_by_date_combined['Bookings YoY (%)'].apply(formatter_percent), df_by_date_combined['Bookings YoY (%)'])


	df_by_date_combined['Revenue_PoP_abs_conditional'] = df_by_date_combined['Revenue PoP (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LP'])
	# Formatter
	df_by_date_combined['Revenue PoP (Abs)'] = df_by_date_combined['Revenue PoP (Abs)'].apply(formatter_currency)

	df_by_date_combined['Revenue_YoY_abs_conditional'] = df_by_date_combined['Revenue YoY (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LY'])
	# Formatter
	df_by_date_combined['Revenue YoY (Abs)'] = df_by_date_combined['Revenue YoY (Abs)'].apply(formatter_currency)

	df_by_date_combined['Revenue_PoP_percent_conditional'] = df_by_date_combined['Revenue PoP (%)'] = np.where((df_by_date_combined['Revenue - LP'] != 0) &  (df_by_date_combined['Revenue - LP'] != 0),\
		(df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LP'])/df_by_date_combined['Revenue - LP'] * 100, df_by_date_combined['Revenue PoP (%)'])
	# Formatter
	df_by_date_combined['Revenue PoP (%)'] = np.where((df_by_date_combined['Revenue - LP'] != 0) &  (df_by_date_combined['Revenue - LP'] != 0),\
		df_by_date_combined['Revenue PoP (%)'].apply(formatter_percent), df_by_date_combined['Revenue PoP (%)'])

	df_by_date_combined['Revenue_YoY_percent_conditional'] = df_by_date_combined['Revenue YoY (%)'] = np.where((df_by_date_combined['Revenue - TY'] != 0) &  (df_by_date_combined['Revenue - LY'] != 0),\
		(df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LY'])/df_by_date_combined['Revenue - LY'] * 100, df_by_date_combined['Revenue YoY (%)'])
	# Formatter
	df_by_date_combined['Revenue YoY (%)'] = np.where((df_by_date_combined['Revenue - TY'] != 0) &  (df_by_date_combined['Revenue - LY'] != 0),\
		df_by_date_combined['Revenue YoY (%)'].apply(formatter_percent), df_by_date_combined['Revenue YoY (%)'])

	# Format Numbers
	df_by_date_combined['Spend TY'] = df_by_date_combined['Spend TY'].apply(formatter_currency) 
	df_by_date_combined['Spend - LP'] = df_by_date_combined['Spend - LP'].apply(formatter_currency) 
	df_by_date_combined['Spend LY'] = df_by_date_combined['Spend LY'].apply(formatter_currency) 

	df_by_date_combined['Sessions - TY'] = df_by_date_combined['Sessions - TY'].apply(formatter_number)
	df_by_date_combined['Sessions - LP'] = df_by_date_combined['Sessions - LP'].apply(formatter_number)
	df_by_date_combined['Sessions - LY'] = df_by_date_combined['Sessions - LY'].apply(formatter_number)
	df_by_date_combined['Bookings - TY'] = df_by_date_combined['Bookings - TY'].apply(formatter_number)
	df_by_date_combined['Bookings - LP'] = df_by_date_combined['Bookings - LP'].apply(formatter_number)
	df_by_date_combined['Bookings - LY'] = df_by_date_combined['Bookings - LY'].apply(formatter_number)

	df_by_date_combined['Revenue - TY'] = df_by_date_combined['Revenue - TY'].apply(formatter_currency) 
	df_by_date_combined['Revenue - LP'] = df_by_date_combined['Revenue - LP'].apply(formatter_currency) 
	df_by_date_combined['Revenue - LY'] = df_by_date_combined['Revenue - LY'].apply(formatter_currency)
	# Rearrange the columns
	df_by_date_combined_dt = df_by_date_combined[[
		 'Placement type', 
		 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)',
		 'Sessions - TY', 'Sessions - LP', 'Sessions PoP (%)', 'Sessions - LY', 'Sessions YoY (%)',
		 'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', 
		 'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)', 
		 # 'Spend_PoP_percent_conditional', 
		 ]]

	data_df = df_by_date_combined.to_dict("rows")
	return data_df

# First Data Table Download Function
def update_first_download(start_date, end_date, category, aggregation):
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%Y-%m-%d')
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%Y-%m-%d')
	days_selected = (end_date - start_date).days

	prior_start_date = start_date - timedelta(days_selected + 1)
	prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%d')
	prior_end_date = end_date - timedelta(days_selected + 1)
	prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%d')

	if aggregation == 'Placement type':
		df1 = df[(df['Category'] == category)].groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
	elif aggregation == 'GA Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'GA Category':'Placement type'}, inplace=True)
	elif aggregation == 'Birst Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'Birst Category':'Placement type'}, inplace=True)

	# Calculate Differences on-the-fly
	df_by_date_combined['Spend PoP (%)'] = np.nan
	df_by_date_combined['Spend YoY (%)'] = np.nan
	df_by_date_combined['Sessions PoP (%)'] = np.nan
	df_by_date_combined['Sessions YoY (%)'] = np.nan
	df_by_date_combined['Bookings PoP (%)'] = np.nan
	df_by_date_combined['Bookings YoY (%)'] = np.nan
	df_by_date_combined['Revenue PoP (%)'] = np.nan
	df_by_date_combined['Revenue YoY (%)'] = np.nan

	df_by_date_combined['Spend PoP (Abs)'] = ((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend - LP']))
	df_by_date_combined['Spend PoP (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend - LP'] != 0),\
		(((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend - LP'])/df_by_date_combined['Spend - LP']) * 100), df_by_date_combined['Spend PoP (%)'])
	df_by_date_combined['Spend YoY (%)'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Spend LY'] != 0),\
		((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend LY'])/df_by_date_combined['Spend LY']) * 100, df_by_date_combined['Spend YoY (%)'])

	df_by_date_combined['Sessions PoP (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LP'] != 0),\
		((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LP'])/df_by_date_combined['Sessions - LP']) * 100, df_by_date_combined['Sessions PoP (%)'])
	df_by_date_combined['Sessions YoY (%)'] = np.where((df_by_date_combined['Sessions - TY'] != 0) &  (df_by_date_combined['Sessions - LY'] != 0),\
		((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LY'])/df_by_date_combined['Sessions - LY']) * 100, df_by_date_combined['Sessions YoY (%)'])

	df_by_date_combined['Bookings PoP (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LP'])
	df_by_date_combined['Bookings YoY (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LY'])

	df_by_date_combined['Bookings PoP (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LP'] != 0),\
		(df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LP'])/df_by_date_combined['Bookings - LP'] * 100, df_by_date_combined['Bookings PoP (%)'])
	df_by_date_combined['Bookings YoY (%)'] = np.where((df_by_date_combined['Bookings - TY'] != 0) &  (df_by_date_combined['Bookings - LY'] != 0),\
		(df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LY'])/df_by_date_combined['Bookings - LY'] * 100, df_by_date_combined['Bookings YoY (%)'])

	df_by_date_combined['Revenue PoP (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LP'])
	df_by_date_combined['Revenue YoY (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LY'])

	df_by_date_combined['Revenue PoP (%)'] = np.where((df_by_date_combined['Revenue - LP'] != 0) &  (df_by_date_combined['Revenue - LP'] != 0),\
		(df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LP'])/df_by_date_combined['Revenue - LP'] * 100, df_by_date_combined['Revenue PoP (%)'])
	df_by_date_combined['Revenue YoY (%)'] = np.where((df_by_date_combined['Revenue - TY'] != 0) &  (df_by_date_combined['Revenue - LY'] != 0),\
		(df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LY'])/df_by_date_combined['Revenue - LY'] * 100, df_by_date_combined['Revenue YoY (%)'])

	# Calculate CPS, CR, CPA
	df_by_date_combined['CPS - TY'] = np.nan
	df_by_date_combined['CPS - LP'] = np.nan
	df_by_date_combined['CPS - LY'] = np.nan
	df_by_date_combined['CPS PoP (Abs)'] = np.nan
	df_by_date_combined['CPS YoY (Abs)'] = np.nan
	df_by_date_combined['CVR - TY'] = np.nan
	df_by_date_combined['CVR - LP'] = np.nan
	df_by_date_combined['CVR - LY'] = np.nan
	df_by_date_combined['CVR PoP (Abs)'] = np.nan
	df_by_date_combined['CVR YoY (Abs)'] = np.nan
	df_by_date_combined['CPA - TY'] = np.nan
	df_by_date_combined['CPA - LP'] = np.nan
	df_by_date_combined['CPA - LY'] = np.nan
	df_by_date_combined['CPA PoP (Abs)'] = np.nan
	df_by_date_combined['CPA YoY (Abs)'] = np.nan

	df_by_date_combined['CPS PoP (%)'] = np.nan
	df_by_date_combined['CPS YoY (%)'] = np.nan
	df_by_date_combined['CVR PoP (%)'] = np.nan
	df_by_date_combined['CVR YoY (%)'] = np.nan
	df_by_date_combined['CPA PoP (%)' ] = np.nan
	df_by_date_combined['CPA YoY (%)'] = np.nan

	df_by_date_combined['CPS - TY'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Sessions - TY'] != 0),\
									  (df_by_date_combined['Spend TY']/df_by_date_combined['Sessions - TY']), df_by_date_combined['CPS - TY'])

	df_by_date_combined['CPS - LP'] = np.where((df_by_date_combined['Spend - LP'] != 0) &  (df_by_date_combined['Sessions - LP'] != 0),\
									  (df_by_date_combined['Spend - LP']/df_by_date_combined['Sessions - LP']), df_by_date_combined['CPS - LP'])
	df_by_date_combined['CPS PoP (Abs)'] =  (df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LP'])

	df_by_date_combined['CPS PoP (%)'] =  np.where((df_by_date_combined['CPS - TY'] != 0) &  (df_by_date_combined['CPS - LP'] != 0),\
		((df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LP'])/df_by_date_combined['CPS - LP']), df_by_date_combined['CPS PoP (%)'])
					   
	df_by_date_combined['CPS - LY'] = np.where((df_by_date_combined['Spend LY'] != 0) &  (df_by_date_combined['Sessions - LY'] != 0),\
									  (df_by_date_combined['Spend LY']/df_by_date_combined['Sessions - LY']), df_by_date_combined['CPS - LY'])
	df_by_date_combined['CPS YoY (Abs)'] =  (df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LY'])

	df_by_date_combined['CPS YoY (%)'] = np.where((df_by_date_combined['CPS - TY'] != 0) &  (df_by_date_combined['CPS - LY'] != 0),\
		((df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LY'])/df_by_date_combined['CPS - LY']), df_by_date_combined['CPS YoY (%)'] )

	df_by_date_combined['CVR - TY'] = np.where(((df_by_date_combined['Bookings - TY'] != 0) & (df_by_date_combined['Sessions - TY'] != 0)), \
									 (df_by_date_combined['Bookings - TY']/df_by_date_combined['Sessions - TY'] * 100), df_by_date_combined['CVR - TY'])
	df_by_date_combined['CVR - LP'] = np.where(((df_by_date_combined['Bookings - LP'] != 0) & (df_by_date_combined['Sessions - LP'] != 0)), \
							 (df_by_date_combined['Bookings - LP']/df_by_date_combined['Sessions - LP'] * 100), df_by_date_combined['CVR - LP'])
	df_by_date_combined['CVR PoP (Abs)'] =  np.where((df_by_date_combined['CVR - TY'].notnull() & df_by_date_combined['CVR - LP'].notnull()), \
							  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LP'])), df_by_date_combined['CVR PoP (Abs)'])

	df_by_date_combined['CVR PoP (%)'] =  np.where(((df_by_date_combined['CVR - TY'] != 0) & (df_by_date_combined['CVR - LP'] != 0)), \
		((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LP'])/df_by_date_combined['CVR - LP']), df_by_date_combined['CVR PoP (%)'])

	df_by_date_combined['CVR - LY'] = np.where(((df_by_date_combined['Bookings - LY'] != 0) & (df_by_date_combined['Sessions - LY'] != 0)), \
							 (df_by_date_combined['Bookings - LY']/df_by_date_combined['Sessions - LY'] * 100), df_by_date_combined['CVR - LY'])
	df_by_date_combined['CVR YoY (Abs)'] =  np.where((df_by_date_combined['CVR - TY'].notnull() & df_by_date_combined['CVR - LY'].notnull()), \
							  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LY'])), df_by_date_combined['CVR YoY (Abs)'])

	df_by_date_combined['CVR YoY (%)'] =  np.where(((df_by_date_combined['CVR - TY'] != 0) & (df_by_date_combined['CVR - LY'] != 0)), \
		((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LY'])/df_by_date_combined['CVR - LY']), df_by_date_combined['CVR YoY (%)'])

	df_by_date_combined['CPA - TY'] = np.where((df_by_date_combined['Spend TY'] != 0) & (df_by_date_combined['Bookings - TY'] != 0), \
									  (df_by_date_combined['Spend TY']/df_by_date_combined['Bookings - TY']), df_by_date_combined['CPA - TY'])
	df_by_date_combined['CPA - LP'] = np.where((df_by_date_combined['Spend - LP'] != 0) & (df_by_date_combined['Bookings - LP'] != 0), \
									  (df_by_date_combined['Spend - LP']/df_by_date_combined['Bookings - LP']), df_by_date_combined['CPA - LP'])
	df_by_date_combined['CPA PoP (Abs)'] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LP'] != 0), \
									  (df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LP']), df_by_date_combined['CPA PoP (Abs)'])

	df_by_date_combined['CPA PoP (%)' ] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LP'] != 0), \
		((df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LP'])/df_by_date_combined['CPA - LP']), df_by_date_combined['CPA PoP (%)' ] )


	df_by_date_combined['CPA - LY'] = np.where((df_by_date_combined['Spend LY'] != 0) & (df_by_date_combined['Bookings - LY'] != 0), \
									  (df_by_date_combined['Spend LY']/df_by_date_combined['Bookings - LY']), df_by_date_combined['CPA - LY'])
	df_by_date_combined['CPA YoY (Abs)'] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LY'] != 0), \
									  (df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LY']), df_by_date_combined['CPA YoY (Abs)'])

	df_by_date_combined['CPA YoY (%)'] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LY'] != 0), \
		(df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LY'])/df_by_date_combined['CPA - LY'], df_by_date_combined['CPA YoY (%)'])

	df_by_date_combined['TY Start Date'] = start_date_string
	df_by_date_combined['TY End Date'] = end_date_string
	df_by_date_combined['LP Start Date'] = prior_start_date_string
	df_by_date_combined['LP End Date'] = prior_end_date_string

	last_years_start_date = start_date - timedelta(364)
	last_years_start_date_string = datetime.strftime(last_years_start_date, '%Y-%m-%d')
	last_years_end_date = end_date - timedelta(364)
	last_years_end_date_string = datetime.strftime(last_years_end_date, '%Y-%m-%d')

	df_by_date_combined['LY Start Date'] = last_years_start_date_string
	df_by_date_combined['LY End Date'] = last_years_end_date_string

	# Rearrange the columns
	df_by_date_combined_dt = df_by_date_combined[[
		 'Placement type', 'TY Start Date', 'TY End Date', 'LP Start Date', 'LP End Date', 'LY Start Date', 'LY End Date',
		 'Spend TY', 'Spend - LP', 'Spend PoP (Abs)', 'Spend PoP (%)', 'Spend LY', 'Spend YoY (%)',
		 'Sessions - TY', 'Sessions - LP', 'Sessions PoP (%)', 'Sessions - LY', 'Sessions YoY (%)',
		 'Bookings - TY', 'Bookings - LP', 'Bookings PoP (%)', 'Bookings PoP (Abs)', 'Bookings - LY', 'Bookings YoY (%)', 'Bookings YoY (Abs)', 
		 'Revenue - TY', 'Revenue - LP', 'Revenue PoP (Abs)', 'Revenue PoP (%)', 'Revenue - LY', 'Revenue YoY (%)', 'Revenue YoY (Abs)',  
		 'CPS - TY', 
		 'CPS - LP', 'CPS PoP (Abs)', 'CPS PoP (%)', 
		 'CPS - LY',  'CPS YoY (Abs)', 'CPS YoY (%)', 
		 'CVR - TY', 
		 'CVR - LP', 'CVR PoP (Abs)', 'CVR PoP (%)', 
		 'CVR - LY', 'CVR YoY (Abs)', 'CVR YoY (%)', 
		 'CPA - TY', 
		 'CPA - LP', 'CPA PoP (Abs)', 'CPA PoP (%)', 
		 'CPA - LY', 'CPA YoY (Abs)', 'CPA YoY (%)'
		 ]]


	download_df_1 = df_by_date_combined_dt
	return download_df_1

# Second Data Table Update Function
def update_second_datatable(start_date, end_date, category, aggregation):
	if start_date is not None:
		start_date = dt.strptime(start_date, '%Y-%m-%d')
		start_date_string = start_date.strftime('%Y-%m-%d')
	if end_date is not None:
		end_date = dt.strptime(end_date, '%Y-%m-%d')
		end_date_string = end_date.strftime('%Y-%m-%d')
	days_selected = (end_date - start_date).days

	prior_start_date = start_date - timedelta(days_selected + 1)
	prior_start_date_string = datetime.strftime(prior_start_date, '%Y-%m-%d')
	prior_end_date = end_date - timedelta(days_selected + 1)
	prior_end_date_string = datetime.strftime(prior_end_date, '%Y-%m-%d')

	if aggregation == 'Placement type':
		df1 = df[(df['Category'] == category)].groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
	elif aggregation == 'GA Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'GA Category':'Placement type'}, inplace=True)
	elif aggregation == 'Birst Category':
		df1 = df.groupby(['Date', aggregation]).sum()[columns].reset_index()
		df_by_date = df1[(df1['Date'] >= start_date_string) & (df1['Date'] <= end_date_string)].groupby([aggregation]).sum()[columns].reset_index()
		df_by_date_prior = df1[(df1['Date'] >= prior_start_date_string) & (df1['Date'] <= prior_end_date_string)].groupby([aggregation]).sum()[['Spend TY', 'Sessions - TY', 'Bookings - TY', 'Revenue - TY']].reset_index()
		df_by_date_prior.rename(columns={'Spend TY' : 'Spend - LP', 'Sessions - TY' : 'Sessions - LP',  'Bookings - TY' : 'Bookings - LP','Revenue - TY' : 'Revenue - LP'}, inplace=True)
		df_by_date_combined =  pd.merge(df_by_date, df_by_date_prior, on=[aggregation])
		df_by_date_combined.rename(columns={'Birst Category':'Placement type'}, inplace=True)

	# Calculate Differences on-the-fly
	# Calculate Percentage Changes
	df_by_date_combined['Spend PoP (Abs)'] = ((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend - LP'])/df_by_date_combined['Spend - LP']) * 100
	df_by_date_combined['Spend PoP (Abs)'] = df_by_date_combined.apply(lambda x: "{:,.0f}%".format(x['Spend PoP (Abs)']), axis=1)
	df_by_date_combined['Spend YoY (%)'] = ((df_by_date_combined['Spend TY'] - df_by_date_combined['Spend LY'])/df_by_date_combined['Spend LY']) * 100
	df_by_date_combined['Spend YoY (%)'] = df_by_date_combined.apply(lambda x: "{:,.0f}%".format(x['Spend YoY (%)']), axis=1)

	df_by_date_combined['Sessions PoP (%)'] = ((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LP'])/df_by_date_combined['Sessions - LP']) * 100
	df_by_date_combined['Sessions PoP (%)'] = df_by_date_combined.apply(lambda x: "{:,.0f}%".format(x['Sessions PoP (%)']), axis=1)
	df_by_date_combined['Sessions YoY (%)'] = ((df_by_date_combined['Sessions - TY'] - df_by_date_combined['Sessions - LY'])/df_by_date_combined['Sessions - LY']) * 100
	df_by_date_combined['Sessions YoY (%)'] = df_by_date_combined.apply(lambda x: "{:,.0f}%".format(x['Sessions YoY (%)']), axis=1)

	df_by_date_combined['Bookings PoP (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LP'])
	df_by_date_combined['Bookings PoP (Abs)'] = df_by_date_combined.apply(lambda x: "{:,.0f}".format(x['Bookings PoP (Abs)']), axis=1)
	df_by_date_combined['Bookings YoY (Abs)'] = (df_by_date_combined['Bookings - TY'] - df_by_date_combined['Bookings - LY'])
	df_by_date_combined['Bookings YoY (Abs)'] = df_by_date_combined.apply(lambda x: "{:,.0f}".format(x['Bookings YoY (Abs)']), axis=1)

	df_by_date_combined['Revenue PoP (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LP'])
	df_by_date_combined['Revenue PoP (Abs)'] = df_by_date_combined.apply(lambda x: "{:,.0f}".format(x['Revenue PoP (Abs)']), axis=1)
	df_by_date_combined['Revenue YoY (Abs)'] = (df_by_date_combined['Revenue - TY'] - df_by_date_combined['Revenue - LY'])
	df_by_date_combined['Revenue YoY (Abs)'] = df_by_date_combined.apply(lambda x: "{:,.0f}".format(x['Revenue YoY (Abs)']), axis=1)


	# Calculate CPS, CR, CPA
	df_by_date_combined['CPS - TY'] = np.nan
	df_by_date_combined['CPS - LP'] = np.nan
	df_by_date_combined['CPS - LY'] = np.nan
	df_by_date_combined['CPS PoP (Abs)'] = np.nan
	df_by_date_combined['CPS YoY (Abs)'] = np.nan
	df_by_date_combined['CVR - TY'] = np.nan
	df_by_date_combined['CVR - LP'] = np.nan
	df_by_date_combined['CVR - LY'] = np.nan
	df_by_date_combined['CVR PoP (Abs)'] = np.nan
	df_by_date_combined['CVR YoY (Abs)'] = np.nan
	df_by_date_combined['CPA - TY'] = np.nan
	df_by_date_combined['CPA - LP'] = np.nan
	df_by_date_combined['CPA - LY'] = np.nan
	df_by_date_combined['CPA PoP (Abs)'] = np.nan
	df_by_date_combined['CPA YoY (Abs)'] = np.nan

	df_by_date_combined['CPS - TY'] = np.where((df_by_date_combined['Spend TY'] != 0) &  (df_by_date_combined['Sessions - TY'] != 0),\
									  (df_by_date_combined['Spend TY']/df_by_date_combined['Sessions - TY']), df_by_date_combined['CPS - TY'])

	df_by_date_combined['CPS - LP'] = np.where((df_by_date_combined['Spend - LP'] != 0) &  (df_by_date_combined['Sessions - LP'] != 0),\
									  (df_by_date_combined['Spend - LP']/df_by_date_combined['Sessions - LP']), df_by_date_combined['CPS - LP'])
	# df_by_date_combined['CPS_PoP_abs_conditional'] =  
	df_by_date_combined['CPS PoP (Abs)'] =  (df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LP'])
	df_by_date_combined['CPS_PoP_percent_conditional'] = df_by_date_combined['CPS PoP (%)'] = ((df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LP'])/df_by_date_combined['CPS - LP'] * 100)
					   
	df_by_date_combined['CPS - LY'] = np.where((df_by_date_combined['Spend LY'] != 0) &  (df_by_date_combined['Sessions - LY'] != 0),\
									  (df_by_date_combined['Spend LY']/df_by_date_combined['Sessions - LY']), df_by_date_combined['CPS - LY'])
	df_by_date_combined['CPS_YoY_abs_conditional'] =  df_by_date_combined['CPS YoY (Abs)'] =  (df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LY'])
	df_by_date_combined['CPS_PoP_percent_conditional'] = df_by_date_combined['CPS YoY (%)'] = ((df_by_date_combined['CPS - TY'] - df_by_date_combined['CPS - LY'])/df_by_date_combined['CPS - LY']) * 100

	df_by_date_combined['CVR - TY'] = np.where(((df_by_date_combined['Bookings - TY'] != 0) & (df_by_date_combined['Sessions - TY'] != 0)), \
									 (df_by_date_combined['Bookings - TY']/df_by_date_combined['Sessions - TY'] * 100), df_by_date_combined['CVR - TY'])
	df_by_date_combined['CVR - LP'] = np.where(((df_by_date_combined['Bookings - LP'] != 0) & (df_by_date_combined['Sessions - LP'] != 0)), \
							 (df_by_date_combined['Bookings - LP']/df_by_date_combined['Sessions - LP'] * 100), df_by_date_combined['CVR - LP'])

	df_by_date_combined['CVR_PoP_abs_conditional'] =  df_by_date_combined['CVR PoP (Abs)'] =  np.where((df_by_date_combined['CVR - TY'].notnull() & df_by_date_combined['CVR - LP'].notnull()), \
							  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LP'])), df_by_date_combined['CVR PoP (Abs)'])
	df_by_date_combined['CVR_PoP_percent_conditional'] =  df_by_date_combined['CVR PoP (%)'] =  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LP'])/df_by_date_combined['CVR - LP']) * 100
	df_by_date_combined['CVR - LY'] = np.where(((df_by_date_combined['Bookings - LY'] != 0) & (df_by_date_combined['Sessions - LY'] != 0)), \
							 (df_by_date_combined['Bookings - LY']/df_by_date_combined['Sessions - LY'] * 100), df_by_date_combined['CVR - LY'])
	df_by_date_combined['CVR_YoY_abs_conditional'] =  df_by_date_combined['CVR YoY (Abs)'] =  np.where((df_by_date_combined['CVR - TY'].notnull() & df_by_date_combined['CVR - LY'].notnull()), \
							  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LY'])), df_by_date_combined['CVR YoY (Abs)'])
	df_by_date_combined['CVR_YoY_percent_conditional'] =  df_by_date_combined['CVR YoY (%)'] =  ((df_by_date_combined['CVR - TY'] - df_by_date_combined['CVR - LY'])/df_by_date_combined['CVR - LY'] * 100)

	df_by_date_combined['CPA - TY'] = np.where((df_by_date_combined['Spend TY'] != 0) & (df_by_date_combined['Bookings - TY'] != 0), \
									  (df_by_date_combined['Spend TY']/df_by_date_combined['Bookings - TY']), df_by_date_combined['CPA - TY'])
	df_by_date_combined['CPA - LP'] = np.where((df_by_date_combined['Spend - LP'] != 0) & (df_by_date_combined['Bookings - LP'] != 0), \
									  (df_by_date_combined['Spend - LP']/df_by_date_combined['Bookings - LP']), df_by_date_combined['CPA - LP'])
	df_by_date_combined['CPA_PoP_abs_conditional'] =  df_by_date_combined['CPA PoP (Abs)'] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LP'] != 0), \
									  (df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LP']), df_by_date_combined['CPA PoP (Abs)'])

	df_by_date_combined['CPA_PoP_percent_conditional'] =  df_by_date_combined['CPA PoP (%)' ] =  ((df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LP'])/df_by_date_combined['CPA - LP'] * 100)


	df_by_date_combined['CPA - LY'] = np.where((df_by_date_combined['Spend LY'] != 0) & (df_by_date_combined['Bookings - LY'] != 0), \
									  (df_by_date_combined['Spend LY']/df_by_date_combined['Bookings - LY']), df_by_date_combined['CPA - LY'])
	df_by_date_combined['CPA_YoY_abs_conditional'] =  df_by_date_combined['CPA YoY (Abs)'] =  np.where((df_by_date_combined['CPA - TY'] != 0) & (df_by_date_combined['CPA - LY'] != 0), \
									  (df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LY']), df_by_date_combined['CPA YoY (Abs)'])
	df_by_date_combined['CPA_YoY_percent_conditional'] =  df_by_date_combined['CPA YoY (%)'] =  (df_by_date_combined['CPA - TY'] - df_by_date_combined['CPA - LY'])/df_by_date_combined['CPA - LY'] * 100

	df_by_date_combined['CPS_PoP_abs_conditional'] =  df_by_date_combined['CPS PoP (Abs)']

	#### REMEMBER FORMATTING MUST BE DONE AFTER MAKING CALCULATIONS
	df_by_date_combined['CPS - TY'] = np.where((df_by_date_combined['CPS - TY'].notnull()), \
		df_by_date_combined['CPS - TY'].apply(formatter_currency_with_cents), df_by_date_combined['CPS - TY'])

	df_by_date_combined['CPS - LP'] = np.where((df_by_date_combined['CPS - LP'].notnull()), \
		df_by_date_combined['CPS - LP'].apply(formatter_currency_with_cents), df_by_date_combined['CPS - LP'])

	df_by_date_combined['CPS - LY'] = np.where((df_by_date_combined['CPS - LY'].notnull()), \
		df_by_date_combined['CPS - LY'].apply(formatter_currency_with_cents), df_by_date_combined['CPS - LY'])

	df_by_date_combined['CPS PoP (Abs)'] = np.where((df_by_date_combined['CPS PoP (Abs)'].notnull()), \
		df_by_date_combined['CPS PoP (Abs)'].apply(formatter_currency_with_cents), df_by_date_combined['CPS PoP (Abs)'])

	df_by_date_combined['CPS YoY (Abs)'] = np.where((df_by_date_combined['CPS YoY (Abs)'].notnull()), \
		df_by_date_combined['CPS YoY (Abs)'].apply(formatter_currency_with_cents), df_by_date_combined['CPS YoY (Abs)'])

	df_by_date_combined['CPA - TY'] = np.where((df_by_date_combined['CPA - TY'].notnull()), \
		df_by_date_combined['CPA - TY'].apply(formatter_currency_with_cents), df_by_date_combined['CPA - TY'])

	df_by_date_combined['CPA - LP'] = np.where((df_by_date_combined['CPA - LP'].notnull()), \
		df_by_date_combined['CPA - LP'].apply(formatter_currency_with_cents), df_by_date_combined['CPA - LP'])

	df_by_date_combined['CPA - LY'] = np.where((df_by_date_combined['CPA - LY'].notnull()), \
		df_by_date_combined['CPA - LY'].apply(formatter_currency_with_cents), df_by_date_combined['CPA - LY'])

	df_by_date_combined['CPA PoP (Abs)'] = np.where((df_by_date_combined['CPA PoP (Abs)'].notnull()), \
	df_by_date_combined['CPA PoP (Abs)'].apply(formatter_currency_with_cents), df_by_date_combined['CPA PoP (Abs)'])

	df_by_date_combined['CPA YoY (Abs)'] = np.where((df_by_date_combined['CPA YoY (Abs)'].notnull()), \
		df_by_date_combined['CPA YoY (Abs)'].apply(formatter_currency_with_cents), df_by_date_combined['CPA YoY (Abs)'])

	df_by_date_combined['CPA PoP (%)'] = np.where((df_by_date_combined['CPA PoP (%)'].notnull()), \
		df_by_date_combined['CPA PoP (%)'].apply(formatter_percent), df_by_date_combined['CPA PoP (%)'])

	df_by_date_combined['CPA YoY (%)'] = np.where((df_by_date_combined['CPA YoY (%)'].notnull()), \
		df_by_date_combined['CPA YoY (%)'].apply(formatter_percent), df_by_date_combined['CPA YoY (%)'])

	df_by_date_combined['CPS PoP (%)'] = np.where((df_by_date_combined['CPS PoP (%)'].notnull()), \
		df_by_date_combined['CPS PoP (%)'].apply(formatter_percent), df_by_date_combined['CPS PoP (%)'])

	df_by_date_combined['CPS YoY (%)'] = np.where((df_by_date_combined['CPS YoY (%)'].notnull()), \
		df_by_date_combined['CPS YoY (%)'].apply(formatter_percent), df_by_date_combined['CPS YoY (%)'])

	df_by_date_combined['CVR PoP (%)'] = np.where((df_by_date_combined['CVR PoP (%)'].notnull()), \
		df_by_date_combined['CVR PoP (%)'].apply(formatter_percent), df_by_date_combined['CVR PoP (%)'])

	df_by_date_combined['CVR YoY (%)'] = np.where((df_by_date_combined['CVR YoY (%)'].notnull()), \
		df_by_date_combined['CVR YoY (%)'].apply(formatter_percent), df_by_date_combined['CVR YoY (%)'])

	df_by_date_combined['CVR - TY'] = np.where((df_by_date_combined['CVR - TY'].notnull()), \
		df_by_date_combined['CVR - TY'].apply(formatter_percent_2_digits), df_by_date_combined['CVR - TY'])

	df_by_date_combined['CVR - LP'] = np.where((df_by_date_combined['CVR - LP'].notnull()), \
		df_by_date_combined['CVR - LP'].apply(formatter_percent_2_digits), df_by_date_combined['CVR - LP'])

	df_by_date_combined['CVR - LY'] = np.where((df_by_date_combined['CVR - LY'].notnull()), \
		df_by_date_combined['CVR - LY'].apply(formatter_percent_2_digits), df_by_date_combined['CVR - LY'])

	df_by_date_combined['CVR PoP (Abs)'] = np.where((df_by_date_combined['CVR PoP (Abs)'].notnull()), \
		df_by_date_combined['CVR PoP (Abs)'].apply(formatter_percent_2_digits), df_by_date_combined['CVR PoP (Abs)'])

	df_by_date_combined['CVR YoY (Abs)'] = np.where((df_by_date_combined['CVR YoY (Abs)'].notnull()), \
		df_by_date_combined['CVR YoY (Abs)'].apply(formatter_percent_2_digits), df_by_date_combined['CVR YoY (Abs)'])


	# Rearrange the columns
	df_by_date_combined = df_by_date_combined[[
		'Placement type', 
		'CPS - TY', 
		'CPS - LP', 'CPS PoP (Abs)', 'CPS PoP (%)', 
		'CPS - LY',  'CPS YoY (Abs)', 'CPS YoY (%)', 
		'CVR - TY', 
		'CVR - LP', 'CVR PoP (Abs)', 'CVR PoP (%)', 
		'CVR - LY', 'CVR YoY (Abs)', 'CVR YoY (%)', 
		'CPA - TY', 
		'CPA - LP', 'CPA PoP (Abs)', 'CPA PoP (%)', 
		'CPA - LY', 'CPA YoY (Abs)', 'CPA YoY (%)',
		'CPS_PoP_abs_conditional', 'CPS_PoP_percent_conditional', 'CPS_YoY_abs_conditional', 'CPS_PoP_percent_conditional', 
		'CVR_PoP_abs_conditional', 'CVR_PoP_percent_conditional', 'CVR_YoY_abs_conditional', 'CVR_YoY_percent_conditional',
		'CPA_PoP_abs_conditional', 'CPA_PoP_percent_conditional', 'CPA_YoY_abs_conditional', 'CPA_YoY_percent_conditional'
		]]

	data_df = df_by_date_combined.to_dict("rows")
	return data_df

######################## FOR GRAPHS  ########################

def update_graph(filtered_df, end_date):
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
    if end_date_string <= '2018-12-29':
        current_year = 2018
    else:
        current_year = 2019

    # Calulate YoY Differences
    filtered_df['Spend YoY (%)'] = ((filtered_df['Spend TY'] - filtered_df['Spend LY'])/filtered_df['Spend LY']) * 100
    filtered_df['Sessions YoY (%)'] = ((filtered_df['Sessions - TY'] - filtered_df['Sessions - LY'])/filtered_df['Sessions - LY']) * 100
    filtered_df['Bookings - % - PY'] = ((filtered_df['Bookings - TY'] - filtered_df['Bookings - LY'])/filtered_df['Bookings - LY']) * 100
    filtered_df['Revenue - % - PY'] = ((filtered_df['Revenue - TY'] - filtered_df['Revenue - LY'])/filtered_df['Revenue - LY']) * 100

    # Calculate CPS, CR, CPA
    filtered_df['CPS - TY'] = np.nan
    filtered_df['CPS - LY'] = np.nan
    filtered_df['% YoY_CPS'] = np.nan

    filtered_df['CVR - TY'] = np.nan
    filtered_df['CVR - LY'] = np.nan
    filtered_df['CVR YoY (Abs)'] = np.nan

    filtered_df['CPA - TY'] = np.nan
    filtered_df['CPA - LY'] = np.nan
    filtered_df['% YoY_CPA'] = np.nan

    filtered_df['CPS - TY'] = np.where((filtered_df['Spend TY'] != 0) &  (filtered_df['Sessions - TY'] != 0), (filtered_df['Spend TY']/filtered_df['Sessions - TY']), filtered_df['CPS - TY'])                      
    filtered_df['CPS - LY'] = np.where((filtered_df['Spend LY'] != 0) &  (filtered_df['Sessions - LY'] != 0), (filtered_df['Spend LY']/filtered_df['Sessions - LY']), filtered_df['CPS - LY'])
    filtered_df['% YoY_CPS'] =  np.where((filtered_df['CPS - TY'] != 0) &  (filtered_df['CPS - LY'] != 0), ((filtered_df['CPS - TY'] - filtered_df['CPS - LY'])/filtered_df['CPS - LY']), filtered_df['% YoY_CPS'])

    filtered_df['CVR - TY'] = np.where(((filtered_df['Bookings - TY'] != 0) & (filtered_df['Sessions - TY'] != 0)), (filtered_df['Bookings - TY']/filtered_df['Sessions - TY'] * 100), filtered_df['CVR - TY'])
    filtered_df['CVR - LY'] = np.where(((filtered_df['Bookings - LY'] != 0) & (filtered_df['Sessions - LY'] != 0)), (filtered_df['Bookings - LY']/filtered_df['Sessions - LY'] * 100), filtered_df['CVR - LY'])
    filtered_df['CVR YoY (Abs)'] =  np.where((filtered_df['CVR - TY'].notnull() & filtered_df['CVR - LY'].notnull()), ((filtered_df['CVR - TY'] - filtered_df['CVR - LY'])), filtered_df['CVR YoY (Abs)'])

    filtered_df['CPA - TY'] = np.where((filtered_df['Spend TY'] != 0) & (filtered_df['Bookings - TY'] != 0), (filtered_df['Spend TY']/filtered_df['Bookings - TY']), filtered_df['CPA - TY'])                     
    filtered_df['CPA - LY'] = np.where((filtered_df['Spend LY'] != 0) & (filtered_df['Bookings - LY'] != 0), (filtered_df['Spend LY']/filtered_df['Bookings - LY']), filtered_df['CPA - LY'])
    filtered_df['% YoY_CPA'] =  np.where((filtered_df['CPA - TY'] != 0) & (filtered_df['CPA - LY'] != 0), ((filtered_df['CPA - TY'] - filtered_df['CPA - LY'])/filtered_df['CPA - LY']) * 100, filtered_df['% YoY_CPA'])


    # Sessions Graphs 
    sessions_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Sessions - TY'],
      text='Sessions - TY'
    )
    sessions_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['Sessions - TY'],
      text='Sessions - LY'
    )
    sessions_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Sessions YoY (%)'],
      text='Sessions YoY (%)', opacity=0.6
    )
    # Spend Graphs
    spend_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Spend TY'],
      text='Spend TY'
    )
    spend_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['Spend TY'],
      text='Spend LY'
    )
    spend_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Spend YoY (%)'],
      text='Spend YoY (%)', opacity=0.6
    )
    # Bookings Graphs
    bookings_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Bookings - TY'],
      text='Bookings - TY'
    )
    bookings_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['Bookings - TY'],
      text='Bookings - LY'
    )
    bookings_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['Bookings - % - PY'],
      text='Bookings - % - PY', opacity=0.6
    )
    cpa_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['CPA - TY'],
      text='CPA - TY'
    )
    cpa_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['CPA - TY'],
      text='CPA - LY'
    )
    cpa_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['% YoY_CPA'],
      text='% CPA - YoY', opacity=0.6
    )
    cps_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['CPS - TY'],
      text='CPS - TY'
    )
    cps_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['CPS - TY'],
      text='CPS - LY'
    )
    cps_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['% YoY_CPS'],
      text='% CPS - YoY', opacity=0.6
    )
    cr_ty = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['CVR - TY'],
      text='CVR - TY'
    )
    cr_ly = go.Scatter(
      x=filtered_df[(filtered_df['Year'] == current_year-1)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year-1)]['CVR - TY'],
      text='CVR - LY'
    )
    cr_yoy = go.Bar(
      x=filtered_df[(filtered_df['Year'] == current_year)]['Week'],
      y=filtered_df[(filtered_df['Year'] == current_year)]['CVR YoY (Abs)'],
      text='CVR YoY (Abs)', opacity=0.6
    )

    fig = tools.make_subplots(
      rows=6, 
      cols=1, 
      shared_xaxes=True,
      subplot_titles=(								# Be sure to have same number of titles as number of graphs
        'Sessions', 
        'Spend',
        'Bookings', 
        'Cost per Acquisition',
        'CPS',
        'Conversion Rate'
        ))

    fig.append_trace(sessions_ty, 1, 1)		# 0
    fig.append_trace(sessions_ly, 1, 1)		# 1
    fig.append_trace(sessions_yoy, 1, 1)	# 2
    fig.append_trace(spend_ty, 2, 1)		# 3
    fig.append_trace(spend_ly, 2, 1)		# 4
    fig.append_trace(spend_yoy, 2, 1)		# 5
    fig.append_trace(bookings_ty, 3, 1)		# 6
    fig.append_trace(bookings_ly, 3, 1)		# 7
    fig.append_trace(bookings_yoy, 3, 1)	# 8
    fig.append_trace(cpa_ty, 4, 1)			# 9
    fig.append_trace(cpa_ly, 4, 1)			# 10
    fig.append_trace(cpa_yoy, 4, 1)			# 11
    fig.append_trace(cps_ty, 5, 1)			# 12
    fig.append_trace(cps_ly, 5, 1)			# 13
    fig.append_trace(cps_yoy, 5, 1)			# 14
    fig.append_trace(cr_ty, 6, 1)			# 15
    fig.append_trace(cr_ly, 6, 1)			# 16
    fig.append_trace(cr_yoy, 6, 1)			# 17

    # integer index below is the index of the trace
    # yaxis indices below need to start from the number of total graphs + 1 since they are on right-side
    # overlaing and anchor axes correspond to the graph number

    fig['data'][2].update(yaxis='y7')
    fig['layout']['yaxis7'] = dict(overlaying='y1', anchor='x1', side='right', showgrid=False, title='% Change YoY')

    fig['data'][5].update(yaxis='y8')
    fig['layout']['yaxis8'] = dict(overlaying='y2', anchor='x2', side='right', showgrid=False, title='% Change YoY')

    fig['data'][8].update(yaxis='y9')
    fig['layout']['yaxis9'] = dict(overlaying='y3', anchor='x3', side='right', showgrid=False, title='% Change YoY')

    fig['data'][11].update(yaxis='y10')
    fig['layout']['yaxis10'] = dict(overlaying='y4', anchor='x4', side='right', showgrid=False, title='% Change YoY')

    fig['data'][14].update(yaxis='y11')
    fig['layout']['yaxis11'] = dict(overlaying='y5', anchor='x5', side='right', showgrid=False, title='% Change YoY')

    fig['data'][17].update(yaxis='y12')
    fig['layout']['yaxis12'] = dict(overlaying='y6', anchor='x6', side='right', showgrid=False, title='% Change YoY')

    fig['layout']['xaxis'].update(title='Week of the Year' + ' - ' + str(current_year))
    for i in fig['layout']['annotations']:
      i['font'] = dict(size=12,
        # color='#ff0000'
        )
    fig['layout'].update(
      height= 1500,
      # width=750, 
      showlegend=False, 
      xaxis=dict(
        # tickmode='linear',
        # ticks='outside',
        # tick0=1,
        dtick=5,
        ticklen=8,
        tickwidth=2,
        tickcolor='#000',
        showgrid=True,
        zeroline=True,
        # showline=True,
        # mirror='ticks',
        # gridcolor='#bdbdbd',
        gridwidth=2
    ),
      )
    updated_fig = fig
    return updated_fig


