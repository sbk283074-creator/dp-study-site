/* The declared length comes from the file. Trusting it is a buffer overflow
   that anybody who can write the file can trigger. */
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

int main() {
    const char *path = "evil.log";

    /* A record that claims 4096 bytes of payload but carries 32. */
    std::FILE *f = std::fopen(path, "wb");
    std::fprintf(f, "4096 00000000 ");
    std::fprintf(f, "0123456789abcdef0123456789abcdef");
    std::fclose(f);

    f = std::fopen(path, "rb");
    std::size_t len = 0;
    unsigned crc = 0;
    if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) return 1;

    std::string rest;
    int c;
    while ((c = std::fgetc(f)) != EOF) rest += static_cast<char>(c);
    std::fclose(f);
    std::printf("the header claims %zu byte(s); the file carries %zu\n",
                len, rest.size());

    /* The reader believes the length. */
    char *buf = static_cast<char *>(std::malloc(64));
    std::memcpy(buf, rest.data(), len);
    std::printf("copied %zu byte(s)\n", len);
    std::free(buf);
    return 0;
}
