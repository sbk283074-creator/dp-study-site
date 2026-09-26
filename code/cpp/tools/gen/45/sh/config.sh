rm -f notes.conf
printf 'port = 9000\nworkers=8\nrounds=2000\n\n# a blank line above, a comment here, neither is a setting\n' > notes.conf

echo "--- nothing set: every value has come from the default ---"
./server --print-config

echo "--- the file layer ---"
./server --config=notes.conf --print-config

echo "--- the environment layer beats the file ---"
NOTESD_PORT=9100 ./server --config=notes.conf --print-config

echo "--- and argv beats everything ---"
NOTESD_PORT=9100 ./server --config=notes.conf --port=9200 --print-config

echo "--- refusing to start is a promise kept ---"
./server --port=0 --print-config 2>&1
echo "exit status: $?"
./server --workers=999 --print-config 2>&1
echo "exit status: $?"
./server --nope=1 --print-config 2>&1
echo "exit status: $?"
./server --config=missing.conf --print-config 2>&1
echo "exit status: $?"
