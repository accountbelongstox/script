// ==UserScript==
// @name         🔥ncss query
// @namespace    https://github.com/adlered
// @version      4.2.2
// @description  ⚡️ncss query
// @author       Adler
// @include      *://www.baidu.com/*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @license      AGPL-3.0-or-later
// ==/UserScript==
class TimerClass {
    ourls = {
        ourl: "",
        text: "",
        open: false
    }
    startTime = Date.now();
    isHttpPostInProgress = false;
    lastSrc = null;

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
    generatePositionKeys(initialPosition) {
        const position_keys = [];
        let position = initialPosition;
        while (position.length >= 2) {
            position_keys.push(position);
            position = position.slice(1);
        }
        for (let i = initialPosition.length - 1; i >= 1; i--) {
            position_keys.push(initialPosition.slice(0, i));
        }
        position_keys.sort((a, b) => b.length - a.length);
        return position_keys;
    }

    tick(force = ``) {
        if (this.isHttpPostInProgress) {
            console.log("httpPost is still in progress. Skipping tick.");
            return;
        }
        const currentTime = Date.now();
        const elapsedTimeInSeconds = Math.floor((currentTime - this.startTime) / 1000);
        console.log(`Elapsed time: ${elapsedTimeInSeconds} seconds`);
        this.isHttpPostInProgress = true;
        this.httpPost({}, 'get_key', (data) => {
            const timestamp = data.timestamp
            console.log(`currentTime - timestamp`, currentTime - timestamp)
            if (data && data.src) {
                let timeout = 0
                const [id, url, initialPosition, compny] = data.src.split(`,`);
                const key_input = `${compny} ${initialPosition}`
                let ValueAndPosition = this.getValueAndPosition(`#kw`)
                if (key_input != ValueAndPosition) {
                    this.clearInput(`#kw`);
                    this.simulateInput(`#kw`, key_input);
                    this.simulateClick(`#su`,);
                    console.log("data.src is the same as the previous one. Giving a prompt.");
                    this.lastSrc = data.src;
                    timeout = 1000
                }
                setTimeout(() => {
                    this.findElement(`#content_left`, (success) => {
                        this.isHttpPostInProgress = false;
                        if (success) {
                            this.getResult(ValueAndPosition)
                        }
                    })
                }, timeout)
            } else {
                this.isHttpPostInProgress = false
            }
        })
    }

    start() {
        setInterval(()=>{
            this.tick()
        },1000)
    }

