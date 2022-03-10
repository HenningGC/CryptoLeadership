import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.ticker as ticker
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import time
import numpy as np
from scipy import stats
import pandas_ta as ta

def themeSelector():
	url = 'https://coinmarketcap.com/cryptocurrency-category/'
	response = requests.get(url)
	doc = BeautifulSoup(response.text, 'html.parser')

	categories_links = doc.find_all('a',{'class':'cmc-link'})

	categories_names = []
	for link in categories_links:
		categories_names.append(link.get('href'))

	def themeFilter(category):
		if '/view/' in category:
			return True
		return False

	categories_clean = list(filter(themeFilter, categories_names))
	categories_output = [(index,element.replace('/view/','').replace('/','')) for index,element in enumerate(categories_clean)]
	
	print(categories_output)
	themeSelector = str(input('Select Theme: '))

	return themeSelector
	

def scrape_crypto(crypto, limit):

	counter = 0

	data = dict()

	for ticker in crypto:
		
		if (counter >= limit) or (counter >= len(crypto)):
			break
		print(ticker)
		req = requests.get(url='https://coinmarketcap.com/currencies/{}/'.format(ticker),headers={'user-agent':'my-app'})
		html = BeautifulSoup(req.text, 'html')

		# print(html.find_all('div',{'class':'sc-16r8icm-0 nds9rn-0 dAxhCK'}))
		stats = html.find_all('div',{'class':'sc-16r8icm-0 fmPyWa'})

		vals = [i.text for i in stats]
		if vals:
			priceValues = vals[0].split('Price')
			vals = vals[3].split('/')
		else:
			print(vals)
			exit()
		# print(vals)

		def extractPrice(values):
			for i in values:
				if '$' in i:
					return (i.replace(',','').replace('$',''))

		vals = [i for i in vals if 'Week High' in i or 'All Time' in i]
		priceValues = float(extractPrice(priceValues))
		

		for char in ('$','Week','Low','High','52  ','All','Time',','):
			vals = [i.replace(char,'') for i in vals]

		vals[-1] = vals[-1].split(' ')[0]
		vals = [i.strip(" ") for i in vals]
		vals.append(priceValues)
		try:
			vals = [float(i) for i in vals]
			data[ticker] = vals
			counter += 1
		except:
			continue

	weekLow_data = list()
	weekHigh_data = list()
	price_data = list()

	for key, value in data.items():
		weekLow_data.append(value[0])
		weekHigh_data.append(value[1])
		price_data.append(value[2])

	df = pd.DataFrame({'Symbol' : data.keys(),
					   'Price' : price_data,
                       '52 Week Low' : weekLow_data,
                       '52 Week High': weekHigh_data})

	return (df)

def VisualizeData(df):

	df['p Low'] = ((df['Price'] - df['52 Week Low']) / df['52 Week Low']) * 100
	df['p High'] = ((df['Price'] - df['52 Week High']) / df['52 Week High']) * 100

	df = df.drop(df[df['p Low'] == np.inf].index)
	# print(df['p Low'])

	fig, ax = plt.subplots(figsize=(10,6))
	ax.scatter(x = df['p Low'], y = df['p High'])

	plt.ylim(-90, 0)
	plt.xlim(0,25600)
	# plt.xlim(0,max(df['p Low']))

	# x_ticks = [0,100,300,700,1500,3100,6300,12700,25500]
	x_labels = ['1.0','2.0','4.0','8.0','16.0','32.0','64.0','128.0','256.0']


	# ax.xaxis.set_major_formatter(ticker.FixedFormatter(x_labels))

	ax.add_patch(Polygon([[0,min(df['52 Week High'])],[0,0],[700,min(df['52 Week High'])]], closed=True,fill=False))
	ax.add_patch(Polygon([[25600,-60],[90,0],[25600,0]], closed=True,fill=False))

	plt.xlabel('Gain Factor 52 Week Low')
	plt.ylabel('(%) from 52 Week High') 



	# index value
	for i, txt in enumerate(df['Symbol']):
		
		ax.annotate(txt, (df['p Low'].iloc[i], df['p High'].iloc[i]))


	plt.show()

if __name__ == '__main__':

	doTheme = str(input("Would you like to choose a theme?: ")).lower()
	url = None
	
	if doTheme in ('yes','y'):

		theme = themeSelector()
		url = 'https://coinmarketcap.com/view/'+theme

	else:	
		url = 'https://coinmarketcap.com/'

	response = requests.get(url)
	doc = BeautifulSoup(response.text, 'html.parser')

	crypto_links = doc.find_all('a',{'class':'cmc-link'})

	crypto_names = []
	for link in crypto_links:
		crypto_names.append(link.get('href'))

	crypto_names = [i for i in crypto_names if '/currencies' in i]

	for x in ('/currencies/','/markets/','/','period=7d','?'):
		crypto_names = [i.replace(x,'') for i in crypto_names]

	clean = []

	for i in crypto_names:
		if i not in clean:
			clean.append(i)

	limit = int(input('Set limit: '))

	VisualizeData(scrape_crypto(clean, limit))