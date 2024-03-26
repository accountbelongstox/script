const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  execTheFile: (file_name) => {
    ipcRenderer.send('ondragstart', file_name)
  }
})