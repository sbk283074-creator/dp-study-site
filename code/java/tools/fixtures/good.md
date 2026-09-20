```java run
public class Main {
    public static void main(String[] args) {
        System.out.println("two plus two = " + (2 + 2));
    }
}
```

```text
two plus two = 4
```

```java warn
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List items = List.of(1);
        System.out.println(items.size());
    }
}
```

```text
warning: [rawtypes] found raw type: List
```

```java throw
public class Main {
    public static void main(String[] args) {
        String s = null;
        System.out.println(s.length());
    }
}
```

```text
NullPointerException
```

```java compile
public class Main {
    public static void main(String[] args) throws Exception {
        java.net.ServerSocket s = new java.net.ServerSocket(0);
        System.out.println(s.getLocalPort() > 0);
        s.close();
    }
}
```

```java run-files
// ===== Note.java =====
public record Note(String title) {}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        Note n = new Note("first");
        System.out.println(n);
    }
}
```

```text
Note[title=first]
```

```sh run
echo "shell works"
```

```text
shell works
```
