"use client";

import React, { useState } from "react";

interface QueryFormProps {
  onSelectTeam: (teamName: string) => void;
}

export default function QueryForm({ onSelectTeam }: QueryFormProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSelectTeam(query.trim());
    setQuery(""); // clear input after submit
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter team name"
        style={{
          padding: "0.5rem",
          marginRight: "0.5rem",
          width: "200px",
          borderRadius: "4px",
          border: "1px solid #ccc",
        }}
      />
      <button
        type="submit"
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: "#1E90FF",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Submit
      </button>
    </form>
  );
}
