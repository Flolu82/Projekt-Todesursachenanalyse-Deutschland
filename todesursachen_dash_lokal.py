# Import required libraries
from pathlib import Path
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from itertools import cycle

# -----------------------------
# Robust local file path
# -----------------------------
HERE = Path(__file__).parent.resolve()
file_path = HERE / "Todesdaten8.xlsx"
if not file_path.exists():
    # Fallback: data/ subfolder
    file_path = HERE / "data" / "Todesdaten8.xlsx"
if not file_path.exists():
    raise FileNotFoundError(
        f"Excel-Datei nicht gefunden: {HERE/'Todesdaten8.xlsx'} oder {HERE/'data/Todesdaten8.xlsx'}.\n"
        "Lege die Datei an eine der beiden Stellen oder passe 'file_path' im Skript an."
    )

# Load the Excel file
data = pd.ExcelFile(file_path)

# Load the relevant sheet
sheet_name = '23211-0001'
df = data.parse(sheet_name, skiprows=5, header=None)

# Adjust the dataframe
year_row = df.iloc[0].fillna(method="ffill")
gender_row = df.iloc[2]
new_header = [f"{year} {gender}" for year, gender in zip(year_row, gender_row)]
new_header[0] = "TDU Code"
new_header[1] = "Todesursachen"
df.columns = new_header
df = df[3:-3]

# Convert relevant columns to numeric for years 1990-2023
columns_to_numeric = [col for col in df.columns if any(str(year) in str(col) for year in range(1990, 2024))]
df[columns_to_numeric] = df[columns_to_numeric].apply(pd.to_numeric, errors='coerce')

# Extract unique causes of death for dropdown options
unique_causes = sorted([c for c in df["Todesursachen"].dropna().unique().tolist() if str(c).strip()])

# Dash App Setup (local)
app = dash.Dash(__name__)

default_selection = unique_causes[:2] if unique_causes else None

app.layout = html.Div([
    html.H1("Interactive Visualization of Death Causes (1990–2023)", style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='cause-selector',
            options=[{'label': cause, 'value': cause} for cause in unique_causes],
            value=default_selection,
            multi=True,
            placeholder="Select Causes of Death"
        )
    ], style={'width': '80%', 'margin': 'auto'}),
    dcc.Graph(id='death-cause-graph')
])

# Updated Blue and Red palettes
BLUE_PALETTE = ['#1f77b4', '#76c7c0', '#17becf', '#4c78a8', '#5a6dba']  # Männlich
RED_PALETTE  = ['#d62728', '#ff7f0e', '#e377c2', '#9467bd', '#f57b71']  # Weiblich

@app.callback(
    Output('death-cause-graph', 'figure'),
    [Input('cause-selector', 'value')]
)
def update_graph(selected_causes):
    if not selected_causes:
        return go.Figure()

    # Initialize an empty figure
    fig = go.Figure()

    # Years to analyze (1990-2023)
    years_all = [str(year) for year in range(1990, 2024)]

    # Filter data for selected causes
    filtered_df = df[df["Todesursachen"].isin(selected_causes)]

    # Recreate color cycles on every update for stable mapping order
    blue_cycle = cycle(BLUE_PALETTE)
    red_cycle = cycle(RED_PALETTE)

    # Add traces for each selected cause
    for _, row in filtered_df.iterrows():
        cause = row["Todesursachen"]
        
        # Separate male and female data
        male_data = [row.get(f"{year} männlich", 0) for year in years_all]
        female_data = [row.get(f"{year} weiblich", 0) for year in years_all]
        
        # Get next colors from the palette
        male_color = next(blue_cycle)
        female_color = next(red_cycle)
        
        # Add male data to the plot
        fig.add_trace(go.Scatter(
            x=years_all,
            y=male_data,
            mode='lines+markers',
            name=f"{cause} (Männlich)",
            line=dict(color=male_color, dash='solid'),
            marker=dict(symbol='circle')
        ))

        # Add female data to the plot
        fig.add_trace(go.Scatter(
            x=years_all,
            y=female_data,
            mode='lines+markers',
            name=f"{cause} (Weiblich)",
            line=dict(color=female_color, dash='dot'),
            marker=dict(symbol='x')
        ))

    # Update layout for better readability
    fig.update_layout(
        title="Deaths by Selected Causes (Männlich vs. Weiblich)",
        xaxis_title="Year",
        yaxis_title="Number of Deaths",
        legend_title="Todesursachen",
        template="plotly_white",
        height=600
    )

    return fig

if __name__ == "__main__":
    # Local run
    app.run_server(debug=True)
    # Hinweis: Für GCP würdest du zusätzlich unten exportieren:
    # server = app.server
