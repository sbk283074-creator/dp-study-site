import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** A JSON value. Sealed, so a switch over it is checked for exhaustiveness. */
public sealed interface Json
        permits Json.Obj, Json.Arr, Json.Str, Json.Num, Json.Bool, Json.Nil {

    /** An object keeps insertion order, so a parse/write round trip is stable. */
    record Obj(Map<String, Json> members) implements Json {
        public Obj {
            members = new LinkedHashMap<>(members);
        }

        public Json get(String name) {
            return members.get(name);
        }
    }

    record Arr(List<Json> items) implements Json {
        public Arr {
            items = List.copyOf(items);
        }
    }

    record Str(String value) implements Json {}

    /** The raw text is kept: a double cannot hold every number JSON allows. */
    record Num(String raw) implements Json {
        public double asDouble() {
            return Double.parseDouble(raw);
        }

        public long asLong() {
            return Long.parseLong(raw);
        }

        public boolean isIntegral() {
            return raw.indexOf('.') < 0 && raw.indexOf('e') < 0 && raw.indexOf('E') < 0;
        }
    }

    record Bool(boolean value) implements Json {}

    record Nil() implements Json {}
}
