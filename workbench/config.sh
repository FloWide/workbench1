#!/bin/bash


tee /usr/share/nginx/html/assets/auth_config.json << END
{
    "url":"https://$SERVER-gw.$DOMAIN/auth",
    "realm":"$SERVER-gw",
    "clientId":"flowide-workbench"
}
END


tee /usr/share/nginx/html/assets/connector_list.json << END
{
    "api":{
        "api":"https://$SERVER-gw.$DOMAIN/workbench-api",
        "streamlit_apps":"https://$SERVER-gw.$DOMAIN/streamlit-cloud"
    },
    "dcm_connections":[
        {
            "location_name": "$SERVER-GW",
            "api_base_url": "https://$SERVER-gw.$DOMAIN"
        }
    ]
}
END

tee /etc/nginx/conf.d/default.conf << END
server {
    listen 80;
    listen [::]:80;

    root /usr/share/nginx/html;

    index index.html index.htm;

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
END