def plot_merge(source: dict, *updates: list[dict]):
    for update in updates:
        for k, v in update.items():
            if k not in source:
                source[k] = v
                continue
            if isinstance(source[k], list):
                source[k].extend(v)
                continue
            if isinstance(source[k], list):
                s = source[k]
                for k1, v1 in v:
                    s[k1] = v1
                continue
    return source
