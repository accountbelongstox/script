import json
from pprint import pprint
import hashlib
import time
import asyncio
# import openai
from openai import AsyncOpenAI
from pathlib import Path

def generate_prompts(file_content):

    data = json.loads(file_content)

    title = data['title']

    prompts = []
    for section_index, section_data in enumerate(data['outline']):
        section = section_data['section']
        for content_index, content_title in enumerate(section_data['content']):

            prompt = f"根据之前的《{title}》论文：第 {section} 章 -> {content_title}，请生成 {content_title} 内容，字数300字，并附上配图及引用文档链接。"
            timestamp = int(time.time())
            hash_id = hashlib.md5(f"user{timestamp}{section_index}{content_index}".encode()).hexdigest()
            id = f"{hash_id}{timestamp}{section_index}{content_index}"
            prompts.append({"id": id, "content": prompt})
    return prompts


file_path = './a.json'
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

messages_queue = generate_prompts(file_content)
pprint(messages_queue)
#
#
#
#
# # 初始化 OpenAI 客户端

client = AsyncOpenAI(api_key="")#
# sk-7nVZaP1jPhutqnHnDhGm
# T3BlbkFJoFoK3iAoOiUZp0ES7r87

#
# async def handle_message(message):
#     """处理单个消息，并保存响应"""
#     response = await client.chat.completions.create(
#         messages=[
#             {"role": "user", "content": message["content"]}
#         ],
#         model="gpt-3.5-turbo",
#     )
#     # 将响应保存为文本文件
#     Path(f"{message['id']}.txt").write_text(response.choices[0].message.content)
#
# async def main():
#     """主函数，处理消息队列"""
#     for message in messages_queue:
#         await handle_message(message)
#
# # 运行主函数
# asyncio.run(main())
#
#
# pprint(messages_queue)
#