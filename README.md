# Minecraft Server Manager 
This is a simple program to help managing Minecraft servers. For example with automatic updates, setting up the server as a systemd service, or installing a specific version.
## Configuration
Configuration is done with the `mc_servers_config.json` file.
 
	{
		"servers": [
			{
				"name": "MySMPserver",
				"version": "latest",
				"location": "/servers/Minecraft/MySMPserver/",
				"port": "25565",
				"rcon.port": "25575",
				"rcon.password": "hunter2"
			}
		],
		"update_interval": 24
	}
	
Every field is self explainatory. The `port`, `rcon.port`, and `rcon.password` can be found or set in the servers `server.properties`. If the server manager creates the server these values will be set in the `server.properties`.

### Available alternatives for `version`

	latest           Get the latest normal release of the game
	latest-snapshot  Get the latest snapshot
	latest+snapshot  Get the latest version, wheter it's a normal release or a snapshot
	x.y.z            Get the specified version
	x.y.z-snapshot   Get the latest snapshot for the specified version
	x.y.z+snapshot   Get the latest snapshot for the specified verison, or the normal release when it's available
