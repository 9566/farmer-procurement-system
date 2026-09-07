/*
============================================================
AGRIBOT CHATBOT FRONTEND
============================================================
*/

const CHATBOT_API_URL = "https://farmer-procurement-system.onrender.com/chatbot";


// ============================================================
// ELEMENTS
// ============================================================

const botButton = document.getElementById("agriBotButton");
const chatWindow = document.getElementById("agriChatWindow");
const minimizeButton = document.getElementById("agriBotMinimize");
const chatMessages = document.getElementById("agriChatMessages");
const chatInput = document.getElementById("agriChatInput");
const sendButton = document.getElementById("agriChatSend");
const typingIndicator = document.getElementById("agriTyping");


// ============================================================
// CHECK ELEMENTS
// ============================================================

if (!botButton) {
    console.error("AgriBot: agriBotButton not found");
}

if (!chatWindow) {
    console.error("AgriBot: agriChatWindow not found");
}

if (!chatInput) {
    console.error("AgriBot: agriChatInput not found");
}


// ============================================================
// OPEN CHAT
// ============================================================

function openChat() {

    if (!chatWindow || !botButton) {
        return;
    }

    chatWindow.classList.add("active");

    botButton.style.display = "none";

    setTimeout(function () {

        if (chatInput) {
            chatInput.focus();
        }

    }, 200);
}


// ============================================================
// MINIMIZE CHAT
// ============================================================

function minimizeChat() {

    if (!chatWindow || !botButton) {
        return;
    }

    chatWindow.classList.remove("active");

    botButton.style.display = "flex";
}


// ============================================================
// EVENTS
// ============================================================

if (botButton) {

    botButton.addEventListener(
        "click",
        openChat
    );

}


if (minimizeButton) {

    minimizeButton.addEventListener(
        "click",
        minimizeChat
    );

}


if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendMessage
    );

}


if (chatInput) {

    chatInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


// ============================================================
// ADD USER MESSAGE
// ============================================================

function addUserMessage(message) {

    const wrapper = document.createElement("div");

    wrapper.className =
        "agri-message user-message";


    const content = document.createElement("div");

    content.className =
        "agri-message-content";


    content.textContent = message;


    wrapper.appendChild(content);


    chatMessages.appendChild(wrapper);


    scrollToBottom();
}


// ============================================================
// ADD BOT MESSAGE
// ============================================================

function addBotMessage(answer, tag) {

    const wrapper = document.createElement("div");

    wrapper.className =
        "agri-message bot-message";


    const content = document.createElement("div");

    content.className =
        "agri-message-content";


    content.innerHTML =
        formatBotText(answer);


    wrapper.appendChild(content);


    // --------------------------------------------------------
    // TAG
    // --------------------------------------------------------

    const tagElement = document.createElement("span");

    tagElement.className = "agri-tag";


    if (tag === "FAQ QUESTION") {

        tagElement.classList.add("faq-tag");

    } else {

        tagElement.classList.add("general-tag");

    }


    tagElement.textContent =
        tag || "GENERAL QUESTION";


    wrapper.appendChild(tagElement);


    chatMessages.appendChild(wrapper);


    scrollToBottom();
}


// ============================================================
// FORMAT BOT RESPONSE
// ============================================================

function formatBotText(text) {

    if (!text) {
        return "";
    }


    let formatted =
        escapeHtml(String(text));


    // Convert **text** to bold

    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );


    // Convert line breaks

    formatted = formatted.replace(
        /\n/g,
        "<br>"
    );


    return formatted;
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(text) {

    const div =
        document.createElement("div");


    div.textContent = text;


    return div.innerHTML;
}


// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {

    if (!typingIndicator) {
        return;
    }


    typingIndicator.classList.add("active");


    scrollToBottom();
}


function hideTyping() {

    if (!typingIndicator) {
        return;
    }


    typingIndicator.classList.remove("active");
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    if (!chatInput) {
        return;
    }


    const question =
        chatInput.value.trim();


    if (!question) {
        return;
    }


    // Show user question

    addUserMessage(question);


    // Clear input

    chatInput.value = "";


    // Disable controls

    if (sendButton) {
        sendButton.disabled = true;
    }


    chatInput.disabled = true;


    // Show typing

    showTyping();


    try {

        const response =
            await fetch(
                CHATBOT_API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            question: question
                        })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server returned HTTP " +
                response.status
            );

        }


        const data =
            await response.json();


        hideTyping();


        addBotMessage(
            data.answer,
            data.tag
        );


    } catch (error) {

        console.error(
            "AgriBot error:",
            error
        );


        hideTyping();


        addBotMessage(
            "Sorry, I am unable to connect to the chatbot server right now. Please make sure the FastAPI backend is running.",
            "GENERAL QUESTION"
        );

    }


    // Enable controls again

    if (sendButton) {
        sendButton.disabled = false;
    }


    chatInput.disabled = false;


    chatInput.focus();
}


// ============================================================
// AUTO SCROLL
// ============================================================

function scrollToBottom() {

    if (!chatMessages) {
        return;
    }


    setTimeout(
        function () {

            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        },
        50
    );
}