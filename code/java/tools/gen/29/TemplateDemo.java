import java.util.LinkedHashMap;
import java.util.Map;

public class TemplateDemo {
    public static void main(String[] args) {
        Template page = Template.of(
                "<article>\n"
                + "  <h2>{{title}}</h2>\n"
                + "  <p>{{body}}</p>\n"
                + "  <footer>by {{author}}</footer>\n"
                + "</article>");

        Map<String, String> values = new LinkedHashMap<>();
        values.put("title", "Notes & <thoughts>");
        values.put("body", "A <b>bold</b> claim, 5 > 3, and a \"quote\".");
        values.put("author", "Lucas");

        System.out.println(page.render(values));

        System.out.println();
        System.out.println("every value went through the engine, so every value is escaped");
        System.out.println();
        System.out.println("escaped: " + Template.of("{{body}}").render(values));
        System.out.println("raw    : " + Template.of("{{{body}}}").render(values));

        System.out.println();
        System.out.println("a missing value is an error, not an empty string:");
        try {
            Template.of("{{nope}}").render(values);
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }
    }
}
