# Driving the finished service the way an operator would: real HTTP, real cookies,
# a real database file, and a real SIGTERM at the end.
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

rm -f acc.db acc.log jar jar2

./server --port="$PORT" --db=acc.db --log=acc.log --workers=4 >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

# Ask the listener whether it is up rather than sleeping and hoping.
# --noproxy '*': a proxy in the environment would swallow even a 127.0.0.1 request.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/healthz" && break
  sleep 0.2
done

B="http://127.0.0.1:$PORT"

echo "--- a stranger gets the sign-in page and nothing else ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' "$B/" \
  | grep -o '<h1>[^<]*</h1>\|<h2>[^<]*</h2>\|\[[0-9]*\]'

echo "--- and a stranger may not write ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -X POST -d 'title=x&body=y' "$B/notes" \
  | grep -o '<h1>[^<]*</h1>\|\[[0-9]*\]'

echo "--- sign up, then sign in ---"
curl -s --noproxy '*' -X POST -d 'user=alice&password=correct-horse' "$B/signup"
curl -s --noproxy '*' -c jar -X POST -d 'user=alice&password=correct-horse' "$B/login"
echo "   the cookie jar now holds $(grep -c 'sid' jar) session cookie"

echo "--- the same visitor is recognised on the next request ---"
curl -s --noproxy '*' -b jar "$B/" | grep -o "<h1>[^<]*</h1>\|[0-9]* note(s)"

echo "--- write a note: 303, and the browser would follow it to / ---"
curl -s --noproxy '*' -b jar -o /dev/null -w '   status [%{http_code}] location %{redirect_url}\n' \
  -X POST --data-urlencode 'title=first' --data-urlencode 'body=hello' "$B/notes"
curl -s --noproxy '*' -b jar "$B/" | grep -o '[0-9]* note(s)\|<li>.*</li>'

echo "--- the note title is data, not markup ---"
curl -s --noproxy '*' -b jar -o /dev/null -X POST \
  --data-urlencode 'title=<script>alert(1)</script>' --data-urlencode 'body=hi' "$B/notes"
curl -s --noproxy '*' -b jar "$B/" | grep -o '&lt;script&gt;[^<]*'

echo "--- a second user cannot see the first user's note ---"
curl -s --noproxy '*' -o /dev/null -X POST -d 'user=bob&password=another-horse' "$B/signup"
curl -s --noproxy '*' -c jar2 -o /dev/null -X POST -d 'user=bob&password=another-horse' "$B/login"
curl -s --noproxy '*' -b jar2 -w ' [%{http_code}]\n' "$B/notes/1" \
  | grep -o '<h1>[^<]*</h1>\|\[[0-9]*\]'
curl -s --noproxy '*' -b jar2 "$B/" | grep -o '[0-9]* note(s)'

echo "--- what the log knows about the password ---"
echo "   occurrences of the password: $(grep -c 'correct-horse' acc.log)"
grep '"msg": "signup"' acc.log | sed 's/"t": [0-9]*/"t": <epoch>/'

kill -TERM "$SRV"
wait "$SRV"
echo "exit status after SIGTERM: $?"
grep '"msg": "shutdown"' acc.log \
  | sed 's/"t": [0-9]*/"t": <epoch>/; s/"requests": "[0-9]*"/"requests": "<n>"/'
