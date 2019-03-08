import dash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname='/cc-travel-report/paid-search/')
server = app.server
app.config.suppress_callback_exceptions = True

# import dash_auth

# VALID_USERNAME_PASSWORD_PAIRS = [
#     ['alg', 'mexicovacation']
# ]

# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )
