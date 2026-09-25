import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.charset.StandardCharsets;

public class SerialBlob {
    record Person(String name, int age) implements java.io.Serializable {}

    public static void main(String[] args) throws Exception {
        Person before = new Person("Ada", 36);

        ByteArrayOutputStream sink = new ByteArrayOutputStream();
        try (ObjectOutputStream out = new ObjectOutputStream(sink)) {
            out.writeObject(before);
        }
        byte[] blob = sink.toByteArray();

        System.out.println("bytes           = " + blob.length);
        System.out.printf("magic           = %02x%02x%02x%02x%n",
                blob[0] & 0xff, blob[1] & 0xff, blob[2] & 0xff, blob[3] & 0xff);
        System.out.println("names the class = "
                + new String(blob, StandardCharsets.ISO_8859_1).contains("SerialBlob$Person"));

        Person after;
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(blob))) {
            after = (Person) in.readObject();
        }
        System.out.println("round trip      = " + after.equals(before));
    }
}
