import json
import logging
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.text import Text
from rich.style import Style

from enum import Enum

PATH = "settings.json"

STANDRD_COLOR = "#a0a0a0"
STANDRD_COLOR_DARK = "#3b3b3b"

class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    OFF = 5

def modify(modifier=None):
    if modifier is None:
        modifier = {}
    if os.path.exists(PATH):
        with open(PATH, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}
    config.update(modifier)
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_config() -> dict | None:
    if not os.path.exists(PATH):
        return None
    with open(PATH, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            return None
    return config

def get_log_level() -> LogLevel:
    config = get_config()
    if not config:
        return LogLevel.INFO
    log_level = config.get("log_level")
    return log_level

def set_log_level(log_level: LogLevel = None):
    if log_level is not None:
        modify({"log_level": log_level})

class GradientMode(Enum):
    CHARS = "chars"
    LINES = "lines"
    BLOCK = "block"
    DIAGONAL = "diagonal"
    ANTI_DIAGONAL = "anti_diagonal"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class GradientPreset(Enum):
    RAINBOW = "rainbow"
    FIRE = "fire"
    ICE = "ice"
    MATRIX = "matrix"
    SUNSET = "sunset"
    GALAXY = "galaxy"
    OCEAN = "ocean"
    LAVA = "lava"
    FOREST = "forest"
    NEON = "neon"
    PASTEL = "pastel"
    CYBERPUNK = "cyberpunk"
    CANDY = "candy"
    AURORA = "aurora"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    PRIDE = "pride"
    VOID = "void"
    TOXIC = "toxic"

class TextBuilder:
    def __init__(self, default_style=STANDRD_COLOR):
        self.default_style = default_style
        self._text = Text()
        self._last_range = None

    def _append(self, content, style):
        start = len(self._text)
        self._text.append(content, style=style)
        end = len(self._text)
        self._last_range = (start, end)
        return self

    def add(self, content, style=None, bold=False, italic=False, underline=False, strike=False, color=None):
        base_style = style or color or self.default_style
        applied_style = Style.parse(base_style)
        applied_style = applied_style + Style(bold=bold, italic=italic, underline=underline, strike=strike)
        return self._append(content, applied_style)

    def _interpolate_color(self, c1, c2, ratio):
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        return f"rgb({r},{g},{b})"

    def _multi_gradient(self, colors, ratio):
        ratio = min(max(ratio, 0), 1)
        segment = ratio * (len(colors) - 1)
        idx = min(int(segment), len(colors) - 2)
        frac = segment - idx
        return self._interpolate_color(colors[idx], colors[idx + 1], frac)

    def gradient(
        self,
        content,
        preset=GradientPreset.RAINBOW,
        mode=GradientMode.LINES,
        bold=False,
        italic=False,
        underline=False,
        strike=False,
    ):
        presets = {
            GradientPreset.RAINBOW: [(255,0,0),(255,165,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255)],
            GradientPreset.FIRE: [(255,0,0),(255,140,0),(255,255,0)],
            GradientPreset.ICE: [(0,200,255),(0,100,200),(200,255,255)],
            GradientPreset.MATRIX: [(0,255,0),(0,128,0),(0,64,0)],
            GradientPreset.SUNSET: [(255,94,77),(255,195,113),(255,255,204)],
            GradientPreset.GALAXY: [(75,0,130),(138,43,226),(255,20,147),(0,0,139)],
            GradientPreset.OCEAN: [(0,105,148),(0,168,232),(144,224,239),(0,191,255)],
            GradientPreset.LAVA: [(207,16,32),(255,85,0),(255,200,0)],
            GradientPreset.FOREST: [(34,139,34),(0,100,0),(107,142,35)],
            GradientPreset.NEON: [(57,255,20),(0,255,255),(255,20,147),(255,255,0)],
            GradientPreset.PASTEL: [(255,179,186),(255,223,186),(255,255,186),(186,255,201),(186,225,255)],
            GradientPreset.CYBERPUNK: [(255,0,255),(0,255,255),(255,255,0)],
            GradientPreset.CANDY: [(255,105,180),(255,182,193),(255,255,255),(173,216,230)],
            GradientPreset.AURORA: [(0,255,127),(127,0,255),(0,191,255)],
            GradientPreset.GOLD: [(255,215,0),(238,180,34),(184,134,11)],
            GradientPreset.SILVER: [(192,192,192),(169,169,169),(128,128,128)],
            GradientPreset.BRONZE: [(205,127,50),(184,115,51),(150,75,0)],
            GradientPreset.PRIDE: [(228,3,3),(255,140,0),(255,237,0),(0,128,38),(0,77,255),(117,7,135)],
            GradientPreset.VOID: [(0,0,0),(25,25,112),(75,0,130),(139,0,139)],
            GradientPreset.TOXIC: [(173,255,47),(0,255,0),(50,205,50),(34,139,34)],
        }
        colors = presets.get(preset, presets[GradientPreset.RAINBOW])

        lines = content.splitlines() or [content]
        total_y = len(lines)

        for y, line in enumerate(lines):
            total_x = len(line)
            for x, char in enumerate(line):
                if mode == GradientMode.CHARS:
                    ratio = (x / max(total_x-1, 1) + y / max(total_y-1, 1)) / 2
                elif mode == GradientMode.LINES:
                    ratio = y / max(total_y - 1, 1)
                elif mode == GradientMode.BLOCK:
                    ratio = ((y / max(total_y-1,1)) + (x / max(total_x-1,1) if total_x>1 else 0)) / 2
                elif mode == GradientMode.DIAGONAL:
                    ratio = (x / max(total_x-1,1) + y / max(total_y-1,1)) / 2
                elif mode == GradientMode.ANTI_DIAGONAL:
                    ratio = (x + (total_y - 1 - y)) / max(total_x + total_y - 2, 1)
                    ratio = min(max(ratio, 0), 1)
                elif mode == GradientMode.HORIZONTAL:
                    ratio = x / max(total_x - 1, 1) if total_x > 1 else 0
                elif mode == GradientMode.VERTICAL:
                    ratio = y / max(total_y - 1, 1)
                else:
                    ratio = 0

                ratio = min(max(ratio, 0), 1)
                color = self._multi_gradient(colors, ratio)

                style = Style.parse(color) + Style(
                    bold=bold, italic=italic, underline=underline, strike=strike
                )

                self._append(char, style)

            if y < total_y - 1:
                self._append("\n", None)

        return self

    
    def add_custom_gradient(
        self,
        content: str,
        palette: list[str],
        mode: GradientMode = GradientMode.CHARS,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strike: bool = False,
    ):
        def hex_to_rgb(hex_color: str):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        colors = [hex_to_rgb(c) for c in palette]

        lines = content.splitlines() or [content]
        total_y = len(lines)

        for y, line in enumerate(lines):
            total_x = len(line)
            for x, char in enumerate(line):
                if mode == GradientMode.CHARS:
                    ratio = (x / max(total_x - 1, 1) + y / max(total_y - 1, 1)) / 2
                elif mode == GradientMode.LINES:
                    ratio = y / max(total_y - 1, 1)
                elif mode == GradientMode.BLOCK:
                    ratio = ((y / max(total_y - 1, 1)) + (x / max(total_x - 1, 1) if total_x > 1 else 0)) / 2
                elif mode == GradientMode.DIAGONAL:
                    ratio = (x / max(total_x - 1, 1) + y / max(total_y - 1, 1)) / 2
                elif mode == GradientMode.ANTI_DIAGONAL:
                    ratio = (x + (total_y - 1 - y)) / max(total_x + total_y - 2, 1)
                    ratio = min(max(ratio, 0), 1)
                elif mode == GradientMode.HORIZONTAL:
                    ratio = x / max(total_x - 1, 1) if total_x > 1 else 0
                elif mode == GradientMode.VERTICAL:
                    ratio = y / max(total_y - 1, 1)
                else:
                    ratio = 0

                ratio = min(max(ratio, 0), 1)
                color = self._multi_gradient(colors, ratio)

                applied_style = Style.parse(color) + Style(
                    bold=bold,
                    italic=italic,
                    underline=underline,
                    strike=strike
                )
                self._append(char, applied_style)

            if y < total_y - 1:
                self._append("\n", None)
        return self

    def _apply_last(self, bold=None, italic=None, underline=None, strike=None, color=None):
        if not self._last_range:
            return self
        start, end = self._last_range
        for span in list(self._text.spans):
            if span.start >= start and span.end <= end:
                base_style = span.style if isinstance(span.style, Style) else Style.parse(str(span.style))

                new_style = base_style + Style(
                    bold=bold if bold is not None else base_style.bold,
                    italic=italic if italic is not None else base_style.italic,
                    underline=underline if underline is not None else base_style.underline,
                    strike=strike if strike is not None else base_style.strike,
                    color=color or base_style.color,
                )

                self._text.stylize(new_style, span.start, span.end)
        return self


    def add_bold(self, content=None, color=None):
        if content is not None:
            return self.add(content, bold=True, color=color)
        return self._apply_last(bold=True, color=color)

    def add_italic(self, content=None, color=None):
        if content is not None:
            return self.add(content, italic=True, color=color)
        return self._apply_last(italic=True, color=color)

    def add_underline(self, content=None, color=None):
        if content is not None:
            return self.add(content, underline=True, color=color)
        return self._apply_last(underline=True, color=color)

    def add_strike(self, content=None, color=None):
        if content is not None:
            return self.add(content, strike=True, color=color)
        return self._apply_last(strike=True, color=color)

    def add_newline(self, lines=1):
        self._append("\n" * lines, None)
        return self

    def add_link(self, content, link, style=None):
        text = Text(content, style=style or self.default_style)
        text.stylize(f"link {link}", 0, len(content))
        self._append(text, None)
        return self

    def build(self):
        if not self._text.style and not self._text.spans:
            self._text.stylize(self.default_style)
        return self._text

    def __str__(self):
        return str(self._text)

    def __rich__(self):
        return self._text

console = Console()

class FancyLogger(logging.Logger):
    LEVEL_STYLES = {
        "PLAIN": f"bold {STANDRD_COLOR}",
        "DEBUG": "bold #00bfff",
        "INFO": "bold #00ff00",
        "WARNING": "bold #ffff00",
        "ERROR": "bold #ff0000",
        "CRITICAL": "bold #ff00ff",
    }

    def _log_with_prefix(self, level_name, text, prefix=None, in_new_line: bool = False, end="\n"):
        style = self.LEVEL_STYLES.get(level_name, "")
        prefix_str = (
            f"[bold {STANDRD_COLOR_DARK}][[/bold {STANDRD_COLOR_DARK}]"
            f"[{style}]{level_name}[/{style}]"
            f"[bold {STANDRD_COLOR_DARK}]][/bold {STANDRD_COLOR_DARK}]"
        )
        if prefix:
            prefix_str += (
                f" [bold {STANDRD_COLOR_DARK}][[/bold {STANDRD_COLOR_DARK}]"
                f"{prefix}"
                f"[bold {STANDRD_COLOR_DARK}]][/bold {STANDRD_COLOR_DARK}]"
            )

        if isinstance(text, Text):
            if not text.style and not text.spans:
                text.stylize(STANDRD_COLOR)
        else:
            text = Text(str(text), style=STANDRD_COLOR)

        console.print(prefix_str, text, sep=" ", end=end, new_line_start=in_new_line)

    def plain(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.OFF:
            return

        prefix_str = ""

        if prefix:
            prefix_str = (
                f"[bold {STANDRD_COLOR_DARK}][[/bold {STANDRD_COLOR_DARK}]"
                f"{prefix}"
                f"[bold {STANDRD_COLOR_DARK}]][/bold {STANDRD_COLOR_DARK}]"
            )
        if isinstance(text, Text):
            if not text.style and not text.spans:
                text.stylize(STANDRD_COLOR)
        else:
            text = Text(str(text), style=STANDRD_COLOR)
        if prefix_str:
            console.print(prefix_str, text, sep=" ", end=end)
        else:
            console.print(text, end=end, new_line_start=in_new_line)

    def debug(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.DEBUG:
            return
        self._log_with_prefix(level_name="DEBUG", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def info(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.INFO:
            return
        self._log_with_prefix(level_name="INFO", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def warn(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.WARNING:
            return
        self._log_with_prefix(level_name="WARNING", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def warning(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.WARNING:
            return
        self._log_with_prefix(level_name="WARNING", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def error(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.ERROR:
            return
        self._log_with_prefix(level_name="ERROR", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def critical(self, text, prefix=None, in_new_line: bool = False, end="\n"):
        if get_log_level() > LogLevel.CRITICAL:
            return
        self._log_with_prefix(level_name="CRITICAL", text=text, prefix=prefix, in_new_line=in_new_line, end=end)

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def next_line(self, lines=1):
        console.print("\n" * lines, end="")

logging.setLoggerClass(FancyLogger)
logger = logging.getLogger("main")

class Question():
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.last_answer = None
    
    def ask(self, default=None, valid_inputs=None, not_empty=True):
        try:
            while True:
                logger.plain(f"{self.prompt}{f' (Default: {default})' if default is not None else ''}: ", "#", end="")
                self.last_answer = input()
                if not self.last_answer.strip():
                    if default is not None:
                        return default
                    if not_empty:
                        continue
                if valid_inputs is None or self.last_answer in valid_inputs:
                    return self.last_answer
                
                logger.error("Invaild input.")
        except KeyboardInterrupt:
            logger.error("User aborted input.", in_new_line=True)
            return default
    
    # set default to None will automatically put this in a loop
    def ask_boolean(self, default: bool = False) -> bool:
        try:
            while True:
                logger.plain(f"{self.prompt} {f"(Default: {"Y" if default is True else "N"}) " if default is not None else ""}[Y/n]: ", "#", end="")
                self.last_answer = input().strip().lower()
                if self.last_answer in ["y", "yes", "yeah", "n", "no"]:
                    break
                if default is not None:
                    return default
                logger.warn("Please enter a valid answer (y/n).")
            return self.last_answer in ["y", "yes", "yeah"]
        except KeyboardInterrupt:
            logger.error("User aborted input.")
            return default if default is not None else False