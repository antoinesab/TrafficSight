# coding: utf8

import urllib.request, datetime
from bs4 import BeautifulSoup
import os, re
import psycopg2
from datetime import datetime
import DB


def main():	
	#print(DB.getAccidentPOSTGRES('2017-03-31 10:00:00.00','2017-03-31 14:00:00.00'))
	runExtractGMData()
	
def runExtractGMData():
	f = urllib.request.urlopen('http://www.infotrafic.com/route.php?link=accidents.php')
	myfile = f.read()
	#print(myfile)
	soup=BeautifulSoup(myfile,'html.parser')
	#print(soup.prettify())
	#print(type(soup.find_all('div',{"class":"central"})[0]))
	listaccidentsSOUP = soup.find_all('div',{"class":"central"})[0]
	
	nb_nouveau_evenement = 0
	
	for link in listaccidentsSOUP.find_all('p'):
		tHeader = link.find_all('b')[0].get_text()
		t=link.get_text()
		m = re.search('Début.+(\d{2}\-\d{2}\-\d{4}\s\d{2}:\d{2})', t)
		dateDebut = m.group(1)
		m2 = re.search('terminé', t)
		if m2:
			evTerminee=True
		else:
			evTerminee=False
			
		nb_nouveau_evenement += DB.insertAccidentPOSTGRES({'date_event':dateDebut,'description':t,'header' : tHeader});
		
	
	
	print('Nouveaux evenements',nb_nouveau_evenement)
	
if __name__ == '__main__':
	main()
	