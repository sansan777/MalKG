import os
import re
import json
import itertools
import spacy

nlp = spacy.load("en_core_web_sm")

#Takes in raw text and uses the SpaCy sentence parser to break it down into sentences
def getSpaCySentences(text):
    sentences = []

    doc = nlp(text)

    for word in doc:
        if word.is_sent_start: #Creates a new sentences if a SpaCy thinks a word is the start of a sentence
            sentences.append([])
        if word.text.strip() != '': #Excludes words containing only whitespaces
            sentences[-1].append(word)
    return [sentence for sentence in sentences if sentence] #Excludes empty sentences

def getDocREDVertexSetFromBratAnnotations(text, annotation, sentences):
    vertexSet = []
    bratIDtoDocREDID = {}
    bratEntities = [] #{id, type, name, start, end}
    for line in annotation.splitlines(): #Process all BRAT
        if line[0] == "T": #Skips relation entries
            line = line.split("\t")
            bratEntities.append({"id": line[0], "type": line[1].split()[0].strip(), "name": line[2].strip(), "start": int(line[1].split()[1]), "end": int(line[1].split()[2])})

    bratEntities.sort(key = lambda entity: entity["start"])

    entity_id = 0
    sent_id = 0
    wordIDX = 0
    startPos = -1
    while sent_id < len(sentences) and entity_id < len(bratEntities):
        while wordIDX < len(sentences[sent_id]) and entity_id < len(bratEntities):
            if sentences[sent_id][wordIDX].idx + len(sentences[sent_id][wordIDX]) > bratEntities[entity_id]["start"] and sentences[sent_id][wordIDX].idx <= bratEntities[entity_id]["start"]:
                startPos = wordIDX
            if sentences[sent_id][wordIDX].idx + len(sentences[sent_id][wordIDX]) >= bratEntities[entity_id]["end"]:
                #Error checking which insures that the exact words containing the entity are selected
                '''
                if ''.join([word.text for word in sentences[sent_id][startPos:wordIDX + 1]]).find(bratEntities[entity_id]["name"].replace(" ", "")) == -1:
                    print("CATASTROPHIC FAILURE, named entity was not part of sentence")
                    print(''.join([word.text for word in sentences[sent_id][startPos:wordIDX + 1]]))
                    print(bratEntities[entity_id]["name"].replace(" ", ""))
                    input()

                if len(sentences[sent_id][startPos:wordIDX + 1]) > 1 and ''.join([word.text for word in sentences[sent_id][startPos + 1:wordIDX + 1]]).find(bratEntities[entity_id]["name"].replace(" ", "")) != -1:
                    print([word.text for word in sentences[sent_id][startPos:wordIDX + 1]])
                    print(bratEntities[entity_id]["name"].replace(" ", ""))
                    print("CATASTROPHIC FAILURE, captured a word before entity appears")
                    input()

                if len(sentences[sent_id][startPos:wordIDX + 1]) > 1 and ''.join([word.text for word in sentences[sent_id][startPos:wordIDX]]).find(bratEntities[entity_id]["name"].replace(" ", "")) != -1:
                    print("CATASTROPHIC FAILURE, captured a word after entity appears")
                    input()
                '''
                vertexSet.append([{
                    "name": bratEntities[entity_id]["name"],
                    "pos": [startPos, wordIDX + 1],
                    "sent_id": sent_id,
                    "type": bratEntities[entity_id]["type"]
                }])

                bratIDtoDocREDID[bratEntities[entity_id]["id"]] = entity_id

                entity_id += 1
                wordIDX = startPos
                startPos = -1
                continue
            wordIDX += 1
        if startPos != -1:
            sentences[sent_id].extend(sentences[sent_id + 1])
            del sentences[sent_id + 1]
        else:
            sent_id += 1
            wordIDX = 0

    return vertexSet, bratIDtoDocREDID

def getDocREDLabels(text, annotation, vertexSet, bratsIDtoDocREDID, relInfo):
    labels = []
    for line in annotation.splitlines():
        if line[0] != "R": #Skip entity entries
            continue

        line = line.split('\t')[1].split()

        r = list(relInfo.keys())[list(relInfo.values()).index(line[0].lower())] #Finds the relationship ID used by DocRED
        h = bratsIDtoDocREDID[line[1].split(':')[1]]
        t = bratsIDtoDocREDID[line[2].split(':')[1]]

        evidence = set()
        for vertex in itertools.chain(vertexSet[h], vertexSet[t]):
            evidence.add(vertex['sent_id'])
        evidence = sorted(evidence)

        labels.append({
            "r": r,
            "h": h,
            "t": t,
            "evidence": evidence
        })
    return labels

def getDocREDDocumentObject(textFilePath, annotationFilePath, relInfoFilePath):
    with open(textFilePath, 'r', encoding = 'utf-8') as textFile, open(annotationFilePath, 'r', encoding = 'utf-8') as annotationFile, open(relInfoFilePath, 'r', encoding = 'utf-8') as relInfoFile:
        text = textFile.read()
        annotation = annotationFile.read()
        sentences = getSpaCySentences(text)
        vertexSet, bratsIDtoDocREDID = getDocREDVertexSetFromBratAnnotations(text, annotation, sentences)
        labels = getDocREDLabels(text, annotation, vertexSet, bratsIDtoDocREDID, json.load(relInfoFile))

    #Build the Document Object
    documentObject = {
        "vertexSet": vertexSet,
        "labels": labels,
        "title": os.path.splitext(os.path.basename(os.path.normpath(textFilePath)))[0], #Uses the text file name as the title of the document
        "sents": [[word.text for word in sentence] for sentence in sentences] #Gets the text from the SpaCy Token objects
    }
    return documentObject

if __name__ == "__main__":
    documents = []
    for filename in os.listdir("input/annotations"):
        if filename[0] != '.':
            annotationFilePath = "input/annotations/" + filename
            textFilePath = "input/text/" + os.path.splitext(filename)[0] + ".txt"
            print(textFilePath)
            documents.append(getDocREDDocumentObject(textFilePath, annotationFilePath, "rel_info.json"))

    with open("../Preprocessing/annotated_data.json", 'w', encoding = 'utf-8') as file:
        json.dump(documents, file)
