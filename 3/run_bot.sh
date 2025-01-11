#!/bin/bash

# Запуск Redis в фоновом режиме
redis-server --port 6379 &

# Пауза, чтобы Redis успел запуститься
sleep 2

# Запуск бота в текущем терминале (внутри VS Code)
cd /workspaces/tgbot
source myenv/bin/activate
python main.py