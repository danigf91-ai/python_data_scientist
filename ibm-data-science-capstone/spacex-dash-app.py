import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()
launch_sites = sorted(spacex_df["Launch Site"].dropna().unique())

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1("SpaceX Launch Records Dashboard", style={"textAlign": "center", "color": "#503D36", "fontSize": 40}),
    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] + [{"label": site, "value": site} for site in launch_sites],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id="success-pie-chart")),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id="payload-slider", min=0, max=10000, step=1000,
        marks={0:"0",2500:"2500",5000:"5000",7500:"7500",10000:"10000"},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    html.Div(dcc.Graph(id="success-payload-scatter-chart"))
])

@app.callback(Output("success-pie-chart","figure"), Input("site-dropdown","value"))
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        success_counts = spacex_df[spacex_df["class"] == 1].groupby("Launch Site").size().reset_index(name="Success Count")
        return px.pie(success_counts, values="Success Count", names="Launch Site", title="Total Successful Launches by Site")
    filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
    outcome_counts = filtered_df["class"].value_counts().rename_axis("class").reset_index(name="Count")
    outcome_counts["Outcome"] = outcome_counts["class"].map({0:"Failure",1:"Success"})
    return px.pie(outcome_counts, values="Count", names="Outcome", title=f"Launch Outcomes for {entered_site}")

@app.callback(Output("success-payload-scatter-chart","figure"), [Input("site-dropdown","value"), Input("payload-slider","value")])
def get_payload_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= low) & (spacex_df["Payload Mass (kg)"] <= high)]
    if entered_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        title = f"Payload vs. Launch Outcome for {entered_site}"
    else:
        title = "Payload vs. Launch Outcome for All Sites"
    fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", hover_data=["Launch Site"], title=title)
    fig.update_yaxes(tickmode="array", tickvals=[0,1], ticktext=["Failure","Success"])
    return fig

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