    getResult(compny, initialPosition) {
        const links = this.extractLinksAndText(`#content_left`)
        if (links) {
            let ourl_is_set = false, text = `${compny} ${initialPosition}`;
            if (this.ourls.text == text) {
                ourl_is_set = true
                return setTimeout(() => {
                    this.start()
                }, 1000)
            } else {
                this.ourls.open = false
                ourl_is_set = false
            }
            const jobPlatforms = ['BOSS直聘', '职友', '58', '看准', '前程', '人才', `公司`, `聘`, `职`];
            for (const link of links) {
                if (ourl_is_set) break;
                for (const jkey of jobPlatforms) {
                    if (link.webname.includes(jkey)) {
                        this.ourls.text = text
                        this.ourls.ourl = link.href
                        ourl_is_set = true
                        break;
                    }
                }
            }
            if (!ourl_is_set) {
                const compny_keys = this.generatePositionKeys(compny);
                const position_keys = this.generatePositionKeys(initialPosition);
                for (const link of links) {
                    if (ourl_is_set) break;
                    for (const key of position_keys) {
                        if (ourl_is_set) break;
                        if (link.content.includes(key)) {
                            for (const ckey of compny_keys) {
                                if (ourl_is_set) break;
                                if (link.content.includes(ckey)) {
                                    this.ourls.text = text
                                    this.ourls.ourl = link.href
                                    ourl_is_set = true
                                }
                            }
                        }
                    }
                }
            }
            if (!ourl_is_set) {
                this.ourls.text = text
                this.ourls.ourl = links[0].href;
                ourl_is_set = true
            }
            if (this.ourls.text == text && !this.ourls.open) {
                this.ourls.open = true
                window.open(this.ourls.ourl, '_blank');
            }
            // this.httpPost({ oriurl: links[0] }, 'put_result', () => {
            //     this.start()
            // })
        }
    }
    getValueAndPosition(selector) {
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`Element with selector ${selector} not found`);
            return null;
        }
        const value = element.value;
        if (!value) {
            console.error(`Value is empty for element with selector ${selector}`);
            return null;
        }
        const values = value.split(/\s+/);
        if (values.length < 2) {
            console.error(`Unable to split value for element with selector ${selector}`);
            return null;
        }
        const compny = values[0];
        const initialPosition = values[1];
        return `${compny} ${initialPosition}`;
    }
    extractLinksAndText(selector) {
        const contentLeftElement = document.querySelector(selector);
        if (contentLeftElement) {
            const containerElements = contentLeftElement.querySelectorAll('.result.c-container');

            const linksAndText = [];
            for (let i = 0; i < containerElements.length; i++) {
                const container = containerElements[i];
                const c_title = container.querySelector(`.c-title`);
                const c_href = container.querySelector(`a`);
                const c_color_gray = container.querySelector(`.c-color-gray`);
                const c_container = container.querySelector(`.c-container`);
                let href = ``
                let title = ``
                let content = ``
                let webname = ``
                if (c_container) {
                    const firstDiv = c_container.querySelector('div');
                    if (firstDiv) {
                        const lastDiv = firstDiv.lastElementChild;
                        content = lastDiv.textContent.trim();
                    }
                }
                if (c_title) {
                    title = c_title.textContent.trim();
                }
                if (c_href) {
                    href = c_href.getAttribute('href');
                }
                if (c_color_gray) {
                    webname = c_color_gray.textContent.trim();
                }
                linksAndText.push({ href, title, webname, content });
                // const titleContainer = containerElements2[i];
                // const anchorElement = container.querySelector('a');
                // let title = ``
                // if(titleContainer){
                //     const c_color_gray = contentLeftElement.querySelector('.c-color-gray');
                //     console.log(`c_color_gray`,c_color_gray)
                //     if(c_color_gray){
                //         title = c_color_gray.textContent;
                //     }
                // }
                // if (anchorElement) {
                //     const href = anchorElement.getAttribute('href');
                //     const textContent = container.textContent.trim();
                //     linksAndText.push({ href, content: textContent ,title});
                // }
            }
            return linksAndText;
        } else {
            return null;
        }
    }

    parseUrlParameters() {
        // Extract parameters from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const id = (urlParams.get('id') || '').trim().replace(/^\s+|\s+$/g, ''); // Trim and remove leading/trailing spaces and newlines
        const url = (urlParams.get('url') || '').trim().replace(/^\s+|\s+$/g, ''); // Trim and remove leading/trailing spaces and newlines
        const position = (urlParams.get('position') || '').trim().replace(/^\s+|\s+$/g, ''); // Trim and remove leading/trailing spaces and newlines
        return { id, url, position };
    }

    processElements(callback) {
        const findElementInterval = setInterval(() => {
            let realCorpNameElement = document.getElementById(`realCorpName`);
            if (!realCorpNameElement) {
                realCorpNameElement = document.getElementById(`corpName`);
            }
            if (realCorpNameElement) {
                clearInterval(findElementInterval); // 清除定时器
                const processedText = realCorpNameElement.textContent.trim().replace(/^\s+|\s+$/g, '');
                callback(processedText); // 执行回调函数并传递结果
            }
        }, 500);
    }

    stop() {
        clearInterval(this.intervalId);
    }

    isValidUrl(url) {
        // You can implement a more robust URL validation logic if needed
        const urlPattern = /^(http|https):\/\/[^ "]+$/;
        return urlPattern.test(url);
    }

    simulateInput(selector, inputText) {
        const targetElement = document.querySelector(selector);

        if (targetElement) {
            targetElement.focus();
            for (const char of inputText) {
                const event = new KeyboardEvent('keydown', { key: char }); // 模拟按下键盘按键
                targetElement.dispatchEvent(event);
                targetElement.value += char; // 将字符添加到输入框的值
            }

            const inputEvent = new Event('input', { bubbles: true }); // 模拟输入事件
            targetElement.dispatchEvent(inputEvent);
            targetElement.blur(); // 失去焦点
        } else {
            console.error(`Element with selector '${selector}' not found.`);
        }
    }
    clearInput(selector) {
        const targetElement = document.querySelector(selector);

        if (targetElement) {
            targetElement.value = ''; // 清空输入框的值
            const inputEvent = new Event('input', { bubbles: true }); // 模拟输入事件
            targetElement.dispatchEvent(inputEvent);
        } else {
            console.error(`Element with selector '${selector}' not found.`);
        }
    }
    simulateClick(selector) {
        const targetElement = document.querySelector(selector);
        targetElement.click()
        return
        if (targetElement) {
            const clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
            targetElement.dispatchEvent(clickEvent);
        } else {
            console.error(`Element with selector '${selector}' not found.`);
        }
    }

    async getRealUrl(url) {
        const response = await fetch(url, { method: 'HEAD' });
        const headers = response.headers;
        if (response.ok) {
            return url;
        } else if (response.status === 301 || response.status === 302) {
            const locationHeader = headers.get('location');
            if (Array.isArray(locationHeader)) {
                return locationHeader[locationHeader.length - 1];
            } else {
                return locationHeader;
            }
        } else {
            return url;
        }
    }
}

// Example usage:
const timerInstance = new TimerClass();
timerInstance.start();

// Uncomment the following line to stop the timer after 10 seconds
// setTimeout(() => timerInstance.stop(), 10000);
