quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

say() {
  printf '%s\n' "$1"
}

say '$ printf "milk and eggs\n" | quill add Groceries'
printf 'milk and eggs\n' | quill add Groceries
echo
say '$ printf "chapter 23\n" | quill add Reading'
printf 'chapter 23\n' | quill add Reading
echo
say '$ quill list'
quill list
echo
say '$ quill show 2'
quill show 2
echo
say '$ quill delete 1'
quill delete 1
echo
say '$ quill delete 1'
quill delete 1
echo
say '$ quill --vault other list'
quill --vault other list
