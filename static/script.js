document.addEventListener("DOMContentLoaded", () => {
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");
    const chatWindow = document.getElementById("chat-window");
    const retrainBtn = document.getElementById("retrain-btn");
    const dropupBtn = document.getElementById("dropupBtn");
    const dropupMenu = document.getElementById("dropup-menu");
    function addMessage(sender, text) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", `${sender}-message`);
        messageElement.innerHTML = text.replace(/\n/g, '<br>'); 
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight; 
    }

    function showTypingIndicator() {
        const typingIndicator = document.createElement("div");
        typingIndicator.classList.add("chat-message", "bot-message");
        typingIndicator.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        typingIndicator.id = "typing-indicator";
        chatWindow.appendChild(typingIndicator);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById("typing-indicator");
        if (typingIndicator) {
            chatWindow.removeChild(typingIndicator);
        }
    }

    async function handleUserMessage(messageText) {
        if (messageText === "") return;
        addMessage("user", messageText);
        messageInput.value = "";
        sendBtn.disabled = true;
        messageInput.disabled = true;
        dropupBtn.disabled = true; 
        showTypingIndicator();

        try {
            const response = await fetch("/predict", { 
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: messageText }),
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }

            const data = await response.json();
            hideTypingIndicator();
            addMessage("bot", data.answer); 

        } catch (error) {
            hideTypingIndicator();
            addMessage("bot", `Sorry, something went wrong. Error: ${error.message}. Please try again later.`);
            console.error("Error during prediction:", error);
        } finally {
            sendBtn.disabled = false;
            messageInput.disabled = false;
            dropupBtn.disabled = false; 
            messageInput.focus();
        }
    }
    sendBtn.addEventListener("click", () => handleUserMessage(messageInput.value.trim()));
    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            handleUserMessage(messageInput.value.trim());
        }
    });

    retrainBtn.addEventListener("click", async () => {
        const originalButtonContent = retrainBtn.innerHTML;
        retrainBtn.disabled = true;
        retrainBtn.classList.add('retrain-loading');
        retrainBtn.innerHTML = `<svg class="w-4 h-4 text-white spin-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004 12c0 2.21.817 4.227 2.158 5.765M18 19v-5h-.582m-15.356-2A8.001 8.001 0 0020 12c0-2.21-.817-4.227-2.158-5.765"></path></svg> <span>Reloading...</span>`;
        addMessage("bot", "Initiating model reload... This will update responses if 'train.py' has been run recently.", { source: 'system' });

        try {
            const response = await fetch("/retrain", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }

            const data = await response.json();
            addMessage("bot", data.status + " The chatbot is ready for new queries.", { source: 'system' });
        } catch (error) {
            addMessage("bot", `Failed to reload the model. Error: ${error.message}. Please check the backend console and ensure 'train.py' was run.`, { source: 'error' });
            console.error("Error during retraining:", error);
        } finally {
            retrainBtn.disabled = false;
            retrainBtn.classList.remove('retrain-loading');
            retrainBtn.innerHTML = originalButtonContent;
        }
    });

    window.toggleDropdown = function() {
        dropupMenu.classList.toggle("show");
    };

    window.onclick = function(event) {
        if (!event.target.matches('.dropup-btn') && !event.target.closest('.dropup-menu')) {
            if (dropupMenu.classList.contains('show')) {
                dropupMenu.classList.remove('show');
            }
        }
    };

    dropupMenu.addEventListener('click', (event) => {
        if (event.target.matches('[data-message]')) {
            const message = event.target.dataset.message;
            messageInput.value = message;
            handleUserMessage(message);
            toggleDropdown(); 
        }
    });

    addMessage("bot", "Hello! I am your AI Tool Guide. How can I assist you with the app today?");
    messageInput.focus();
});
