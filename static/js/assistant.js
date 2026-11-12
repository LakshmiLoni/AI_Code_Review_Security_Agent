/**
 * AI Code Review - Conversational Assistant Chat Script
 */

document.addEventListener("DOMContentLoaded", function () {
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("chatSendBtn");
  const clearBtn = document.getElementById("clearChatBtn");
  const activeReviewId = document.getElementById("activeReviewId")?.value || "";

  if (!chatInput || !sendBtn) return;

  function scrollToBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function appendMessage(role, text, citations, model) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;

    if (role === "user") {
      bubble.textContent = text;
    } else {
      // Basic formatting for Markdown headers, bold, and code blocks
      let formatted = text
        .replace(/\n\n/g, "<br><br>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/### ([^\n<]+)/g, "<h5 class='fw-bold mt-2'>$1</h5>");

      bubble.innerHTML = formatted;

      if (citations && citations.length > 0) {
        const citeBox = document.createElement("div");
        citeBox.className = "chat-citation-box mt-3";
        let citeHtml = "<strong><i class='bi bi-book'></i> Grounded Knowledge Base Citations:</strong><ul class='mb-0 ps-3 mt-1'>";
        citations.forEach((c) => {
          citeHtml += `<li><code>${c.source_file}</code> § ${c.section} (Match: ${(c.relevance_score * 100).toFixed(0)}%)</li>`;
        });
        citeHtml += "</ul>";
        citeBox.innerHTML = citeHtml;
        bubble.appendChild(citeBox);
      }

      if (model) {
        const modelTag = document.createElement("div");
        modelTag.className = "text-muted small mt-2 text-end fst-italic";
        modelTag.textContent = `Generated via: ${model}`;
        bubble.appendChild(modelTag);
      }
    }

    chatMessages.appendChild(bubble);
    scrollToBottom();
  }

  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    appendMessage("user", message);
    chatInput.value = "";
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Typing placeholder
    const typingBubble = document.createElement("div");
    typingBubble.className = "chat-bubble assistant fst-italic text-muted";
    typingBubble.id = "typingIndicator";
    typingBubble.textContent = "Analyzing knowledge base and formulating response...";
    chatMessages.appendChild(typingBubble);
    scrollToBottom();

    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: message,
        review_id: activeReviewId,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        const indicator = document.getElementById("typingIndicator");
        if (indicator) indicator.remove();

        if (data.success) {
          appendMessage("assistant", data.answer, data.citations, data.model_used);
        } else {
          appendMessage("assistant", "Error: " + (data.error || "Could not complete request."));
        }
      })
      .catch((err) => {
        const indicator = document.getElementById("typingIndicator");
        if (indicator) indicator.remove();
        appendMessage("assistant", "Network or server connection error: " + err.message);
      })
      .finally(() => {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
      });
  }

  sendBtn.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Suggestion Pills
  const promptPills = document.querySelectorAll(".prompt-suggestion");
  promptPills.forEach((pill) => {
    pill.addEventListener("click", function () {
      chatInput.value = this.textContent.trim();
      sendMessage();
    });
  });

  // Clear Chat Button
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      if (confirm("Clear all conversation messages?")) {
        fetch("/api/chat/clear", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ review_id: activeReviewId }),
        })
          .then(() => {
            chatMessages.innerHTML = `
              <div class="chat-bubble assistant">
                Hello! I am your AI Code Review & Security Assistant. Ask me anything about
                OWASP vulnerabilities, code quality improvements, or the findings from your review.
              </div>
            `;
          });
      }
    });
  }
});
