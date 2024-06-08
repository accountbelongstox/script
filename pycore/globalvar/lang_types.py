lang_types = {
    "Python": {"ext": ".py",
               "description": "Python is a high-level, interpreted programming language known for its simplicity and readability."},
    "JavaScript": {"ext": ".js",
                   "description": "JavaScript is a popular scripting language used primarily for web development."},
    "Java": {"ext": ".java",
             "description": "Java is a widely-used, class-based, object-oriented programming language."},
    "C": {"ext": ".c", "description": "C is a procedural programming language commonly used for system programming."},
    "C++": {"ext": ".cpp",
            "description": "C++ is an extension of the C programming language, adding object-oriented features."},
    "C#": {"ext": ".cs", "description": "C# is a multi-paradigm programming language developed by Microsoft."},
    "Ruby": {"ext": ".rb", "description": "Ruby is a dynamic, reflective, object-oriented programming language."},
    "PHP": {"ext": ".php", "description": "PHP is a server-side scripting language designed for web development."},
    "Swift": {"ext": ".swift",
              "description": "Swift is a general-purpose, compiled programming language developed by Apple for iOS, macOS, watchOS, and tvOS."},
    "Objective-C": {"ext": ".m",
                    "description": "Objective-C is a general-purpose, object-oriented programming language used by Apple for macOS and iOS development."},
    "Kotlin": {"ext": ".kt",
               "description": "Kotlin is a statically-typed programming language that runs on the Java Virtual Machine (JVM)."},
    "Go": {"ext": ".go",
           "description": "Go, also known as Golang, is a statically-typed, compiled programming language developed by Google."},
    "Rust": {"ext": ".rs",
             "description": "Rust is a systems programming language that emphasizes safety and concurrency."},
    "TypeScript": {"ext": ".ts",
                   "description": "TypeScript is a typed superset of JavaScript that compiles to plain JavaScript."},
    "HTML": {"ext": ".html",
             "description": "HTML (Hypertext Markup Language) is the standard markup language for creating web pages and web applications."},
    "CSS": {"ext": ".css",
            "description": "CSS (Cascading Style Sheets) is a stylesheet language used to describe the presentation of a document written in HTML or XML."},
    "SQL": {"ext": ".sql",
            "description": "SQL (Structured Query Language) is a domain-specific language used in programming and designed for managing data held in a relational database management system (RDBMS)."},
    "Shell": {"ext": ".sh",
              "description": "Shell scripting refers to a script written for a shell, or command-line interpreter, of an operating system."},
    "Perl": {"ext": ".pl",
             "description": "Perl is a family of two high-level, general-purpose, interpreted, dynamic programming languages."},
    "Scala": {"ext": ".scala",
              "description": "Scala is a modern multi-paradigm programming language designed to express common programming patterns in a concise, elegant, and type-safe way."},
    "Haskell": {"ext": ".hs",
                "description": "Haskell is a purely functional programming language with a strong, static type system and lazy evaluation."},
    "Lua": {"ext": ".lua",
            "description": "Lua is a lightweight, multi-paradigm programming language designed primarily for embedded systems and clients."},
    "MATLAB": {"ext": ".m", "description": "MATLAB is a high-performance language for technical computing."},
    "R": {"ext": ".r",
          "description": "R is a programming language and free software environment for statistical computing and graphics."},
    "VHDL": {"ext": ".vhd",
             "description": "VHDL (VHSIC Hardware Description Language) is a hardware description language used in electronic design automation to describe digital and mixed-signal systems."},
    "Verilog": {"ext": ".v",
                "description": "Verilog is a hardware description language used to model electronic systems."},
    "Pascal": {"ext": ".pas",
               "description": "Pascal is an imperative and procedural programming language designed in the late 1960s."},
    "Fortran": {"ext": ".f90",
                "description": "Fortran (formerly FORTRAN, derived from Formula Translation) is a general-purpose, imperative programming language."},
    "Ada": {"ext": ".adb",
            "description": "Ada is a structured, statically typed, imperative, and object-oriented high-level computer programming language."},
    "COBOL": {"ext": ".cbl",
              "description": "COBOL (Common Business-Oriented Language) is a compiled English-like computer programming language designed for business use."},
    "Dart": {"ext": ".dart",
             "description": "Dart is a client-optimized programming language for apps on multiple platforms."},
    "Elm": {"ext": ".elm",
            "description": "Elm is a functional programming language for declaratively creating web browser-based graphical user interfaces."},
    "F#": {"ext": ".fs",
           "description": "F# is a functional-first, strongly-typed programming language for the .NET ecosystem."},
    "Erlang": {"ext": ".erl",
               "description": "Erlang is a general-purpose, concurrent, functional programming language."},
    "Prolog": {"ext": ".pl",
               "description": "Prolog is a logic programming language associated with artificial intelligence and computational linguistics."},
    "Lisp": {"ext": ".lisp",
             "description": "Lisp is a family of programming languages with a long history and a distinctive, fully parenthesized prefix notation."},
    "Scheme": {"ext": ".scm",
               "description": "Scheme is a functional programming language and one of the two main dialects of the Lisp programming language."},
    "Groovy": {"ext": ".groovy",
               "description": "Groovy is an object-oriented programming language for the Java platform."},
    "OCaml": {"ext": ".ml",
              "description": "OCaml is a general-purpose, high-level programming language with an emphasis on expressiveness and safety."},
    "Smalltalk": {"ext": ".st",
                  "description": "Smalltalk is an object-oriented, dynamically typed reflective programming language."},
    "Solidity": {"ext": ".sol",
                 "description": "Solidity is an object-oriented, high-level programming language for implementing smart contracts."},
    "Julia": {"ext": ".jl",
              "description": "Julia is a high-level, high-performance dynamic programming language for technical computing."},
    "Assembly": {"ext": ".asm",
                 "description": "Assembly language is a low-level programming language for a computer or other programmable device specific to a particular computer architecture."},
    "Markdown": {"ext": ".md",
                 "description": "Markdown is a lightweight markup language with plain-text formatting syntax."},
    "YAML": {"ext": ".yaml",
             "description": "YAML (YAML Ain't Markup Language) is a human-readable data-serialization language."},
    "JSON": {"ext": ".json", "description": "JSON (JavaScript Object Notation) "},
    "XML": {"ext": ".xml",
            "description": "XML (eXtensible Markup Language) is a markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable. It is commonly used for representing structured data in web development, configuration files, and data interchange between different systems."},
    "Tcl": {"ext": ".tcl",
            "description": "Tcl (Tool Command Language) is a scripting language used for a wide range of tasks including software testing, controlling embedded systems, and rapid prototyping."},
    "VBScript": {"ext": ".vbs",
                 "description": "VBScript (Visual Basic Scripting Edition) is an active scripting language developed by Microsoft. It is modeled on Visual Basic but is simpler and less powerful."},
    "Batch": {"ext": ".bat",
              "description": "Batch file is a script file in DOS, OS/2 and Microsoft Windows. It consists of a series of commands to be executed by the command-line interpreter, stored in plain text files containing lines of text."},
}
