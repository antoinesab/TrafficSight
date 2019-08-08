$(document).ready(function(){

	var max_date_raw=d3.max(JSONObject.current_traffic, function(d) { return d.date_raw;});
	var lastDate=new Date(max_date_raw)
	$('#last-refresh').html(lastDate.getHours()+':'+lastDate.getMinutes());
	
	
	
	JSONObject.current_traffic.forEach(function (e,i) {
		if(e.date_raw==max_date_raw) {
			current_trafic_jam=e.r4+e.r3;
			index_current=i;
		}
	});
	console.log(current_trafic_jam,index_current)
	
	var length_forecast=JSONObject.forecast_traffic.length-1;
	for(var i=0;i<length_forecast;i++) {
		if(max_date_raw>=JSONObject.forecast_traffic[i].date_raw && max_date_raw<=JSONObject.forecast_traffic[i+1].date_raw) {
			reference_traffic_jam=JSONObject.forecast_traffic[i].fr4+JSONObject.forecast_traffic[i].fr3;
			reference_traffic_index=i;
		}
		
	}
	console.log(reference_traffic_jam,reference_traffic_index)
		
	if((current_trafic_jam > 0.7*reference_traffic_jam 
		&& current_trafic_jam < 1.3*reference_traffic_jam )
		|| Math.abs(current_trafic_jam-reference_traffic_jam) < 20) {
		//conforme prévisions
		$('.forecast-state-1').removeClass('d-none');
	} else if (current_trafic_jam < 0.7*reference_traffic_jam) {
		//prévision souséstimés
		$('.forecast-state-3').removeClass('d-none');
	} else {
		//prévision  suréstimés
		$('.forecast-state-2').removeClass('d-none');
	}
	
	if(current_trafic_jam<100) {
		//peu de trafic
		$('#traffic-state-1').removeClass('d-none');
	} else if (current_trafic_jam >= 100 && current_trafic_jam<200 ) {
		//trafic modéré
		$('#traffic-state-2').removeClass('d-none');
	} else {
		//trafic important
		$('#traffic-state-3').removeClass('d-none');
	}

	$('.nb_kilometer-jam').text('Actuellement '+current_trafic_jam+' km')
	
});