if [ ! -d "venv" ]; then
	python3 -m venv venv

	venv/bin/pip install -r requirements.txt
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

service=$(cat manager.service)

cat >/etc/systemd/system/mc_manager.service <<EOL
${service//"{path}"/$DIR}
EOL

cat >mc_servers_config.json << EOL
{
	"servers": [],
	"update_interval": 24
}
EOL

systemctl daemon-reload
systemctl enable mc_manager
systemctl start mc_manager
