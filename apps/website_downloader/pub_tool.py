
class tools:
    @staticmethod
    def recursive_traversal( obj, unique_set):
        if isinstance(obj, (list, tuple)):
            for item in obj:
                tools.recursive_traversal(item, unique_set)
        elif isinstance(obj, dict):
            for value in obj.values():
                tools.recursive_traversal(value, unique_set)
        else:
            unique_set.add(obj)
        return unique_set


    @staticmethod
    def decode( content):
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
                return content
            except Exception as e:
                print(f"Error decode: {str(e)}")
                return None
        return content
