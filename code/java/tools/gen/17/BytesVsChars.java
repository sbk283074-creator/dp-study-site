import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class BytesVsChars {
    public static void main(String[] args) throws IOException {
        String text = "caf\u00e9 \u2014 \u5496\u5561";
        Path file = Path.of("utf8.txt");
        Files.writeString(file, text);

        byte[] bytes = Files.readAllBytes(file);
        System.out.println("text          = " + text);
        System.out.println("chars in heap = " + text.length());
        System.out.println("code points   = " + text.codePointCount(0, text.length()));
        System.out.println("utf8 bytes    = " + bytes.length);
        System.out.println("round trip    = " + Files.readString(file).equals(text));

        byte[] latin = text.getBytes(StandardCharsets.ISO_8859_1);
        String back = new String(latin, StandardCharsets.ISO_8859_1);
        System.out.println("latin1 bytes  = " + latin.length);
        System.out.println("lossless      = " + back.equals(text));
    }
}
