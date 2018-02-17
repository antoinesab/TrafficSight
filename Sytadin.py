import urllib.request, datetime
from PIL import Image
import os, re
import psycopg2
from datetime import datetime
import DB

PIXEL_PER_KM = 40.8
AVG_DETECTED_KM = 49000

def main():	
	nowDT = datetime.now()
	
	#On enrengistre de 5h du matin à minuit
	if nowDT.hour >= 5:
		createDAYRepositoryIFNOTEXISTS(nowDT)
		runExtractGMData()
		lastImage=getOldedImage()
		pathImage=removeImageToDayRepository(lastImage['filename'],str(nowDT.date()))
		resTraffic=analyseTrafficImage(pathImage)
		DB.insertTrafficPOSTGRES({
			'filename':"'"+pathImage+"'",
			'road_value_lvl_1':resTraffic['road_value_lvl_1'],
			'road_value_lvl_2':resTraffic['road_value_lvl_2'],
			'road_value_lvl_3':resTraffic['road_value_lvl_3'],
			'road_value_lvl_4':resTraffic['road_value_lvl_4'],
			'date_raw':lastImage['dateRaw']
		});
		print('DONE',str(nowDT))

	
def runExtractGMData():
	os.system("phantomjs GM_DATA_EXTRACT.js")

	
#Return path new image(after remove)
def removeImageToDayRepository(filename,date):
	os.rename('StImages/'+filename,'StImages/'+ date +'/'+filename)
	return 'StImages/'+ date +'/'+filename
	
#Filename in the good path(need to class every images within the right repository)
def analyseTrafficImage(filename):
	im = Image.open(filename)
	pix = im.load()

	nbX=im.size[0];
	nbY=im.size[1];
	
	pixelsBouchons=0
	pixelsGrosBouchons=0
	pixelsFluide=0
	pixelsIntermediaire=0

	for i in range(0, nbX-1):
		for j in range(0,nbY-1):
			if(pix[i,j][0] > 235 and pix[i,j][0] < 250 and pix[i,j][1] < 70 and pix[i,j][1] > 55 and pix[i,j][2] < 55 and pix[i,j][2] > 45):
				pixelsBouchons=pixelsBouchons+1
			if(pix[i,j][0] > 95 and pix[i,j][0] < 105 and pix[i,j][1] < 220 and pix[i,j][1] > 205 and pix[i,j][2] < 110 and pix[i,j][2] > 100):
				pixelsFluide=pixelsFluide+1
			if(pix[i,j][0] > 250 and pix[i,j][0] < 256 and pix[i,j][1] < 160 and pix[i,j][1] > 145 and pix[i,j][2] < 80 and pix[i,j][2] > 75):
				pixelsIntermediaire=pixelsIntermediaire+1
			if(pix[i,j][0] > 125 and pix[i,j][0] < 135 and pix[i,j][1] < 32 and pix[i,j][1] > 27 and pix[i,j][2] < 32 and pix[i,j][2] > 27 ):
				pixelsGrosBouchons=pixelsGrosBouchons+1

	
	print('Gros bouchons',pixelsGrosBouchons);
	print('bouchons',pixelsBouchons);
	print('Ralentissements',pixelsIntermediaire);
	print('Fluide',pixelsFluide);
	print('Totale route analysé',pixelsGrosBouchons+pixelsBouchons+pixelsIntermediaire+pixelsFluide)
	
	return {
		'road_value_lvl_1':pixelsFluide,
		'road_value_lvl_2':pixelsIntermediaire,
		'road_value_lvl_3':pixelsBouchons,
		'road_value_lvl_4':pixelsGrosBouchons,
	}
	
#return dict: filename:str , dateRaw:int
def getOldedImage():
	allFiles=os.listdir('StImages')
	allFilesWithDates=list()
	maxDate=0
	maxIndex=0
	
	for i,k in enumerate(allFiles):
		m = re.search('\d+',k)
		d=int(m.group(0))

		if d > maxDate:
			maxDate=d
			maxIndex=i
		allFilesWithDates.append({'filename':k,'dateRaw':d})
		
	return allFilesWithDates[maxIndex]
	
#dt: datetime 
def createDAYRepositoryIFNOTEXISTS(dt):
	nowDT = datetime

	if os.path.isdir('StImages/'+str(dt.date())):
		return 0
	else:
		print('--Creating new directory',str(dt.date()))
		os.mkdir("StImages/"+str(dt.date()))
		return 1
		
# 
#
def scalePixelToKm(pix):
	return pix / PIXEL_PER_KM
	
# 
#
def normalizeKM(totalKM,KM):
	try:
		a=float(AVG_DETECTED_KM)/float(totalKM)
		return KM * a
	except:
		return 0

	
# listCourbes un dico d'element de type array
# abscisse un array
def lisageCourbe(listCourbes,abscisse):

	
	for key,valeurs in enumerate(listCourbes):
		#valeurs=[5,8,6,9,5,7,9,12,16,18,1,7,20,15,9,10,8,6,3,4,2,2,3,1]
		#abscisse = range(0,30)
		
		nbPoints = math.floor(len(valeurs)/2)
		valeursBis = [0] * nbPoints
		tempsBis = [0] * nbPoints
		i = 0
		j = 0
		while i<len(valeurs)-1 :
			valeursBis[j] = int((valeurs[i] + valeurs[i+1])/2)
			tempsBis[j] = int((abscisse[i] + abscisse[i+1])/2)
			j = j + 1
			i = i + 2
			
		#print(valeursBis)
		#print(tempsBis)
		#
		#print(valeurs)
		#print(temps)

	
if __name__ == '__main__':
	main()
	