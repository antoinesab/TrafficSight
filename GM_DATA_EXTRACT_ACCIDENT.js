var page = require('webpage').create();

page.viewportSize = {width: 512, height: 512};

page.open('http://www.infotrafic.com/route.php?link=accidents.php&region=IDF', function(status) {
	date = new Date()
	console.log("Status: " + status);
	if(status === "success") {
		window.setTimeout(function () {
			console.log('done');
			page.render('StImages/st'+date.getTime()+'.png');
			phantom.exit();
		},5000)

	}
});

