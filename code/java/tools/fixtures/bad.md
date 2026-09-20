```java bad
public class Main {
    public static void main(String[] args) {
        int x = "not a number";
    }
}
```

```java run
public class Main {
    public static void main(String[] args) {
        System.out.println("this output fence is wrong");
    }
}
```

```text
a completely different string
```

```java run
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List items = List.of(1);
        System.out.println(items.size());
    }
}
```

```java throw
public class Main {
    public static void main(String[] args) {
        System.out.println("exits zero, so throw cannot pass");
    }
}
```

```java warn
public class Main {
    public static void main(String[] args) {
        System.out.println("compiles silently, so there is no warning to quote");
    }
}
```

```sh run
echo one
```

```text
two
```
