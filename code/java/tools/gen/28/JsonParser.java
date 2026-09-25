import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A recursive-descent parser for JSON, over a String, with positions in its errors.
 *
 * <p>The cursor is one int index and every method advances it. There is no lookahead beyond a single
 * character, which is the whole reason the grammar fits on a page.
 */
public final class JsonParser {
    /** What {@code peek()} returns past the end. A raw NUL outside a string is illegal JSON. */
    private static final char END = '\0';

    private final String text;
    private final int maxDepth;
    private int at;

    private JsonParser(String text, int maxDepth) {
        this.text = text;
        this.maxDepth = maxDepth;
    }

    /** No depth limit. Do not use this on input you did not produce. */
    public static Json parse(String text) {
        return parse(text, Integer.MAX_VALUE);
    }

    public static Json parse(String text, int maxDepth) {
        JsonParser parser = new JsonParser(text, maxDepth);
        parser.skip();
        Json value = parser.value(0);
        parser.skip();
        if (parser.at != parser.text.length()) {
            throw parser.error("trailing text after the value");
        }
        return value;
    }

    private Json value(int depth) {
        if (depth > maxDepth) {
            throw error("nested deeper than " + maxDepth + " levels");
        }
        return switch (peek()) {
            case '{' -> object(depth);
            case '[' -> array(depth);
            case '"' -> new Json.Str(string());
            case 't' -> literal("true", new Json.Bool(true));
            case 'f' -> literal("false", new Json.Bool(false));
            case 'n' -> literal("null", new Json.Nil());
            case END -> throw error("the input ended where a value was expected");
            default -> number();
        };
    }

    private Json.Obj object(int depth) {
        expect('{');
        Map<String, Json> members = new LinkedHashMap<>();
        skip();
        if (peek() == '}') {
            at++;
            return new Json.Obj(members);
        }
        while (true) {
            skip();
            if (peek() != '"') {
                throw error("expected a member name");
            }
            String name = string();
            skip();
            expect(':');
            skip();
            members.put(name, value(depth + 1));
            skip();
            if (peek() == ',') {
                at++;
                continue;
            }
            expect('}');
            return new Json.Obj(members);
        }
    }

    private Json.Arr array(int depth) {
        expect('[');
        List<Json> items = new ArrayList<>();
        skip();
        if (peek() == ']') {
            at++;
            return new Json.Arr(items);
        }
        while (true) {
            skip();
            items.add(value(depth + 1));
            skip();
            if (peek() == ',') {
                at++;
                continue;
            }
            expect(']');
            return new Json.Arr(items);
        }
    }

    private String string() {
        expect('"');
        StringBuilder out = new StringBuilder();
        while (true) {
            char c = peek();
            switch (c) {
                case '"' -> {
                    at++;
                    return out.toString();
                }
                case '\\' -> {
                    at++;
                    out.append(escape());
                }
                case END -> throw error("unterminated string");
                default -> {
                    if (c < 0x20) {
                        throw error("a raw control character in a string");
                    }
                    out.append(c);
                    at++;
                }
            }
        }
    }

    private char escape() {
        char c = peek();
        at++;
        return switch (c) {
            case '"' -> '"';
            case '\\' -> '\\';
            case '/' -> '/';
            case 'b' -> '\b';
            case 'f' -> '\f';
            case 'n' -> '\n';
            case 'r' -> '\r';
            case 't' -> '\t';
            case 'u' -> (char) Integer.parseInt(hex4(), 16);
            default -> throw error("unknown escape \\" + c);
        };
    }

    private String hex4() {
        if (at + 4 > text.length()) {
            throw error("a \\u escape needs four hex digits");
        }
        String digits = text.substring(at, at + 4);
        for (int i = 0; i < 4; i++) {
            if (Character.digit(digits.charAt(i), 16) < 0) {
                throw error("not a hex digit: '" + digits.charAt(i) + "'");
            }
        }
        at += 4;
        return digits;
    }

    private Json literal(String word, Json value) {
        if (!text.startsWith(word, at)) {
            throw error("expected '" + word + "'");
        }
        at += word.length();
        return value;
    }

    private Json number() {
        int start = at;
        if (peek() == '-') {
            at++;
        }
        if (!isDigit(peek())) {
            throw error("expected a value");
        }
        if (peek() == '0') {
            at++;
        } else {
            while (isDigit(peek())) {
                at++;
            }
        }
        if (peek() == '.') {
            at++;
            if (!isDigit(peek())) {
                throw error("expected a digit after '.'");
            }
            while (isDigit(peek())) {
                at++;
            }
        }
        if (peek() == 'e' || peek() == 'E') {
            at++;
            if (peek() == '+' || peek() == '-') {
                at++;
            }
            if (!isDigit(peek())) {
                throw error("expected a digit in the exponent");
            }
            while (isDigit(peek())) {
                at++;
            }
        }
        return new Json.Num(text.substring(start, at));
    }

    private void skip() {
        while (at < text.length()) {
            char c = text.charAt(at);
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
                at++;
            } else {
                return;
            }
        }
    }

    private void expect(char c) {
        if (peek() != c) {
            throw error("expected '" + c + "' but found " + describe(peek()));
        }
        at++;
    }

    private char peek() {
        return at < text.length() ? text.charAt(at) : END;
    }

    private static String describe(char c) {
        return c == END ? "the end of the input" : "'" + c + "'";
    }

    private static boolean isDigit(char c) {
        return c >= '0' && c <= '9';
    }

    private IllegalArgumentException error(String message) {
        int line = 1;
        int column = 1;
        int limit = Math.min(at, text.length());
        for (int i = 0; i < limit; i++) {
            if (text.charAt(i) == '\n') {
                line++;
                column = 1;
            } else {
                column++;
            }
        }
        return new IllegalArgumentException(message + " at line " + line + ", column " + column);
    }
}
