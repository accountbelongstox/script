import json
import os
import time
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from kernel.practicals import env
import apps.openai_assistant.functions as functions

class ChatBot:
    def __init__(self, openai_api_key, port=8080):
        self.port = int(port)
        self.OPENAI_API_KEY = openai_api_key
        self.app = Flask(__name__)
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        self.assistant_id = functions.create_assistant(self.client)

        @self.app.route('/start', methods=['GET'])
        def start_conversation():
            print("Starting curses.pyc new conversation...")
            thread = self.client.beta.threads.create()
            print(f"New thread created with ID: {thread.id}")
            return jsonify({"thread_id": thread.id})

        @self.app.route('/chat', methods=['POST'])
        def chat():
            data = request.json
            thread_id = data.get('thread_id')
            user_input = data.get('message', '')

            if not thread_id:
                print("Error: Missing thread_id")
                return jsonify({"error": "Missing thread_id"}), 400

            print(f"Received message: {user_input} for thread ID: {thread_id}")

            self.process_user_message(thread_id, user_input)
            response = self.get_assistant_response(thread_id)

            print(f"Assistant response: {response}")
            return jsonify({"response": response})

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port)

    def process_user_message(self, thread_id, user_input):
        self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_input)

    def get_assistant_response(self, thread_id):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=self.assistant_id)

        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id)

            if run_status.status == 'completed':
                break
            elif run_status.status == 'requires_action':
                self.handle_function_calls(thread_id, run)
            time.sleep(1)

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value

    def handle_function_calls(self, thread_id, run):
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "solar_panel_calculations":
                arguments = json.loads(tool_call.function.arguments)
                output = functions.solar_panel_calculations(
                    arguments["address"], arguments["monthly_bill"])
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    }])
            elif tool_call.function.name == "create_lead":
                arguments = json.loads(tool_call.function.arguments)
                output = functions.create_lead(
                    arguments["name"], arguments["phone"], arguments["address"])
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    }])

openai_api_key = env.get_env("OPENAI_API_KEY")
port = env.get_env("OPENAI_PORT")
chat_bot = ChatBot(openai_api_key,port)
