import time
import requests
import os
import json
from typing import Dict, List
import re

PRODUCER_ADDR=os.environ["PRODUCER_ADDR"]
session = requests.Session()
session.trust_env = False
with open("/ingest/data","r") as f:
    for line in f:
        while(True):
            try:
                res=session.post(url="http://"+PRODUCER_ADDR+"/data/push",json=json.loads(line))
                if not res.ok:
                    raise Exception(res.status_code)
                print(res.json())
                break
            except Exception as e:
                print("ERROR",e,PRODUCER_ADDR)
                print("skip")
                break