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
say '$ printf "bread\nand cheese\n" | quill add Shopping'
printf 'bread\nand cheese\n' | quill add Shopping
echo
say '$ quill list'
quill list
