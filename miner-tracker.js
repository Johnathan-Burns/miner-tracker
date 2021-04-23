const miner = ':[INSERT ETHEREUM MINING ADDRESS HERE]'
//const token = '[INSERT DISCORD BOT TOKEN HERE]'
//const cid = '[INSERT CHANNEL ID HERE]'
// Modify these as needed for the workers in your sub-pool
const workers = [ 'jb0', 'jb1', 'tj', 'andrew', 'beefin', 'verekone' ]

const Discord = require('discord.js');
const bot = new Discord.Client();

bot.login(token);

bot.on('ready', () => {
  console.log(`Logged in as ${bot.user.tag}!`)

	// Gets the total number of shares from the api for each individual worker and post them on discord
	for (var worker of workers)
	{
		let channel = bot.channels.cache.get(cid)
		let message = getWorkerShares(miner, worker, function(message) {
			console.log(message)
			channel.send(message)
		});

	}

	setTimeout(exitfunc, 1000 * 30); // Quit in 30 seconds
});

function getWorkerShares(miner, worker, callback) {
	var sum = 0
	var msg = ''

	const https = require('https')
	const options = {
		hostname: 'api.ethermine.org',
		port: 443,
		path: '/miner/' + miner + '/worker/' + worker + '/history',
		method: 'GET'
	}

	const req = https.request(options, res => {

		let body = ""
  		console.log(`statusCode: ${res.statusCode}`)
		res.setEncoding('utf8');

  	res.on('data', (chunk) => {
			body += chunk
  	})

		res.on("end", () => {
        	try {
            	let json = JSON.parse(body);

		for(let x of json.data)
		{
			// Want only on-the-hour values
			if(x.time % 3600 == 0 && x.validShares != null && x.staleShares != null)
			{
				// Create a new JavaScript Date object based on the timestamp
				// multiplied by 1000 so that the argument is in milliseconds, not seconds.
				var date = new Date(x.time * 1000);
				var hours = date.getHours();
				var minutes = '0' + date.getMinutes();
				var seconds = '0' + date.getSeconds();
				var month =  '0' + (date.getMonth() + 1);
				var day = '0' + date.getDate();
				var year = date.getFullYear();

				// Will display time in 10:30:23 format
				var formattedTime = year + '-' + month.substr(-2) + '-' + day.substr(-2) + ' ' + hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
				var tmp = formattedTime + ' | Worker ' + worker + ' had ' + x.validShares + ' valid and ' + x.staleShares + ' stale shares.\n'
				msg += tmp

				sum = sum + x.validShares + x.staleShares
			}
		}

		msg = msg + 'Worker **' + worker + '** had **' + sum + '** total shares in the last 12 hours.\n'
		callback(msg);

        	} catch (error) {
            	console.error(error.message);
        	};
    	})
	})

	req.on('error', error => {
  	console.error(error)
	})

	req.end()
}

function exitfunc()
{
	console.log('Exiting!')
	bot.destroy()
	process.exit()
}
