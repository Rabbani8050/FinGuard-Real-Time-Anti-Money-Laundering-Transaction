"use strict";
const WS_URL = `ws://${location.host}/ws/live`;
let socket;

function connectWS(onMessage) {
  socket = new WebSocket(WS_URL);
  socket.onmessage = (e) => onMessage(JSON.parse(e.data));
  socket.onclose   = () => setTimeout(() => connectWS(onMessage), 2000);
  socket.onerror   = () => socket.close();
  // Send keep-alive ping every 20s
  setInterval(() => { if (socket.readyState === 1) socket.send("ping"); }, 20000);
}
