"""Audio sources."""

import abc
import sys
import typing
from abc import ABC
from io import BytesIO
from pathlib import Path
from urllib import request

import marimo
import numpy
import scipy
import soundfile
from marimo import Html
from marimo._plugins.ui._impl.input import FileUploadResults
from marimo._runtime.state import State
from numpy.typing import NDArray

from melopa import math, util

random = numpy.random.default_rng()


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


class SourceChirp(Source):
    """Generate chirp signal."""

    def __init__(self, rate: int = 48_000, time: float = 2.0) -> None:
        """Create a SourceChirp instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "chirp"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        time = numpy.linspace(0, self._time, int(self._time * self._rate))
        return scipy.signal.chirp(time, f0=80, f1=4000, t1=self._time), self._rate


class SourceConstant(Source):
    """Generate constant signal."""

    def __init__(
        self, value: float = 0.0, rate: int = 48_000, time: float = 2.0
    ) -> None:
        """Create a SourceConstant instance."""
        self._value = value
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "constant"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        return self._value + numpy.zeros(int(self._time * self._rate)), self._rate


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
            "mefrancis13-crowded_room.wav",
            "realwisut1993-snare_midlow.wav",
            "talitha5-cafe_ambience.wav",
            "templeofhades-scratch_sample.wav",
            "unfa-fail_jingle.wav",
            "zuluonedrop-drum_fill.wav",
        ]

    def name(self) -> str:
        """Find name."""
        return self._file.stem

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal.

        Raises:
            FileNotFoundError: If unable to find source notebook.
        """
        folder = marimo.notebook_location()
        if folder is None:
            message = "Unable to find notebook location."
            raise FileNotFoundError(message)

        if sys.platform == "emscripten":
            url = str(folder / f"data/audio/{self._file}")
            content = BytesIO(request.urlopen(url).read())  # ruff:ignore[suspicious-url-open-usage]
            signal, rate = soundfile.read(content)
        else:
            path = util.repo_path() / f"data/audio/{self._file}"
            signal, rate = soundfile.read(path)
        if len(signal.shape) > 1:
            signal = numpy.mean(signal, axis=1)
        return math.normalize(signal), rate


class SourceInput(Source):
    """Read signals from a Marimo input."""

    def __init__(self, value: FileUploadResults) -> None:
        """Create a SourceInput instance."""
        self._input = value

    def name(self) -> str:
        """Find name."""
        return Path(self._input.name).stem

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        signal, rate = soundfile.read(BytesIO(self._input.contents))
        if len(signal.shape) > 1:
            signal = numpy.mean(signal, axis=1)
        return math.normalize(signal), rate


class SourceImpulse(Source):
    """Generate impulse signal."""

    def __init__(self, rate: int = 48_000, time: float = 2.0) -> None:
        """Create a SourceImpulse instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "impulse"

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

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "linear"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        return numpy.linspace(-1, 1, int(self._time * self._rate)), self._rate


class SourcePinkNoise(Source):
    """Generate pink noise signal."""

    def __init__(self, rate: int = 48_000, time: float = 1.0) -> None:
        """Create a SourcePinkNoise instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "pink_noise"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        length = int(self._rate * self._time)
        white_noise = random.uniform(-1.0, 1.0, length)
        freq = numpy.fft.rfftfreq(length, d=1 / self._rate)

        pink_freq = numpy.fft.rfft(white_noise)
        pink_freq[1:] /= numpy.sqrt(freq[1:])
        pink_noise = numpy.fft.irfft(pink_freq)
        return math.normalize(pink_noise), self._rate


