cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) throws Exception {
        byte[] salt = Secrets.salt();
        String one = Secrets.derive("same-password", salt, 4096);
        String two = Secrets.derive("same-password", salt, 4096);
        byte[] other = Secrets.salt();
        String three = Secrets.derive("same-password", other, 4096);

        System.out.println("same salt, same password : " + one.equals(two));
        System.out.println("different salt           : " + one.equals(three));
        System.out.println("salt length in bytes     : " + salt.length);
        System.out.println("record length in hex     : " + one.length());
        System.out.println();
        System.out.println("the salt is stored next to the hash and is not a secret. What it");
        System.out.println("buys is that two users with one password get two different records,");
        System.out.println("so one stolen hash does not reveal who shared a password");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
