import sys
import time
from mcrcon import MCRcon

def main():
	if len(sys.argv) < 2:
		print("Usage: {port} {password}")
		return

	port = sys.argv[0]
	password = sys.argv[1]

	with MCRcon("127.0.0.1", password, port=port) as mcr:

		warnCommand = "/tellraw @a [\"[\",{\"text\":\"McServerManager\",\"color\":\"blue\"},\"]: Server will shut down in \",{\"text\":\"10\",\"color\":\"red\"},\" seconds for update to \",{\"text\":\"1.2.5\",\"color\":\"green\"}]"
		mcr.command(warnCommand)

		time.sleep(10)

		resp = mcr.command("/stop")

	time.sleep(2)


if __name__ == "__main__":
	main()
