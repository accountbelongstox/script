from openai import OpenAI
import time
from flask import Flask, render_template, request
<<<<<<< HEAD
from kernel.practicals import env
from kernel.utils import file
=======
from pycore.practicals import env
from pycore.utils import file
>>>>>>> origin/main


class OpenAIAssistantApp:
    def __init__(self):
        self.openai_api_key = env.get_env("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)
        self.OPENAI_ASSISTANT_ID = env.get_env("OPENAI_ASSISTANT_ID")
        self.assistant = self.client.beta.assistants.retrieve(self.OPENAI_ASSISTANT_ID)
<<<<<<< HEAD
        template_folder = file.resolve_path(file.get_root_dir(), "apps/openai_assistant/templates")
=======
        template_folder = file.resolve_path(file.get_root_dir(), "applications/openai_assistant/templates")
>>>>>>> origin/main
        print("template_folder", template_folder)
        self.app = Flask(__name__)
        self.port = int(env.get_env("OPENAI_PORT"))
        self.thread = self.client.beta.threads.create()

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/get", methods=["GET", "POST"])
        def completion_response():
            user_input = request.args.get('msg')
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_input,
            )
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )

            def wait_on_run(run, thread):
                while run.status == "queued" or run.status == "in_progress":
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id,
                    )
                    time.sleep(0.5)
                return run

            run = wait_on_run(run, self.thread)
            wait_on_run(run, self.thread)
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id, limit="10", order="asc", after=message.id  # 升序排列
            )
            for msg in messages.data:
                if msg.role == "assistant":
                    response = msg.content[0].text.value
            return str(response)

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port)


# Instantiate and run the app
openai_app = OpenAIAssistantApp()
