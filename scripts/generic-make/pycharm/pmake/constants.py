STANDARD_MODULES = [
    ("math", math),
    ("datetime", datetime),
    ("itertools", itertools),
    ("os", os),
]

STANDARD_VARIABLES = [
    ("VERSION", version.VERSION, "Version of the program"),
    ("UTCDATE", datetime.datetime.utcnow(), "time when the program started (in UTC)"),
    ("DATE", datetime.datetime.now(), "time when the program started (in user timezone)"),
]