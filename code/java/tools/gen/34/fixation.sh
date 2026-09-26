cat > Fixation.java <<'JAVA'
public class Fixation {
    public static void main(String[] args) {
        String planted = "attacker-knows-this-id";
        System.out.println("--- a session id the attacker chose ---");
        System.out.println("  planted before login : " + planted);

        String afterLogin = Ids.newId();
        System.out.println("  issued at login      : <32 hex chars, never sent before>");
        System.out.println("  rotated              : " + !afterLogin.equals(planted));
        System.out.println("  length               : " + afterLogin.length());
        System.out.println();
        System.out.println("a server that keeps the pre-login id after authentication has");
        System.out.println("handed the attacker a session it already knows. The fix is one");
        System.out.println("line: issue a fresh id at every privilege change, and invalidate");
        System.out.println("the old one rather than merely overwriting it");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Fixation.java
java -cp out Fixation
