
import requests
import json
import bs4
import pandas as pd
import xlwings as xw
from time import sleep
from datetime import datetime
import os


excel='open_chain.xlsx'
wb=xw.Book(excel)
ws = wb.sheets[0]
ws.name = "CE"

pd.set_option('display.width',1500)
pd.set_option('display.max_columns',75)
pd.set_option('display.max_rows',1500)

df_list=[]

url="https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

expiray="25-Jun-2020"


oi_filename=os.path.join("Files","Data_{}.json".format(datetime.now().strftime("%d%m%y")))



def fetch(df):

    tries=0

    while tries<4:
        headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                    'Accept-Language':'en-US,en;q=0.9','Accept-Encoding':'gzip, deflate, br'}

        r=requests.get(url,headers=headers).json()
        print(r)
        with open('records.json','w') as F:
            F.write(json.dumps(r,indent=4))

        CE=[d['CE'] for d in r['records']['data'] if 'CE' in d and str(d['expiryDate']).lower()==str(expiray).lower()]
        PE=[d['PE'] for d in r['records']['data'] if 'PE' in d and str(d['expiryDate']).lower()==str(expiray).lower()]
        
        with open('r.json','w') as F:
            F.write(json.dumps(PE,indent=4)) 
        Cd=pd.DataFrame(CE)
        Pd=pd.DataFrame(PE)

        
        Cd=Cd.sort_values(['strikePrice'])
        Pd=Pd.sort_values(['strikePrice'])
        print(Cd)
        
        
        ws.range('A1').options(index=False).value=Cd.drop(["expiryDate","underlying","identifier","totalTradedVolume","totalBuyQuantity","totalSellQuantity",
            "bidQty",
            "bidprice",
            "askQty",
            "askPrice",
            "underlyingValue",
            ],axis=1)[['openInterest','changeinOpenInterest',
        'pchangeinOpenInterest','impliedVolatility','lastPrice','change','pChange','strikePrice']]
        
        ws.range('I1').options(index=False).value=Pd.drop(["expiryDate","underlying","identifier","totalTradedVolume","totalBuyQuantity","totalSellQuantity",
            "bidQty",
            "bidprice",
            "askQty",
            "askPrice",
            "underlyingValue",
            ],axis=1)[['strikePrice','openInterest','changeinOpenInterest',
        'pchangeinOpenInterest','impliedVolatility','lastPrice','change','pChange']]

        Cd['type']='CE'
        Pd['type']='PE'

        df1=pd.concat([Cd,Pd])
        print(df1.head())
        if len(df_list)>0:
            df1['Time']=df_list[-1][0]['Time']
        if len(df_list)>0 and df1.to_dict('records')==df_list[-1]:
            print("Duplicate data..")
            sleep(10)
            tries+=1
            continue

        df1['Time']=datetime.now().strftime("%H:%M")


        df=pd.concat([df,df1])
        df_list.append(df1.to_dict('records'))
        with open(oi_filename,'w+') as file:
            file.write(json.dumps(df_list,indent=4,sort_keys=True))
        return df 

if __name__ == "__main__":
    print("Vk")

    try:
        print(oi_filename)
        #df_list=json.loads(open(oi_filename,'r').read())
    except Exception as error:
        print('Error Reading Data...bcoz\n',error)
    if df_list:
        df=pd.DataFrame()
        for i in df_list:
            df=pd.concat([df,pd.DataFrame(i)])
    else:
        df=pd.DataFrame()


    fetch(df)