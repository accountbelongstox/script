import random
import string
import uuid
from pycore._base import Base

class Repos(Base):
    def genepwd(self,length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        first_letter = random.choice(string.ascii_letters)
        password = first_letter + ''.join(random.choice(characters) for _ in range(length - 1))
        print(password)
        return password

    def generate_unique_id(self,):
        unique_id = str(uuid.uuid4())
        print(unique_id)
        return unique_id

    def arr_to_dict(self,array):
        result = {}
        for item in array:
            if isinstance(item,list) and len(item) > 1:
                key, val = item[0], item[1]
                result[key] = val
        return result

    def dict_to_arr(self,dictionary):
        result = []
        for key, value in dictionary.items():
            result.append([key, value])
        return result

repos = Repos()