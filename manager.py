"""

Version alternatives:
	latest 			// Get the latest normal release of the game
	latest-snapshot // Get the latest snapshot
	latest+snapshot // Get the latest version, wheter it's a normal release or a snapshot
	x.y.z 			// Get the specified version
	x.y.z-snapshot 	// Get the latest snapshot for the specified version
	x.y.z+snapshot 	// Get the latest snapshot for the specified verison, and when it's released the normal release

"""


VERSION_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

SYSTEMD_PATH = "/etc/system/systemd/"

import json
import requests
import argparse
import urllib.request
import re
import os
import logging
import shutil
import datetime
import time
import math
import string

PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

def setUpLogger():
	class CustomLoggerFormatter(logging.Formatter):
		def __init__(self, toFile = False):
			self._toFile = toFile

		def getColor(self, color):
			if self._toFile or color == "none":
				return ""
			if color == "green":
				return "\033[32m"
			elif color == "yellow":
				return "\033[93m"
			elif color == "red":
				return "\033[91m"
			elif color == "end":
				return "\033[0m"

		def indentStack(self, indent, excInfo, color = None):
			return "\n" + "\n".join([" " * indent + self.getColor(color) + "|" + self.getColor("end") + " " + x for x in (self.formatException(excInfo)).split("\n")])

		def format(self, record):
			t = datetime.datetime.fromtimestamp(record.created).strftime("%y%m%d %H:%M:%S")

			# Create a header that will start every log. Pad the level name so that the rest always start at the same position
			# 8 is the longest logging livel name, "CRITICAL"
			header = "{}{} {}| ".format(record.levelname, " " * (8 - len(record.levelname)), t)

			try:
				message = record.msg % record.args
			except:
				message = record.msg

			color = "red" if record.levelno >= 40 else "yellow" if record.levelno >= 30 else "green" if record.levelno >= 10 and record.levelno < 20 else "none"
			indentedStack = "" if record.exc_info == None else self.indentStack(len(header) - 2, record.exc_info, color)

			# Setup the out variable
			out = self.getColor(color) + header + message

			# If there's no indentedStack - there should be other helpfull information
			if indentedStack == "":
				# For errors and above, add file name and line number
				if record.levelno >= 40:
					out += " [{} Line: {}]".format(record.pathname, record.lineno)
				# For information and warnings, add the logger name
				elif record.levelno >= 20:
					out += " [{}]".format(record.name)

			# End the color
			out += self.getColor("end")
			# Add the indented stack trace
			out += indentedStack

			# Must be last
			# For critical and above...
			if record.levelno >= 50:
				divider = self.getColor(color) + ("=" * 80) + self.getColor("end")
				# ...surround the whole log with a divider
				out = divider + "\n" + out + "\n" + divider

			return out

	# Setup the logger
	fh = logging.FileHandler(PATH + "/logging.log")
	ch = logging.StreamHandler()
	fh.setFormatter(CustomLoggerFormatter(True))
	ch.setFormatter(CustomLoggerFormatter())
	fh.level = 10
	ch.level = 20
	logging.basicConfig(handlers=[fh, ch], level=0)

def readConfig():
	global config

	with open(PATH + "mc_servers_config.json", "r") as f:
		config = json.load(f)

	for server in config["servers"]:
		# Add PATH if the given path isn't absolute
		server["location"] = server["location"] if server["location"].startswith("/") else PATH + server["location"]

def getManifest():
	global manifest

	rManifest = requests.get(VERSION_MANIFEST_URL)
	manifest = rManifest.json()

def getVersionInManifest(s):
	if s == "latest":
		for v in manifest["versions"]:
			if v["id"] == manifest["latest"]["release"]:
				return v
		return False

	if s == "latest-snapshot":
		for v in manifest["versions"]:
			if v["id"] == manifest["latest"]["snapshot"]:
				return v
		return False

	if s == "latest+snapshot":
		return manifest["versions"][0]

	if re.match("^\\d+\\.\\d+(\\.\\d+)?$", s):
		for v in manifest["versions"]:
			if v["id"] == s:
				return v
		return False

	# Get x.y.z±snapshot

	vSnapMatch = re.match("^\\d+\\.\\d+(\\.\\d+)?(\\+|-)snapshot$", s)
	if vSnapMatch:
		sep = vSnapMatch.group(2) # The "+" or "-" between "x.y.z" and "snapshot"
		ver = vSnapMatch.group(0).split(sep)[0]

		includeRelease = sep == "+"

		for v in manifest["versions"]:
			if includeRelease and re.match("^" + ver.replace(".", "\\.") + "$", v["id"]):
				return v

			if re.match("^" + ver.replace(".", "\\.") + "-pre\\d+$", v["id"]):
				return v
		return False

