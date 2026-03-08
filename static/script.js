// Get elements from the HTML page
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// When the send button is clicked
sendBtn.addEventListener("click", sendMessage);

// Allow sending message by pressing Enter
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Function to send message
function sendMessage() {

    // Get text from input box
    let message = userInput.value.trim();

    // If message is empty, do nothing
    if (message === "") {
        return;
    }

    // Show user's message in chat
    addMessage(message, "user");

    // Clear input box
    userInput.value = "";

    // Send message to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {

        // Show bot reply
        if (data.success) {
            addMessage(data.answer, "bot");
        } else {
            addMessage("Sorry, I could not understand.", "bot");
        }

    })
    .catch(function(error) {
        addMessage("Server error. Please try again.", "bot");
    });
}

// Function to display messages in chat
function addMessage(text, sender) {

    let messageDiv = document.createElement("div");

    if (sender === "user") {
        messageDiv.className = "message user-message";
    } else {
        messageDiv.className = "message bot-message";
    }

    messageDiv.innerHTML = "<p>" + text + "</p>";

    chatBox.appendChild(messageDiv);

    // Scroll chat to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}
