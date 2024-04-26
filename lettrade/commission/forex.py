from .commission import Commission


class ForexCommission(Commission):
    def __init__(
        self,
        *,
        commission=0,
        multiple=1,
        margin=None,
        leverage=1,
    ) -> None:
        super().__init__(
            commission=commission,
            multiple=multiple,
            margin=margin,
            leverage=leverage,
        )
