// ==UserScript==
// @name         Code Monitoring Script
// @namespace    http://your-namespace.com
// @version      1.0
// @description  Monitor code boxes and send their content to the server
// @author       Your Name
// @match        http://*/*
// @match        https://*/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

class CodeMonitor {
    constructor() {
        this.interval = 10000; // 10 seconds
        this.monitor();
    }

    monitor() {
        setInterval(() => {
            this.checkCodeBoxes();
        }, this.interval);
    }

    checkCodeBoxes() {
        const codeBoxes = document.querySelectorAll('code');
        codeBoxes.forEach(box => {
            this.sendCode(box.textContent, box.textContent.split('\n').length);
        });
    }

    sendCode(codeContent, lineCount) {
        GM_xmlhttpRequest({
            method: "POST",
            url: "http://localhost:1820/receive-code",
            data: JSON.stringify({ code: codeContent, lines: lineCount }),
            headers: {
                "Content-Type": "application/json"
            },
            onload: function(response) {
                console.log(response.responseText);
            }
        });
    }
}

// Initialize the CodeMonitor class
new CodeMonitor();
