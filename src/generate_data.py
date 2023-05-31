import datetime
import random
import sys
import logging

from ipaddress import IPv4Address, IPv6Address
from typing import Tuple, Optional, Callable, List

import psycopg2
import psycopg2.extras

BIP39_WORDS = ["abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
               "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
               "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit", "adult",
               "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent", "agree", "ahead",
               "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien", "all", "alley", "allow",
               "almost", "alone", "alpha", "already", "also", "alter", "always", "amateur", "amazing", "among",
               "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry", "animal", "ankle",
               "announce", "annual", "another", "answer", "antenna", "antique", "anxiety", "any", "apart", "apology",
               "appear", "apple", "approve", "april", "arch", "arctic", "area", "arena", "argue", "arm", "armed",
               "armor", "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "artefact", "artist",
               "artwork", "ask", "aspect", "assault", "asset", "assist", "assume", "asthma", "athlete", "atom",
               "attack", "attend", "attitude", "attract", "auction", "audit", "august", "aunt", "author", "auto",
               "autumn", "average", "avocado", "avoid", "awake", "aware", "away", "awesome", "awful", "awkward", "axis",
               "baby", "bachelor", "bacon", "badge", "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner",
               "bar", "barely", "bargain", "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty",
               "because", "become", "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench",
               "benefit", "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology",
               "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless", "blind",
               "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body", "boil", "bomb", "bone",
               "bonus", "book", "boost", "border", "boring", "borrow", "boss", "bottom", "bounce", "box", "boy",
               "bracket", "brain", "brand", "brass", "brave", "bread", "breeze", "brick", "bridge", "brief", "bright",
               "bring", "brisk", "broccoli", "broken", "bronze", "broom", "brother", "brown", "brush", "bubble",
               "buddy", "budget", "buffalo", "build", "bulb", "bulk", "bullet", "bundle", "bunker", "burden", "burger",
               "burst", "bus", "business", "busy", "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus",
               "cage", "cake", "call", "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon", "canoe",
               "canvas", "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry",
               "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category", "cattle",
               "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census", "century", "cereal",
               "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge", "chase", "chat",
               "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief", "child", "chimney", "choice",
               "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle", "citizen", "city",
               "civil", "claim", "clap", "clarify", "claw", "clay", "clean", "clerk", "clever", "click", "client",
               "cliff", "climb", "clinic", "clip", "clock", "clog", "close", "cloth", "cloud", "clown", "club", "clump",
               "cluster", "clutch", "coach", "coast", "coconut", "code", "coffee", "coil", "coin", "collect", "color",
               "column", "combine", "come", "comfort", "comic", "common", "company", "concert", "conduct", "confirm",
               "congress", "connect", "consider", "control", "convince", "cook", "cool", "copper", "copy", "coral",
               "core", "corn", "correct", "cost", "cotton", "couch", "country", "couple", "course", "cousin", "cover",
               "coyote", "crack", "cradle", "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream",
               "credit", "creek", "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd",
               "crucial", "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture", "cup",
               "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle", "dad",
               "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day", "deal", "debate",
               "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer", "defense", "define",
               "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist", "deny", "depart",
               "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design", "desk", "despair",
               "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial", "diamond", "diary",
               "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur", "direct",
               "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display", "distance",
               "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin", "domain",
               "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon", "drama", "drastic",
               "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive", "drop", "drum", "dry", "duck",
               "dumb", "dune", "during", "dust", "dutch", "duty", "dwarf", "dynamic", "eager", "eagle", "early", "earn",
               "earth", "easily", "east", "easy", "echo", "ecology", "economy", "edge", "edit", "educate", "effort",
               "egg", "eight", "either", "elbow", "elder", "electric", "elegant", "element", "elephant", "elevator",
               "elite", "else", "embark", "embody", "embrace", "emerge", "emotion", "employ", "empower", "empty",
               "enable", "enact", "end", "endless", "endorse", "enemy", "energy", "enforce", "engage", "engine",
               "enhance", "enjoy", "enlist", "enough", "enrich", "enroll", "ensure", "enter", "entire", "entry",
               "envelope", "episode", "equal", "equip", "era", "erase", "erode", "erosion", "error", "erupt", "escape",
               "essay", "essence", "estate", "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact",
               "example", "excess", "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust",
               "exhibit", "exile", "exist", "exit", "exotic", "expand", "expect", "expire", "explain", "expose",
               "express", "extend", "extra", "eye", "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith",
               "fall", "false", "fame", "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat",
               "fatal", "father", "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed",
               "feel", "female", "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure",
               "file", "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm", "first", "fiscal",
               "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor", "flee", "flight", "flip",
               "float", "flock", "floor", "flower", "fluid", "flush", "fly", "foam", "focus", "fog", "foil", "fold",
               "follow", "food", "foot", "force", "forest", "forget", "fork", "fortune", "forum", "forward", "fossil",
               "foster", "found", "fox", "fragile", "frame", "frequent", "fresh", "friend", "fringe", "frog", "front",
               "frost", "frown", "frozen", "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget",
               "gain", "galaxy", "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas",
               "gasp", "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine", "gesture",
               "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give", "glad", "glance", "glare",
               "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove", "glow", "glue", "goat", "goddess",
               "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown", "grab", "grace", "grain",
               "grant", "grape", "grass", "gravity", "great", "green", "grid", "grief", "grit", "grocery", "group",
               "grow", "grunt", "guard", "guess", "guide", "guilt", "guitar", "gun", "gym", "habit", "hair", "half",
               "hammer", "hamster", "hand", "happy", "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk",
               "hazard", "head", "health", "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen",
               "hero", "hidden", "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey", "hold", "hole",
               "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror", "horse", "hospital", "host",
               "hotel", "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred", "hungry", "hunt",
               "hurdle", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea", "identify", "idle", "ignore",
               "ill", "illegal", "illness", "image", "imitate", "immense", "immune", "impact", "impose", "improve",
               "impulse", "inch", "include", "income", "increase", "index", "indicate", "indoor", "industry", "infant",
               "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury", "inmate", "inner", "innocent",
               "input", "inquiry", "insane", "insect", "inside", "inspire", "install", "intact", "interest", "into",
               "invest", "invite", "involve", "iron", "island", "isolate", "issue", "item", "ivory", "jacket", "jaguar",
               "jar", "jazz", "jealous", "jeans", "jelly", "jewel", "job", "join", "joke", "journey", "joy", "judge",
               "juice", "jump", "jungle", "junior", "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key",
               "kick", "kid", "kidney", "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee",
               "knife", "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language",
               "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit", "layer",
               "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal", "legend", "leisure",
               "lemon", "lend", "length", "lens", "leopard", "lesson", "letter", "level", "liar", "liberty", "library",
               "license", "life", "lift", "light", "like", "limb", "limit", "link", "lion", "liquid", "list", "little",
               "live", "lizard", "load", "loan", "lobster", "local", "lock", "logic", "lonely", "long", "loop",
               "lottery", "loud", "lounge", "love", "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury",
               "lyrics", "machine", "mad", "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal", "man",
               "manage", "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin", "marine",
               "market", "marriage", "mask", "mass", "master", "match", "material", "math", "matrix", "matter",
               "maximum", "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media", "melody", "melt",
               "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry", "mesh", "message", "metal",
               "method", "middle", "midnight", "milk", "million", "mimic", "mind", "minimum", "minor", "minute",
               "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed", "mixture", "mobile", "model", "modify",
               "mom", "moment", "monitor", "monkey", "monster", "month", "moon", "moral", "more", "morning", "mosquito",
               "mother", "motion", "motor", "mountain", "mouse", "move", "movie", "much", "muffin", "mule", "multiply",
               "muscle", "museum", "mushroom", "music", "must", "mutual", "myself", "mystery", "myth", "naive", "name",
               "napkin", "narrow", "nasty", "nation", "nature", "near", "neck", "need", "negative", "neglect",
               "neither", "nephew", "nerve", "nest", "net", "network", "neutral", "never", "news", "next", "nice",
               "night", "noble", "noise", "nominee", "noodle", "normal", "north", "nose", "notable", "note", "nothing",
               "notice", "novel", "now", "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige",
               "obscure", "observe", "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer", "office",
               "often", "oil", "okay", "old", "olive", "olympic", "omit", "once", "one", "onion", "online", "only",
               "open", "opera", "opinion", "oppose", "option", "orange", "orbit", "orchard", "order", "ordinary",
               "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor", "outer", "output", "outside",
               "oval", "oven", "over", "own", "owner", "oxygen", "oyster", "ozone", "pact", "paddle", "page", "pair",
               "palace", "palm", "panda", "panel", "panic", "panther", "paper", "parade", "parent", "park", "parrot",
               "party", "pass", "patch", "path", "patient", "patrol", "pattern", "pause", "pave", "payment", "peace",
               "peanut", "pear", "peasant", "pelican", "pen", "penalty", "pencil", "people", "pepper", "perfect",
               "permit", "person", "pet", "phone", "photo", "phrase", "physical", "piano", "picnic", "picture", "piece",
               "pig", "pigeon", "pill", "pilot", "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place",
               "planet", "plastic", "plate", "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet",
               "point", "polar", "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible",
               "post", "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer",
               "prepare", "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison",
               "private", "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof",
               "property", "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse",
               "pumpkin", "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle",
               "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit",
               "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp", "ranch", "random",
               "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor", "ready", "real", "reason", "rebel",
               "rebuild", "recall", "receive", "recipe", "record", "recycle", "reduce", "reflect", "reform", "refuse",
               "region", "regret", "regular", "reject", "relax", "release", "relief", "rely", "remain", "remember",
               "remind", "remove", "render", "renew", "rent", "reopen", "repair", "repeat", "replace", "report",
               "require", "rescue", "resemble", "resist", "resource", "response", "result", "retire", "retreat",
               "return", "reunion", "reveal", "review", "reward", "rhythm", "rib", "ribbon", "rice", "rich", "ride",
               "ridge", "rifle", "right", "rigid", "ring", "riot", "ripple", "risk", "ritual", "rival", "river", "road",
               "roast", "robot", "robust", "rocket", "romance", "roof", "rookie", "room", "rose", "rotate", "rough",
               "round", "route", "royal", "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle",
               "sadness", "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same", "sample", "sand",
               "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan", "scare", "scatter", "scene",
               "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script", "scrub",
               "sea", "search", "season", "seat", "second", "secret", "section", "security", "seed", "seek", "segment",
               "select", "sell", "seminar", "senior", "sense", "sentence", "series", "service", "session", "settle",
               "setup", "seven", "shadow", "shaft", "shallow", "share", "shed", "shell", "sheriff", "shield", "shift",
               "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop", "short", "shoulder", "shove", "shrimp",
               "shrug", "shuffle", "shy", "sibling", "sick", "side", "siege", "sight", "sign", "silent", "silk",
               "silly", "silver", "similar", "simple", "since", "sing", "siren", "sister", "situate", "six", "size",
               "skate", "sketch", "ski", "skill", "skin", "skirt", "skull", "slab", "slam", "sleep", "slender", "slice",
               "slide", "slight", "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke",
               "smooth", "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soda", "soft",
               "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon", "sorry", "sort", "soul",
               "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn", "speak", "special", "speed",
               "spell", "spend", "sphere", "spice", "spider", "spike", "spin", "spirit", "split", "spoil", "sponsor",
               "spoon", "sport", "spot", "spray", "spread", "spring", "spy", "square", "squeeze", "squirrel", "stable",
               "stadium", "staff", "stage", "stairs", "stamp", "stand", "start", "state", "stay", "steak", "steel",
               "stem", "step", "stereo", "stick", "still", "sting", "stock", "stomach", "stone", "stool", "story",
               "stove", "strategy", "street", "strike", "strong", "struggle", "student", "stuff", "stumble", "style",
               "subject", "submit", "subway", "success", "such", "sudden", "suffer", "sugar", "suggest", "suit",
               "summer", "sun", "sunny", "sunset", "super", "supply", "supreme", "sure", "surface", "surge", "surprise",
               "surround", "survey", "suspect", "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweet",
               "swift", "swim", "swing", "switch", "sword", "symbol", "symptom", "syrup", "system", "table", "tackle",
               "tag", "tail", "talent", "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi", "teach",
               "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text", "thank", "that", "theme",
               "then", "theory", "there", "they", "thing", "this", "thought", "three", "thrive", "throw", "thumb",
               "thunder", "ticket", "tide", "tiger", "tilt", "timber", "time", "tiny", "tip", "tired", "tissue",
               "title", "toast", "tobacco", "today", "toddler", "toe", "together", "toilet", "token", "tomato",
               "tomorrow", "tone", "tongue", "tonight", "tool", "tooth", "top", "topic", "topple", "torch", "tornado",
               "tortoise", "toss", "total", "tourist", "toward", "tower", "town", "toy", "track", "trade", "traffic",
               "tragic", "train", "transfer", "trap", "trash", "travel", "tray", "treat", "tree", "trend", "trial",
               "tribe", "trick", "trigger", "trim", "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet",
               "trust", "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle",
               "twelve", "twenty", "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella", "unable",
               "unaware", "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform", "unique",
               "unit", "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade", "uphold",
               "upon", "upper", "upset", "urban", "urge", "usage", "use", "used", "useful", "useless", "usual",
               "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van", "vanish", "vapor", "various",
               "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue", "verb", "verify", "version", "very",
               "vessel", "veteran", "viable", "vibrant", "vicious", "victory", "video", "view", "village", "vintage",
               "violin", "virtual", "virus", "visa", "visit", "visual", "vital", "vivid", "vocal", "voice", "void",
               "volcano", "volume", "vote", "voyage", "wage", "wagon", "wait", "walk", "wall", "walnut", "want",
               "warfare", "warm", "warrior", "wash", "wasp", "waste", "water", "wave", "way", "wealth", "weapon",
               "wear", "weasel", "weather", "web", "wedding", "weekend", "weird", "welcome", "west", "wet", "whale",
               "what", "wheat", "wheel", "when", "where", "whip", "whisper", "wide", "width", "wife", "wild", "will",
               "win", "window", "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise", "wish", "witness",
               "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world", "worry", "worth", "wrap", "wreck",
               "wrestle", "wrist", "write", "wrong", "yard", "year", "yellow", "you", "young", "youth", "zebra", "zero",
               "zone", "zoo"]