class SourceRectangle(Source):
    """Generate rectangle signal."""

    def __init__(self, rate: int = 48_000, time: float = 1.0) -> None:
        """Create a SourceRectangle instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "rectangle"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        length = int(self._rate * self._time)
        wave = numpy.zeros(length)
        wave[length // 4 : 3 * length // 4] = 1.0
        return wave, self._rate


class SourceSawtooth(Source):
    """Generate sawtooth signal."""

    def __init__(
        self, freq: float = 8.0, rate: int = 48_000, time: float = 1.0
    ) -> None:
        """Create a SourceSawtooth instance."""
        self._freq = freq
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "sawtooth"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        wave = numpy.linspace(-1, 1, int(self._rate / self._freq))
        return numpy.concatenate(int(self._freq * self._time) * (wave,)), self._rate


class SourceSequence(Source):
    """Generate a sequence of notes to form a signal."""

    def __init__(self, notes: list[Source]) -> None:
        """Create a SourceSequence instance."""
        self._notes = notes

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "sequence"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        signal = numpy.concatenate([note.read()[0] for note in self._notes])
        return signal, self._notes[0].read()[1]


class SourceSine(Source):
    """Generate sine signal."""

    def __init__(
        self, freq: float = 8.0, rate: int = 48_000, time: float = 1.0
    ) -> None:
        """Create a SourceSine instance."""
        self._freq = freq
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "sine"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        time = numpy.linspace(0, self._time, int(self._time * self._rate))
        return numpy.sin(2 * numpy.pi * self._freq * time), self._rate


class SourceSquare(Source):
    """Generate square signal."""

    def __init__(
        self, freq: float = 8.0, rate: int = 48_000, time: float = 1.0
    ) -> None:
        """Create a SourceSquare instance."""
        self._freq = freq
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "square"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        period = int(self._rate / self._freq)
        wave = numpy.ones(period)
        wave[period // 2 :] = -1.0
        return numpy.concatenate(int(self._freq * self._time) * (wave,)), self._rate


class SourceUnitStep(Source):
    """Generate unit step signal."""

    def __init__(self, rate: int = 48_000, time: float = 1.0) -> None:
        """Create a SourceUnitStep instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "unit_step"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        length = int(self._rate * self._time)
        wave = numpy.zeros(length)
        wave[length // 2 : length] = 1.0
        return wave, self._rate


class SourceWhiteNoise(Source):
    """Generate white noise signal."""

    def __init__(self, rate: int = 48_000, time: float = 1.0) -> None:
        """Create a SourceWhiteNoise instance."""
        self._rate = rate
        self._time = time

    @typing.override
    def name(self) -> str:
        """Find name."""
        return "white_noise"

    def read(self) -> tuple[NDArray, int]:
        """Load audio signal."""
        length = int(self._rate * self._time)
        return random.uniform(-1.0, 1.0, length), self._rate


def select(name: str) -> Source:
    """Find source corresponding to given name."""
    synth = synths().get(name)
    if synth is None:
        return SourceFile(name)
    return synth()


def synths() -> dict[str, type[Source]]:
    """Find list of synth source names."""
    return {
        "chirp": SourceChirp,
        "constant": SourceConstant,
        "impulse": SourceImpulse,
        "linear": SourceLinear,
        "pink_noise": SourcePinkNoise,
        "rectangle": SourceRectangle,
        "sawtooth": SourceSawtooth,
        "sine": SourceSine,
        "square": SourceSquare,
        "unit_step": SourceUnitStep,
        "white_noise": SourceWhiteNoise,
    }


def ui(default: str) -> tuple[State[Source], Html]:
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
        list(synths()),
        allow_select_none=True,
        label="Synth Generator",
        on_change=lambda name: set_file(select(name)),
        value=None,
    )
    upload = marimo.ui.file(
        filetypes=[".wav"],
        kind="button",
        label="Upload File",
        on_change=lambda input_: set_file(SourceInput(input_[0])),
    )
    return get_file, Html(
        """
<div style="display: flex; flex-direction: row; gap: 1rem;">
    {file}{synth}{upload}
</div>
        """.strip()
    ).batch(
        file=file,
        synth=synth,
        upload=upload,
    )


def ui_synth(default: str) -> Html:
    """Marimo input element to select an audio synth."""
    return marimo.ui.dropdown(
        synths(),
        allow_select_none=True,
        label="Synth Generator",
        value=default,
    )
