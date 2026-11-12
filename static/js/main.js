/**
 * AI Code Review - Core Frontend JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Dynamic Language Detection for Textarea Input
  const codeEditor = document.getElementById("codeEditor");
  const langBadge = document.getElementById("detectedLangBadge");

  if (codeEditor && langBadge) {
    let debounceTimer = null;
    codeEditor.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const text = codeEditor.value.trim();
        if (text.length > 15) {
          fetch("/api/detect-language", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: text }),
          })
            .then((res) => res.json())
            .then((data) => {
              if (data.success && data.language) {
                langBadge.textContent = "Detected: " + data.language.toUpperCase();
                langBadge.className = "badge badge-orange px-3 py-2 fs-6";
              }
            })
            .catch(() => {});
        } else {
          langBadge.textContent = "Language: Auto-Detect";
          langBadge.className = "badge badge-orange px-3 py-2 fs-6";
        }
      }, 500);
    });
  }

  // 2. File Upload Label Updating
  const fileInput = document.getElementById("codeFileInput");
  const fileNameDisplay = document.getElementById("fileNameDisplay");
  if (fileInput && fileNameDisplay) {
    fileInput.addEventListener("change", function () {
      if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = fileInput.files[0].name;
      }
    });
  }

  // 3. Filter Findings Table
  const filterButtons = document.querySelectorAll("[data-filter-severity]");
  filterButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const targetSev = this.getAttribute("data-filter-severity");
      filterButtons.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");

      const findingRows = document.querySelectorAll(".finding-card-row");
      findingRows.forEach((row) => {
        const rowSev = row.getAttribute("data-severity");
        if (targetSev === "ALL" || rowSev === targetSev) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  });

  // 4. Copy Code Snippet Helper
  window.copySnippet = function (elementId) {
    const el = document.getElementById(elementId);
    if (el) {
      navigator.clipboard.writeText(el.innerText).then(() => {
        alert("Code copied to clipboard!");
      });
    }
  };
});