EXAMPLE_DOMAINS = ["example.com", "example.net", "example.org"]

SERVICE_NAMES = ["sshd", "dropbear", "apache-auth", "nginx-http-auth", "vsftpd", "postfix", "exim", "cyrus-imap",
                 "dovecot-imap", "dovecot-pop3", "mysqld-auth", "mssql-auth", "mongodb-auth"]

MAX_IPV4 = 2 ** IPv4Address(0).max_prefixlen
MAX_IPV6 = 2 ** IPv6Address(0).max_prefixlen


def generate_random_ipv4() -> IPv4Address:
    return IPv4Address(random.randint(0, MAX_IPV4))


def generate_random_ipv6() -> IPv6Address:
    return IPv6Address(random.randint(0, MAX_IPV6))


def generate_random_hostname() -> str:
    domain = random.choice(EXAMPLE_DOMAINS)
    subdomain = random.choice(BIP39_WORDS)
    return f"{subdomain}.{domain}"


def generate_random_service() -> str:
    return random.choice(SERVICE_NAMES)


def generate_hosts_row():
    host_chance = 0.8
    ipv6_chance = 0.6

    if random.random() > host_chance:
        if random.random() > ipv6_chance:
            return None, generate_random_ipv4()
        else:
            return None, generate_random_ipv6()
    else:
        return generate_random_hostname(), None