def downloadFile(url, fileName):
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		with open(fileName, "wb") as f:
			for chunk in r.iter_content(chunk_size=8192): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)

def getServerServiceName(name):
	 return "".join([x for x in name.replace(" ", "_") if x in string.ascii_letters + "0123456789-_"]).lower()

def install(v, toInstall):
	# Get the server download url
	rVersionManifest = requests.get(v["url"])
	versionManifest = rVersionManifest.json()
	serverDownloadURL = versionManifest["downloads"]["server"]["url"]

	versionId = v["id"]

	# Set up temporary dir to download to

	downloadDir = PATH + "temp/"

	if not os.path.exists(downloadDir):
		os.mkdir(downloadDir)

	# Download the file
	logging.info("Downloading version " + versionId)

	fileName = downloadDir + versionId.replace(".", "_") + ".jar"
	downloadFile(serverDownloadURL, fileName)

	for server in toInstall:
		serverPath = server["location"]

		if not os.path.exists(serverPath):
			os.makedirs(serverPath)

			# If the path doesn't exist it means that this is a new server
			# Create new server.properties from server config
			with open(serverPath + "server.properties", "w") as f:
				gamePort = "25565" if "port" not in server else server["port"]
				rconPort = server["rcon.port"]
				rconPassword = server["rcon.password"]

				f.write("port={}\nrcon.port={}\nrcon.password={}\nenable-rcon=True".format(gamePort, rconPort, rconPassword))

			logging.info("Wrote new server.properties at '{}'".format(serverPath + "server.properties"))

			# /etc/systemd/system/alfons.service

			with open(PATH + "template.service") as f:
				template = f.read()

			keys = [("name", server["name"]), ("server_path", serverPath), ("path", PATH), ("rcon_port", server["rcon.port"]), ("rcon_password", server["rcon.password"])]

			for k in keys:
				template = template.replace("{" + k[0] + "}", k[1])

			serverServiceName = getServerServiceName(server["name"])

			with open("/etc/systemd/system/mc_server_" + serverServiceName + ".service", "w") as f:
				f.write(template)

			os.system("systemctl daemon-reload")
			os.system("systemctl enable mc_server_{}".format(serverServiceName))
		
		os.system("systemctl stop mc_server_" + getServerServiceName(server["name"]))

		# Remove old "server.jar"
		try:
			os.remove(serverPath + "server.jar")
		except FileNotFoundError:
			pass

		logging.debug("Removed '{}'".format(serverPath + "server.jar"))

		# Copy the new "server.jar" to the location
		shutil.copy(fileName, serverPath + "server.jar")

		logging.info("Copied '{}' to '{}'".format(fileName.replace(PATH[:-1], "..."), serverPath + "server.jar"))

		# Write the version number
		with open(serverPath + "mc_version.txt", "w") as f:
			f.write(versionId)

		logging.debug("Wrote versionfile '{}'".format(serverPath + "mc_version.txt"))
		logging.debug("Starting server '{}'".format(server["name"]))

		os.system("systemctl start mc_server_" + getServerServiceName(server["name"]))

	os.remove(fileName)
	os.removedirs(downloadDir)

	logging.debug("Removed '{}' and {}".format(fileName, downloadDir))

def checkForUpdates():
	getManifest()

	toUpdate = {}

	for server in config["servers"]:
		v = getVersionInManifest(server["version"])

		if not v:
			logging.warning("Version '{}' not found".format(server["version"]))
			continue

		serverPath = server["location"]

		# Get the installed version

		installedVersion = False

		if os.path.exists(serverPath + "mc_version.txt"):
			with open(serverPath + "mc_version.txt") as f:
				installedVersion = f.readline()

		if installedVersion == False:
			logging.info("New server '{}'".format(server["name"]))

		if v["id"] != installedVersion:
			logging.debug("'{}' doesn't match installed '{}' for '{}'. Will download".format(v["id"], installedVersion, server["name"]))

			if v["id"] not in toUpdate:
				toUpdate[v["id"]] = {}
				toUpdate[v["id"]]["v"] = v
				toUpdate[v["id"]]["servers"] = []

			toUpdate[v["id"]]["servers"].append(server)
		else:
			logging.debug("'{}' already have version '{}'".format(server["name"], v["id"]))

	for ver in toUpdate:
		install(toUpdate[ver]["v"],
		 toUpdate[ver]["servers"])

if __name__ == "__main__":
	setUpLogger()
	readConfig()

	interval = (60 * 60 * 24) / int(config["update_interval"])

	while True:
		checkForUpdates()

		today = time.time() % (60 * 60 * 24)
		wait = (interval * (math.floor(today / interval) + 1)) - today

		logging.debug("Sleeping '{}' seconds until '{}'".format(wait, time.time() + wait))

		time.sleep(wait)
