// Global variables
let state = {
    room: "",
    username: ""
};
const socket = io("https://dev-bus.vjstartup.com");
socket.on("connect", () => {
    console.log("✅ Connected:", socket.id);
});

socket.on("disconnect", () => {
    console.log("❌ Disconnected");
});

socket.on("connect_error", (err) => {
    console.error("🚨 Connection Error:", err);
});
// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Initialize event listeners
    initializeEventListeners();
    
    // Check for stored user data and prefill form
    setupUserData();
    
    // Initialize socket listeners
    initializeSocketListeners();
    
    // Show chat list when page loads
    showChatList();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Input field event listeners for enter key navigation
    const nameInput = document.getElementById("name");
    if (nameInput) {
        nameInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                document.getElementById("route").focus();
            }
        });
    }

    const routeInput = document.getElementById("route");
    if (routeInput) {
        routeInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                document.getElementById("join").click();
            }
        });
    }
    
    const messageInput = document.getElementById("message");
    if (messageInput) {
        messageInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Navigation buttons
    const homeBtn = document.getElementById("homeBtn");
    if (homeBtn) {
        homeBtn.addEventListener("click", function() {
            window.location.href = "https://dev-bus.vjstartup.com";
        });
    }
    
    const chatBtn = document.getElementById("chatBtn");
    if (chatBtn) {
        chatBtn.addEventListener("click", function() {
            window.location.href = "https://dev-bus.vjstartup.com/chat";
        });
    }
    
    // Chat buttons
    const joinBtn = document.getElementById("join");
    if (joinBtn) {
        joinBtn.addEventListener("click", joinRoom);
    }
    
    const leaveBtn = document.getElementById("leave-btn");
    if (leaveBtn) {
        leaveBtn.addEventListener("click", leaveRoom);
    }
    
    const sendBtn = document.querySelector(".send-button");
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }
    
}

/**
 * Setup user data from cookies and local storage
 */
function setupUserData() {
    // Setup name input from cookie
    const storedName = getCookieValue("user") 
        ? JSON.parse(getCookieValue("user")).family_name 
        : "";
    
    const nameInput = document.getElementById("name");
    if (nameInput) {
        if (storedName) {
            nameInput.value = storedName;
            nameInput.readOnly = true;
        } else {
            nameInput.readOnly = false;
        }
    }
    
    // Setup route input from local storage
    const roomID = localStorage.getItem("busApplicationSelectedRouteByStudent");
    const roomInput = document.getElementById("route");
    if (roomInput && roomID) {
        const routeNumber = roomID.split("Route-")[1]?.split(" ")[0]; // "S-2"
        roomInput.value = routeNumber || "";
        roomInput.readOnly = false;
    }
}

/**
 * Initialize socket event listeners
 */
function initializeSocketListeners() {
    // Listen for chat history events
    socket.on("chat_history", function(data) {
        if (data.room === state.room) {
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML = "";
            
            data.messages.forEach(msg => {
                addMessage(msg.sender, msg.message, msg.sender === state.username);
            });
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    });
    
    // Listen for chat message events
    socket.on("chat_message", function(data) {
        addMessage(data.sender, data.message, data.sender === state.username);
        
        const messagesDiv = document.getElementById("messages");
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
}

/**
 * Get cookie value by name
 * @param {string} name - Cookie name
 * @returns {string|null} - Cookie value or null if not found
 */
function getCookieValue(name) {
    const cookieString = document.cookie;
    const cookies = cookieString.split('; ');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].split('=');
        if (cookie[0] === name) {
            return decodeURIComponent(cookie[1]);
        }
    }
    return null;
}

/**
 * Handle joining a chat room
 */
function joinRoom() {
    state.username = document.getElementById("name").value.trim();
    state.room = document.getElementById("route").value.trim();
    
    if (!state.username || !state.room) {
        alert("Please enter your name and Room ID.");
        return;
    }

    socket.emit("join_room", { 
        room: state.room, 
        sender: state.username 
    });
    
    // Update UI
    document.getElementById("room-name").innerText = state.room;
    document.getElementById("initial-header").style.display = "none";
    document.getElementById("chat-header").style.display = "block";
    document.getElementById("chat").style.display = "block";
    document.getElementById("join-section").style.display = "none";
    document.getElementById("leave-btn").style.display = "block";
}

/**
 * Handle leaving a chat room
 */
function leaveRoom() {
    socket.emit("leave_room", { 
        room: state.room, 
        sender: state.username 
    });
    
    location.reload();
}

/**
 * Send a message to the current room
 */
function sendMessage() {
    const messageInput = document.getElementById("message");
    const message = messageInput.value.trim();
    
    if (message) {
        socket.emit("send_message", { 
            room: state.room, 
            sender: state.username, 
            message 
        });
        
        messageInput.value = "";
    }
}

/**
 * Send message on Enter key press
 * @param {Event} event - Keydown event
 */
function sendOnEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Add a message to the chat display
 * @param {string} sender - Message sender
 * @param {string} message - Message content
 * @param {boolean} isCurrentUser - Whether the sender is the current user
 */
function addMessage(sender, message, isCurrentUser) {
    const messagesDiv = document.getElementById("messages");
    const messageElement = document.createElement("div");
    
    messageElement.classList.add("message");
    messageElement.classList.add(isCurrentUser ? "user-message" : "received-message");
    
    // Get current time for timestamp
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const timestamp = `${hours}:${minutes}`;
    
    messageElement.innerHTML = `
        <small class="username">${sender}</small>
        <div>${message}</div>
        <div class="timestamp">${timestamp}</div>
    `;
    
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * Focus next input field
 * @param {Event} event - Keydown event
 * @param {string} nextId - ID of the next element to focus
 */
function focusNext(event, nextId) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById(nextId).focus();
    }
}

