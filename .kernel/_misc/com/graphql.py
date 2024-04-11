from pycore.base.base import *
import requests
import json


class Graphql(Base):
    def __init__(self,args):
        self.localstore_namespace = "dictThousandDaysOfDict"
        self.apiUrl = "https://api.local.12gm.com:888/graphql"
        self.com_module = "com_dictionary"
        self.qurest_key = "9LrQN0~14,dSmoO^"
        self.base_remote_url = ""

    def remote_resourceurl(self, suffix):
        return f"{self.get_remove_url()}/static/{suffix}"

    def sendGraphQLNotAuto(self, query, variables={}):
        return self.sendGraphQLAuth(query, variables, False)

    def sendGraphQLAuth(self, query, variables={}, auth=True):
        body = {
            "query": query,
            "variables": variables
        }
        headers = {
            "Content-Type": "application/json"
        }
        if auth:
            jwt = self.useJWT()
            headers["Authorization"] = f"Bearer {jwt}"
        response = requests.post(self.apiUrl, headers=headers, data=json.dumps(body))
        if response.status_code != 200:
            print("error", response.text)
            return {}

    def queryNotTranslate(self, ):
        valid_condition = "{ translation: { eq: {} } },"
        query = f"""
            query GetDictionaries( $pagination: PaginationArg) {{
                dictionaries(
                    filters: {{
                        and: [
                            {valid_condition}
                        ]
                    }},
                    pagination: $pagination
                ) {{
                    data {{
                        id
                        attributes {{
                            word
                            is_delete
                            word_sort
                            phonetic_us
                            phonetic_us_sort
                            phonetic_us_length
                            phonetic_uk
                            phonetic_uk_sort
                            phonetic_uk_length
                            word_length
                            translation
                        }}
                    }}
                }}
            }}
        """
        pagination = {
            "limit": 1000
        }
        variables = {
            "pagination": pagination
        }
        print(query)
        print(variables)
        data = self.sendGraphQLNotAuto(query, variables)
        return data
