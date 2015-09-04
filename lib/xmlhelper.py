import os
import socket
import datetime
from xml.dom import minidom
__author__ = 'mathieu'


def createApplicationTags(arrayOfTuple):
    """Utility that write into XML the <application> protocole
    """

    xmlDocument = minidom.Document()

    def __createXmlTag(xmlDocument, name, text):
        xmlTag = xmlDocument.createElement(name)
        xmlText = xmlDocument.createTextNode(text)
        xmlTag.appendChild(xmlText)
        return xmlTag

    def __createServerTags(xmlDocument, hostname, toadname, uname):
        xmlSoftware = xmlDocument.createElement('server')
        xmlSoftware.appendChild(__createXmlTag(xmlDocument, "hostname", hostname))
        xmlSoftware.appendChild(__createXmlTag(xmlDocument, "toadname", toadname))
        xmlSoftware.appendChild(__createXmlTag(xmlDocument, "uname", uname))
        return xmlSoftware

    def __createSoftwareTags(xmlDocument, name, version):
        xmlSoftware = xmlDocument.createElement('software')
        xmlSoftware.appendChild(__createXmlTag(xmlDocument, "name", name))
        xmlSoftware.appendChild(__createXmlTag(xmlDocument, "version", version))
        return xmlSoftware

    applicationXml = xmlDocument.createElement("application")
    applicationXml.setAttribute("timestamp", datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    serverName = os.environ.get('TOADSERVER')
    if serverName is None:
        serverName = "local"

    applicationXml.appendChild(__createServerTags(xmlDocument, socket.gethostname(), serverName, " ".join(os.uname())))

    softwaresXml = xmlDocument.createElement("softwares")
    applicationXml.appendChild(softwaresXml)

    for (name, version) in arrayOfTuple:
        softwaresXml.appendChild(__createSoftwareTags(xmlDocument, name, version))

    return applicationXml