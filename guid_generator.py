import uuid 

def generate_guid():
    while True:
        guid = str(uuid.uuid4().hex)
        if not guid[0].isnumeric() or guid == None or guid == "":
            return guid
            break
      