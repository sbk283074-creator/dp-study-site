import java.util.Scanner;

public class Sol1 {
    static final String INPUT = "42\nAda Lovelace\n";

    public static void main(String[] args) {
        System.out.println("-- nextInt() then nextLine() --");
        Scanner a = new Scanner(INPUT);
        int n1 = a.nextInt();
        String s1 = a.nextLine();
        System.out.println("int  = " + n1);
        System.out.println("line = '" + s1 + "'");

        System.out.println();
        System.out.println("-- nextInt() then a second nextLine() --");
        Scanner b = new Scanner(INPUT);
        int n2 = b.nextInt();
        b.nextLine();
        String s2 = b.nextLine();
        System.out.println("int  = " + n2);
        System.out.println("line = '" + s2 + "'");

        System.out.println();
        System.out.println("-- nextLine() and parse --");
        Scanner c = new Scanner(INPUT);
        int n3 = Integer.parseInt(c.nextLine());
        String s3 = c.nextLine();
        System.out.println("int  = " + n3);
        System.out.println("line = '" + s3 + "'");
    }
}
