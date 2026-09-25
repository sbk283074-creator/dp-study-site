quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

say() {
  printf '%s\n' "$1"
}

say '$ printf "milk and eggs\nbread\n" | quill add Groceries'
printf 'milk and eggs\nbread\n' | quill add Groceries
echo
say '$ quill list'
quill list
echo
say '$ cat vault/notes.tsv'
cat vault/notes.tsv
