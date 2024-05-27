def plot_merge(source: dict, update: dict):
    for k, v in update.items():
        if k not in source:
            source[k] = v
            continue
        if isinstance(source[k], list):
            source[k].extends(v)
            continue
        if isinstance(source[k], list):
            s = source[k]
            for k1, v1 in v:
                s[k1] = v1
            continue
