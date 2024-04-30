from .commission import Commission


class ForexCommission(Commission):
    def __init__(
        self,
        *,
        commission=0,
        leverage=1,
    ) -> None:
        super().__init__(
            commission=commission,
            leverage=leverage,
        )
