import json
import math
import random

nerMap = {
    "MD5": "MALWARE",
    "Indicator": "MALWARE",
    "Malware": "MALWARE",
    "Time": "DATE",
    "File": "PRODUCT",
    "Address": "MALWARE",
    "ExploitTargetObject": "PRODUCT",
    "Country": "GPE",
    "Software": "PRODUCT",
    "SHA-1": "MALWARE",
    "Organization": "ORG",
    "Campaign": "ORG",
    "Exploit": "MALWARE",
    "Attacker": "PERSON",
    "Vulnerability": "VULNERABILITY",
    "TrojanHorse": "MALWARE",
    "Email": "MALWARE",
    "MalwareCharacteristics": "MALWARECHARACTERISTICS", #UNCHANGED
    "CourseOfAction": "COURSEOFACTION", #UNCHANGED
    "Payload": "MALWARE",
    "Dropper": "MALWARE",
    "Obfuscation": "OBFUSCATION", #UNCHANGED
    "Person": "PERSON",
    "Location": "LOC",
    "SHA-256": "SHA-256", #UNCHANGED
    "SystemConfigurationInformation": "INFORMATION",
    "MalwareFamily": "MALWAREFAMILY", #UNCHANGED
    "Password": "PASSWORD", #UNCHANGED
    "Hash": "HASH", #UNCHANGED
    "SystemInformation": "INFORMATION",
    "AttackerGroup": "ORG",
    "Host": "HOST", #UNCHANGED
    "Region": "GPE",
    "Information": "INFORMATION",
    "SourceCodeInformation": "INFORMATION",
    "Account": "ACCOUNT", #UNCHANGED
    "TechnologyInformation": "INFORMATION",
    "ThreatActor": "ORG",
    "GeneralVirus": "MALWARE",
    "Vector": "VECTOR", #UNCHANGED
    "System": "SYSTEM", #UNCHANGED
    "BusinessInformation": "INFORMATION",
    "NetworkInformation": "INFORMATION",
    "UserName": "PERSON",
    "FinancialInformation": "INFORMATION",
    "Event": "EVENT",
    "AccountAuthenticationInformation": "INFORMATION",
    "UniquelyIdentifiableInformation": "INFORMATION",
    "EmailAction": "EMAILACTION", #UNCHANGED,
    "Action": "EVENT",
    "ModificationAction": "EVENT"
}

#Modify to handle max words as well
def splitDocumentByVertexCount(data, maxVertexCount):
    allDocuments = []
    for document in data:
        startSentenceID = 0
        sortedIDXToUnsortedIDX = dict(zip(range(len(document["vertexSet"])), sorted(range(len(document["vertexSet"])), key = lambda i: (document["vertexSet"][i][0]["sent_id"], document["vertexSet"][i][0]["pos"][0]))))
        unsortedIDXToSortedIDX = {unsortedIDX: sortedIDX for sortedIDX, unsortedIDX in sortedIDXToUnsortedIDX.items()}
        if "labels" in document:
            for label in document["labels"]:
                label["h"] = unsortedIDXToSortedIDX[label["h"]]
                label["t"] = unsortedIDXToSortedIDX[label["t"]]
        for i in range(math.ceil(len(document["vertexSet"])/maxVertexCount)):
            minIDX = i * maxVertexCount #Inclusive Lower Bound
            maxIDX = i * maxVertexCount + maxVertexCount #Exclusive Upper Bound
            if maxIDX >= len(document["vertexSet"]):
                maxIDX = len(document["vertexSet"])

            vertexSet = []
            for j in range(minIDX, maxIDX):
                document["vertexSet"][sortedIDXToUnsortedIDX[j]][0]["sent_id"] -= startSentenceID
                vertexSet.append(document["vertexSet"][sortedIDXToUnsortedIDX[j]])

            if "labels" in document:
                labels = []
                for label in document["labels"]:
                    if minIDX <= label["h"] and label["h"] < maxIDX and minIDX <= label["t"] and label["t"] < maxIDX:
                        label["h"] -= minIDX
                        label["t"] -= minIDX
                        labels.append(label)

            if "labels" in document:
                allDocuments.append({
                    "vertexSet": vertexSet,
                    "title": document["title"],
                    "labels": labels,
                    "sents": document["sents"][startSentenceID:startSentenceID + vertexSet[-1][0]["sent_id"] + 1]
                })
            else:
                allDocuments.append({
                    "vertexSet": vertexSet,
                    "title": document["title"],
                    "sents": document["sents"][startSentenceID:startSentenceID + vertexSet[-1][0]["sent_id"] + 1]
                })
            startSentenceID = vertexSet[-1][0]["sent_id"]
    return allDocuments

