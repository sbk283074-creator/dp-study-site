say() {
  printf '%s\n' "$1"
}

say '$ java -cp out SelfTest'
java -cp out SelfTest 2>&1
echo "  -> exit $?"
