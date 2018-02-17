import urllib.request, datetime
from PIL import Image
import os, re, time
import psycopg2
from datetime import datetime
import DB
import math



PIXEL_PER_KM = 40.8
AVG_DETECTED_KM = 49000

def main():	

	print("hello")
	#a=datetime.today().replace(hour=5,minute=12,second=0)
	#print(a)
	n=datetime.now().hour
	print(n)
	#dStart = datetime.strptime( "2017-03-25T00:00:00", "%Y-%m-%dT%H:%M:%S" )
	#dEnd = datetime.strptime( "2017-03-25T22:08:12", "%Y-%m-%dT%H:%M:%S" )
	#result=DB.getTrafficPOSTGRES(dStart,dEnd)
	#print(result)
	#d = datetime.now()
	#a = int(time.time() * 1000)
	#print(datetime.utcnow().timetuple())
	#print(time.mktime(datetime.utcnow().timetuple()))
	#print(int(time.mktime(datetime.utcnow().timetuple()) * 1000))
#	resTraffic=analyseTrafficImage('test.png')
	
	
def runExtractGMData():
	os.system("phantomjs.exe GM_DATA_EXTRACT.js")
	

	
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
			if(pix[i,j][0] > 220 and pix[i,j][0] < 240 and pix[i,j][1] < 10 and pix[i,j][2] < 10):
				pixelsBouchons=pixelsBouchons+1
			if(pix[i,j][0] > 125 and pix[i,j][0] < 140 and pix[i,j][1] < 210 and pix[i,j][1] > 195 and pix[i,j][2] < 85 and pix[i,j][2] > 75):
				pixelsFluide=pixelsFluide+1
			if(pix[i,j][0] > 235 and pix[i,j][0] < 250 and pix[i,j][1] < 130 and pix[i,j][1] > 115 and pix[i,j][2] < 10 and pix[i,j][2] > 0):
				pixelsIntermediaire=pixelsIntermediaire+1
			if(pix[i,j][0] > 150 and pix[i,j][0] < 165 and pix[i,j][1] < 25 and pix[i,j][1] > 15 and pix[i,j][2] < 25 and pix[i,j][2] > 15):
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
	

# 
#
def scalePixelToKm(pix):
	return pix / PIXEL_PER_KM
	
# 
#
def normalizeKM(totalKM,KM):
	a=float(AVG_DETECTED_KM)/float(totalKM)
	return KM * a
	
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
	
def insertTrafficPOSTGRES(obj):
	try:
		conn = psycopg2.connect("dbname='Sytadin' user='Sytadin_user' host='localhost' password='admin123'")
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database')
		return 0;
		
	obj['id']=1
	
	cur = conn.cursor()
	qry=""" SELECT max("id_Traffic") FROM public."Traffic"; """
	try:
		cur.execute(qry)
	except:
		print('--Erreur DB')
		print(cur.query)
	rows = cur.fetchall()
	if len(rows) > 0 and rows[0][0] is not None:
		obj['id']=rows[0][0]+1

	cstrParameters=','.join([
		obj['filename'],
		str(obj['id']),
		str(obj['road_value_lvl_1']),
		str(obj['road_value_lvl_2']),
		str(obj['road_value_lvl_3']),
		str(obj['road_value_lvl_4']),
		str(obj['date_raw'])
	])
	try:
		cur2 = conn.cursor()
		cur2.execute("""INSERT INTO public."Traffic"("filename_Image", "id_Traffic", road_value_lvl_1, road_value_lvl_2, road_value_lvl_3, road_value_lvl_4, date_raw)
	VALUES (%(filename)s,%(id)s,%(road_value_lvl_1)s,%(road_value_lvl_2)s,%(road_value_lvl_3)s,%(road_value_lvl_4)s,%(date_raw)s);""",obj)
	except:
		print('--Erreur DB')
		print(cur2.query)
		
#dt: datetime 
def createDAYRepositoryIFNOTEXISTS(dt):
	nowDT = datetime

	if os.path.isdir('StImages/'+str(dt.date())):
		return 0
	else:
		print('--Creating new directory',str(dt.date()))
		os.mkdir("StImages/"+str(dt.date()))
		return 1

	
if __name__ == '__main__':
	main()
	