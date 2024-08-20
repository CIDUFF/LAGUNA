#!/bin/bash
nohup ngrok http --domain=flying-barely-magpie.ngrok-free.app 8000 >/tmp/ngrok.$$.out 2>&1 &
echo Aplicação iniciada.
echo URL: https://flying-barely-magpie.ngrok-free.app/
echo Arquivo de log: /tmp/ngrok.$$.out
