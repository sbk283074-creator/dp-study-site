# Four workers, one database file, forty clients arriving at once. SQLite serialises
# writers regardless, and the mutex around it says so out loud -- the question is not
# whether the writes are safe but whether any of them went missing.
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

rm -f load.db load.log jar

./server --port="$PORT" --db=load.db --log=load.log --workers=4 --rounds=1000 >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/healthz" && break
  sleep 0.2
done

B="http://127.0.0.1:$PORT"
curl -s --noproxy '*' -o /dev/null -X POST -d 'user=alice&password=correct-horse' "$B/signup"
curl -s --noproxy '*' -c jar -o /dev/null -X POST -d 'user=alice&password=correct-horse' "$B/login"

seq 1 40 | xargs -P 8 -I{} curl -s --noproxy '*' -b jar -o /dev/null -X POST \
  --data-urlencode 'title=note {}' --data-urlencode 'body=written by client {}' "$B/notes"

echo "every write was answered:"
echo "   POST /notes logged:            $(grep -c '"target": "/notes"' load.log)"
echo "   notes the database admits to:  $(curl -s --noproxy '*' -b jar "$B/" | grep -o '[0-9]* note(s)')"

echo "and none of them was rejected: $(grep -c '"status": "303"' load.log) redirects, $(grep -c '"status": "40[0-9]"' load.log) client errors, $(grep -c '"status": "500"' load.log) server errors"

echo "--- now stop it while it is idle and see what it reports ---"
kill -TERM "$SRV"
wait "$SRV"
echo "exit status after SIGTERM: $?"
grep '"msg": "shutdown"' load.log \
  | sed 's/"t": [0-9]*/"t": <epoch>/; s/"requests": "[0-9]*"/"requests": "<n>"/'
