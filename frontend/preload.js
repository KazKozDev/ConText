// Electron preload script
const { contextBridge, ipcRenderer } = require('electron');

// Expose limited IPC methods to renderer

contextBridge.exposeInMainWorld(
  'electron',
  {
    send: (channel, data) => {
      // Only allow whitelisted channels
      let validChannels = ['toMain'];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    receive: (channel, func) => {
      let validChannels = ['fromMain'];
      if (validChannels.includes(channel)) {
        // Strip event to avoid exposing sender
        ipcRenderer.on(channel, (event, ...args) => func(...args));
      }
    }
  }
); 