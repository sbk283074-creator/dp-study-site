#include "store.h"

#include <cstdio>
#include <string>
#include <vector>

namespace {

const char *kPath = "data.log";

int cmd_add(const std::string &payload) {
    if (!append_record(kPath, payload)) {
        std::printf("add failed\n");
        return 1;
    }
    std::printf("added: %s\n", payload.c_str());
    return 0;
}

int cmd_list() {
    const Scan s = scan_log(kPath);
    for (const std::string &r : s.records) std::printf("%s\n", r.c_str());
    if (s.refused > 0) {
        std::printf("[%ld record(s) refused: the log ends in a torn or corrupt record]\n",
                    s.refused);
    }
    if (s.junk_bytes > 0) {
        std::printf("[%ld byte(s) of trailing junk after the last good record]\n",
                    s.junk_bytes);
    }
    return 0;
}

int cmd_recover() {
    const Scan s = scan_log(kPath);
    if (s.refused == 0 && s.junk_bytes == 0) {
        std::printf("nothing to recover: %zu record(s), log is clean\n", s.records.size());
        return 0;
    }
    if (!truncate_to(kPath, s.good_bytes)) {
        std::printf("recover failed\n");
        return 1;
    }
    std::printf("dropped the torn tail at byte %ld; %zu record(s) kept\n",
                s.good_bytes, s.records.size());
    return 0;
}

void selftest() {
    std::remove(kPath);
    std::printf("append three records\n");
    append_record(kPath, "widget");
    append_record(kPath, "gasket");
    append_record(kPath, "bolt");
    cmd_list();

    std::printf("\na torn tail: five bytes short\n");
    const Scan s = scan_log(kPath);
    truncate_to(kPath, s.good_bytes - 5);
    cmd_list();

    std::printf("\nrecover, then carry on\n");
    cmd_recover();
    append_record(kPath, "washer");
    cmd_list();
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--help") {
        std::printf("usage: %s            run the built-in self-test\n", argv[0]);
        std::printf("       %s add TEXT   append one record\n", argv[0]);
        std::printf("       %s list       print every readable record\n", argv[0]);
        std::printf("       %s recover    drop the torn tail\n", argv[0]);
        return 0;
    }
    if (argc == 2 && std::string(argv[1]) == "list")    return cmd_list();
    if (argc == 2 && std::string(argv[1]) == "recover") return cmd_recover();
    if (argc == 3 && std::string(argv[1]) == "add")     return cmd_add(argv[2]);
    if (argc == 1) {
        selftest();
        return 0;
    }
    std::printf("usage: prog [add TEXT | list | recover]\n");
    return 2;
}
