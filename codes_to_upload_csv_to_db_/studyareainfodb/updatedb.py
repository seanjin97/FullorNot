import pandas as pd
import requests

baseurl = 'https://fabstudyareainfo.herokuapp.com/'
# baseurl = 'http://127.0.0.1:5000/'
def updateSA():
    df = pd.read_csv("studyareas.csv")
    url = baseurl + "updatearea/"
    l = list(df.itertuples(index=False, name=None))
    d = [dict(location_id=t[0], semantic_place=t[1], assumption = t[2], location_recode=t[3], location_id_recode=t[4], info=t[5], max_capacity=t[6]) for t in l]
    params = {"password":"boss", "data":d}
    r = requests.post(url, json = params)
    return r

updateSA()