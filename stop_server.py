import sys
import time
from mcrcon import MCRcon

def main():
	if len(sys.argv) < 2:
		print("Usage: {port} {password}")
		return

	port = int(sys.argv[1])
	password = sys.argv[2]

	with MCRcon("127.0.0.1", password, port=port) as mcr:
		print("Connected. Showing warning...")

		warnCommand = "tellraw @a [\"[\",{\"text\":\"McServerManager\",\"color\":\"blue\"},\"]: Server will shut down in \",{\"text\":\"10\",\"color\":\"red\"},\" seconds\"]"
		mcr.command(warnCommand)

		print("Sent warning, sleeping for 10 seconds...")

		time.sleep(10)

		print("Sleep done. Running /stop command")

		resp = mcr.command("stop")
		print("Stop command sent")
		print("Server responded with:", resp)

	time.sleep(2)


if __name__ == "__main__":
	main()
