#!/bin/bash
PORT=${PORT:-3000}
echo "Starting frontend on port $PORT..."
exec npx serve -s dist -l $PORT
