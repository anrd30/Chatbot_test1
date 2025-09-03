import React, { useState } from "react";

const ChatInput = ({ onSend }) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div style={{ marginTop: "10px", display: "flex" }}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask about IIT Ropar..."
        style={{ flex: 1, padding: "10px", borderRadius: "10px", border: "1px solid #ccc" }}
      />
      <button
        onClick={handleSend}
        style={{ marginLeft: "5px", padding: "10px 20px", borderRadius: "10px", backgroundColor: "#0d6efd", color: "white", border: "none" }}
      >
        Send
      </button>
    </div>
  );
};

export default ChatInput;
