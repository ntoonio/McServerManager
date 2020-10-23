# Create a python venv and then install requirements
if [ ! -d "venv" ]; then
	python3 -m venv venv

	venv/bin/pip install -r requirements.txt
fi

# Find the path to the manager

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Add mc_manager as a systemd service, with the correct path

service=$(cat manager.service)

cat >/etc/systemd/system/mc_manager.service <<EOL
${service//"{path}"/$DIR}
EOL

# Create an "empty" server config file so that the manager can run

cat >mc_servers_config.json << EOL
{
	"servers": [],
	"update_interval": 24
}
EOL

# Start the manager service

systemctl daemon-reload
systemctl enable mc_manager
systemctl start mc_manager
