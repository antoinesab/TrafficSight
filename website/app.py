from flask import Flask, request, jsonify
from flask import render_template
import sys, os,time
from datetime import datetime
import json
sys.path.insert(0, '../')
import DB
import Sytadin

app = Flask(__name__)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route("/")
def index():
	#specifique time
	#dStart = datetime.strptime( "2017-03-26T10:00:00", "%Y-%m-%dT%H:%M:%S" )
	#dEnd   = datetime.strptime( "2017-03-26T22:08:12", "%Y-%m-%dT%H:%M:%S" )

	
	dStart = datetime.today().replace(hour=5,minute=0,second=0)
	dEnd   = datetime.today().replace(hour=23,minute=59,second=59)
	
	month = datetime.now().month
	
	day = request.args.get('day')
	if day is not None:
		dStart = datetime.strptime( day, "%Y%m%d" ).replace(hour=5,minute=0,second=0)
		dEnd   = datetime.strptime( day, "%Y%m%d" ).replace(hour=23,minute=59,second=59)
		
	datas         = DB.getTrafficPOSTGRES(dStart,dEnd)
	datasForecast = DB.getTrafficStatsPOSTGRES({'date_forecast':day})
	dataDailyReport = DB.getDailyReportPOSTGRES({'month':month});
	
	if datas != -1:
		for data in datas:
			#on normalise
			totalKM=data['r1']+data['r2']+data['r3']+data['r4']
			data['r1'] = int(Sytadin.normalizeKM(totalKM,data['r1']))
			data['r2'] = int(Sytadin.normalizeKM(totalKM,data['r2']))
			data['r3'] = int(Sytadin.normalizeKM(totalKM,data['r3']))
			data['r4'] = int(Sytadin.normalizeKM(totalKM,data['r4']))
			
			
			#on scale en KM
			data['r1'] = int(Sytadin.scalePixelToKm(data['r1']))
			data['r2'] = int(Sytadin.scalePixelToKm(data['r2']))
			data['r3'] = int(Sytadin.scalePixelToKm(data['r3']))
			data['r4'] = int(Sytadin.scalePixelToKm(data['r4']))
		
	if datasForecast != -1:
		for dataForecast in datasForecast:
			totalKM=dataForecast['fr1']+dataForecast['fr2']+dataForecast['fr3']+dataForecast['fr4']
			dataForecast['fr1'] = int(Sytadin.normalizeKM(totalKM,dataForecast['fr1']))
			dataForecast['fr2'] = int(Sytadin.normalizeKM(totalKM,dataForecast['fr2']))
			dataForecast['fr3'] = int(Sytadin.normalizeKM(totalKM,dataForecast['fr3']))
			dataForecast['fr4'] = int(Sytadin.normalizeKM(totalKM,dataForecast['fr4']))
			
			
			#on scale en KM
			dataForecast['fr1'] = int(Sytadin.scalePixelToKm(dataForecast['fr1']))
			dataForecast['fr2'] = int(Sytadin.scalePixelToKm(dataForecast['fr2']))
			dataForecast['fr3'] = int(Sytadin.scalePixelToKm(dataForecast['fr3']))
			dataForecast['fr4'] = int(Sytadin.scalePixelToKm(dataForecast['fr4']))
		
		
	

	data_json = json.dumps(({
		'current_traffic':datas,
		'forecast_traffic':datasForecast,
		'daily_report':dataDailyReport
	}))
	#data_json = json.dumps(datas)
	return render_template("index.html",data_json=data_json)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)