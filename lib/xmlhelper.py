import os
import re
import sys
import socket
import datetime
import operator
from xml.dom import minidom

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]

class XmlWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, items):

        if items.startswith('create') and items.endswith('Tag'):
            functionName = items[len('create'):-len('Tag')]

        def wrapper(*args):
            """
            you can enter any number of Element/Text node

            createTestFooBar('toad', 'woopy') will produce:
                                                <test>
                                                    <foo>toad</foo>
                                                    <bar>woopy</bar>
                                                </test>
            """
            tagNames = re.findall('[A-Z][^A-Z]*', functionName)
            tagNames = [x.lower() for x in tagNames]
            if (len(tagNames) == len(args) +1) and (len(tagNames) > 1):
                xmlDocument = minidom.Document()
                headTag = xmlDocument.createElement(tagNames.pop(0))
                xmlDocument.appendChild(headTag)
                for index, tagName in enumerate(tagNames):
                    tagXml = xmlDocument.createElement(tagName)
                    textXml = xmlDocument.createTextNode(args[index])
                    tagXml.appendChild(textXml)
                    headTag.appendChild(tagXml)
                return headTag
        return wrapper


    def getNewestApplicationTag(self, xmlDocumentFileName):
        """

        Args
            xmlDocumentFileName:

        Returns


        """
        if os.path.exists(xmlDocumentFileName):
            xmlDocument = minidom.parse(xmlDocumentFileName)
            applicationTags = xmlDocument.getElementsByTagName("application")
            tagsDictionnary={}
            for tag in applicationTags:
                tagsDictionnary[tag.getAttribute('timestamp')] = tag
            sortedTags = sorted(tagsDictionnary.items(), key=operator.itemgetter(0))
            return sortedTags.pop()[1]
        return None


    def createOrParseXmlDocument(self, xmlDocumentFileName):
        rootXmlTag = "applications"
        if os.path.exists(xmlDocumentFileName):
            xmlDocument = minidom.parse(xmlDocumentFileName)
            if len(xmlDocument.getElementsByTagName(rootXmlTag)) == 1:
                rootTag = xmlDocument.getElementsByTagName(rootXmlTag)[0]
        else:
            xmlDocument = minidom.Document()
            rootTag = xmlDocument.createElement(rootXmlTag)
            rootTag.setAttribute("name", os.path.basename(sys.argv[0]))
            xmlDocument.appendChild(rootTag)
        return rootTag


    def createApplicationTags(self, softwareTag):
        """Utility that write into XML the <application> protocole
        """
        xmlDocument = minidom.Document()
        applicationXml = xmlDocument.createElement("application")
        applicationXml.setAttribute("timestamp", datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

        serverName = os.environ.get('TOADSERVER')
        if serverName is None:
            serverName = "local"

        applicationXml.appendChild(self.createServerHostnameToadnameUnameTag(socket.gethostname(), serverName, " ".join(os.uname())))
        applicationXml.appendChild(softwareTag)
        return applicationXml

sys.modules[__name__] = XmlWrapper(sys.modules[__name__])



