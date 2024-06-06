import plotly.io as pio

from .helper import *
from .indicator import *
from .plotly import PlotlyPlotter, Plotter

pio.templates.default = "plotly_dark"

if __debug__:  # __debug__ to remove code in production
    from lettrade.utils.docs import is_docs_session
    from lettrade.utils.notebook import is_notebook_session

    if is_docs_session() or is_notebook_session():
        pio.renderers.default = "notebook"
