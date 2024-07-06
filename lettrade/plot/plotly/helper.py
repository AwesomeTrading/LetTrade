def plot_merge(
    source: dict,
    *updates: list[dict],
    recursive: int = 0,
    recursive_max: int = 1,
) -> dict:
    """Merge multiple update plot config to source config

    Args:
        source (dict): _description_
        *updates (list[dict]): _description_

    Returns:
        dict: Merged config
    """
    for update in updates:
        for key, value in update.items():
            if key not in source:
                source[key] = value
                continue

            if isinstance(source[key], list):
                source[key].extend(value)
                continue
            if isinstance(source[key], dict):
                if recursive >= recursive_max:
                    source[key] = value
                    continue

                sub = source[key]
                plot_merge(
                    sub,
                    value,
                    recursive=recursive + 1,
                    recursive_max=recursive_max,
                )
                continue
    return source
