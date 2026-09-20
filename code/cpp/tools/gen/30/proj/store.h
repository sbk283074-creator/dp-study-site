#ifndef STORE_H
#define STORE_H

#include <string>
#include <vector>

/* An append-only log of arbitrary payloads, framed so that a torn write at
   the tail is detectable and the records before it survive. */

struct Scan {
    std::vector<std::string> records;
    long good_bytes = 0;   /* bytes covered by complete, verified records */
    long refused = 0;      /* records that failed verification */
    long junk_bytes = 0;   /* bytes left over after the last good record */
};

std::string frame(const std::string &payload);

/* Reads the log, stopping at the first record that is incomplete or does not
   match its checksum. good_bytes is where a clean log ends. */
Scan scan_log(const std::string &path);

/* Appends one framed record and fsyncs. Returns false if any step failed. */
bool append_record(const std::string &path, const std::string &payload);

/* Drops the torn tail, keeping the first `bytes` bytes. */
bool truncate_to(const std::string &path, long bytes);

#endif
