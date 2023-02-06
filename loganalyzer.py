import sys
import zipfile
import re
import json
import xlsxwriter

startingPhrase = ["tag: 'eID Result',", "tag: 'Re-Scan eID Result',"]
falsephrase = "securityChecks: \'{\"untamperedDocument\":{\"name\":\"Untampered Document\",\"passed\":false}"
truephrase = "securityChecks: \'{\"untamperedDocument\":{\"name\":\"Untampered Document\",\"passed\":true}"
endLine = "endLine"

def checkIfZipFileIsInArgument():
    if len(sys.argv) < 2:
        print("Please give a zip file to extract")
        quit()

def isZipFile():
    return zipfile.is_zipfile()

def extractZip():
    try:
        with zipfile.ZipFile(sys.argv[1], "r") as logZip:
            logZip.extractall("./LogAnalyzer/LogFiles/")
            return logZip.namelist()
    except:
        print("Error Occured")
        return []

def readLogFile(fileName):
    with open("./LogAnalyzer/LogFiles/" + fileName) as file:
        f = file.readlines()

    result = []
    textBlock = ""
    for line in f:
        if any(s in line for s in startingPhrase):
            textBlock += "{\n"
        elif textBlock != "":
            analyzeResult = analyseLineAfterStartingTextBlock(line)
            if analyzeResult == "" :
                textBlock = ""
            elif analyzeResult == endLine :
                data = removeUnNecessaryChars(line, 33, len(line))
                data = removeUnNecessaryChars(data, 0, 86)
                # textBlock += convertToJsonFormat(data) + "\"}\",\n}\n}"
                textBlock += "\n }\n}"
                result.append(textBlock + "\n")
                textBlock = ""
                # print(result)
            else:
                try:
                    textBlock += prepareToAddObjectFields(line)
                except Exception as e:
                    print()
                    print("Converting to JSON error")
                    print(e)
    return result

def prepareToAddObjectFields(line):
    removedChars = removeUnNecessaryChars(line, 33, len(line))
    finalText = removeCommaFromLastLine(removedChars)
    return convertToJsonFormat(finalText)


def removeCommaFromLastLine(line):
    if "dob" in line:
        return line[:-2]
    else:
        return line

def readMultipleLogFiles(nameList):
    result = []
    for file in nameList:
        try:
            data = readLogFile(file)
            for log in data:
                result.append(converToJson(log))

        except Exception as e:
            print("Json Error")
            print(e)
    createExcel(result)
    # print(result)

def createExcel(resultList):
    workbook = xlsxwriter.Workbook('./LogAnalyzer/Excel/1_2_2023.xlsx')
    worksheet = workbook.add_worksheet()
    counter = 2

    worksheet.write('A1', 'VideoID')
    worksheet.write('B1', 'Country')
    worksheet.write('C1', 'Name')
    worksheet.write('D1', 'IdNo')
    worksheet.write('E1', 'MSISDN')

    for log in resultList :
        data = log['info']
        worksheet.write('A' + str(counter), data['videoID'])
        worksheet.write('B' + str(counter), data['country'])
        worksheet.write('C' + str(counter), data['name'])
        worksheet.write('D' + str(counter), data['idNo'])
        counter = counter + 1

    workbook.close()

def converToJson(text):
    return json.loads(text)

def convertToJsonFormat(line):
    line = replaceFirstTwoWhiteSpace(line)
    line = "\"" + line
    if line.index(':') > -1:
        line = line[:line.index(':')] + "\"" + line[line.index(':'):]
    line = line.replace("\'", "\"")
    return line
    
def replaceFirstTwoWhiteSpace(line):
    if "info:" not in line: 
        return line[2:len(line)]
    else:
        return line

def removeUnNecessaryChars(line, start, end):
    # return re.sub("\(\d{1,2}\/\d{1,2}\/\d{1,2}\)","", line)
    return line[start:end]

def analyseLineAfterStartingTextBlock(line):
    if truephrase in line:
        return ""
    elif falsephrase in line:
        return endLine
    else:
        return "nextLine"

def extractAndReadLogFiles():
    fileNameList = extractZip() #extract Zip file and get the file names after unzipping
    if len(fileNameList) > 0: 
        readMultipleLogFiles(fileNameList) 
    else:
        print("Maybe your zip is empty or not sure what happened but there is an error")

def main():
    checkIfZipFileIsInArgument()
    if (isZipFile):
        extractAndReadLogFiles() 
    else:
        print("Needed a zipfile")
            
main()