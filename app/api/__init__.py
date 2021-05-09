def create_status_docs(response_map: dict, model) -> dict:
    status_docs = {}
    for item in response_map.values():
        status_docs[item["code"]] = {"model": item["model"] if "model" in item else model, "description": item["description"]}
    return status_docs
