"""Released message roles, JSON-object mode and parse retries, on our transport."""

from expbench.gateway import ModelError, parse_structured


def original_messages(prompt):
    return [{"role": "system", "content": prompt}, {"role": "user", "content": ""}]


def query_original(gateway, prompt, schema, attempts=3):
    for _ in range(attempts):
        # Transport failures propagate; retry only a completed malformed answer.
        response = gateway.complete("judge", original_messages(prompt), json_object=True)
        try:
            return parse_structured(response, schema)
        except ModelError:
            continue
    raise ModelError(f"Invalid {schema.__name__} after {attempts} parse attempts")
