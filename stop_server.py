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

		warnCommand = "/tellraw @a [\"[\",{\"text\":\"McServerManager\",\"color\":\"blue\"},\"]: Server will shut down in \",{\"text\":\"10\",\"color\":\"red\"},\" seconds\"]"
		mcr.command(warnCommand)

		time.sleep(10)

		resp = mcr.command("/stop")

	time.sleep(2)


if __name__ == "__main__":
	main()
