// ==UserScript==
// @name         🔥ncss 插件
// @namespace    https://github.com/adlered
// @version      4.2.2
// @description  ⚡️ncss 插件
// @author       Adler
// @connect      www.ncss.cn
// @include      *://*.ncss.cn/*
// @require      https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/jquery-cookie/1.4.1/jquery.cookie.min.js
// @require      https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/nprogress/0.2.0/nprogress.min.js
// @require      https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/clipboard.js/2.0.10/clipboard.min.js
// @supportURL   https://github.com/adlered/CSDNGreener/issues/new?assignees=adlered&labels=help+wanted&template=ISSUE_TEMPLATE.md&title=
// @contributionURL https://doc.stackoverflow.wiki/web/#/21?page_id=138
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @license      AGPL-3.0-or-later
// @antifeature  ads CSDNGreener 脚本中嵌入了可一键永久关闭的小广告，不会影响您的使用体验:) 请放心安装！
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
          // 调用回调函数，传递结果
          callback(null, result);
        })
        .catch(error => {
          console.error('Error during HTTP POST:', error.message);
          // 调用回调函数，传递错误信息
          callback(error, null);
        });
    } catch (error) {
      console.error('Error during HTTP POST:', error.message);
      // 调用回调函数，传递错误信息
      callback(error, null);
    }
  }


  start() {
    this.processElements((processedText) => {
      if (processedText !== null) {
        const { id, url, position } = this.parseUrlParameters();
        let title = `\n${id},${url},${position},${processedText}`;
        title = title.trim().replace(/^\s+|\s+$/g, '');
        this.httpPost({ title }, 'put_company', (result) => {
          this.tick((status, ids) => {
            if (status) {
              window.location.href = ids.urlWithParams; // 修改当前窗口的 URL
              this.start();
            } else {
              setTimeout(() => {
                this.start();
              }, 500);
            }
          });
        });
      } else {
        setTimeout(() => {
          this.start();
        }, 500);
      }
    });
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

  tick(callback) {
    this.httpPost({}, 'get_data', (error, data) => {
      if (error) {
        console.error('Error during tick:', error.message);
        callback(error, null);
      } else {
        if (data && data.src && Array.isArray(data.src) && data.src.length === 3) {
          const [id, url, position] = data.src;
          if (this.isValidUrl(url)) {
            console.log('Decomposed array:', 'ID:', id, 'URL:', url, 'position:', position);
            const queryParams = new URLSearchParams({ id, url, position });
            const urlWithParams = `${url}?${queryParams.toString()}`;
            callback(true, { id, url, position, urlWithParams });
          } else {
            callback();
          }
        } else {
          callback();
        }
      }
    });
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

// Uncomment the following line to stop the timer after 10 seconds
// setTimeout(() => timerInstance.stop(), 10000);
