import enum


class ProgressState(enum.Enum):
    not_started = 1
    in_progress = 2
    is_finished = 3
