# coding: utf8

import urllib.request, datetime
import os, re, time
import psycopg2
from datetime import datetime
import trafficSight_conf


def getTrafficPOSTGRES(dateStart,dateEnd):
	dS = int(time.mktime(dateStart.timetuple()) * 1000)
	dE = int(time.mktime(dateEnd.timetuple()) * 1000)

	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database getTrafficPOSTGRES')
		return -2;

	cur = conn.cursor()
	qry=""" SELECT * FROM public."Traffic" where date_raw >=  """+str(dS)+""" and date_raw <"""+str(dE)+""" order by date_raw desc; """
	
	print(qry)
	
	try:
		cur.execute(qry)
		rows = cur.fetchall()
		result=list()
		for row in rows:
			result.append({
				'r1' : row[2],#roadlvl_1
				'r2' : row[3],
				'r3' : row[4],
				'r4' : row[5],
				'date_raw'         : row[6]
			});
		return result
	except:
		print('--Erreur DB')
		print(cur.query)
		return -1
		
def getTrafficStatsPOSTGRES(opts):
	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database getTrafficStatsPOSTGRES')
		return -2;
		
	day_week=day_week=datetime.today().weekday()+1
	date_forecast='current_date'
	
	if opts is not None:
		if 'day_week' in opts:
			day_week=opts['day_week']
	
	if opts is not None:
		if 'date_forecast' in opts:
			date_forecast=str(opts['date_forecast'])+"'::date"	
	
	cur = conn.cursor()
	qry=""" SELECT nb_traffic_stats,road_value_lvl_1,
	road_value_lvl_2,road_value_lvl_3,road_value_lvl_4,
	ind_day_week,EXTRACT(EPOCH FROM '"""+str(date_forecast)+""" + tm_traffic_stats) *1000 as date_raw FROM public."Traffic_Stats" where ind_day_week =  """+str(day_week)+""" 
	order by date_raw; """
	
	print(qry)
	
	try:
		cur.execute(qry)
		rows = cur.fetchall()
		result=list()
		for row in rows:
			result.append({
				'nb_traffic_stats' : row[0],
				'fr1' : row[1],
				'fr2' : row[2],
				'fr3' : row[3],
				'fr4' : row[4],
				'date_raw'                  : row[6],
				'ind_day_week'              : row[5]
			});
		return result
	except:
		print('--Erreur DB')
		print(cur.query)
		return -1


def insertTrafficPOSTGRES(obj):
	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database insertTrafficPOSTGRES')
		return -2;
		
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
		
		
def getAccidentPOSTGRES(dateStart,dateEnd):
	dS = dateStart
	dE = dateEnd
	print(dS)

	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database getAccidentPOSTGRES')
		return -2;

	cur = conn.cursor()
	qry=""" SELECT * FROM public."Accident" where date_debut_accident >=  '"""+str(dS)+"""' and date_debut_accident < '"""+str(dE)+"""' ; """
	
	print(qry)
	try:
		cur.execute(qry)
		rows = cur.fetchall()
		result=list()
		for row in rows:
			result.append({
				'date_debut_accident' : row[1],
				'header' : row[4]
			});
		return result
	except:
		print('--Erreur DB')
		print(cur.query)
		return -1
		
