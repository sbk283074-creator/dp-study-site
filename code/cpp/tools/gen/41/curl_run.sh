PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

./prog "$PORT" > server.log 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

# Wait for the listener by asking it, rather than by sleeping and hoping.
# --noproxy: an HTTP proxy in the environment would send even a 127.0.0.1
# request to the proxy, and the proxy cannot reach this process.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/probe" && break
  sleep 0.2
done

echo "--- GET /hello ---"
curl -s --noproxy '*' "http://127.0.0.1:$PORT/hello"
echo "--- GET /stats ---"
curl -s --noproxy '*' "http://127.0.0.1:$PORT/stats"
echo "--- the server's own log ---"
cat server.log

kill $SRV 2>/dev/null
wait $SRV 2>/dev/null
echo "server stopped"
