let currentLanguage = "en";  // Default language

function createMessage(text, isUser = false) {
    const time = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    return `
        <div class="message ${isUser ? "user" : "bot"}">
            <input type="checkbox" ${isUser ? "" : "checked"}>
            <div class="content">
                <p>${text}</p>
                <span class="time">${time}</span>
            </div>
        </div>
    `;
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text) return;

    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += createMessage(text, true);
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
    })
    .then(res => res.json())
    .then(data => {
        chatBox.innerHTML += createMessage(data.response);
        currentLanguage = data.language;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(console.error);
}

function startVoiceRecognition() {
    if (!("webkitSpeechRecognition" in window)) {
        alert("Voice input not supported in your browser!");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = currentLanguage;

    recognition.onresult = function (e) {
        const transcript = e.results[0][0].transcript;
        document.getElementById("userInput").value = transcript;
        sendMessage();
    };

    recognition.start();
}

function readAloud() {
    const lastResponse = document.querySelector("#chatBox .message.bot:last-child p")?.innerText;
    if (!lastResponse) return;

    fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: lastResponse,
            language: currentLanguage
        })
    })
    .then(res => res.json())
    .then(data => {
        const audio = new Audio(data.audio);
        audio.play();
    });
}

document.getElementById("userInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});
