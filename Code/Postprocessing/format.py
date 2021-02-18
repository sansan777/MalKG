import os
import json
import csv

def getCSVLine(triple, data, id2Relation):
    fileName = triple["title"]
    relationType = id2Relation[triple["r"]]

    document = data[triple["index"]]
    entityOneMention = document["vertexSet"][triple["h_idx"]][0]["name"]
    entityOneType = document["vertexSet"][triple["h_idx"]][0]["type"]

    entityTwoMention = document["vertexSet"][triple["t_idx"]][0]["name"]
    entityTwoType = document["vertexSet"][triple["t_idx"]][0]["type"]

    begin, end = document["vertexSet"][triple["h_idx"]][0]["sent_id"], document["vertexSet"][triple["t_idx"]][0]["sent_id"]
    if begin > end:
        tmp = end
        end = begin
        begin = tmp

    context = ""
    for i in range(begin, end + 1):
        for word in document["sents"][i]:
            context += word + ' '

    return [fileName, relationType, entityOneMention, entityOneType, entityTwoMention, entityTwoType, context]

#Each directory is expected to contain the folders triples, data set, and csvs. The triples folder should contain DocRED output, and the
#data set folder should hold the JSON files used to test DocRED. Pairs of these files should end with _identifier, where the identifiers
#indicate which test file produced which triple file.
def convertDirectoryToCSV(directoryName):
    with open("rel_info.json", 'r') as id2RelationFile:
        id2Relation = json.load(id2RelationFile)
    owd = os.getcwd()
    os.chdir(directoryName)
    for tripleFilename in os.listdir("triples/"):
        if tripleFilename[0] != '.':
            identifier = os.path.splitext(tripleFilename)[0].split('_')[-1]
            datafilename = None
            for filename in os.listdir("data set/"):
                if identifier == os.path.splitext(filename)[0].split('_')[-1]:
                    datafilename = filename
                    break
            with open(os.path.join("triples/", tripleFilename), 'r', encoding = "utf-8") as triplesFile, open(os.path.join("data set/", datafilename), 'r', encoding = "utf-8") as dataFile, open("csvs/" + os.path.splitext(tripleFilename)[0] + ".csv", 'w', encoding = "utf-8") as csvfile:
                triples = json.load(triplesFile)
                data = json.load(dataFile)
                csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csvwriter.writerow(["FileName","RelationType","Entity1Mention","Entity1Type","Entity2Mention","Entity2Type","Context"])
                for triple in triples:
                    csvwriter.writerow(getCSVLine(triple, data, id2Relation))
    os.chdir(owd)

def combineFiles(inputDirectoryPath, outputFilePath):
    with open(outputFilePath, 'w', encoding = "ISO-8859-1") as outputfile:
        for inputfile in os.listdir(inputDirectoryPath):
            if inputfile[0] != '.':
                outputfile.write(open(os.path.join(inputDirectoryPath, inputfile), 'r', encoding = "ISO-8859-1").read())

def main():
    print("Processing Flair12 Triples...")
    convertDirectoryToCSV("Threat Reports Flair12 Data")
    combineFiles("Threat Reports Flair12 Data/csvs", "../../Results/threatreports_flair12_triple_data.csv")
    print("Completed!")
    print("Processing SetExpan Triples...")
    convertDirectoryToCSV("Threat Reports SetExpan Data")
    combineFiles("Threat Reports SetExpan Data/csvs", "../../Results/threatreports_setexpan_triple_data.csv")
    print("Completed!")

if __name__ == "__main__":
    main()
