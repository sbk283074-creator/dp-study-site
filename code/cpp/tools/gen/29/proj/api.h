#ifndef API_H
#define API_H

#include "json.h"

#include <string>

/* The payloads the service answers with. */
Json items_payload();

/* Returns nothing when there is no such item. It deliberately does not return
   an error payload: a function that builds a body cannot also choose the status
   code, and a body that says 404 inside a 200 response is worse than no answer. */
std::optional<Json> item_payload(const std::string &id);

Json error_payload(int status, const std::string &message);

/* The whole response, headers included, exactly as it goes on the wire. */
std::string render_json(const Json &body, int status, const char *reason);

#endif
