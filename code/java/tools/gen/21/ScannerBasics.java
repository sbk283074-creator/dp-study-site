import java.util.Scanner;

public class ScannerBasics {
    public static void main(String[] args) {
        String input = "42\nAda Lovelace\n";

        Scanner scanner = new Scanner(input);
        int number = scanner.nextInt();
        String afterInt = scanner.nextLine();
        String name = scanner.nextLine();

        System.out.println("number      = " + number);
        System.out.println("afterInt    = '" + afterInt + "' (length " + afterInt.length() + ")");
        System.out.println("name        = '" + name + "'");

        System.out.println();

        Scanner fixed = new Scanner(input);
        int parsed = Integer.parseInt(fixed.nextLine());
        String rest = fixed.nextLine();
        System.out.println("parsed      = " + parsed);
        System.out.println("rest        = '" + rest + "'");
    }
}
