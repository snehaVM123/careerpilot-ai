// Wait for the DOM to fully load before setting up event listeners
document.addEventListener("DOMContentLoaded", () => {
    const inputElement = document.getElementById("message");

    // Allow user to send a message by pressing the "Enter" key
    inputElement.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});

async function sendMessage() {
    const inputElement = document.getElementById("message");
    const chatBox = document.getElementById("chatBox");
    const userMessage = inputElement.value.trim();

    // Prevent sending empty messages
    if (!userMessage) return;

    // 1. Display the user's message in the chat box
    chatBox.innerHTML += `
        <div class="message user-msg" style="margin-bottom: 12px; text-align: right;">
            <span style="background: #e1ffc7; padding: 8px 12px; display: inline-block; border-radius: 8px; max-width: 75%; text-align: left;">
                <strong>You:</strong> ${escapeHTML(userMessage)}
            </span>
        </div>
    `;

    // Clear input field and focus back on it
    inputElement.value = "";
    inputElement.focus();

    // 2. Create and display a temporary loading state for the AI
    const loadingId = "loading-" + Date.now();
    chatBox.innerHTML += `
        <div id="${loadingId}" class="message ai-msg" style="margin-bottom: 12px; text-align: left;">
            <span style="background: #f1f0f0; padding: 8px 12px; display: inline-block; border-radius: 8px; max-width: 75%; color: #666; font-style: italic;">
                CareerPilot AI is typing...
            </span>
        </div>
    `;
    
    // Auto-scroll down to show the loader
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 3. Send the message payload to the FastAPI backend
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userMessage })
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        // Remove the loading text placeholder
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();

        // 4. Display the real AI reply
        chatBox.innerHTML += `
            <div class="message ai-msg" style="margin-bottom: 12px; text-align: left;">
                <span style="background: #f1f0f0; padding: 8px 12px; display: inline-block; border-radius: 8px; max-width: 75%;">
                    <strong>AI:</strong> ${formatAIResponse(data.reply)}
                </span>
            </div>
        `;

    } catch (error) {
        console.error("Error:", error);
        
        // Remove the loading text placeholder if an error happens
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();

        // Display an error message to the user
        chatBox.innerHTML += `
            <div style="margin-bottom: 12px; text-align: left;">
                <span style="background: #ffebee; color: #c62828; padding: 8px 12px; display: inline-block; border-radius: 8px;">
                    <strong>Error:</strong> Failed to get a response. Please check your API key setup.
                </span>
            </div>
        `;
    }

    // Always scroll to the bottom so the latest messages are visible
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Helper function to prevent malicious XSS injections
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// Helper function to handle basic markdown/line breaks sent by the AI
function formatAIResponse(text) {
    // Converts newlines (\n) into actual web line breaks (<br>)
    // Converts basic markdown **bold** text into HTML <strong> tags
    return text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}