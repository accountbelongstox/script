from pycore.base.base import Base
import xml.dom.minidom
#import xml.etree.ElementTree as etree
class Xml(Base):
    def __init__(self,args):
        pass

    def from_string(self,string):
        if type(self) == str:url = self
        return xml.dom.minidom.parseString(string)


    def find_all(self,doc,string):
        #doc = self.from_string()
        contents = doc.getElementsByTagName(string)
        nodes = []
        for content in contents:
            for node in content.childNodes:
                if(node.nodeType == node.TEXT_NODE):
                    nodes.append( node.data )
        return nodes