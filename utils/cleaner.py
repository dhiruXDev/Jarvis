NOISE_WORDS = [
    "jara",
    "zara",
    "please",
    "bhai",
    "yaar",
    "bro",
    "na",
    "toh",
    "kar",
    "karo",
    "do",
    "de",
    "hello",
    "jarvis",
    "ok",
    "thanks",
    "thank",
    "you",
    "thik",
    "theek",
    "hai"
]

def clean_command(command):

    command = command.lower().strip()

    words = command.split()

    filtered_words = [
        word for word in words
        if word not in NOISE_WORDS
    ]

    cleaned = " ".join(filtered_words)

    print(f"[CLEANED COMMAND] {cleaned}")

    return cleaned