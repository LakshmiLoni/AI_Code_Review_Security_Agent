/**
 * AI Code Review - Dashboard Visualizations (Chart.js)
 * Refined White & Orange Palette
 */

document.addEventListener("DOMContentLoaded", function () {
  const chartCanvas = document.getElementById("severityChart");
  if (!chartCanvas) return;

  const crit = parseInt(chartCanvas.getAttribute("data-critical") || "0", 10);
  const high = parseInt(chartCanvas.getAttribute("data-high") || "0", 10);
  const med = parseInt(chartCanvas.getAttribute("data-medium") || "0", 10);
  const low = parseInt(chartCanvas.getAttribute("data-low") || "0", 10);

  const total = crit + high + med + low;

  if (total === 0) {
    // Show placeholder if no findings recorded
    const ctx = chartCanvas.getContext("2d");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Clean / No Findings"],
        datasets: [{
          data: [1],
          backgroundColor: ["#0d9488"], // Subtle teal clean indicator
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { enabled: false },
        },
        cutout: "70%",
      },
    });
    return;
  }

  const ctx = chartCanvas.getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Critical", "High", "Medium", "Low"],
      datasets: [{
        data: [crit, high, med, low],
        backgroundColor: [
          "#dc2626", // Red for Critical
          "#ea580c", // Dark Orange for High
          "#f59e0b", // Amber for Medium
          "#94a3b8", // Slate neutral for Low
        ],
        hoverOffset: 4,
        borderWidth: 2,
        borderColor: "#ffffff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            boxWidth: 12,
            padding: 16,
            font: { size: 12, family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" },
            color: "#525252",
          },
        },
        tooltip: {
          backgroundColor: "#171717",
          titleColor: "#ffffff",
          bodyColor: "#ffffff",
          padding: 10,
          cornerRadius: 6,
          callbacks: {
            label: function (context) {
              const count = context.raw || 0;
              const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
              return ` ${context.label}: ${count} (${pct}%)`;
            },
          },
        },
      },
      cutout: "70%",
    },
  });
});
