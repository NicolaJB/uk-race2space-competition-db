"use client";

import React, { useState } from "react";
import QueryForm from "../components/QueryForm";
import TeamInsights from "../components/TeamInsights";

export default function HomePage() {
  const [selectedTeam, setSelectedTeam] = useState("");

  return (
    <div
      style={{
        backgroundColor: "#121212",
        color: "#fff",
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <header style={{ marginBottom: "2rem" }}>
        <img
          src="/R2S-Logo.png"
          alt="Race2Space Logo"
          style={{ height: "80px", marginBottom: "1rem" }}
        />
        <h1
          style={{
            fontSize: "2.5rem",
            fontWeight: "bold",
            margin: "0.5rem 0",
          }}
        >
          R2S Competition DB Query
        </h1>
        <p>
          Welcome! This database lets you explore Race2Space competition
          results. Enter a team name below to see their engine scores.
        </p>
        <p>
          Visit our official site:{" "}
          <a
            href="https://race2space.org.uk"
            target="_blank"
            style={{ color: "#1E90FF" }}
          >
            race2space.org.uk
          </a>
        </p>
      </header>

      {/* Query form */}
      <QueryForm onSelectTeam={setSelectedTeam} />

      {/* Team insights */}
      {/* TeamInsights will fetch data when selectedTeam changes */}
      {selectedTeam && <TeamInsights teamName={selectedTeam} />}
    </div>
  );
}
