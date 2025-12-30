"use client";

import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface TeamInsightsProps {
  teamName: string;
}

interface Insight {
  metric: string;
  value: number;
}

interface TeamData {
  insights: Insight[];
  notes: string;
  mentor: string;
  sponsor: string;
  chart: string | null;
}

const DEFAULT_INSIGHTS: Insight[] = [
  { metric: "Hybrids Score", value: 0 },
  { metric: "Biprops Score", value: 0 },
  { metric: "AI/ML Score", value: 0 },
];

export default function TeamInsights({ teamName }: TeamInsightsProps) {
  const [teamData, setTeamData] = useState<TeamData>({
    insights: DEFAULT_INSIGHTS,
    notes: "None listed",
    mentor: "None listed",
    sponsor: "None listed",
    chart: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!teamName) return;

    const fetchInsights = async () => {
      setLoading(true);
      setError("");

      try {
        const res = await fetch("http://127.0.0.1:8000/team-insights", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ team_name: teamName }),
        });

        if (!res.ok) {
          const text = await res.text();
          throw new Error(text);
        }

        const data = await res.json();
        if (data.error) throw new Error(data.error);

        setTeamData({
          insights:
            Array.isArray(data.insights) && data.insights.length > 0
              ? data.insights.map((i: any) => ({
                  metric: i.metric,
                  value: Number(i.value) || 0,
                }))
              : DEFAULT_INSIGHTS,
          notes: data.notes || "None listed",
          mentor: data.mentor || "None listed",
          sponsor: data.sponsor || "None listed",
          chart: data.chart || null,
        });
      } catch (err: any) {
        setError(err.message || "Failed to fetch team insights");
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [teamName]);

  if (!teamName) return null;

  return (
    <div style={{ marginTop: "2rem", color: "white" }}>
      <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
        {teamName} Insights
      </h2>

      {loading && <p>Loading team insights...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* TABLE */}
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          marginTop: "1rem",
          backgroundColor: "#111",
        }}
      >
        <thead>
          <tr>
            <th style={{ borderBottom: "1px solid #fff", padding: "0.5rem" }}>
              Metric
            </th>
            <th style={{ borderBottom: "1px solid #fff", padding: "0.5rem" }}>
              Value
            </th>
          </tr>
        </thead>
        <tbody>
          {teamData.insights.map((insight) => (
            <tr key={insight.metric}>
              <td style={{ padding: "0.5rem", borderBottom: "1px solid #444" }}>
                {insight.metric}
              </td>
              <td style={{ padding: "0.5rem", borderBottom: "1px solid #444" }}>
                {insight.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* CHART */}
      {teamData.insights.length > 0 && (
        <div
          style={{
            marginTop: "1rem",
            height: 320,
            maxWidth: "800px",
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={teamData.insights}>
              <XAxis dataKey="metric" tick={{ fill: "#fff" }} />
              <YAxis tick={{ fill: "#fff" }} />
              <Tooltip contentStyle={{ backgroundColor: "#333", color: "#fff" }} />
              <Legend wrapperStyle={{ color: "#fff" }} />
              <Bar dataKey="value" fill="#1E90FF" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* TEAM DETAILS */}
      <div
        style={{
          marginTop: "2rem",
          maxWidth: "800px",
          marginLeft: "auto",
          marginRight: "auto",
          backgroundColor: "#111",
          border: "1px solid #444",
          borderRadius: "8px",
          padding: "1rem",
          fontWeight: "bold",
        }}
      >
        Team Details
        <p style={{ fontWeight: "normal" }}>
          <strong>Notes:</strong> <em>{teamData.notes}</em>
        </p>
        <p style={{ fontWeight: "normal" }}>
          <strong>Mentor:</strong> {teamData.mentor}
        </p>
        <p style={{ fontWeight: "normal" }}>
          <strong>Sponsor:</strong> {teamData.sponsor}
        </p>
      </div>

      {/* ================= ALL-TEAMS CHART EXPLANATION ================= */}
      <p
        style={{
          marginTop: "1rem",
          maxWidth: "800px",
          marginLeft: "auto",
          marginRight: "auto",
          textAlign: "center",
        }}
      >
        <strong>Predicted Total Performance Scores (All Teams)</strong>
      </p>
      <p
        style={{
          marginTop: "0.5rem",
          maxWidth: "800px",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        Team currently selected is shown in red. Score predictions use a linear regression model based on component metrics:{" "}
        <em>innovation scores, testing, documentation, and presentation (both Hybrids and Biprops)</em>.
      </p>

      {/* ================= TEAM-SPECIFIC CHART EXPLANATION ================= */}

      {/* BASE64 CHART */}
      {teamData.chart && (
        <div
          style={{
            marginTop: "2rem",
            maxWidth: "800px",
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <img
            src={`data:image/png;base64,${teamData.chart}`}
            alt={`${teamName} chart`}
            style={{ width: "100%" }}
          />
        </div>
      )}
    </div>
  );
}