def getDailyReportPOSTGRES(opts):
	if opts is None:
		return -1
	else:
		print(opts)
		if 'today' in opts:
			qry="""
select 
	date_traffic::char(10),
	ratio_TrafficJam::char(8),
	flag_validity
from view_traffic_ratio_interval_days 
where date_traffic = now()
 ;""";
		if 'day' in opts:
			qry="""
select 
	date_traffic::char(10),
	ratio_TrafficJam::char(8),
	flag_validity
from view_traffic_ratio_interval_days 
where date_traffic = """+str(opts['day'])+""" ;""";
		if 'thismonth' in opts:
			qry="""
select 
date_traffic,
ratio_TrafficJam,
flag_validity
from (
select *, row_number() over (partition by date_traffic order by validity desc) as seq
	from (
		select 
			date_traffic::char(10),
			ratio_TrafficJam::char(8),
			flag_validity,
			1 as validity
		from view_traffic_ratio_interval_days 
		where EXTRACT(MONTH FROM date_traffic) = EXTRACT(MONTH FROM now())
		and EXTRACT(YEAR FROM date_traffic) = EXTRACT(YEAR FROM now())
		union all
		select i::char(10),v::char(8),c,0 as validity from (
		select *,  -1 as v,'KO' c  from (
		select i::date from generate_series(date_trunc('month', current_date), 
		  (date_trunc('month', current_date::date) + interval '1 month' - interval '1 day')::date, '1 day'::interval) i) t
		  ) t2
	 ) t3
 )t4
where seq = 1
order by date_traffic
 ;""";
		if 'month' in opts:
			qry="""
select 
date_traffic,
ratio_TrafficJam,
flag_validity
from (
select *, row_number() over (partition by date_traffic order by validity desc) as seq
	from (
		select 
			date_traffic::char(10),
			ratio_TrafficJam::char(8),
			flag_validity,
			1 as validity
		from view_traffic_ratio_interval_days 
		where EXTRACT(MONTH FROM date_traffic) = """+str(opts['month'])+"""
		and EXTRACT(YEAR FROM date_traffic) = EXTRACT(YEAR FROM now())
		union all
		select i::char(10),v::char(8),c,0 as validity from (
		select *,  -1 as v,'KO' c  from (
		select i::date from generate_series(date_trunc('month', ( extract(year from current_date)||'-01-01')::date+ interval '"""+str((int(opts['month'])-1))+""" month'), 
		  (date_trunc('month', (extract(year from current_date)||'-01-01')::date+ interval '"""+str((int(opts['month'])-1))+""" month') + interval '1 month' - interval '1 day')::date, '1 day'::interval) i) t
		  ) t2
	 ) t3
 )t4
where seq = 1
order by date_traffic
;""";
		else:
			return -3;
	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database getDailyReportPOSTGRES')
		return -2;
	cur = conn.cursor()
	
	try:
		cur.execute(qry)
		rows = cur.fetchall()
		result=list()
		for row in rows:
			result.append({
				'date_traffic'     : row[0],
				'ratio_TrafficJam' : row[1],
				'flag_validity'    : row[2]
			});
		return result
	except:
		print('--Erreur DB')
		print(cur.query)
		return -1
		

def insertAccidentPOSTGRES(obj):
	try:
		c=trafficSight_conf.getDBconf()
		conn = psycopg2.connect(
			"dbname='"+c['DBNAME_DB_SYTADIN']
			+"' user='"+c['USR_DB_SYTADIN']
			+"' host='"+c['HOST_DB_SYTADIN']
			+"' password='"+c['PWD_DB_SYTADIN']+"'"
		);
		conn.autocommit = True
	except:
		print('--I am unable to connect to the database insertAccidentPOSTGRES')
		return -2;
		
	obj['id']=1
	
	cur = conn.cursor()
	qry=""" SELECT max("id_Accident") FROM public."Accident"; """
	try:
		cur.execute(qry)
	except:
		print('--Erreur DB')
		print(cur.query)
	rows = cur.fetchall()
	if len(rows) > 0 and rows[0][0] is not None:
		obj['id']=rows[0][0]+1
		
	try:
		cur.execute(""" SELECT * FROM public."Accident" where header = '""" + str(obj['header']) + """' ; """)
	except:
		print('--Erreur DB')
		print(cur.query.decode("utf-8"))
	if cur.fetchall():
		print('existe deja')
		return -4
	else:
		print('new')

	cstrParameters=','.join([
		str(obj['id']),
		str(obj['header']),
		str(obj['date_event']),
		str(obj['description'])
	])
	try:
		cur2 = conn.cursor()
	#	sqlParam = "str(obj['id'])
	#	sql="""INSERT INTO public."Traffic"("id_Accident", "header", "date_debut_accident", "description")
	#VALUES ("""+str(obj['id'])+"""," """+str(obj['header'])+""" "," """+str(obj['date_event'])+""" "," """+str(obj['description'])+""" ");""";
	#	cur2.execute(sql)
		cur2.execute("""INSERT INTO public."Accident"("id_Accident", "header", "date_debut_accident", "description")
	VALUES (%(id)s,%(header)s,%(date_event)s,%(description)s);""",obj)
		return 1
	except:
		print('--Erreur DB')
		print(cur2.query.decode("utf-8"))
		
		

		
		
if __name__ == '__main__':
	print('Ceci est une bibliothèque')
	
	