/**
 * Set active navigation item
 * @param {HTMLElement} element - Element to set as active
 */
function setActive(element) {
    document.querySelectorAll(".menu-item").forEach(function(item) {
        item.classList.remove("active");
    });
    
    element.classList.add("active");
}

/**
 * Show the chat list section
 */
function showChatList() {
    // Hide other sections
    document.getElementById("initial-header").style.display = "block";
    document.getElementById("chat-header").style.display = "none";
    document.getElementById("chat").style.display = "none";
    document.getElementById("join-section").style.display = "none";
    document.getElementById("new-chat-section").style.display = "none";
    
    // Show chat list section
    document.getElementById("chat-list-section").style.display = "block";
    
    // Load chat list
    loadChatList();
}

/**
 * Load and display the chat list
 */
function loadChatList() {
    const chatList = document.getElementById("chat-list");
    chatList.innerHTML = "<p>Loading Rooms...</p>";
    
    // Get chat rooms from server
    socket.emit("get_all_rooms", {}, function(rooms) {
        chatList.innerHTML = "";
        
        if (rooms && rooms.length > 0) {
            rooms.forEach(roomId => {
                const chatItem = document.createElement("div");
                chatItem.className = "chat-list-item";
                chatItem.innerHTML = `
                    <div class="chat-list-item-avatar">
                        <i class="fas fa-bus"></i>
                    </div>
                    <div class="chat-list-item-details">
                        <h4 class="chat-list-item-name">Chat ${roomId}</h4>
                        <p class="chat-list-item-last-message" style="display:inline; ">Click to join this chat</p>
                    </div>
                `;
                
                chatItem.addEventListener("click", function() {
                    selectChat(roomId);
                });
                
                chatList.appendChild(chatItem);
            });
        } else {
            chatList.innerHTML = "<p>No chat rooms available. Create a new chat to get started.</p>";
        }
        
        // Add event listener for new chat button
        document.getElementById("new-chat-btn").addEventListener("click", function() {
            showNewChatForm();
        });
    });
}

/**
 * Show the new chat form
 */
function showNewChatForm() {
    // Hide other sections
    document.getElementById("chat-list-section").style.display = "none";
    
    // Show new chat section
    document.getElementById("new-chat-section").style.display = "block";
    
    // Add event listeners for new chat form
    document.getElementById("create-chat").addEventListener("click", createNewChat);
    document.getElementById("cancel-new-chat").addEventListener("click", showChatList);
}

/**
 * Create a new chat
 */
function createNewChat() {
    const chatName = document.getElementById("new-chat-name").value.trim();
    if (chatName) {
        // Get username from cookie or prompt
        const storedName = getCookieValue("user") 
            ? JSON.parse(getCookieValue("user")).family_name 
            : "";
        
        let username = "";
        if (storedName) {
            username = storedName;
        } else {
            username = prompt("Enter your name:");
            if (!username) {
                alert("Name is required to create a chat room.");
                return;
            }
        }
        
        // Create the new room on the server
        socket.emit("create_room", { 
            room: chatName, 
            sender: username 
        }, function(response) {
            if (response && response.status === "success") {
                // Set state and join the room
                state.username = username;
                state.room = chatName;
                
                // Join the room
                socket.emit("join_room", { 
                    room: state.room, 
                    sender: state.username 
                });
                
                // Update UI
                document.getElementById("room-name").innerText = state.room;
                document.getElementById("initial-header").style.display = "none";
                document.getElementById("chat-header").style.display = "block";
                document.getElementById("chat").style.display = "block";
                document.getElementById("new-chat-section").style.display = "none";
                document.getElementById("leave-btn").style.display = "block";
            } else {
                alert("Failed to create chat room. Please try again.");
            }
        });
        
        document.getElementById("new-chat-name").value = "";
    } else {
        alert("Please enter a chat name");
    }
}

/**
 * Select a chat and join directly
 */
function selectChat(chatId) {
    // Get username from cookie or prompt
    const storedName = getCookieValue("user") 
        ? JSON.parse(getCookieValue("user")).family_name 
        : "";
    
    if (storedName) {
        state.username = storedName;
        document.getElementById("name").value = storedName;
    } else {
        // Show join section to get username
        document.getElementById("chat-list-section").style.display = "none";
        document.getElementById("join-section").style.display = "flex";
        document.getElementById("route").value = chatId;
        document.getElementById("name").focus();
        return;
    }
    
    state.room = chatId;
    
    socket.emit("join_room", { 
        room: state.room, 
        sender: state.username 
    });
    
    // Update UI
    document.getElementById("room-name").innerText = state.room;
    document.getElementById("initial-header").style.display = "none";
    document.getElementById("chat-header").style.display = "block";
    document.getElementById("chat").style.display = "block";
    document.getElementById("chat-list-section").style.display = "none";
    document.getElementById("join-section").style.display = "none";
    document.getElementById("leave-btn").style.display = "block";
}
