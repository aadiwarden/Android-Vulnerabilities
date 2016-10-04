# coding=utf-8

import web
import os
import json
import re
from bs4 import BeautifulSoup
  
urls = (
    '/cmd_exe(.*)', 'cmd_exe',
    '/cmd2_exe(.*)', 'cmd2_exe',
    '/clear_exe(.*)','clear_exe',
    '/apk_upload', 'apk_upload',
    '/(.*)', 'hello',
)
app = web.application(urls, globals())

#RUN_COVERT = "sh /home/ubuntu/covert_dist/covert.sh bundle"
RUN_COVERT = "sh /Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/covert.sh bundle"

def did_fail():

    blocks_of_lines=""
    blocks_of_lines_hash=""
    with open('/Users/Aadi/Documents/SoftwareArchitect/Assignment4/didfail/toyapps/out/flows.out') as input_data:
    
        for line in input_data:
            if line.strip() == '--------------------':  
                break

        for line in input_data: 
            if line.strip() == '--------------------':
                break
        
            blocks_of_lines+=line
    input_data.close()
    index2 = 0
    tx = []
    rx = []
    src = []
    answer2 = []

    while "###" in blocks_of_lines:

        firstInd = blocks_of_lines.find("###");
        blocks_of_lines = blocks_of_lines[firstInd:]
        m = re.match('### (.*?): ###',blocks_of_lines)
        index = m.end()
        temp1 = (m.group()).find("tx=(")
        curGr = m.group();
        tempStr1 = (curGr)[curGr.index("tx=(") + 5:curGr.index(", None)") - 1]
        temp2 = (m.group()).find("rx=(")
        tempStr2 = (curGr)[temp2 + 5:curGr.index(", None), intent") - 1]

        temp3 = (blocks_of_lines).find("'Src:")
        tempStr3 = (blocks_of_lines)[temp3 + 7:blocks_of_lines.index(">")]

        blocks_of_lines = blocks_of_lines[index:]
        d = {
            "Transmitter" : tempStr1,
            "Receiver" : tempStr2,
            "Source" : tempStr3
        }     
        answer2.append(d)

    curPath ="/Users/Aadi/Documents/SoftwareArchitect/Assignment4/didfail/toyapps/out/"
    path, dirs, files = os.walk(curPath).next()
    cnt = 0
    eachFlow = []
    entireAns = []
    allPNames = []

    for file in files:
        if cnt != 0:
            f1 = open(curPath + file)
            soup = BeautifulSoup(f1,"xml")

            if(soup.find('results')):
                # allStr += "\n" + file

                pkgName = soup.find('results')['package']

                for theFlow in soup.find_all('flow'):
                    eachSink = theFlow.find('sink')['method']
                    eachsource = theFlow.find('source')
                    eachSrc = eachsource['method']
                    eachComp = eachsource['component']
                    d = {
                        "theSink" : eachSink,
                        "theSource" : eachSrc,
                        "theComponent" : eachComp
                    }
                    eachFlow.append(d)

                eachPackage = {
                "thePackage" : pkgName,
                "allFlows" : eachFlow
                }
                entireAns.append(eachPackage)
                allPNames.append(pkgName)

            f1.close()  
        cnt = cnt + 1

    print "=======================\n"
    
    didFailAnswer = []
    for oneAns in answer2:
        count1 = 0
        count2 = 0
        for onePack in entireAns:
            if(oneAns['Transmitter'] == onePack['thePackage']):
                curTxPack = allPNames.index(onePack['thePackage'])
                count1 = 1

            if(oneAns['Receiver'] == onePack['thePackage']):
                curRxPack = allPNames.index(onePack['thePackage'])
                count2 = 1

        ansComponent1 = ""
        ansComponent2 = ""
        if(count1 == 1 and count2 == 1):
            for oneFlow in entireAns[curTxPack]['allFlows']:
                if(oneFlow['theSource'] == "<"+oneAns['Source']+">"):
                    ansComponent1 = oneFlow['theComponent']
                    curSink = oneFlow['theSink']
                    for twoFlow in entireAns[curRxPack]['allFlows']:
                        if(curSink == twoFlow['theSink']):
                            ansComponent2 = twoFlow['theComponent']
                            break
                    d6 = {'Component1' : ansComponent1,
                            'Component2' : ansComponent2,
                            'theCommonAction' : 'Blah'}
                    didFailAnswer.append(d6)
                    break
    print "\n"
    return didFailAnswer

