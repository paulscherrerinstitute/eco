import json

def loadConfig(fina):
    with open(fina,'r') as f:
        return json.load(f)

def writeConfig(fina,obj):
    with open(fina,'w') as f:
        json.dump(obj,f)