def generate_tracked_remotes_row():
    ipv6_chance = 0.4
    single_observation_chance = 0.8
    lower_time_limit = datetime.datetime(2023, 5, 1, 0, 0, 0)
    time_range = datetime.timedelta(days=7)

    if random.random() > ipv6_chance:
        ip_address = generate_random_ipv4()
    else:
        ip_address = generate_random_ipv6()

    begin_time_delta = random.randint(0, int(time_range.total_seconds()))
    end_time_delta = begin_time_delta

    if random.random() > single_observation_chance:
        end_time_delta += random.randint(1, int(time_range.total_seconds()) - begin_time_delta)

    assert begin_time_delta <= end_time_delta

    first_observation_time = lower_time_limit + datetime.timedelta(seconds=begin_time_delta)
    last_observation_time = lower_time_limit + datetime.timedelta(seconds=end_time_delta)

    return ip_address, first_observation_time, last_observation_time


def generate_services_row() -> Tuple[str]:
    return generate_random_service(),


def convert_ip_to_string(ip: IPv4Address | IPv6Address) -> str:
    return ip.compressed


def adapt_hosts_row(row: Tuple[Optional[str], Optional[IPv4Address | IPv6Address]]) -> Tuple[
    Optional[str], Optional[str]]:
    return row[0], convert_ip_to_string(row[1]) if row[1] is not None else None


