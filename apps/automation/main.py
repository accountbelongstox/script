import os
import os.path
import time

from apps.automation.lib.ctrler.operation import operation
from apps.automation.lib.flask.auto_flask_conf import config
from apps.automation.lib.flask.router import Router
from apps.automation.lib.instance.handle import handle
from apps.task.task import task
from kernel.base.base import Base
from kernel.threads import FlaskThread
from kernel.utils import file

class autoMain(Base):
    current_screen_file = None
    default_prompts_dir = ".prompts"

    def __init__(self):
        pass

    def start(self):
        flask = FlaskThread(config=config, router=Router)
        flask.start()
        return
        tick_interval = 30
        """
        The prompt word has been processed and the network request is also empty
        The prompt word GPT processing was successful and has been obtained. The length is:
        """
        while True:
            operation.check_status()
            if operation.is_chat_enable():
                self.success("GPT is currently idle, Start curses.pyc new mission.")
                time.sleep(2)
                if task.task_is_empty():
                    self.success("The current queue is empty, request curses.pyc new queue.")
                    task.fetch_task()
                else:
                    task_len = task.task_len()
                    self.success(f"There is another {task_len} task in the current queue.")
                key, one_task = task.pop_task()
                if task:
                    prompt = one_task.get("task_content")
                    group = one_task.get("group")
                    self.success(f"Prompt word request successful, type: generic, length: {len(prompt)}")
                    task.set_current_prompt(prompt)
                    task.set_current_key(key)
                    res = operation.chat_input(prompt)
                    complete = task.is_complete(key)
                    while complete == False:
                        self.info("Waiting for prompt words to complete...")
                        time.sleep(2)
                        complete = task.is_complete(key)
                    operation.to_chat_bottom()
                    self.info(f"complete: {complete} ")
                    self.info(
                        f"A task {key} has been processed and is being submitted to the task server, as well as saving the local cache.")
                    task.put_complete_and_pop(key)
                    # try:
                    #     prompt = one_task.get("task_content")
                    #     group = one_task.get("group")
                    #     self.success(f"Prompt word request successful, type: generic, length: {len(prompt)}")
                    #     task.set_current_prompt(prompt)
                    #     task.set_current_key(key)
                    #     res = operation.chat_input(prompt)
                    #     complete = task.is_complete(key)
                    #     while complete == True:
                    #         prompt("Waiting for prompt words to complete...")
                    #         time.sleep(2)
                    #         complete = task.is_complete(key)
                    #     self.info(f"complete: {complete} ")
                    #     self.info(
                    #         f"A task {key} has been processed and is being submitted to the task server, as well as saving the local cache.")
                    #     task.put_complete_and_pop(key)
                    # except Exception as e:
                    #     self.warn("Task Error"+str(e))
                    #     self.warn("Task Key"+str(key))
                    #     self.warn("Task Info"+str(one_task))
                    # time.sleep(2)
            else:
                self.info("GPT does not have an open interface, please manually open it")
            self.info(f"sleep {tick_interval} s")
            time.sleep(tick_interval)
    #
    #         while True:
    #             self.info("sleep 30 s")
    #             time.sleep(30)
    #         handle.tick()
    #         text = """
    #         const tag = child.tagName.toLowerCase();
    # if (liTags.includes(tag)) {
    #     const texts = {};
    #
    #     const traverseElements = (element) => {
    #         let textContent = element.textContent.trim();
    #
    #         // Recursive function to traverse child elements
    #         for (let i = 0; i < element.children.length; i++) {
    #             const childTag = element.children[i].tagName.toLowerCase();
    #             if (liTags.includes(childTag)) {
    #                 const nestedTexts = traverseElements(element.children[i]);
    #                 textContent += nestedTexts;
    #             }
    #         }
    #
    #         return textContent;
    #     };
    #
    #     const nestedText = traverseElements(child);
    #
    #     texts["text_" + index] = {
    #         type: "listText",
    #         content: nestedText // Assign the hierarchical content here
    #     };
    # }
    #
    # 请分析以上代码.
    #         """
    #         res = operation.chat_input(text)
    #         self.info("res",res)

    def create_prompts_dir(self, file_path):
        self.default_prompts_dir = os.path.join(file_path, "default_prompts_dir")
        file.mkdir(self.default_prompts_dir)
        return self.default_prompts_dir


auto_main = autoMain()
