from abc import ABC, abstractmethod


class Plotter(ABC):
    """
    Base class help to plot strategy
    """

    @abstractmethod
    def load(self):
        """Load plot config from `Strategy.plot()` and setup candlestick/equity"""

    @abstractmethod
    def plot(self, **kwargs):
        """Plot `equity`, `orders`, and `positions` then show"""

    @abstractmethod
    def stop(self):
        """stop plotter"""
