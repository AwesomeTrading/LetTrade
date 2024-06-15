from importlib.util import find_spec

if find_spec("ray") is not None:
    from ray.util.queue import Queue

    class LetOptimizeRay:
        _data: dict

        def dumps(self, data: dict, lt: "LetTradeBackTest"):
            self._data = data

            # Patch: overrite lettrade queue
            q = Queue()
            data["kwargs"]["queue"] = q
            lt._stats._q = q

        @property
        def data(self) -> dict:
            return self._data