def adapt_tracked_remotes_row(row: Tuple[IPv4Address | IPv6Address, datetime.datetime, datetime.datetime]) -> Tuple[
    str, datetime.datetime, datetime.datetime]:
    return convert_ip_to_string(row[0]), row[1], row[2]


def deduplicate(rows: list, key_fn: Callable) -> None:
    keys = set()

    for row in list(rows):
        key = key_fn(row)

        if key is None:
            continue

        if key in keys:
            rows.remove(row)
            continue

        keys.add(key)


def do_random_partition(l: list, n: int) -> List[list]:
    l = list(l)
    output = [[] for _ in range(n)]

    while l:
        l.remove(e := random.choice(l))
        random.choice(output).append(e)

    return output


def main() -> int:
    service_observation_chance = 0.005
    single_observation_chance = 0.4
    match_global_observation_time_chance = 0.8
    hosts_number = 100
    tracked_remotes_number = 5000
    services_number_upper_limit = 10
    service_observations_upper_limit = 10
    ban_duration = datetime.timedelta(days=14)

    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

    hosts = [(i + 1, *adapt_hosts_row(generate_hosts_row())) for i in range(hosts_number)]
    deduplicate(hosts, lambda row: row[1])
    deduplicate(hosts, lambda row: row[2])

    logging.debug(f"Generated {len(hosts)} host(s)")

    services = []

    service_id = 0
    for host_id, *_ in hosts:
        services_number = random.randint(0, services_number_upper_limit)

        for _ in range(services_number):
            service_id += 1
            services.append((service_id, host_id, *generate_services_row()))

    deduplicate(services, lambda row: (row[1], row[2]))
    logging.debug(f"Generated {len(services)} service(s)")

    tracked_remotes = [(i + 1, *adapt_tracked_remotes_row(generate_tracked_remotes_row())) for i in
                       range(tracked_remotes_number)]
    deduplicate(tracked_remotes, lambda row: row[1])
    logging.debug(f"Generated {len(tracked_remotes)} remote(s)")

    tracks = []

    track_id = 0
    for service_id, *_ in services:
        for tracked_remote_id, _, first_observation_time, last_observation_time in tracked_remotes:
            if random.random() > service_observation_chance:
                continue

            if first_observation_time == last_observation_time or random.random() < single_observation_chance:
                first_service_observation_time = first_observation_time
                last_service_observation_time = last_observation_time
                observations_count = 1
            elif random.random() < match_global_observation_time_chance:
                first_service_observation_time = first_observation_time
                last_service_observation_time = last_observation_time
                observations_count = random.randint(2, service_observations_upper_limit)
            else:
                first_service_observation_timestamp = random.randint(int(first_observation_time.timestamp()),
                                                                     int(last_observation_time.timestamp()) - 1)
                last_service_observation_timestamp = random.randint(int(first_service_observation_timestamp) + 1,
                                                                    int(last_observation_time.timestamp()))

                first_service_observation_time = datetime.datetime.fromtimestamp(first_service_observation_timestamp)
                last_service_observation_time = datetime.datetime.fromtimestamp(last_service_observation_timestamp)
                observations_count = random.randint(2, service_observations_upper_limit)

            assert first_service_observation_time <= last_service_observation_time

            track_id += 1
            tracks.append((track_id, service_id, tracked_remote_id, first_service_observation_time,
                           last_service_observation_time, observations_count))

    logging.debug(f"Generated {len(tracks)} track(s)")

    bans = []

    ban_id = 0
    for track_id, _, _, _, last_observation_time, observations_count in tracks:
        if observations_count < service_observations_upper_limit:
            continue

        ban_id += 1
        bans.append((ban_id, track_id, last_observation_time, ban_duration))

    logging.debug(f"Generated {len(bans)} ban(s)")

    with psycopg2.connect(
            host="taurus.sergeykozharinov.com",
            port="44356",
            database="postgres",
            user="postgres",
            password="iMyF4nzNGcTGkU2T"
    ) as connection:
        logging.info("Established connection to the DB")

        with connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE events, bans, tracks, tracked_remotes, services, hosts, host_access_rules, service_access_rules")

            logging.debug("Truncated existing data")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO hosts (id, hostname, ip) OVERRIDING SYSTEM VALUE VALUES %s",
                                           hosts)

            logging.debug(f"Inserted {len(hosts)} host(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO services (id, host_id, short_name) OVERRIDING SYSTEM VALUE VALUES %s",
                                           services)

            logging.debug(f"Inserted {len(services)} service(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO tracked_remotes (id, ip, first_observation_time, last_observation_time) OVERRIDING SYSTEM VALUE VALUES %s",
                                           tracked_remotes)

            logging.debug(f"Inserted {len(tracked_remotes)} remote(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO tracks (id, service_id, tracked_remote_id, first_observation_time, last_observation_time, observations_count) OVERRIDING SYSTEM VALUE VALUES %s",
                                           tracks)

            logging.debug(f"Inserted {len(tracks)} track(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO bans (id, track_id, begin_time, duration) OVERRIDING SYSTEM VALUE VALUES %s",
                                           bans)

            logging.debug(f"Inserted {len(bans)} ban(s)")

            cursor.execute("SELECT id FROM users")
            user_ids = list(map(lambda row: row[0], cursor.fetchall()))

            host_ids_by_user = do_random_partition([row[0] for row in hosts], len(user_ids))

            host_access_rules = []

            host_indices = {}

            for i, (user_id, host_ids) in enumerate(zip(user_ids, host_ids_by_user)):
                for host_id in host_ids:
                    host_indices[host_id] = i
                    host_access_rules.append((host_id, user_id, "admin"))

            logging.debug(f"Generated {len(host_access_rules)} host access rule(s)")

            service_ids_by_user = [[] for _ in range(len(user_ids))]

            for service_id, host_id, *_ in services:
                l: List[int] = service_ids_by_user[host_indices[host_id]]
                l.append(service_id)

            service_access_rules = []

            for user_id, service_ids in zip(user_ids, service_ids_by_user):
                for service_id in service_ids:
                    service_access_rules.append((service_id, user_id, "editor"))

            logging.debug(f"Generated {len(service_access_rules)} service access rule(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO host_access_rules (host_id, user_id, user_role) VALUES %s",
                                           host_access_rules)

            logging.debug(f"Inserted {len(host_access_rules)} host access rule(s)")

            psycopg2.extras.execute_values(cursor,
                                           "INSERT INTO service_access_rules (service_id, user_id, user_role) VALUES %s",
                                           service_access_rules)

            logging.debug(f"Inserted {len(service_access_rules)} service access rule(s)")

            connection.commit()

    logging.info("Done")

    return 0


if __name__ == "__main__":
    sys.exit(main())
