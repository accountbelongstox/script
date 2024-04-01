class Encyclopedia:
    encyclopedia = {}

    def setEncyclopedia(self, obj):
        for key in obj:
            self.encyclopedia[key] = obj[key]

    def getEncyclopedia(self, key=None):
        if key:
            return self.encyclopedia[key]
        return self.encyclopedia

    def setEncyclopediaByKey(self, key, val):
        if key and val:
            self.encyclopedia[key] = val


encyclopedia = Encyclopedia()
