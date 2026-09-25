quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

echo '$ quill list'
quill list
echo
echo '$ quill add Groceries "milk and eggs"'
quill add Groceries "milk and eggs"
echo
echo '$ quill add Reading "chapter 20"'
quill add Reading "chapter 20"
echo
echo '$ quill list'
quill list
echo
echo '$ quill frobnicate'
quill frobnicate
echo
echo '$ quill add Untitled'
quill add Untitled