#Modifies data, but returns a reference to it as well
def vertexNameMapper(data, map):
    for document in data:
        for vertexes in document["vertexSet"]:
            for vertex in vertexes:
                vertex["type"] = map[vertex["type"]]
    return data

def splitTrainingAndValidationData(data, trainingRatio):
    random.shuffle(data)
    return data[:int(len(data) * trainingRatio)], data[int(len(data) * (1 - trainingRatio)):]

def splitDocumentList(data, maxDocuments):
    allDocuments = []
    for i in range(math.ceil(len(data)/maxDocuments)):
        minIDX = i * maxDocuments #Inclusive Lower Bound
        maxIDX = i * maxDocuments + maxDocuments #Exclusive Upper Bound
        if maxIDX >= len(data):
            maxIDX = len(data)
        allDocuments.append(data[minIDX:maxIDX])
    return allDocuments

def cleanDocumentList(data, max_length):
    return [document for document in data if sum(len(sentence) for sentence in document["sents"]) != 0 and sum(len(sentence) for sentence in document["sents"]) < max_length and len(document["vertexSet"]) >= 2]

def main():
    #Processes Training Data
    print("Processing Training Data...")
    with open("annotated_data.json", 'r') as dataFile, open("../DocRED Input/train_data.json", 'w') as trainFile, open("../DocRED Input/validate_data.json", 'w') as validateFile:
        data = json.load(dataFile)
        data = splitDocumentByVertexCount(data, 80)
        data = cleanDocumentList(data, 16384)
        data = vertexNameMapper(data, nerMap)
        trainData, validateData = splitTrainingAndValidationData(data, 0.5)
        json.dump(trainData, trainFile)
        json.dump(validateData, validateFile)
        print("document count:", len(data))
        print("vertex count:", sum(len(document["vertexSet"]) for document in data))
        print("relation count:", sum(len(document["labels"]) for document in data))
    print("Completed!")

    #Processes Flair12 Testing Data
    print("Processing Flair12 Testing Data...")
    with open("threatreport_flair12_data.json", 'r') as dataFile, open("../DocRED Input/threatreport_flair12_test_data_all.json", 'w') as testFile:
        data = json.load(dataFile)
        data = splitDocumentByVertexCount(data, 80)
        data = cleanDocumentList(data, 16384)
        json.dump(data, testFile)
        print("document count:", len(data))
        print("vertex count:", sum(len(document["vertexSet"]) for document in data))
        data = splitDocumentList(data, 256)
        for i in range(len(data)):
            json.dump(data[i], open(f"../DocRED Input/Threat Report Flair12 Data/threatreport_flair12_test_data_{i:02}.json", "w"))
    print("Completed!")

    #Processes SetExpan Testing Data
    print("Processing SetExpan Testing Data...")
    with open("threatreport_setexpan_data.json", 'r') as dataFile, open("../DocRED Input/threatreport_setexpan_test_data_all.json", 'w') as testFile:
        data = json.load(dataFile)
        data = splitDocumentByVertexCount(data, 80)
        data = cleanDocumentList(data, 16384)
        data = vertexNameMapper(data, nerMap)
        json.dump(data, testFile)
        print("document count:", len(data))
        print("vertex count:", sum(len(document["vertexSet"]) for document in data))
        data = splitDocumentList(data, 256)
        for i in range(len(data)):
            json.dump(data[i], open(f"../DocRED Input/Threat Report SetExpan Data/threatreport_setexpan_test_data_{i:02}.json", "w"))
    print("Completed!")


if __name__ == "__main__":
    main()
