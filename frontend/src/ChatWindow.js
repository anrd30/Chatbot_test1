import React, { useRef, useEffect } from "react";

const ChatWindow = ({ messages }) => {
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", height: "400px", overflowY: "scroll", borderRadius: "10px" }}>
      {messages.map((msg, index) => (
        <div key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left", margin: "5px 0" }}>
          <span style={{
            display: "inline-block",
            padding: "8px 12px",
            borderRadius: "15px",
            backgroundColor: msg.sender === "user" ? "#d1e7dd" : "#f8d7da"
          }}>
            {msg.text}
          </span>
        </div>
      ))}
      <div ref={bottomRef}></div>
    </div>
  );
};

export default ChatWindow;