def first_step_covert(str,index2):
    tempStr = str
    f1 = open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/merged/" + tempStr)
    soup = BeautifulSoup(f1,"xml")
    allComponents = []
    allIntents = []
    allFilters = []
    allReceivers = []
    allSenders = []
    allPermissions = []
    for eachComponent in soup.find_all('Component'):
        temp = eachComponent.find('name').string
        allComponents.append(temp)
    for eachComponent in soup.find_all('Intent'):
        temp = eachComponent.find('action').string
        if(temp):
            temp = temp.replace("\"","")
        temp2 = eachComponent.find('sender').string
        if temp is not None:
            allIntents.append(temp)
            allSenders.append(temp2)
        if temp2 not in allComponents:
            allComponents.append(temp2)
 

    for eachComponent in soup.find_all('Component'):
        temp = eachComponent.find('name').string
        temp2 = eachComponent.find('IntentFilter')
        for eachIntentFilter in temp2.find_all('filter'):
            for eachFilterAction in eachIntentFilter.find_all('actions'):
                allFilters.append(eachFilterAction.string)
                allReceivers.append(temp)
                if temp not in allComponents:
                    allComponents.append(temp)


    for eachComponent in soup.find_all('permission'):
        allPermissions.append(eachComponent.string)

    packageName = soup.find('packageName').string                         
    d = {
        'theAppName' : packageName,
        'intentActions' : allIntents,
        'senders' : allSenders,
        'filterActions' : allFilters,
        'receivers' : allReceivers,
        'componentNames' : allComponents,
        'permissions': allPermissions
    }   
    jsonFile = json.dumps(d)


    if index2 == 0:
        f2 = open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/output.json","w+")
        f2.write(jsonFile)
        f2.close()
    else:
        f2 = open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/output.json","a")
        f2.write("\n")
        f2.write(jsonFile)
        f2.close()

    f1.close()    
    return d

def second_step_covert():    
    data = []
    with open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/output.json") as f:
        for line in f:
            data.append(json.loads(line))

    link = []
    allComponent1 = []
    allComponent2 = []
    theCommonAction = []
    answer = []

    for x in range(0,len(data)):
        temp = data[x]['intentActions']
        for x1 in range(0,len(temp)):
            curIntentAction = temp[x1]
            for y in range(0,len(data)):
                innerTemp = data[y]['filterActions']
                for y2 in range(0,len(innerTemp)):
                    curFilterAction = innerTemp[y2]
                    if(curFilterAction == curIntentAction and x != y):
                        allComponent1.append(data[x]['senders'][x1])
                        allComponent2.append(data[y]['receivers'][y2])
                        theCommonAction.append(curIntentAction)
                        d1 = {
                            'Component1' : data[x]['senders'][x1],
                            'Component2' : data[y]['receivers'][y2],
                            'theCommonAction' : curIntentAction
                        }
                        if d1 not in answer:
                            answer.append(d1)
    
    d = {
        'letsCheck' : answer
    }  
    jsonFile = json.dumps(d)
    f2 = open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/finalOutput.json","w")
    f2.write(jsonFile)
    f2.close()        
    return d;

class hello:        
    def GET(self, name):
        print "::::",name
        
        return "HELLO"



class apk_upload:        
    def GET(self, name):
        return "Use POST to upload APK"
    
    def POST(self):
        print "Recieving file.."
        x = web.input(myfile={})
        print "WORK"
        print web.debug(x['myfile'].filename) # This is the filename
        #print web.debug(x['myfile'].value) # This is the file contents
        #print web.debug(x['myfile'].file.read()) # Or use a file(-like) object
        f3 = open("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/" + x['myfile'].filename,"w")
        f3.write(x['myfile'].value)
        f3.close()
        raise web.seeother('/static/index.html')
    
class cmd_exe:
    def GET(self, name):
        # #print "Running at the moment"
        os.popen(RUN_COVERT).read() 
        allApps = []    
        allInteractions = []
        path4 = "/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/merged" 
        path5 = "/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/"
        # f2 = open(path5 + "output","w")
        # f2.close()
        path, dirs, files = os.walk(path4).next()    
        file_count = len(files)
        dirs = os.listdir(path4)
        allStr = ""
        index = 0
        for file in dirs:
            # if index != 0:
            allApps.append(first_step_covert(file,index))
            allStr += file + "!-----------"    
            index += 1

        secondRes = second_step_covert();    
        didRes = did_fail()    

        d = {
            'allApps' : allApps,
            'allInteractions' : secondRes,
            'allDidFails' : didRes
        }  
        
        return json.dumps(d)
        # return json.dumps(d);
        #return "Command executed"

class cmd_exe:
    def GET(self, name):
        #print "Running at the moment"
        os.popen(RUN_COVERT).read() 
        allApps = []    
        allInteractions = []
        path4 = "/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/merged" 
        path5 = "/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/analysis/"
        # f2 = open(path5 + "output","w")
        # f2.close()
        path, dirs, files = os.walk(path4).next()    
        file_count = len(files)
        dirs = os.listdir(path4)
        allStr = ""
        index = 0
        for file in dirs:
            # if index != 0:
            allApps.append(first_step_covert(file,index))
            allStr += file + "!-----------"    
            index += 1

        secondRes = second_step_covert();    
        didRes = did_fail()    

        d = {
            'allApps' : allApps,
            'allInteractions' : secondRes,
            'allDidFails' : didRes
        }  
        
        # return "YO"
        return json.dumps(d);
        #return "Command executed"        

class clear_exe:
    def GET(self, name):
        # os.rmdir("/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/source")
        curPath ="/Users/Aadi/Documents/SoftwareArchitect/Assignment3/covert_dist/app_repo/bundle/"
        path, dirs, files = os.walk(curPath).next()
        index = 0
        allStr = ""
        for file in files:
            # if (file != "source" and file != "analysis" and index != 0):
            if index != 0:
                allStr += "--" + file  
                os.remove(curPath + file)      
            index = index + 1
                
        # raise web.seeother('/static/index.html')    
        return allStr
        # return json.dumps(d);
        #return "Command executed        

    
        
if __name__ == "__main__":
    app.run()
