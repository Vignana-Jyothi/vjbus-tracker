// ======================================
// BUS CHAT
// Part 1
// ======================================

// -------------------------
// Global Variables
// -------------------------
const socket = io("wss://dev-bus.vjstartup.com", {
    transports: ["websocket"]
});
let state = {
    username: "",
    room: ""
};

// -------------------------
// Socket Status
// -------------------------

socket.on("connect", () => {
    console.log("Connected :", socket.id);

    if (state.room && state.username) {
        socket.emit("join_room", {
            room: state.room,
            sender: state.username
        });
    }
});

socket.on("disconnect", () => {
    console.log("Disconnected");
});

socket.on("connect_error", (err) => {
    console.error(err);
});

// -------------------------
// Page Loaded
// -------------------------

document.addEventListener("DOMContentLoaded", () => {

    loadStoredUser();

    initializeSocketEvents();

});

// -------------------------
// Load Name & Route
// -------------------------

function loadStoredUser() {

    const cookie = getCookieValue("user");

    if (cookie) {

        try {

            const user = JSON.parse(cookie);

            document.getElementById("name").value =
                user.family_name || "";

            document.getElementById("name").readOnly = true;

        } catch (e) {}

    }

    const selectedRoute =
        localStorage.getItem("busApplicationSelectedRouteByStudent");

    if (selectedRoute) {

        const route =
            selectedRoute.split("Route-")[1]?.split(" ")[0];

        document.getElementById("route").value = route || "";

    }

}

// -------------------------
// Join Room
// -------------------------

function joinRoom() {

    const username =
        document.getElementById("name").value.trim();

    const room =
        document.getElementById("route").value.trim();

    if (username === "" || room === "") {

        alert("Please enter Name and Bus Number");

        return;

    }

    state.username = username;
    state.room = room;
    console.log("Joined Room:", state.room);
console.log("Username:", state.username);

    socket.emit("join_room", {

        room: room,

        sender: username

    });

    document.getElementById("room-name").innerText = room;

    // Hide Join Page

    document.getElementById("join-section").style.display = "none";

    // Show Chat Page

    document.getElementById("chat-page").style.display = "flex";

    // Clear old messages

    document.getElementById("messages").innerHTML = "";

    document.getElementById("message").focus();

}

// -------------------------
// Leave Room
// -------------------------

function leaveRoom() {

    socket.emit("leave_room", {

        room: state.room,

        sender: state.username

    });

    state.room = "";

    document.getElementById("chat-page").style.display = "none";

    document.getElementById("join-section").style.display = "flex";

    document.getElementById("messages").innerHTML = "";

    document.getElementById("message").value = "";

}

// -------------------------
// Enter Key
// -------------------------

function focusNext(event, nextId) {

    if (event.key === "Enter") {

        event.preventDefault();

        document.getElementById(nextId).focus();

    }

}

function sendOnEnter(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

}
// ======================================
// PART 2
// Socket Events
// ======================================

function initializeSocketEvents() {

    // Previous Messages

    socket.on("chat_history", function(data) {

        if (data.room !== state.room) return;

        const messagesDiv = document.getElementById("messages");

        messagesDiv.innerHTML = "";

        data.messages.forEach(function(msg){

            addMessage(
                msg.sender,
                msg.message,
                msg.sender === state.username,
                msg.timestamp
            );

        });

    });

    // New Incoming Message

    socket.on("chat_message", function(data){

        if(data.room !== state.room) return;

        addMessage(
            data.sender,
            data.message,
            data.sender === state.username,
            data.timestamp
        );

    });

}

// ======================================
// Send Message
// ======================================

function sendMessage(){

    const input = document.getElementById("message");

    const text = input.value.trim();

    if(text === "") return;
      console.log("Sending...");
    console.log("Room:", state.room);
    console.log("Sender:", state.username);
    console.log("Message:", text);
    console.log("Connected:", socket.connected);


    socket.emit("send_message",{

        room: state.room,

        sender: state.username,

        message: text,

        timestamp: new Date().toISOString()

    });

    input.value="";

    input.focus();

}

// ======================================
// Add Message
// ======================================

function addMessage(sender,message,isMine,timestamp){

    const messages = document.getElementById("messages");

    const div = document.createElement("div");

    div.className = "message";

    if(isMine){

        div.classList.add("user-message");

    }else{

        div.classList.add("received-message");

    }

    let time = "";

    if(timestamp){

        const d = new Date(timestamp);

        time = d.toLocaleTimeString([],{

            hour:"2-digit",

            minute:"2-digit"

        });

    }

    div.innerHTML = `

        <span class="username">${sender}</span>

        <div class="message-text">

            ${message}

        </div>

        <div class="timestamp">

            ${time}

        </div>

    `;

    messages.appendChild(div);

    messages.scrollTop = messages.scrollHeight;

}
// ======================================
// PART 3
// Helpers
// ======================================

// Get Cookie

function getCookieValue(name) {

    const cookies = document.cookie.split("; ");

    for (let i = 0; i < cookies.length; i++) {

        const cookie = cookies[i].split("=");

        if (cookie[0] === name) {

            return decodeURIComponent(cookie[1]);

        }

    }

    return null;

}

// ======================================
// Load User
// ======================================

window.onload = function () {

    const cookie = getCookieValue("user");

    if (cookie) {

        try {

            const user = JSON.parse(cookie);

            if (user.family_name) {

                document.getElementById("name").value =
                    user.family_name;

                document.getElementById("name").readOnly = true;

            }

        } catch (e) {

            console.log(e);

        }

    }

    const selectedRoute =
        localStorage.getItem("busApplicationSelectedRouteByStudent");

    if (selectedRoute) {

        const route =
            selectedRoute.split("Route-")[1]?.split(" ")[0];

        if (route) {

            document.getElementById("route").value = route;

        }

    }

};

// ======================================
// Navigation
// ======================================

const homeButton = document.querySelector(".nav-item");

if (homeButton) {

    homeButton.addEventListener("click", function () {

        window.location.href = "/";

    });

}

// ======================================
// Auto Scroll
// ======================================

function scrollToBottom() {

    const messages = document.getElementById("messages");

    messages.scrollTop = messages.scrollHeight;

}

// ======================================
// Clear Chat Screen
// ======================================

function clearChat() {

    document.getElementById("messages").innerHTML = "";

    document.getElementById("message").value = "";

}

// ======================================
// Utility
// ======================================

function formatTime(timestamp) {

    if (!timestamp) return "";

    return new Date(timestamp).toLocaleTimeString([], {

        hour: "2-digit",

        minute: "2-digit"

    });

}