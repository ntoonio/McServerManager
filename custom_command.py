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
		print("Connected! Sending command")

		command = " ".join(sys.argv[3:])
	
		response = mcr.command(command)

		print(response)

if __name__ == "__main__":
	main()
