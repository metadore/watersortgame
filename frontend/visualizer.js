/**
 * visualizer.js — Additional Chart.js helpers and tube heatmap visualizer
 * Complements app.js analytics rendering.
 */

"use strict";

const Visualizer = (() => {

  // Radar chart for level difficulty breakdown
  function renderDifficultyRadar(canvasId, labels, values) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    new Chart(canvas, {
      type: "radar",
      data: {
        labels,
        datasets: [{
          label: "Difficulty",
          data: values,
          backgroundColor: "rgba(123,47,255,.2)",
          borderColor: "#7b2fff",
          borderWidth: 2,
          pointBackgroundColor: "#00d4ff",
        }],
      },
      options: {
        responsive: true,
        scales: {
          r: {
            ticks: { color: "#8ba4cc", backdropColor: "transparent" },
            grid: { color: "rgba(80,160,255,.1)" },
            pointLabels: { color: "#8ba4cc" },
          },
        },
        plugins: { legend: { labels: { color: "#8ba4cc" } } },
      },
    });
  }

  // Doughnut chart for win/loss ratio
  function renderWinRatio(canvasId, wins, total) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: ["Wins", "Attempts"],
        datasets: [{
          data: [wins, Math.max(0, total - wins)],
          backgroundColor: ["rgba(0,255,136,.5)", "rgba(255,68,102,.3)"],
          borderColor: ["#00ff88", "#ff4466"],
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: "#8ba4cc" } } },
        cutout: "65%",
      },
    });
  }

  // 2D heatmap grid for tube click patterns
  function renderInteractiveHeatmap(containerId, heatData, numTubes) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";

    const max = Math.max(...Object.values(heatData), 1);

    for (let i = 0; i < numTubes; i++) {
      const cell = document.createElement("div");
      cell.style.cssText = `
        display:inline-flex; align-items:center; justify-content:center;
        width:44px; height:44px; margin:3px; border-radius:8px;
        font-size:.65rem; font-weight:700; color:#fff;
        font-family:'Orbitron',sans-serif;
        cursor:default;
        transition:transform .2s;
      `;
      cell.addEventListener("mouseenter", () => { cell.style.transform = "scale(1.15)"; });
      cell.addEventListener("mouseleave", () => { cell.style.transform = "scale(1)"; });

      const heat = heatData[String(i)] || 0;
      const ratio = heat / max;
      const r = Math.round(255 * ratio);
      const g = Math.round(100 * (1 - ratio));
      const b = Math.round(200 * (1 - ratio));
      cell.style.background = `rgba(${r},${g},${b},${0.25 + ratio * 0.75})`;
      cell.style.boxShadow = ratio > 0.3 ? `0 0 ${ratio * 16}px rgba(${r},${g},${b},.6)` : "none";
      cell.textContent = `T${i + 1}`;
      cell.title = `Tube ${i + 1}: ${heat} interactions`;
      container.appendChild(cell);
    }
  }

  // Expose utilities
  return { renderDifficultyRadar, renderWinRatio, renderInteractiveHeatmap };
})();