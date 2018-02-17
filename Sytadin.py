import urllib.request, datetime
from PIL import Image
import os, re
import psycopg2
from datetime import datetime
import DB


def main():	
	
	nowDT = datetime.now()
	createDAYRepositoryIFNOTEXISTS(nowDT)
	
	
	
	runExtractGMData()
	lastImage=getOldedImage()
	pathImage=removeImageToDayRepository(lastImage['filename'],str(nowDT.date()))
	resTraffic=analyseTrafficImage(pathImage)
	insertTrafficPOSTGRES({
		'filename':"'"+pathImage+"'",
		'road_value_lvl_1':resTraffic['road_value_lvl_1'],
		'road_value_lvl_2':resTraffic['road_value_lvl_2'],
		'road_value_lvl_3':resTraffic['road_value_lvl_3'],
		'road_value_lvl_4':resTraffic['road_value_lvl_4'],
		'date_raw':lastImage['dateRaw']
	});
	print('DONE',str(nowDT))

	
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
	
#def insertTrafficPOSTGRES(obj):
#	try:
#		conn = psycopg2.connect("dbname='Sytadin' user='Sytadin_user' host='localhost' password='admin123'")
#		conn.autocommit = True
#	except:
#		print('--I am unable to connect to the database')
#		return 0;
#		
#	obj['id']=1
#	
#	cur = conn.cursor()
#	qry=""" SELECT max("id_Traffic") FROM public."Traffic"; """
#	try:
#		cur.execute(qry)
#	except:
#		print('--Erreur DB')
#		print(cur.query)
#	rows = cur.fetchall()
#	if len(rows) > 0 and rows[0][0] is not None:
#		obj['id']=rows[0][0]+1
#
#	cstrParameters=','.join([
#		obj['filename'],
#		str(obj['id']),
#		str(obj['road_value_lvl_1']),
#		str(obj['road_value_lvl_2']),
#		str(obj['road_value_lvl_3']),
#		str(obj['road_value_lvl_4']),
#		str(obj['date_raw'])
#	])
#	try:
#		cur2 = conn.cursor()
#		cur2.execute("""INSERT INTO public."Traffic"("filename_Image", "id_Traffic", road_value_lvl_1, road_value_lvl_2, road_value_lvl_3, road_value_lvl_4, date_raw)
#	VALUES (%(filename)s,%(id)s,%(road_value_lvl_1)s,%(road_value_lvl_2)s,%(road_value_lvl_3)s,%(road_value_lvl_4)s,%(date_raw)s);""",obj)
#	except:
#		print('--Erreur DB')
#		print(cur2.query)
		
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
	