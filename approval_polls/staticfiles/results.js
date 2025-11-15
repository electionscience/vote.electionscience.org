const data = document.currentScript.dataset;
const pollId = parseInt(data.pollId, 10);

document.addEventListener("DOMContentLoaded", async function () {
  const seatsSlider = document.getElementById("seatsSlider");
  const seatsValue = document.getElementById("seatsValue");
  const winnersList = document.getElementById("winnersList");
  const votesTableDiv = document.getElementById("votesTable");
  const allocationLogDiv = document.getElementById("allocationLog");

  let rawBallots = [];
  let choices = [];

  // 1. Fetch raw ballots + choices from /raw endpoint once
  try {
    const response = await fetch(`/polls/${pollId}/raw`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    rawBallots = data.ballots; // e.g. [[1,2], [2,3], ...]
    choices = data.choices; // e.g. [{ id:1, choice_text:'Party A'}, ...]
  } catch (error) {
    console.error("Error fetching raw data:", error);
    allocationLogDiv.textContent =
      "Error loading ballot data. Please try refreshing the page.";
    return;
  }

  // Build a debug table of ballots (optional)
  buildVotesTable(rawBallots, choices);

  // Helper function to detect dark mode
  function isDarkMode() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  // Get chart colors based on dark mode
  function getChartColors() {
    if (isDarkMode()) {
      // Dark mode colors - brighter and more saturated
      return {
        backgroundColor: [
          "rgba(75, 192, 192, 0.8)",
          "rgba(255, 99, 132, 0.8)",
          "rgba(255, 206, 86, 0.8)",
          "rgba(54, 162, 235, 0.8)",
          "rgba(153, 102, 255, 0.8)",
          "rgba(255, 159, 64, 0.8)",
        ],
        borderColor: [
          "rgba(75, 192, 192, 1)",
          "rgba(255, 99, 132, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(255, 159, 64, 1)",
        ],
      };
    } else {
      // Light mode colors
      return {
        backgroundColor: [
          "rgba(75, 192, 192, 0.6)",
          "rgba(255, 99, 132, 0.6)",
          "rgba(255, 206, 86, 0.6)",
          "rgba(54, 162, 235, 0.6)",
          "rgba(153, 102, 255, 0.6)",
          "rgba(255, 159, 64, 0.6)",
        ],
        borderColor: [
          "rgba(75, 192, 192, 1)",
          "rgba(255, 99, 132, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(255, 159, 64, 1)",
        ],
      };
    }
  }

  // 2. Create Chart.js pie chart
  const ctx = document.getElementById("spavChart").getContext("2d");
  const chartColors = getChartColors();
  const spavChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: choices.map((c) => c.choice_text),
      datasets: [
        {
          data: choices.map(() => 0),
          backgroundColor: chartColors.backgroundColor,
          borderColor: chartColors.borderColor,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: isDarkMode() ? "#e0e0e0" : "#000000",
          },
        },
      },
    },
  });

  // Listen for dark mode changes and update chart colors
  if (window.matchMedia) {
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
    darkModeQuery.addEventListener("change", (e) => {
      const newColors = getChartColors();
      spavChart.data.datasets[0].backgroundColor = newColors.backgroundColor;
      spavChart.data.datasets[0].borderColor = newColors.borderColor;
      spavChart.options.plugins.legend.labels.color = e.matches
        ? "#e0e0e0"
        : "#000000";
      spavChart.update();
    });
  }

  // 3. SPAV allowing multiple seats, now with a debug log
  function spav(choices, ballots, seats) {
    const debugLines = [];

    // Each choice gets a seatCount property
    const results = choices.map((c) => ({
      id: c.id,
      text: c.choice_text,
      seatCount: 0,
    }));

    // For each ballot, track how many seats they've contributed to so far
    const ballotWinnerCounts = new Array(ballots.length).fill(0);

    for (let seat = 0; seat < seats; seat++) {
      const seatNumber = seat + 1;
      debugLines.push(`\nSEAT #${seatNumber} Calculation:`);

      // 3.1 Calculate total weight for each choice
      const weights = new Map(); // choiceId -> sum of ballot weights
      results.forEach((r) => weights.set(r.id, 0));

      ballots.forEach((approvedChoices, bIndex) => {
        // Weighted by 1 / (1 + ballotWinnerCounts[bIndex])
        const ballotWeight = 1 / (1 + ballotWinnerCounts[bIndex]);

        approvedChoices.forEach((choiceId) => {
          // This is SPAV, so a choice can keep winning multiple seats
          const prev = weights.get(choiceId) || 0;
          weights.set(choiceId, prev + ballotWeight);
        });
      });

      // Log each choice's weight
      for (const r of results) {
        const w = weights.get(r.id).toFixed(3);
        debugLines.push(`  "${r.text}" => sum weighted votes: ${w}`);
      }

      // 3.2 Find the choice with the highest weight
      let bestChoiceId = null;
      let bestWeight = -1;
      for (const [choiceId, totalWeight] of weights.entries()) {
        if (totalWeight > bestWeight) {
          bestWeight = totalWeight;
          bestChoiceId = choiceId;
        }
      }

      // 3.3 Allocate seat
      if (bestChoiceId !== null) {
        const winner = results.find((r) => r.id === bestChoiceId);
        winner.seatCount += 1;
        debugLines.push(
          `  ==> Winner for seat #${seatNumber}: "${winner.text}" (ID=${winner.id}) with ${bestWeight.toFixed(3)} votes`,
        );

        // Increase 'winner count' for each ballot that approved the winner
        ballots.forEach((approvedChoices, bIndex) => {
          if (approvedChoices.includes(bestChoiceId)) {
            ballotWinnerCounts[bIndex] += 1;
          }
        });
      } else {
        debugLines.push(
          `  No candidates can win seat #${seatNumber} - stopping early.`,
        );
        break;
      }
    }

    return { results, debugLines };
  }

  class SPAVCache {
    constructor(maxSize = 100) {
      this.cache = new Map();
      this.maxSize = maxSize;
    }

    get(seats) {
      return this.cache.get(seats);
    }

    set(seats, value) {
      if (this.cache.size >= this.maxSize) {
        // Remove oldest entry
        const firstKey = this.cache.keys().next().value;
        this.cache.delete(firstKey);
      }
      this.cache.set(seats, value);
    }
  }

  const spavCache = new SPAVCache(100);

  // 4. Update chart + winners + debug log
  function updateAllocation() {
    const seats = parseInt(seatsSlider.value);
    seatsValue.textContent = seats;

    // 1) Check if we have a cached result
    let cached = spavCache.get(seats); // or spavCache.get(seats) if using a Map

    if (!cached) {
      // 2) Not in cache; compute
      const { results, debugLines } = spav(choices, rawBallots, seats);
      // 3) Store it
      cached = { results, debugLines };
      spavCache.set(seats, cached); // or spavCache.set(seats, cached)
    }

    // 4) Use the cached results
    const { results, debugLines } = cached;

    // Now update chart data
    spavChart.data.labels = results.map((a) => a.text);
    spavChart.data.datasets[0].data = results.map((a) => a.seatCount);
    spavChart.update();

    // Update winners list
    const winners = results.filter((a) => a.seatCount > 0);
    let html = "<h4>Winners</h4><ul>";
    winners.forEach((w) => {
      html += `<li>${w.text} (Seats: ${w.seatCount})</li>`;
    });
    html += "</ul>";
    winnersList.innerHTML = html;

    // Display debug log in the page
    allocationLogDiv.textContent = debugLines.join("\n");
  }

  // Listen to slider
  seatsSlider.addEventListener("input", updateAllocation);

  // Initial run
  updateAllocation();

  // (Optional) Build a table for debugging the raw ballots
  function buildVotesTable(ballots, allChoices) {
    let html = '<table class="table table-striped">';
    html +=
      "<thead><tr><th>Ballot #</th><th>Approved IDs</th><th>Approved Text</th></tr></thead>";
    html += "<tbody>";

    ballots.forEach((approvedChoices, index) => {
      const approvedTexts = approvedChoices.map((cid) => {
        const c = allChoices.find((ch) => ch.id === cid);
        return c ? c.choice_text : `Unknown(${cid})`;
      });
      html += `<tr>
        <td>${index + 1}</td>
        <td>${approvedChoices.join(", ")}</td>
        <td>${approvedTexts.join(", ")}</td>
      </tr>`;
    });

    html += "</tbody></table>";
    votesTableDiv.innerHTML = html;
  }
});
