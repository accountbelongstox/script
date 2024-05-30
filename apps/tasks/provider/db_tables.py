tables = [
            {
                "tabname": "duijie",
                "fixed_name": "duijie",
                "fields": {
                    "title": "TEXT",
                    "date": "TEXT",
                    "description":"TEXT",
                    "descriptionText":"TEXT",
                    "skills": "TEXT",
                    "priority": "TEXT",
                    "assignee": "TEXT",
                    "path": "TEXT",
                    "profit": "TEXT",
                    "status": "TEXT"
                }

            },

            {
                "tabname": "testou",
                "fixed_name": "testou",
                "fields": {
                    "group_n": "VARCHAR(200) UNIQUE",
                    "uid": "INTEGER",
                    "group_type": "VARCHAR(100)",
                    "language": "TEXT",
                    "count": "INTEGER",
                    "link_words": "TEXT",
                    "word_frequency": "TEXT",
                    "include_words": "TEXT",
                    "include_words_count": "INTEGER",
                    "invalid_words": "TEXT",
                    "invalid_words_count": "INTEGER",
                    "valid_words": "TEXT",
                    "valid_words_count": "INTEGER",
                    "last_time": "DATETIME",
                    "word_read": "INTEGER",
                    "origin_text": "FILE",
                    "sentence": "TEXT",
                }
            },
            {
                "tabname": "test2",
                "fixed_name": "test2",
                "fields": {
                    "test": "TEXT",
                }
            },
            {
                "tabname": "translation_group",
                "fixed_name": "translation_group",
                "fields": {
                    "group_n": "VARCHAR(200) UNIQUE",
                    "uid": "INTEGER",
                    "group_type": "VARCHAR(100)",
                    "language": "TEXT",
                    "count": "INTEGER",
                    "link_words": "TEXT",
                    "word_frequency": "TEXT",
                    "include_words": "TEXT",
                    "include_words_count": "INTEGER",
                    "invalid_words": "TEXT",
                    "invalid_words_count": "INTEGER",
                    "valid_words": "TEXT",
                    "valid_words_count": "INTEGER",
                    "last_time": "DATETIME",
                    "word_read": "INTEGER",
                    "origin_text": "FILE",
                    "sentence": "TEXT",
                }
            },
            {
                "tabname": "translation_voices",
                "fixed_name": "translation_voices",
                "fields": {
                    "group_id": "INTEGER",
                    "sentence": "TEXT",
                    "voice": "TEXT",
                    "md5": "CHAR(32) UNIQUE",
                    "link_words": "TEXT",
                    "last_time": "DATETIME",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "translation_notebook",
                "fixed_name": "translation_notebook",
                "fields": {
                    "group_id": "INTEGER",
                    "user_id": "INTEGER",
                    "word_id": "INTEGER",
                    "reference_url": "TEXT",
                    "last_time": "DATETIME",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "user",
                "fixed_name": "user",
                "fields": {
                    "user": "VARCHAR(100) UNIQUE",
                    "pwd": "VARCHAR(32)",
                    "role": "INTEGER",
                    "trans_count": "INTEGER",
                    "last_login": "TEXT",
                    "last_time": "DATETIME",
                    "register_time": "DATETIME",
                    "register_ip": "VARCHAR(32)",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "user_gtu_map",
                "fixed_name": "user_gtu_map",
                "fields": {
                    "userid": "INTEGER",
                    "group_id": "INTEGER",
                    "group_map": "TEXT",
                }
            },
            {
                "tabname": "user_gtu_haveread",
                "fixed_name": "user_gtu_haveread",
                "fields": {
                    "userid": "INTEGER",
                    "read_ids": "TEXT",
                    "read_time_day": "DATETIME",
                    "read_time": "DATETIME",
                }
            },
            {
                "tabname": "user_gtu_readcount",
                "fixed_name": "user_gtu_readcount",
                "fields": {
                    "userid": "INTEGER",
                    "read_map": "TEXT",
                }
            },
            {
                "tabname": "translation_dictionarymap",
                "fixed_name": "translation_dictionarymap",
                "fields": {
                    "wordids": "TEXT",
                    "words": "TEXT",
                    "count": "INTEGER",
                    "words_count": "INTEGER",
                    "ids_count": "INTEGER",
                }
            },
        ]