var page = require('webpage').create();

page.viewportSize = {width: 512, height: 512};

page.open('file:///C:/Users/Haloman/Desktop/Sytadin/traffic.html', function(status) {
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

