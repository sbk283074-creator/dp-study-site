import java.util.Map;

public class JsonDemo {
    static final String DOCUMENT =
            "{\"note\":{\"id\":7,\"title\":\"milk\",\"tags\":[\"a\",\"b\"],"
            + "\"done\":false,\"due\":null},\"count\":2}";

    public static void main(String[] args) {
        Json root = JsonParser.parse(DOCUMENT);
        System.out.println("parsed " + DOCUMENT.length() + " character(s)");
        System.out.println();
        print(root, "");
        String back = JsonWriter.write(root);
        System.out.println();
        System.out.println("written back, " + back.length() + " character(s):");
        System.out.println(back);
    }

    static void print(Json value, String indent) {
        switch (value) {
            case Json.Obj o -> {
                System.out.println(indent + "object, " + o.members().size() + " member(s)");
                for (Map.Entry<String, Json> member : o.members().entrySet()) {
                    System.out.println(indent + "  " + member.getKey() + ":");
                    print(member.getValue(), indent + "    ");
                }
            }
            case Json.Arr a -> {
                System.out.println(indent + "array, " + a.items().size() + " item(s)");
                for (Json item : a.items()) {
                    print(item, indent + "  ");
                }
            }
            case Json.Str s -> System.out.println(indent + "string " + s.value());
            case Json.Num n -> System.out.println(indent + "number " + n.raw());
            case Json.Bool b -> System.out.println(indent + "boolean " + b.value());
            case Json.Nil nil -> System.out.println(indent + "null");
        }
    }
}
