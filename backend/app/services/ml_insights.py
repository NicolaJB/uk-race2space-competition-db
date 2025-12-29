import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend
import matplotlib.pyplot as plt
import io
import base64
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

DB_PATH = "race-to-space.db"

def get_team_insights(team_name: str):
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)

    # Load team results
    df_hybrids = pd.read_sql_query("SELECT * FROM hybrids_results", conn)
    df_biprops = pd.read_sql_query("SELECT * FROM biprops_results", conn)
    df_teams = pd.read_sql_query("SELECT * FROM teams", conn)
    df_progress = pd.read_sql_query("SELECT * FROM progress_details", conn)
    conn.close()

    # Merge results by team
    df_hybrids_grouped = df_hybrids.groupby('team_id').agg({
        'total_score': 'sum',
        'innov_complexity':'mean',
        'innov_implementation':'mean',
        'innov_performance':'mean',
        'testing_score':'mean',
        'documentation_score':'mean',
        'presentation_score':'mean'
    }).reset_index()

    df_biprops_grouped = df_biprops.groupby('team_id').agg({
        'total_score': 'sum',
        'innov_complexity':'mean',
        'innov_implementation':'mean',
        'innov_performance':'mean',
        'testing_score':'mean',
        'documentation_score':'mean',
        'presentation_score':'mean'
    }).reset_index()

    # Combine scores
    df_combined = pd.merge(df_hybrids_grouped, df_biprops_grouped, on='team_id', how='outer', suffixes=('_hyb','_bi'))
    df_combined.fillna(0, inplace=True)
    df_combined['total_score'] = df_combined['total_score_hyb'] + df_combined['total_score_bi']

    # Features for ML
    features = [
        'innov_complexity_hyb','innov_implementation_hyb','innov_performance_hyb',
        'testing_score_hyb','documentation_score_hyb','presentation_score_hyb',
        'innov_complexity_bi','innov_implementation_bi','innov_performance_bi',
        'testing_score_bi','documentation_score_bi','presentation_score_bi'
    ]
    X = df_combined[features]
    y = df_combined['total_score']

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train lightweight model
    model = LinearRegression()
    model.fit(X_scaled, y)

    # Predict all teams
    df_combined['predicted_score'] = model.predict(X_scaled)

    # Get selected team info
    team_row = pd.merge(df_combined, df_teams, left_on='team_id', right_on='team_id')
    team_row = team_row[team_row['team_name'].str.lower() == team_name.lower()]
    if team_row.empty:
        return {"error": "Team not found"}

    team_row = team_row.iloc[0]

    hybrids_score = float(team_row.get("total_score_hyb", 0))
    biprops_score = float(team_row.get("total_score_bi", 0))
    ai_ml_score = round((hybrids_score + biprops_score) / 2, 2)

    # Pull progress_details for selected team
    progress_row = df_progress[df_progress['team_id'] == team_row['team_id']]
    if not progress_row.empty:
        progress_row = progress_row.iloc[0]
        team_notes = progress_row.get("team_notes", "") or "None listed"
        mentor = progress_row.get("mentor", "") or "None listed"
        sponsor = progress_row.get("sponsor", "") or "None listed"
    else:
        team_notes = mentor = sponsor = "None listed"

    engine_type = team_row.get("engine_type", "N/A")

    team_pred_score = float(team_row['predicted_score'])

    # Generate chart
    plt.figure(figsize=(10,6))
    plt.bar(df_combined['team_id'], df_combined['predicted_score'], color='gray')
    plt.bar(team_row['team_id'], team_pred_score, color='red')
    plt.xticks(df_combined['team_id'], df_teams.set_index('team_id').loc[df_combined['team_id']]['team_name'], rotation=90)
    plt.ylabel("Predicted Total Score")
    plt.title(f"Team {team_name} vs All Teams")
    plt.tight_layout()

    # Save chart to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return {
        "team_name": team_name,
        "engine_type": engine_type or "N/A",
        "insights": [
            {"metric": "Hybrids Score", "value": hybrids_score},
            {"metric": "Biprops Score", "value": biprops_score},
            {"metric": "AI/ML Score", "value": ai_ml_score},
        ],
        "notes": team_notes,
        "mentor": mentor,
        "sponsor": sponsor,
        "predicted_score": team_pred_score,
        "chart": chart_base64,
    }
