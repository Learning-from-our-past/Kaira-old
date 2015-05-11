# -*- coding: utf-8 -*-
import ntpath
import csv
import json
from abc import abstractmethod
from books.karelians.extractionkeys import KEYS
from interface.valuewrapper import ValueWrapper
from interface.csvbuilderinterface import ResultCsvBuilderInterface

class ResultCsvBuilder(ResultCsvBuilderInterface):

    #TODO: POISTA SISÄISEN TOTETUKSEN FUNKTIOT SILLÄ NE VOIVAT VAPAASTI VAIHDELLA
    def __init__(self):
        pass

    @abstractmethod
    def openCsv(self, filepath):
        self.filepath = filepath
        self.filename = ntpath.basename(self.filepath)
        self._initCsv()
        self.karelianLocationsMax = 0
        self.childrenMax = 0
        self.otherLocationsMax = 0
        self.rowsofcsv = []


    def _initCsv(self):
        self.openedCsv = open(self.filepath, "w", newline='', encoding="utf-8")
        self.csvWriter = csv.writer(self.openedCsv, delimiter="&")


    def _writeCsvHeaders(self):
        headers = ["Surname", "first names", "original family", "birthday", "birthMonth", "birthYear", "birthLocation", "profession/status", "omakotitalo", "imagepath", "returnedToKarelia", "hasSpouse", "spouseName", "spouseOrigFamily", "spouseProfession", "spouseBirthday", "spouseBirthMonth", "spouseBirthYear", "spouseBirthLocation" ]

        headers = headers + ["ChildCount"]
        for i in range(0, self.childrenMax):
            headers = headers + ["Child" + str(i), "ChildBirthYear" + str(i), "childBirthLocation" + str(i), "childBirthLatitude" + str(i), "childBirthLongitude" + str(i)]


        headers = headers + [KEYS["karelianlocationsCount"]]
        for i in range(0, self.karelianLocationsMax):
            headers = headers + ["karelianLocation" + str(i), "movedIn" + str(i), "movedOut" + str(i), "latitude" + str(i), "longitude" + str(i)]

        headers = headers + [KEYS["otherlocationsCount"]]
        for i in range(0, self.otherLocationsMax):
            headers = headers + ["otherLocation" + str(i), "movedIn" + str(i), "movedOut" + str(i), "latitude" + str(i), "longitude" + str(i)]
        self.csvWriter.writerow(headers)

    def writeRow(self, dataDict):
        self.rowsofcsv.append(self._createRowFromDict(dataDict))

    def _unwrap(self, data):
        """
        A recursive function to unwrap all the ValueWrappers and return a pure dict from them.
        :param valuewrap:
        :return:
        """
        if isinstance(data, ValueWrapper):
            if isinstance(data.value, dict):
                result = {}
                for key, value in data.value.items():
                    result[key] = self._unwrap(value)
            elif isinstance(data.value, list):
                result = []
                for index, value in enumerate(data.value):
                    result.append(self._unwrap(value))
            else:
                return data.value   #primitive data structure
        else:
            return data

        return result






    #make a dict of row content divided based on the content
    def _createRowFromDict(self, persondatadict):
        row = {"regular" : [persondatadict[KEYS["surname"]].value, persondatadict[KEYS["firstnames"]].value,
               persondatadict[KEYS["origfamily"]].value, persondatadict[KEYS["birthDay"]].value,
               persondatadict[KEYS["birthMonth"]].value, persondatadict[KEYS["birthYear"]].value,
               persondatadict[KEYS["birthLocation"]].value, persondatadict[KEYS["profession"]].value,
               persondatadict[KEYS["omakotitalo"]].value, persondatadict[KEYS["imagepath"]].value,
               persondatadict[KEYS["returnedkarelia"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["hasSpouse"]].value, persondatadict[KEYS["spouse"]].value[KEYS["spouseName"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseOrigFamily"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseProfession"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseBirthData"]].value[KEYS["birthDay"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseBirthData"]].value[KEYS["birthMonth"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseBirthData"]].value[KEYS["birthYear"]].value,
               persondatadict[KEYS["spouse"]].value[KEYS["spouseBirthData"]].value[KEYS["birthLocation"]].value,

               ] }
        row["children"] = self._addChildren(persondatadict)
        row["karelianLocations"] = self._addKarelianLocations(persondatadict)
        row["otherLocations"] = self._addOtherLocations(persondatadict)

        return row


    def _addChildren(self, persondatadict):
        lrow = []
        children = persondatadict[KEYS["children"]].value

        #childcount
        lrow.append(persondatadict[KEYS["childCount"]].value)

        if len(children) > self.childrenMax:
            self.childrenMax = len(children)

        for l in children:
            lrow.append(l.value["name"].value) #name of the child
            lrow.append(l.value["birthYear"].value) #child's birthYear
            lrow.append(l.value["locationName"].value) #birthplace
            lrow.append(l.value["childCoordinates"].value["latitude"].value) #latitude
            lrow.append(l.value["childCoordinates"].value["longitude"].value) #latitude




        return lrow




    def _addKarelianLocations(self, persondatadict):
        lrow = []
        locations = persondatadict[KEYS["karelianlocations"]].value

        #location count
        lrow.append(persondatadict[KEYS["karelianlocationsCount"]].value)

        if len(locations) > self.karelianLocationsMax:
            self.karelianLocationsMax = len(locations)

        for l in locations:
            lrow.append(l.value[KEYS["karelianlocation"]].value) #name of the place
            lrow.append(l.value["movedIn"].value) #year when moved in
            lrow.append(l.value["movedOut"].value) #year when moved out
            lrow.append(l.value[KEYS["kareliancoordinate"]].value["latitude"].value) #latitude
            lrow.append(l.value[KEYS["kareliancoordinate"]].value["longitude"].value) #latitude



        return lrow

    def _addOtherLocations(self, persondatadict):
        lrow = []
        locations = persondatadict[KEYS["otherlocations"]].value

        #location count
        lrow.append(persondatadict[KEYS["otherlocationsCount"]].value)

        if len(locations) > self.otherLocationsMax:
            self.otherLocationsMax = len(locations)

        for l in locations:
            lrow.append(l.value[KEYS["otherlocation"]].value) #name of the place
            lrow.append(l.value["movedIn"].value) #year when moved in
            lrow.append(l.value["movedOut"].value) #year when moved out
            lrow.append(l.value[KEYS["othercoordinate"]].value["latitude"].value) #latitude
            lrow.append(l.value[KEYS["othercoordinate"]].value["longitude"].value) #latitude


        return lrow


    def _writeToFile(self):
        self._writeCsvHeaders()
        for row in self.rowsofcsv:

            w = row["regular"] + row["children"]
            diff = self.childrenMax*5 - len(row["children"]) +1   #1 for childrencount column
            if diff > 0:            #tasaa rivit lisäämällä tyhjää
                w = w + [""]*diff #5 is the number of cells per location

            w = w + row["karelianLocations"]
            diff = self.karelianLocationsMax*5 - len(row["karelianLocations"]) +1   #1 for locationcount column
            if diff > 0:            #tasaa rivit lisäämällä tyhjää
                w = w + [""]*diff

            w = w + row["otherLocations"]
            diff = self.otherLocationsMax*5 - len(row["otherLocations"]) +1 #1 for locationcount column
            if diff > 0:            #tasaa rivit lisäämällä tyhjää
                w = w + [""]*diff
            self.csvWriter.writerow(w)

    @abstractmethod
    def closeCsv(self):
        self._writeToFile()
        self.openedCsv.close()
        self.openedCsv = None