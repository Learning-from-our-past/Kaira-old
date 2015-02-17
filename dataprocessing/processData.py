# -*- coding: utf-8 -*-
from lxml import etree

import readData
from extraction.dataExtraction import DataExtraction
from extraction.extractionExceptions import *
from chunkerCheck import ChunkChecker
from exceptionlogger import ExceptionLogger
from resultcsvbuilder import ResultCsvBuilder
from errorcsvbuilder import ErrorCsvBuilder

XMLPATH = "../xmldata/"
CSVPATH = "../csv/"

class ProcessData:
    dataFilename = ""
    csvBuilder = None
    errorCsvBuilder = None
    extractor = None
    chunkerCheck = None
    errors = 0
    count = 0
    xmlDataDocument = None

    processUpdateCallbackFunction = None

    def __init__(self, callback):
        self.processUpdateCallbackFunction = callback

    #TODO: Nimeä uudestaan kuvaamaan että se palauttaa valmiin tuloksen?
    def startExtractionProcess(self, filePath):
        self._initProcess(filePath)
        self._processAllEntries()
        self._finishProcess()
        return {"errors": self.errorLogger.getErrors(), "xmlDataDocument" : self.xmlDataDocument, "file": filePath}

    def _initProcess(self, filePath):
        self.errors = 0
        self.count = 0
        self.csvBuilder = ResultCsvBuilder()
        self.csvBuilder.openCsv(filePath)
        self.errorCsvBuilder = ErrorCsvBuilder()
        self.errorCsvBuilder.openCsv(filePath)
        self.extractor = DataExtraction()
        self.chunkerCheck = ChunkChecker()
        self.errorLogger = ExceptionLogger()
        self.dataFilename = filePath
        self.xmlDataDocument = readData.getXMLroot(filePath)
        self.xmlDataDocumentLen = len(self.xmlDataDocument)
        print ("XML file elements: " + str(len(self.xmlDataDocument)))

    def _processAllEntries(self):
        i = 0
        for child in self.xmlDataDocument:
            try:
                self._processEntry(child)
            except ExtractionException as e:
                self._handleExtractionErrorLogging(exception=e, entry=child)
            i +=1
            self.processUpdateCallbackFunction(i, self.xmlDataDocumentLen)

    def _processEntry(self, entry):
        personEntryDict = self.extractor.extraction(entry.text, entry, self.errorLogger)
        self.csvBuilder.writeRow(personEntryDict)
        self.count +=1

    def _handleExtractionErrorLogging(self, exception, entry):
        self.errorLogger.logError(exception.eType, entry)
        self.errorCsvBuilder.writeRow([exception.message, exception.details, exception.eType, entry.text])
        self.errors +=1
        self.count +=1

    def _finishProcess(self):
        self._printStatistics()
        self.csvBuilder.closeCsv()
        self.errorCsvBuilder.closeCsv()

    def _printStatistics(self):
        print ("Errors encountered: " + str(self.errors) + "/" + str(self.count))
        self.errorLogger.printErrorBreakdown()

    #TODO: Muu paikka?
    def saveModificationsToFile(self):
        #write modifications to a new xml-file:
        print ("Kirjoitetaan ")
        f = open(self.dataFilename + ".xml", 'w')
        f.write(etree.tostring(self.xmlDataDocument, pretty_print=True, encoding='unicode').encode("utf8"))
        f.close()
        print ("valmis")

