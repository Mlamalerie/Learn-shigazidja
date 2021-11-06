from secrets import DRII_USER_LOGIN,DRII_USER_PASS
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# https://www.youtube.com/playlist?list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ
PATH = "C:\Program Files\chromedriver.exe"

driver = webdriver.Chrome(PATH)


driver.get("https://swadrii.com/orelc/Users/login")
print(driver.title)

email = driver.find_element_by_id("UserEmail")
email.send_keys(DRII_USER_LOGIN)
password = driver.find_element_by_id("UserPassword")
password.send_keys(DRII_USER_PASS)

email.send_keys(Keys.RETURN)

def get_df_from_letter(letter, mode = 'fr'):
    result = []
    WORDSKEY = "FrenchWords" if mode == 'fr' else 'ShikomoriWords'
    url = "https://swadrii.com/orelc/{}/getWords/{}"
    driver.get(url.format(WORDSKEY, letter))
    soup = BeautifulSoup(str(driver.page_source), 'lxml')

    content_dad = soup.find("div", {"class": "middle_home"}).find("div", {"class": "row"})

    content = content_dad.findChildren()[0]

    divs = content.find_all("div", {"class": "v_desktop"})

    for div in divs:
        w = div.find("div", {"id": "wrapper"})
        if w:
            dict_row = {}
            first = w.find("div", {"id": "first"})

            if mode == 'fr':

                word = first.findChildren()[0].text.strip()
                word_tr = first.findChildren()[-1].text.strip()

                if len(word) > 0:
                    dict_row["key_fr"] = word
                    dict_row["key_km"] = word_tr
            else:

                word = first.findChildren()[0].text.strip()
                word_pl = first.findChildren()[-1].text.strip()

                if len(word) > 0:
                    dict_row["key_km"] = word
                    dict_row["key_fr"] = first.text[len(word) + len(word_pl) + 1:].strip()
                # print("#",,"#")

            if len(dict_row.keys()) > 0:
                dict_row["scrap_mode"] = "FR -> KM" if mode == 'fr' else "KM -> FR"
                dict_row["scrap_letter"] = letter.upper()
                result.append(dict_row)
    print(letter, len(result))
    result_df = pd.DataFrame(result)
    return result_df

print(get_df_from_letter('a'))

def clean_string_df(df):
    if len(df) > 0 :
        df["key_km"] = df["key_km"].apply(lambda x: x[:-1] if x[-1] in ['.',";"] else x)
        df["key_fr"] = df["key_fr"].apply(lambda x: x[:-1] if x[-1] in ['.',";"] else x)
    return df
# print(driver.page_source)
# driver.close() close tab

def get_all_word_from_alphabet():

    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    dfs = []

    for letter in alphabet:
        dfs.append(clean_string_df(get_df_from_letter(letter))) #fr => km
        dfs.append(clean_string_df(get_df_from_letter(letter,mode='km')))  # km => fr

    after_df_result = pd.concat(dfs,ignore_index=True).dropna()
    a = len(after_df_result)
    df_result = after_df_result.drop_duplicates(subset=['key_fr']) # drop duplication
    b = len(df_result)

    print("... Length after_df_result : ",a)
    print("... Length df_result : ",b)
    print("... Gain duplicate : ",round((a-b)*100/a,1),"%")
    return df_result.iloc[df_result.key_fr.str.lower().argsort()].reset_index(drop=True),after_df_result.iloc[after_df_result.key_fr.str.lower().argsort()].reset_index(drop=True) #sort ignoring the case


df_all_swadrii_words,after_df_all_swadrii_words = get_all_word_from_alphabet()

df_all_swadrii_words

print(after_df_all_swadrii_words.scrap_mode.value_counts())
print(df_all_swadrii_words.scrap_mode.value_counts())

df_all_swadrii_words.to_csv("words_swadrii.com_0.csv",index=False)

def get_infos_word(mot, mode='fr'):
    result = {}
    url = "https://swadrii.com/orelc/{}/viewWord/{}"
    WORDSKEY = "FrenchWords" if mode == 'fr' else 'ShikomoriWords'

    driver.get(url.format(WORDSKEY, mot.strip()))
    soup = BeautifulSoup(str(driver.page_source), 'lxml')


    a = soup.select_one(".wordDefinition")
    a_small = soup.select(".wordDefinitionSmall")
    if a:

        papa = a.findParent()
        if mode == 'fr':

            mot_type = papa.findChildren()[-2]
            result["type"] = mot_type.text.strip()

            for x in papa.findParent().findParent().findParent().find("div", {"class": "box col-xs-12"}):
                # print("#",x.text)
                val = x.text.strip().split(" ")[-1].strip()
                if len(val) > 2:
                    val = val[:-1] if val[-1] in [";"] else val
                    val = val[1:] if val[0] in ["✽", "✧", "▲"] else val
                    if "shiMaore" in x.text:
                        result["dialect_shiMaore"] = val
                    elif "shiMwali" in x.text:
                        result["dialect_shiMwali"] = val
                    elif "shiNdzuani" in x.text:
                        result["dialect_shiNdzuani"] = val
                    elif "shiNgazidja" in x.text:
                        result["dialect_shiNgazidja"] = val
                    elif "commun" in x.text:
                        result["dialect_shiMaore"] = val
                        result["dialect_shiMwali"] = val
                        result["dialect_shiNdzuani"] = val
                        result["dialect_shiNgazidja"] = val
                        result["dialect_commun"] = 1
        else:
            result["type"] = papa.findChildren()[2].text.strip().split(" ")[0]
            # for s in a_small:
            #    print("#"," ".join(s.text.strip().split(" ")[1:]).split(")")[-1])
    # print("*",result)
    return result

def update_df(df):
    d = df.to_dict('index')
    for i,(k,v) in enumerate(d.items()):
        q = v['key_fr'].split(";")[0]
        v.update(get_infos_word(q,'fr'))
        d[k] = v
        print(f"{int(round(((i+1)*100)/len(d),0))}",end="%")
    return pd.DataFrame.from_dict(d,orient='index')

df_all_swadrii_words = update_df(df_all_swadrii_words)
df_all_swadrii_words.to_csv("words_swadrii.com.csv",index=False)

print("...quit")
time.sleep(30)
driver.quit() # close driver