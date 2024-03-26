// ==UserScript==
// @name         🔥ncss result
// @namespace    https://github.com/adlered
// @version      4.2.2
// @description  ⚡️ncss result
// @author       Adler
// @include      *://*.*/*
// @include      *://*.*.*/*
// @exclude      *://*.baidu.com/*
// @exclude      *://*.ncss.cn/*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @license      AGPL-3.0-or-later
// ==/UserScript==
class TimerClass {
    constructor() {
        this.intervalId = null;
        this.tickCount = 0;
        this.apiUrl = 'http://localhost:5000'; // Replace with your actual API endpoint
    }

    httpPost(data, queryUrl = ``, callback) {
        try {
            const url = queryUrl ? `${this.apiUrl}/${queryUrl}` : this.apiUrl;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP POST request failed');
                    }
                    return response.json();
                })
                .then(result => {
                    callback(result,);
                })
                .catch(error => {
                    console.error('Error during HTTP POST:', error.message);
                    callback(error, null);
                });
        } catch (error) {
            console.error('Error during HTTP POST:', error.message);
            callback(error, null);
        }
    }

    async findElement(selector, callback, maxAttempts = 10, interval = 500) {
        let attempts = 0;
        const tryToFindElement = async () => {
            const element = document.querySelector(selector);
            if (element) {
                callback(element);
            } else {
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(tryToFindElement, interval);
                } else {
                    console.error(`Reached maximum attempts (${maxAttempts}) to find the element.`);
                    callback(null)
                }
            }
        };
        tryToFindElement();
    }
    start() {
        const checkOriurl = () => {
            const oriurl = window.location.href;
            console.log('Current URL:', oriurl);

            if (oriurl) {
                setTimeout(() => {
                    this.httpPost({ oriurl: window.location.href }, 'put_result', (data) => {
                        window.close();
                    });
                }, 2000)
            } else {
                setTimeout(checkOriurl, 500);
            }
        };

        checkOriurl();
    }



    isValidUrl(url) {
        // You can implement a more robust URL validation logic if needed
        const urlPattern = /^(http|https):\/\/[^ "]+$/;
        return urlPattern.test(url);
    }
}

// Example usage:
const timerInstance = new TimerClass();
timerInstance.start();