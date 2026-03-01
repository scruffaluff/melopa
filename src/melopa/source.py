"""Audio sources."""

import abc
import sys
from abc import ABC
from io import BytesIO
from pathlib import Path
from urllib import request

import marimo
import numpy
from marimo import Html, ui
from marimo._runtime.state import State
from numpy.typing import NDArray
from scipy.io import wavfile

from melopa import math, util


class Source(ABC):
    """Generic interface for loading audio signals."""

    @abc.abstractmethod
    def name(self) -> str:
        """Find name."""
        raise NotImplementedError

    @abc.abstractmethod
    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        raise NotImplementedError


class SourceFile(Source):
    """Read signals from a file."""

    def __init__(self, value: str | Path) -> None:
        """Create a SourceFile instance."""
        self._file = value if isinstance(value, Path) else Path(value)

    @classmethod
    def list(cls) -> list[str]:
        """Find included audio files."""
        return [
            "claretcanelon-baby_parrot.wav",
            "dwsd-kick_laid.wav",
            "esperar-chicken_imitation.wav",
            "gowers-amen_break.wav",
            "hallkev-timpani_roll.wav",
            "karolist-acoustic_kick.wav",
            "mefrancis13-crowded_room.wav",
            "talitha5-cafe_ambience.wav",
            "templeofhades-scratch_sample.wav",
            "unfa-fail_jingle.wav",
        ]

    def name(self) -> str:
        """Find name."""
        return self._file.stem

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        folder = marimo.notebook_location()
        if folder is None:
            message = "Unable to find notebook location."
            raise ValueError(message)

        if sys.platform == "emscripten":
            url = str(folder / f"data/audio/{self._file}")
            content = BytesIO(request.urlopen(url).read())  # noqa: S310
            rate, signal = wavfile.read(content)
        else:
            path = util.repo_path() / f"data/audio/{self._file}"
            rate, signal = wavfile.read(path)
        if len(signal.shape) > 1:
            signal = numpy.mean(signal, axis=1)
        return math.normalize(signal), rate


class SourceInput(Source):
    """Read signals from a Marimo input."""

    def __init__(self, value: ui.file) -> None:
        """Create a SourceInput instance."""
        self._input = value

    def name(self) -> str:
        """Find name."""
        return Path(self._input.name() or "").stem

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        rate, signal = wavfile.read(BytesIO(self._input.contents() or b""))
        if len(signal.shape) > 1:
            signal = numpy.mean(signal, axis=1)
        return math.normalize(signal), rate


class SourceDelta(Source):
    """Generate Kronecker delta signal."""

    def __init__(self, rate: int = 48_000, time: float = 2.0) -> None:
        """Create a SourceDelta instance."""
        self._rate = rate
        self._time = time

    def name(self) -> str:
        """Find name."""
        return "delta"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        signal = numpy.zeros(int(self._time * self._rate))
        signal[0] = 1
        return signal, self._rate


class SourceLinear(Source):
    """Generate linear signal."""

    def __init__(self, rate: int = 48_000, time: float = 2.0) -> None:
        """Create a SourceLinear instance."""
        self._rate = rate
        self._time = time

    def name(self) -> str:
        """Find name."""
        return "linear"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        return numpy.linspace(-1, 1, int(self._time * self._rate)), self._rate


class SourceSine(Source):
    """Generate sine signal."""

    def __init__(
        self, freq: float = 8.0, rate: int = 48_000, time: float = 2.0
    ) -> None:
        """Create a SourceSine instance."""
        self._freq = freq
        self._rate = rate
        self._time = time

    def name(self) -> str:
        """Find name."""
        return "sine"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        time = numpy.linspace(0, 2, int(self._time * self._rate))
        return numpy.sin(2 * numpy.pi * self._freq * time), self._rate


def component(default: str) -> tuple[State[Source], Html]:
    """Marimo input element to select an audio signal."""
    get_file, set_file = marimo.state(select(default))
    file = marimo.ui.dropdown(
        SourceFile.list(),
        allow_select_none=True,
        label="Select File",
        on_change=lambda name: set_file(SourceFile(name)),
        value=None,
    )
    synth = marimo.ui.dropdown(
        synths(),
        allow_select_none=True,
        label="Synth Generator",
        on_change=lambda name: set_file(select(name)),
        value=None,
    )
    upload = marimo.ui.file(
        filetypes=[".wav"],
        kind="button",
        label="Upload File",
        on_change=lambda input_: set_file(SourceInput(input_)),
    )
    return get_file, Html("<div>{file}{synth}{upload}</div>").batch(
        file=file,  # ty:ignore[invalid-argument-type]
        synth=synth,  # ty:ignore[invalid-argument-type]
        upload=upload,  # ty:ignore[invalid-argument-type]
    )


def select(name: str) -> Source:
    """Find source corresponding to given name."""
    match name.lower():
        case "delta":
            return SourceDelta()
        case "linear":
            return SourceLinear()
        case "sine":
            return SourceSine()
        case _:
            return SourceFile(name)


def synths() -> list[str]:
    """Find list of synth source names."""
    return ["delta", "linear", "sine"]
