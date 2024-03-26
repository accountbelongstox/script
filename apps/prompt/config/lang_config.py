from kernel.utils import arr, strtool, tool

class LanguageConfig:
    _pre = "#"
    initializer = "-"
    max_line = 100
    prompt_map = {
        "go": {
            "lang": "Golang",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "py": {
            "lang": "Python",
            "comment_symbol": "#",
            "frameworks": "",
        },
        "java": {
            "lang": "Java",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "cpp": {
            "lang": "C++",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "c": {
            "lang": "C",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "js": {
            "lang": "JavaScript",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "html": {
            "lang": "HTML",
            "comment_symbol": "<!-- -->",
            "frameworks": "",
        },
        "css": {
            "lang": "CSS",
            "comment_symbol": "/* */",
            "frameworks": "",
        },
        "php": {
            "lang": "PHP",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "ruby": {
            "lang": "Ruby",
            "comment_symbol": "#",
            "frameworks": "",
        },
        "swift": {
            "lang": "Swift",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "kotlin": {
            "lang": "Kotlin",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "typescript": {
            "lang": "TypeScript",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "scala": {
            "lang": "Scala",
            "comment_symbol": "//",
            "frameworks": "",
        },
        "rust": {
            "lang": "Rust",
            "comment_symbol": "//",
            "frameworks": "",
        },
    }

    def get_langconfig(self, ext, frameworks=None):
        lang_config = {
            "lang": "",
            "comment_symbol": "",
            "frameworks": "",
        }
        if ext in self.prompt_map:
            lang_config = self.prompt_map[ext].copy()
            if frameworks is not None:
                lang_config["frameworks"] = f"with {frameworks}"
        return lang_config

lang_config = LanguageConfig()
