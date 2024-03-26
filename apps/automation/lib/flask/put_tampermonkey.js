// ==UserScript==
// @name              GPT_Fetch
// @description       gpt
// @version           21.6
// @author            dd
// @icon              data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDUiIGhlaWdodD0iNDUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgogPCEtLSBDcmVhdGVkIHdpdGggTWV0aG9kIERyYXcgLSBodHRwOi8vZ2l0aHViLmNvbS9kdW9waXhlbC9NZXRob2QtRHJhdy8gLS0+CiA8Zz4KICA8dGl0bGU+YmFja2dyb3VuZDwvdGl0bGU+CiAgPHJlY3QgZmlsbD0ibm9uZSIgaWQ9ImNhbnZhc19iYWNrZ3JvdW5kIiBoZWlnaHQ9IjQ3IiB3aWR0aD0iNDciIHk9Ii0xIiB4PSItMSIvPgogIDxnIGRpc3BsYXk9Im5vbmUiIG92ZXJmbG93PSJ2aXNpYmxlIiB5PSIwIiB4PSIwIiBoZWlnaHQ9IjEwMCUiIHdpZHRoPSIxMDAlIiBpZD0iY2FudmFzR3JpZCI+CiAgIDxyZWN0IGZpbGw9InVybCgjZ3JpZHBhdHRlcm4pIiBzdHJva2Utd2lkdGg9IjAiIHk9IjAiIHg9IjAiIGhlaWdodD0iMTAwJSIgd2lkdGg9IjEwMCUiLz4KICA8L2c+CiA8L2c+CiA8Zz4KICA8dGl0bGU+TGF5ZXIgMTwvdGl0bGU+CiAgPGltYWdlIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBQzBBQUFBdENBTUFBQUFOeEJLb0FBQUFObEJNVkVVQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQ0FnSUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFCTHIweWtBQUFBRVhSU1RsTUFJdmZqMXFNNGxHZUN6YnhJZHhXd1ZFcUlTSmdBQUFFdlNVUkJWRWpIemRUYmJvVWdFSVhobVFGQkRoN1crNzlzRWNNR2JOR20yVTM3M2ZySHhHVXlWRVNQRVIvcFlzR2RoVG9NUVBUWEJBQlR5d0dLNld1c3JpKzN3RVFqRTJEL29MWlRaUjlyUVNWdnJ1ZFdyZi9wZ2pNZ094ZDA0R0lYWUtiV0trZ2tnemdpY29KS3JkU0pnb1lsaXpZMmRNSFc2NU1Db0k5R243eGx1ckhoc05FM1RXZ21lbWJieVo1RmVpTysxN2RCY0VkQzIzczg4WmRyb201MEY4VUF3alRHQXBpdVhtbHNiZXZuZC8rd1RtZUR1ZFRHMlptcTJUcFRhdVpVRWdCVGFvZEVjNzJXaVN1MUFkRFdPekpOSjQxc0g5UWJFQllCek90amxnQnNnem9BOW5nUWN4MEJZUXVFUWIwZ2s3V01uQzF0N1p4N2JlSnhtT3ZWU1B4cmsxVDJlenV2UXFRaUJ1Vnp3TC80TCtsVGJYak1kRFVEa0JHY3VMODM5eVpxT0syR3RGYmFVZllCQzNzbUVVWHJITThBQUFBQVNVVk9SSzVDWUlJPSIgaWQ9InN2Z18xIiBoZWlnaHQ9IjQ1IiB3aWR0aD0iNDUiIHk9IjAiIHg9IjAiLz4KIDwvZz4KPC9zdmc+
// @license           GPL-2.0-only
// @match             *://chat.openai.com
// @match             *://chat.openai.com/*
// @grant             GM_addStyle
// @grant             GM_addElement
// @grant             GM_setValue
// @grant             GM_getValue
// @grant             GM_xmlhttpRequest
// @grant             unsafeWindow
// @run-at            document-body
// @noframes
// ==/UserScript==


