say() {
  printf '%s\n' "$1"
}

say '$ javac -Xlint:all -Werror --release 21 -d out *.java'
javac -Xlint:all -Werror --release 21 -d out *.java
echo "  -> exit $?"
echo
say '$ jar --create --file quill.jar --main-class Main -C out .'
jar --create --file quill.jar --main-class Main -C out .
echo "  -> exit $?"
echo
say '$ java -jar quill.jar list'
java -jar quill.jar list 2>&1
echo "  -> exit $?"
echo
say '$ jar --create --file plain.jar -C out .'
jar --create --file plain.jar -C out .
say '$ java -jar plain.jar list'
java -jar plain.jar list 2>&1
echo "  -> exit $?"
