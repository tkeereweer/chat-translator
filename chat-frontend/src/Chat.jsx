import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000", {
    transports: ["websocket"],
});

const Chat = ({ user, accessToken }) => {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const [recipientId, setRecipientId] = useState("");

    // Setup WebSocket connection
    useEffect(() => {
        socket.on("new_message", (data) => {
            setMessages((prevMessages) => [...prevMessages, data]);
        });

        return () => {
            socket.off("new_message");
        };
    }, []);

    const sendMessage = async () => {
        if (message.trim() && recipientId) {
            socket.emit("message", {
                recipient_id: recipientId,
                message_text: message,
                token: accessToken, // Pass the JWT for authentication
            });
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: user.username, message },
            ]);
            setMessage("");
        }
    };

    return (
        <div>
            <h2>Welcome, {user.username}!</h2>
            <h3>Chat with translation</h3>
            <input
                type="text"
                placeholder="Recipient ID"
                value={recipientId}
                onChange={(e) => setRecipientId(e.target.value)}
            />
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <strong>{msg.sender}:</strong> {msg.message}
                    </div>
                ))}
            </div>
            <input
                type="text"
                placeholder="Type your message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default Chat;
