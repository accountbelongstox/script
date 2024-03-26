import docx2txt
import os
import subprocess
import time
from queue import Queue
from pycore._base import Base
from pycore.threads import ComThread
from pycore.utils import file, arr, plattools

class DocConv(Base):
    doc_queue = Queue()
    docx_queue = Queue()

    def __init__(self, ):
        pass

    def check_require(self):
        if not plattools.is_linux():
            self.error("The platform require Linux.")
            return False
        if not plattools.is_command("unoconv"):
            self.error("unoconv is not installed.")
            return False
        if not plattools.is_command("libreoffice"):
            self.error("libreoffice is not installed.")
            return False
        else:
            self.info("DocConverter requirements are satisfied.")
            return True

    def doc_to_txt(self, input_file, output_file):
        if self.check_require():
            command = f"unoconv -f txt -o {output_file} {input_file}"
            self.execute_command([command])

    def docs_to_txt(self, input_path, output_path):
        if self.check_require():
            command_doc = f"unoconv -f txt -o {output_path} {os.path.join(input_path, '*.doc')}"
            command_docx = f"unoconv -f txt -o {output_path} {os.path.join(input_path, '*.docx')}"
            self.execute_command([command_doc, command_docx])

    def execute_command(self, commands):
        all_output = []
        all_error = []
        for command in commands:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            all_output.append(output.decode())
            all_error.append(error.decode())
        return all_output, all_error

    def create_folder_queues(self):
        files = os.listdir(self.input_folder)
        for file_name in files:
            file_path = os.path.join(self.input_folder, file_name)
            if file_name.endswith(".doc"):
                self.doc_queue.put({
                    "file_path": file_path,
                    "input_folder": self.input_folder,
                    "output_folder": self.output_folder,
                })
            elif file_name.endswith(".docx"):
                self.docx_queue.put({
                    "file_path": file_path,
                    "input_folder": self.input_folder,
                    "output_folder": self.output_folder,
                })

        return self.doc_queue, self.docx_queue

    def convert_doc_to_text(self, resolve_obj):
        file_path = resolve_obj["file_path"]
        input_folder = resolve_obj["input_folder"]
        output_folder = resolve_obj["output_folder"]
        input_path = os.path.join(input_folder, file_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}.txt")
        if not file.isFile(output_path):
            try:
                subprocess.run(["unoconv", "--format", "txt", "--output", output_path, input_path], check=True)
            except subprocess.CalledProcessError as e:
                self.error(f"unoconv with unoconv {input_path} : {e}")

    def convert_docx_to_text(self, resolve_obj):

        from zipfile import ZipFile
        from bs4 import BeautifulSoup
        from docx import Document

        def read_xml_content(input_path, doc_xml):
            try:
                zip = ZipFile(input_path)
                return zip.read(doc_xml)
            except Exception as e:
                self.warn(f"read_xml: {e}")
                return None

        def read_document(input_path):
            try:
                document = Document(input_path)
                texts = [paragraph.text for paragraph in document.paragraphs]
                return texts
            except Exception as e:
                self.warn(f"read_document: {e}")
                return None

        file_path = resolve_obj["file_path"]
        input_folder = resolve_obj["input_folder"]
        output_folder = resolve_obj["output_folder"]
        input_path = os.path.join(input_folder, file_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}.txt")

        if not file.isFile(output_path):
            texts = read_document(input_path)
            if texts:
                text_content = "\n".join(texts)
                file.save(output_path, text_content)
            else:
                self.warn(f"read_document failed for: {input_path}")
                xml_content = read_xml_content(input_path, 'word/document.xml')
                if not xml_content:
                    self.warn(f"read_xml_content failed for: word/document.xml")
                    xml_content = read_xml_content(input_path, 'word/document2.xml')
                if not xml_content:
                    self.warn(f"read_xml_content failed for: word/document2.xml")
                    xml_content = read_xml_content(input_path, '_rels/.rels')
                if xml_content:
                    self.warn(f"Using xml_content from: {xml_content}")
                    word_obj = BeautifulSoup(xml_content.decode("utf-8"), "html.parser")
                    texts = word_obj.findAll("w:t")
                    text_content = "\n".join([text.text for text in texts])
                    file.save(output_path, text_content)
                else:
                    self.error(f"All attempts to read XML content failed for: {input_path}")
                    self.error(f"Failed to read XML content: {input_path}")

    def convert_docx_to_text_by_textract(self, resolve_obj):
        import textract
        file_path = resolve_obj["file_path"]
        input_folder = resolve_obj["input_folder"]
        output_folder = resolve_obj["output_folder"]
        input_path = os.path.join(input_folder, file_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}.txt")

        if not file.isFile(output_path):
            try:
                text_content = textract.process(input_path, extension='docx', encoding='utf-8')
                text_content = text_content.decode('utf-8')
                file.save(output_path, text_content)
            except Exception as e:
                self.error(f"textract: {input_path} {e}")
