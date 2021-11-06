import pandas as pd
import requests

def get_image_from_pixabay_api(q,lang = 'fr',printeuh = False):
    API_KEY = "23672740-cba60779b77fa0ce01dc1adc5"
    API_KEY = '14972248-16dc6a93fb1171c338a02329c'
    url = "https://pixabay.com/api/?key={}&q={}&lang={}"

    response = requests.get(url.format(API_KEY,q,lang))
    if q:
        if response.ok:

            hits = response.json()['hits']
            if printeuh:
                print("*",q)
            if len(hits) > 0:
                return hits[0]
        return None
    return None

img = get_image_from_pixabay_api("Rapide")
img

data_drii = pd.read_csv("words_swadrii.com.csv")

img_link_webformatURL = []
img_link_previewURL = []
keys_fr = data_drii["key_fr"].tolist()
for i,key_fr in enumerate(keys_fr):
    q_key_fr = key_fr.split("(")[0].split("/")[0]
    img_dict = get_image_from_pixabay_api(q_key_fr)
    if img_dict:
        img_link_webformatURL.append(img_dict["webformatURL"])
        img_link_previewURL.append(img_dict["previewURL"])
    else:
        img_link_webformatURL.append(None)
        img_link_previewURL.append(None)
    print(f"{int(round(((i + 1) * 100) / len(keys_fr), 0))}", end="%")

data_drii["img_link_webformatURL"] = img_link_webformatURL
data_drii["img_link_previewURL"] = img_link_previewURL

data_drii.to_csv("words_drii.com.csv",index=False)