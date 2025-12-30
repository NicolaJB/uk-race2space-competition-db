import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend
import matplotlib.pyplot as plt
import io
import base64
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# -----------------------
# Absolute DB path
# -----------------------
DB_PATH = "/Users/nicolabuttigieg/PycharmProjects/R2S-CompetitionDB/race-to-space.db"

# -----------------------
# Main function
# -----------------------
def get_team_insights(team_name: str):
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)

    try:
        # Load all relevant tables
        df_hybrids = pd.read_sql_query("SELECT * FROM hybrids_results", conn)
        df_biprops = pd.read_sql_query("SELECT * FROM biprops_results", conn)
        df_teams = pd.read_sql_query("SELECT * FROM teams", conn)
        df_progress = pd.read_sql_query("SELECT * FROM progress_details", conn)
    finally:
        conn.close()

    # Ensure team_id is numeric
    for df in [df_teams, df_progress, df_hybrids, df_biprops]:
        df['team_id'] = df['team_id'].astype(int)

    # Aggregate scores
    df_hybrids_grouped = df_hybrids.groupby('team_id').agg({
        'total_score': 'sum',
        'innov_complexity': 'mean',
        'innov_implementation': 'mean',
        'innov_performance': 'mean',
        'testing_score': 'mean',
        'documentation_score': 'mean',
        'presentation_score': 'mean'
    }).reset_index()

    df_biprops_grouped = df_biprops.groupby('team_id').agg({
        'total_score': 'sum',
        'innov_complexity': 'mean',
        'innov_implementation': 'mean',
        'innov_performance': 'mean',
        'testing_score': 'mean',
        'documentation_score': 'mean',
        'presentation_score': 'mean'
    }).reset_index()

    # Merge scores
    df_combined = pd.merge(
        df_hybrids_grouped,
        df_biprops_grouped,
        on='team_id',
        how='outer',
        suffixes=('_hyb', '_bi')
    )
    df_combined.fillna(0, inplace=True)
    df_combined['total_score'] = df_combined['total_score_hyb'] + df_combined['total_score_bi']

    # Prepare features and target
    features = [
        'innov_complexity_hyb', 'innov_implementation_hyb', 'innov_performance_hyb',
        'testing_score_hyb', 'documentation_score_hyb', 'presentation_score_hyb',
        'innov_complexity_bi', 'innov_implementation_bi', 'innov_performance_bi',
        'testing_score_bi', 'documentation_score_bi', 'presentation_score_bi'
    ]
    X = df_combined[features]
    y = df_combined['total_score']

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train simple regression
    model = LinearRegression()
    model.fit(X_scaled, y)
    df_combined['predicted_score'] = model.predict(X_scaled)

    # Find the requested team
    team_row = pd.merge(df_combined, df_teams, on='team_id')
    team_row = team_row[team_row['team_name'].str.lower() == team_name.lower()]

    if team_row.empty:
        return {"error": "Team not found"}

    team_row = team_row.iloc[0]
    team_id = int(team_row['team_id'])

    hybrids_score = float(team_row.get("total_score_hyb", 0))
    biprops_score = float(team_row.get("total_score_bi", 0))
    ai_ml_score = round((hybrids_score + biprops_score) / 2, 2)
    engine_type = team_row.get("engine_type", "N/A")
    team_pred_score = float(team_row['predicted_score'])

    # Pull progress details
    progress_row = df_progress[df_progress['team_id'] == team_id]
    if not progress_row.empty:
        progress_row = progress_row.iloc[0]
        team_notes = progress_row.get("team_notes", "") or "None listed"
        mentor = progress_row.get("mentor", "") or "None listed"
        sponsor = progress_row.get("sponsor", "") or "None listed"
    else:
        team_notes = mentor = sponsor = "None listed"

    # Generate chart
    plt.figure(figsize=(10, 6))
    plt.bar(df_combined['team_id'], df_combined['predicted_score'], color='gray')
    plt.bar([team_id], [team_pred_score], color='red')
    team_names = df_teams.set_index('team_id').loc[df_combined['team_id'].astype(int)]['team_name']
    plt.xticks(df_combined['team_id'], team_names, rotation=90)
    plt.ylabel("Predicted Total Score")
    plt.title(f"Team {team_name} vs All Teams")
    plt.tight_layout()

    # Convert chart to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Return structured data
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
