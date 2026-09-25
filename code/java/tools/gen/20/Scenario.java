public class Scenario {
    record Loose(String title, String body) {
        String render() {
            return title + "\t" + body;
        }
    }

    record Guarded(String title, String body) {
        Guarded {
            if (title.indexOf('\t') >= 0 || title.indexOf('\n') >= 0) {
                throw new IllegalArgumentException("title may not contain a tab or newline");
            }
        }

        String render() {
            return title + "\t" + body;
        }
    }

    static String show(String s) {
        return "'" + s.replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String pasted = "Groceries\tand more";

        String[] parts = new Loose(pasted, "milk").render().split("\t", 2);
        System.out.println("pasted title     = " + show(pasted));
        System.out.println("title read back  = " + show(parts[0]));
        System.out.println("body read back   = " + show(parts[1]));

        System.out.println();

        try {
            new Guarded(pasted, "milk");
            System.out.println("guarded          = accepted, which would be wrong");
        } catch (IllegalArgumentException e) {
            System.out.println("guarded          = rejected at the boundary");
            System.out.println("message          = " + e.getMessage());
        }
    }
}
