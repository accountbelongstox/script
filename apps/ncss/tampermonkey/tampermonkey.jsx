// ==UserScript==
// @name         抖音自动化(短视频爬取)
// @namespace    http://tampermonkey.net/
// @version      3.0.3
// @description  抖音自动化
// @author       aaaa
// @match        https://www.douyin.com/video/*
// @match        http://www.douyin.com/video/*
// @grant        GM_download
// @grant        GM_addStyle
// @grant        GM_info
// @connect      *
// @icon         https://lf1-cdn-tos.bytegoofy.com/goofy/ies/douyin_web/public/favicon.ico
// @license      MIT License
// @run-at       document-start
// ==/UserScript==

(window.onload = function () {
class AutoClicker {
    constructor() {
        this.isRunning = false;
        this.interval = 5000;
        this.lastClickTime = 0;
        this.apiUrl = 'http://localhost:5000/video';
        this.intervalId = null;
        this.count = 0;
        this.secondsRemaining = 0;
    }
     retryFindElement(selector, callback, maxAttempts = 1000) {
        let attempts = 0;
        const tryFindElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                callback(element);
            } else {
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(tryFindElement, 1000);
                } else {
                    alert(`Element not found after ${maxAttempts} attempts.`);
                }
            }
        };
        tryFindElement();
    }
    clickAdamalibaElement() {
        this.retryFindElement('#adamaliba', (element) => {
            element.click();
        });
    }
    getTitleText(callback) {
        let titleText = null;
        this.retryFindElement('.hE8dATZQ', (element) => {
            titleText = element.innerText || element.textContent;
            if(callback)callback(titleText)
        });
        return titleText;
    }
    start() {
        console.log(`start`)
        this.intervalId = setTimeout(() => {
            this.tick()
        }, 3000)
    }
    stop() {
        this.isRunning = false;
        clearInterval(this.intervalId);
        this.intervalId = null; // Reset intervalId
    }
    tick() {
        console.log(`tick`);
        setTimeout(() => {
            this.getTitleText((title) => {
                console.log(`title`, title);
                this.clickAdamalibaElement()
                this.sendPost({ title }, (responseData) => {
                    console.log('POST request successful:', responseData);
                    this.handleAutoClick(() => {
                        this.tick();
                    });
                });
            });
        }, this.interval);
    }
    handleAutoClick(callback) {
        console.log(`handleAutoClick`)
        this.retryFindElement('[data-e2e="video-switch-next-arrow"]', (element) => {
            const currentTime = new Date().getTime();
            const lastClickTime = this.getLastClickTime('videoSwitchNextArrow');

            if (currentTime - lastClickTime < this.interval) {
                return;
            }
            this.saveLastClickTime('videoSwitchNextArrow', currentTime);
            element.click();
            setTimeout(() => {
                if (callback && typeof callback === 'function') {
                    callback();
                }
            }, this.interval);
        });
    }
    saveLastClickTime(name, time) {
        const clickTimeData = JSON.stringify({ [name]: time });
        localStorage.setItem('lastClickTime', clickTimeData);
    }
    getLastClickTime(name) {
        const clickTimeData = localStorage.getItem('lastClickTime');
        const parsedData = clickTimeData ? JSON.parse(clickTimeData) : {};
        return parsedData[name] || 0;
    }
    sendGet(data, callback) {
        console.log(`sendGet`);
        const queryString = Object.keys(data).map(key => `${key}=${data[key]}`).join('&');
        const urlWithParams = `${this.apiUrl}?${queryString}`;
        fetch(urlWithParams, {
            method: 'GET',
        })
            .then(responseData => {
            console.log('GET request successful:', responseData);
            if (callback && typeof callback === 'function') {
                callback(responseData);
            }
        })
            .catch(error => {
            console.error('Error sending GET request:', error);
            if (callback && typeof callback === 'function') {
                callback(null, error);
            }
        });
    }
    sendPost(data, callback) {
        console.log(`sendPost`);
        fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(responseData => {
            console.log('POST request successful:', responseData);
            if (callback && typeof callback === 'function') {
                callback(responseData);
            }
        })
            .catch(error => {
            console.error('Error sending POST request:', error);
            if (callback && typeof callback === 'function') {
                callback(null, error);
            }
        });
    }

    insertControlDiv() {
        const controlDiv = document.createElement('div');
        controlDiv.style.position = 'fixed';
        controlDiv.style.bottom = '50px';
        controlDiv.style.right = '0';
        controlDiv.style.width = '300px';
        controlDiv.style.height = '50px';
        controlDiv.style.backgroundColor = '#ccc';
        controlDiv.style.display = 'flex';
        controlDiv.style.alignItems = 'center';
        controlDiv.style.justifyContent = 'space-around';
        const startButton = document.createElement('button');
        startButton.textContent = 'Start';
        startButton.addEventListener('click', () => this.handleStartClick(startButton));
        const infoDisplay = document.createElement('div');
        infoDisplay.style.flexGrow = 1; // Allow it to take the remaining space
        infoDisplay.style.textAlign = 'center';
        const countSpan = document.createElement('span');
        countSpan.id = 'countSpan';
        const countdownSpan = document.createElement('span');
        countdownSpan.id = 'countdownSpan';
        const stopButton = document.createElement('button');
        stopButton.textContent = 'Stop';
        stopButton.addEventListener('click', () => this.handleStopClick(stopButton));
        infoDisplay.appendChild(countSpan);
        infoDisplay.appendChild(countdownSpan);
        controlDiv.appendChild(startButton);
        controlDiv.appendChild(infoDisplay);
        controlDiv.appendChild(stopButton);
        document.body.appendChild(controlDiv);
    }

    handleStartClick(button) {
        if (!this.isRunning) {
            this.isRunning = true;
            button.textContent = 'Running';
            this.start();
        }
    }
    handleStopClick(button) {
        if (this.isRunning) {
            this.isRunning = false;
            button.textContent = 'Stop';
            this.stop();
        }
    }
    incrementCount() {
        const countSpan = document.getElementById('countSpan');
        if (countSpan) {
            this.count += 1;
            countSpan.textContent = this.count;
        }
    }
    updateCountdown(seconds) {
        const countdownSpan = document.getElementById('countdownSpan');
        if (countdownSpan) {
            this.secondsRemaining = seconds;
            countdownSpan.textContent = `Countdown: ${this.secondsRemaining} seconds`;
        }
    }
}

const autoClicker = new AutoClicker();
autoClicker.insertControlDiv();
})()