(function () {
    'use strict';
    const chat_selector = `[data-message-author-role="assistant"]`
    const chat_line_id = `data-message-id`
    class ContentFetcher {
        apiUrl = 'http://localhost:5000/chat'
        fetching = false
        previous_key = null
        generating_chat = false
        generating_progress = false
        fragment_data_can_be_submitted = true
        product = false

        constructor() {
            this.cList = {};
        }

        log(...args) {
            if (!this.product) {
                console.log(...args);
            }
        }

        error(...args) {
            if (!this.product) {
                console.error(...args);
            }
        }

        getLastChatId() {
            const elements = document.querySelectorAll(chat_selector);
            if (elements.length) {
                const selector = elements[elements.length - 1];
                const id = selector.getAttribute(chat_line_id);
                return id
            } else {
                this.log(`There are currently no chats.`)
                return null
            }
        }

        isNewChat(setNewChat) {
            const lastChatId = this.getLastChatId()
            if (lastChatId != this.previous_key) {
                if (setNewChat) {
                    this.previous_key = lastChatId
                }
                this.log(`There are currently new chats.`)
                return true
            }
            return false
        }

        getFirstContentElement(element) {
            var children = element.children;
            if (element) {
                if (children.length > 1) {
                    return children[0];
                } else {
                    var grandchildren = children[0].children;
                    if (grandchildren.length > 0) {
                        return grandchildren[0];
                    } else {
                        return null;
                    }
                }
            } else {
                return null;
            }
        }

        getChatContensElements(firstContentElement) {
            if (firstContentElement) {
                const container = firstContentElement.parentNode;
                const children = container.children;
                return Array.from(children);
            }
            return []
        }

        disableContentFetchStatus() {
            this.fetching = true;
        }

        resetContentFetchStatus() {
            this.fetching = false;
        }

        waitContentContainer(id, callback) {
            setTimeout(() => {
                this.log(`The first chat box content has not yet appeared.`)
                this.resetContentFetchStatus();
                this.getContentStep(id, callback)
            }, 2000)
        }

        setContentGetDone(id) {
            this.cList[id].done = true
            this.waitPutC = true
            this.fetching = false;
            this.generating_chat = false
        }

        async extraChatContent(chatOneTagElement) {
            let texts
            const textTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
            const codeTags = ['pre'];
            const liTags = ['ol', `ul`];
            const tag = chatOneTagElement.tagName.toLowerCase();
            if (liTags.includes(tag)) {
                const listTextContent = {}
                const traverseElements = (element, parent_tag = '') => {
                    if (parent_tag) parent_tag += parent_tag
                    let textContent = element.textContent.trim();
                    listTextContent[parent_tag ? parent_tag : "root"] = textContent
                    for (let i = 0; i < element.children.length; i++) {
                        const childTag = element.children[i].tagName.toLowerCase();
                        if (liTags.includes(childTag)) {
                            const nestedTexts = traverseElements(element.children[i], parent_tag);
                            textContent += nestedTexts;
                        }
                    }
                    return textContent;
                };
                traverseElements(chatOneTagElement, '');
                texts = {
                    type: "list",
                    content: listTextContent
                }
            } else if (textTags.includes(tag)) {
                texts = {
                    type: "text",
                    content: chatOneTagElement.textContent
                }
            } else if (codeTags.includes(tag)) {
                let code_content
                // try {

                //     const button = chatOneTagElement.querySelector('button');
                //     this.simulateClick(button)
                //     code_content = await navigator.clipboard.readText();
                // } catch (e) {
                //     console.log(e)
                //     code_content = chatOneTagElement.textContent.split('Copy code')[1]
                // }
                code_content = chatOneTagElement.textContent.split('Copy code')[1]
                texts = {
                    type: "code",
                    content: code_content
                };
            } else {
                texts = {
                    type: "unsupported_tab",
                    content: chatOneTagElement.textContent
                };
                this.log(`unsupported_tab message fetch tag of ${tag}`)
            }
            return texts
        }

        diffAndMergeChatContent(id, texts) {
            let snippet_information = {
                texts: null,
                id,
                done: false,
            }
            if (!this.cList[id]) {
                this.cList[id] = {
                    id,
                    texts,
                    done: false,
                };
                snippet_information.texts = texts
            } else {
                const new_texts = { ...texts }
                for (const key in new_texts) {
                    if (new_texts.hasOwnProperty(key)) {
                        const newItem = new_texts[key];
                        const newTextContent = newItem.content
                        const type = newItem.type
                        const existingItem = this.cList[id].texts[key];
                        if (existingItem) {
                            const existingTextContent = existingItem.content
                            if (existingTextContent && newTextContent.length > existingTextContent.length) {
                                const newContent = newTextContent.slice(existingTextContent.length);
                                snippet_information.texts[key] = {
                                    content: newContent,
                                    type: type,
                                };
                            }
                        }
                    }
                }
                console.log(`new texts`, texts)
                this.cList[id].texts = texts
            }
            if (snippet_information.texts) {
                this.log("Snippet submission.", snippet_information)
                this.putSnippet(snippet_information)
            } else {
                this.log(`Superimposed chat notes.`)
            }
        }

        getContentStep(id, callback) {
            if (this.fetching) {
                this.log(`fetching...`)
                return
            }
            this.disableContentFetchStatus();
            const elements = document.querySelectorAll(chat_selector);
            if (!elements.length) {
                return this.waitContentContainer(id, callback)
            }
            let element = elements[elements.length - 1];
            const firstContentElement = this.getFirstContentElement(element);
            if (!firstContentElement) {
                // 没有出聊天框, 还没有生成第一个聊天框
                return this.waitContentContainer(id, callback)
            }
            const processExtraChatContent = () => {
                setTimeout(() => {
                    const chatContensElements = this.getChatContensElements(firstContentElement)
                    if (!chatContensElements.length) {
                        return processExtraChatContent()
                    }
                    const texts = {};
                    chatContensElements.forEach(async (chatOne, index) => {
                        const contentObject = await this.extraChatContent(chatOne)
                        texts["text_" + index] = contentObject
                    });
                    this.diffAndMergeChatContent(id, texts)
                    if (this.is_generate_done()) {
                        this.setContentGetDone(id)
                        //已经全部生成完毕
                        this.log(`All have been generated`)
                        if (callback) callback()
                        return
                    }
                    return processExtraChatContent()
                }, 1000)
            };
            processExtraChatContent();
        }

        putSnippet(postData) {
            setTimeout(() => {
                if (!this.fragment_data_can_be_submitted) {
                    this.fragment_data_can_be_submitted = true
                    return
                }
                this.submitData(postData)
            }, 500)
        }

        putDone(postData) {
            this.fragment_data_can_be_submitted = false
            postData.done = true
            console.log(`putDone`)
            console.log(postData)
            this.submitData(postData, () => {
                delete this.cList[postData.id]
            })
        }

        submitData(postData, callback) {
            fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            })
                .then(response => response.text())
                .then(data => {
                    this.log('Response:', data);
                    if (callback) callback()
                })
                .catch(error => {
                    this.error('Error:', error);
                });
        }

        simulateClick(btn) {
            const event = new MouseEvent('click', {
                bubbles: true,
                cancelable: true
            });
            btn.dispatchEvent(event);
        }

        simulateClick2(btn) {
            var evt = document.createEvent('Event');
            evt.initEvent('click', true, true);
            btn.dispatchEvent(evt);
        }

        is_generating() {
            this.previous_key
            const pathElement = document.querySelector('[aria-label="Stop generating"]');
            if (!pathElement) {
                this.generating_progress = false
                return this.generating_progress;
            } else {
                this.generating_progress = !!(pathElement.offsetWidth || pathElement.offsetHeight || pathElement.getClientRects().length);
                return this.generating_progress;
            }
        }

        set_stop_generating() {
            setTimeout(() => {
                this.generating_progress = false
            }, 2000)
        }

        is_generate_done() {
            return !this.generating_progress
        }

        submitWaitCompleteContent() {
            for (var key in this.cList) {
                const item = this.cList[key]
                if(item.done === true){
                    this.putDone(item)
                }
            }
        }

        check() {
            const chatId = this.getLastChatId()
            const setNewChat = true;
            if (this.generating_chat || this.is_generating()) {
                contentFetcher.getContentStep(chatId, () => {
                    this.submitWaitCompleteContent()
                });
            } else if (this.isNewChat(setNewChat)) {
                this.generating_chat = true
            } else {
                this.error('Standby status. Neither is in a generated state. You are not sending.')
            }
        }
    }
    const contentFetcher = new ContentFetcher();
    setInterval(() => {
        contentFetcher.check()
    }, 800)
})();