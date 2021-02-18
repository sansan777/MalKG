import os
import sys
import logging
import json
import spacy

from flair.models import SequenceTagger
from flair.data import Sentence

logging.basicConfig(
    level=logging.INFO,
    format=('[%(asctime)s] %(levelname)-8s %(message)s'),
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout),
    ]
)

flair12class = SequenceTagger.load('ner-ontonotes-fast')
nlp = spacy.load("en_core_web_sm")

def getSpaCySentences(text):
    sentences = []

    doc = nlp(text)

    for word in doc:
        if word.is_sent_start:
            sentences.append([])
        if word.text.strip() != '':
            sentences[-1].append(word)
    return [sentence for sentence in sentences if sentence]

def getDocREDVertexSetFromFlairEntities(entities, sentences):
    vertexSet = []

    entities.sort(key = lambda entity: entity["start_pos"])

    entity_id = 0
    sent_id = 0
    wordIDX = 0
    startPos = -1
    while sent_id < len(sentences) and entity_id < len(entities):
        while wordIDX < len(sentences[sent_id]) and entity_id < len(entities):
            if sentences[sent_id][wordIDX].idx + len(sentences[sent_id][wordIDX]) > entities[entity_id]["start_pos"] and sentences[sent_id][wordIDX].idx <= entities[entity_id]["start_pos"]:
                startPos = wordIDX
            if sentences[sent_id][wordIDX].idx + len(sentences[sent_id][wordIDX]) >= entities[entity_id]["end_pos"]:
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
                    "name": entities[entity_id]["text"],
                    "pos": [startPos, wordIDX + 1],
                    "sent_id": sent_id,
                    "type": entities[entity_id]["labels"][0].value
                }])

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

    return vertexSet

def flair12NER(title, text):
    s = Sentence(text)
    flair12class.predict(s)
    entities = s.to_dict(tag_type="ner")
    sentences = getSpaCySentences(entities["text"])
    vertexSet = getDocREDVertexSetFromFlairEntities(entities["entities"], sentences)
    docREDDocumentObject = {
        "vertexSet": vertexSet,
        "title": title,
        "sents": [[word.text for word in sentence] for sentence in sentences]
    }
    return docREDDocumentObject

def main():
    allDocREDDocuments = []
    for root, _, files in os.walk("Threat Reports"):
        for filename in files:
            if filename[0] != '.' and filename.lower() != "readme.txt" and os.path.splitext(filename)[1] == ".txt":
                try:
                    with open(os.path.join(root, filename), "r", encoding="windows_1252") as file:
                        text = file.read()
                except Exception as err:
                    logging.warning("Unable to open/read file '" + os.path.join(root, filename) + "' as windows_1252, attempting ISO-8859-1: " + str(err))
                    try:
                        with open(os.path.join(root, filename), "r", encoding="ISO-8859-1") as file:
                            text = file.read()
                    except Exception as err:
                        logging.error("Unable to open/read file '" + os.path.join(root, filename) + "': " + str(err))
                        continue

                logging.info("Running flair12class algorithm on '" + filename + "'...")
                try:
                    allDocREDDocuments.append(flair12NER(os.path.splitext(filename)[0], text))
                    logging.info("Completed!")
                except Exception as err:
                    logging.error("flair12class failed on '" + os.path.join(root, filename) + "': " + str(err))

    with open("../Preprocessing/threatreport_flair12_data.json", 'w') as file:
        json.dump(allDocREDDocuments, file)

if __name__ == "__main__":
    main()
