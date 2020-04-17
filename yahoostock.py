from lxml import html  
import requests
from time import sleep
import json
from collections import OrderedDict
from bs4 import BeautifulSoup

def parse(ticker):
	 
	url = "http://finance.yahoo.com/quote/%s?p=%s"%(ticker,ticker)
	# Get request to the site
	response = requests.get(url, verify=False)
	print ("Parsing %s"%(url))
	#print(response.text)

	#soup=BeautifulSoup(response.content,'html.parser')
	#print(soup)

	sleep(4)
	parser = html.fromstring(response.text)
	#print(html.tostring(parser))

	#extracting summary-table in the parserusing xpath which is used for finding elts in xml data 
	summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
	
	#Orderd dict to store result in ordered manner
	summary_data = OrderedDict()

	other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(ticker)
	
	# another get request
	summary_json_response = requests.get(other_details_json_link)
#	print(summary_json_response.text)
	try:
	#Decodeing the response

		json_loaded_summary =  json.loads(summary_json_response.text)
		#print(json_loaded_summary)
	
			
		y_Target_Est = json_loaded_summary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"]['raw']
		#print(y_Target_Est)
			
		earnings_list = json_loaded_summary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
		#print(earnings_list)  List of earnings 
		
		eps = json_loaded_summary["quoteSummary"]["result"][0]["defaultKeyStatistics"]["trailingEps"]['raw']
		datelist = []
		#Extracting Date from taht earningslist
		for i in earnings_list['earningsDate']:
			datelist.append(i['fmt'])
		
		earnings_date = ' to '.join(datelist)
		
		
		for table_data in summary_table:
			#Extracting key value pair data

			#here lst code has class C(black) but now it is changed to $primaryColor  
			raw_table_key = table_data.xpath('.//td[contains(@class,"C($primaryColor)")]//text()')
			raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
			#converting into string
			table_key = ''.join(raw_table_key).strip()
			table_value = ''.join(raw_table_value).strip()
			#updating dictonary
			summary_data.update({table_key:table_value})

		#lastly updating the target, EPS
		summary_data.update({'1y Target Est':y_Target_Est,'EPS (TTM)':eps,'Earnings Date':earnings_date,'ticker':ticker,'url':url})
		return summary_data #returning data

	except:
		print ("Failed to parse json response")
		return {"error":"Failed to parse json response"}

if __name__=="__main__":
	#calling parse function for Appal companys information
	scraped_data=parse('aapl')
	print(scraped_data)
	#Writing the data into the json file
	print ("Writing data to output file")
	with open('aapl-summary.json','w') as fp:
		json.dump(scraped_data,fp,indent = 4)
