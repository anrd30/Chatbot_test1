import React, { useState } from "react";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (userMessage) => {
    const newMessages = [...messages, { sender: "user", text: userMessage }];
    setMessages(newMessages);

    try {
      // Use relative path for Vercel deployment
      const response = await axios.post("/api/chat", {
        question: userMessage
      });
      setMessages([...newMessages, { sender: "bot", text: response.data.answer }]);
    } catch (error) {
      setMessages([...newMessages, { sender: "bot", text: "Error connecting to backend" }]);
      console.error(error);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "20px auto", fontFamily: "Arial" }}>
      <h2 style={{ textAlign: "center" }}>IIT Ropar Chatbot</h2>
      <ChatWindow messages={messages} />
      <ChatInput onSend={sendMessage} />
    </div>
  );
}

export default App;
