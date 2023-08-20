import json
import os
import re

import torch

lang_to_m2m_lang_id = {
    "ea": "ar",
    "tnt": "lo",
    "en": "en",
    "de": "de",
    "lKey": "my",
    "wordClass": "th",
}

# Processing and filter functions defining


# load all files from folder
def load_data_from_folder(folder):
    data = []
    files = os.listdir(folder)
    print(f"Ci sono {len(files)} files.")

    for fname in files:
        if fname.endswith(".json"):
            with open(os.path.join(folder, fname), encoding="utf-8") as f:
                data += json.load(f)

    print(f"Caricati {len(data)} datapoints.")

    return data


def extract_data_standard(data, src_lang, tgt_lang):
    # Filter data without ae -> target
    data = filter(
        lambda datapoint: (
            datapoint["metadata"]["source_lang"] == src_lang
            and datapoint["metadata"]["target_lang"] == tgt_lang
            and datapoint["source"] != ""
            and datapoint["target"] != ""
        ),
        data,
    )

    data = map(
        lambda datapoint: {
            "source": datapoint["source"],
            "target": datapoint["target"],
            "metadata": datapoint["metadata"],
        },
        data,
    )

    data = list(data)

    print(f"{src_lang} -> {tgt_lang}: Dopo i filtri abbiamo {len(data)} datapoints.")
    return data


# Extract ea as source and transliteration as target
def extract_data_transliteration_target(data, src_lang):
    # Filter data without ae -> transliteration
    data = filter(
        lambda datapoint: (
            datapoint["metadata"]["source_lang"] == src_lang
            and datapoint["source"] != ""
            and datapoint["transliteration"] != ""
        ),
        data,
    )

    data = map(
        lambda datapoint: {
            "source": datapoint["source"],
            "target": datapoint["transliteration"],
            "metadata": datapoint["metadata"],
        },
        data,
    )

    data = list(data)

    print(f"{src_lang} -> tnt: Dopo i filtri abbiamo {len(data)} datapoints.")
    return data


# Extract transliteration as source and traduction as target
def extract_data_transliteration_source(data, trg_lang):
    # Filter data without traduction -> transliteration
    data = filter(
        lambda datapoint: (
            datapoint["metadata"]["target_lang"] == trg_lang
            and datapoint["target"] != ""
            and datapoint["transliteration"] != ""
        ),
        data,
    )

    data = map(
        lambda datapoint: {
            "source": datapoint["transliteration"],
            "target": datapoint["target"],
            "metadata": datapoint["metadata"],
        },
        data,
    )

    data = list(data)

    print(f"tnt -> {trg_lang}: Dopo i filtri abbiamo {len(data)} datapoints.")
    return data


# Extract ea as source and lKey/wordClass as target
def extract_data_ea_lKey_or_wordClass(data, lKey_or_wordClass):
    assert lKey_or_wordClass in ("lKey", "wordClass")

    # Filter data without ae -> lKey_or_wordClass
    data = filter(
        lambda datapoint: (
            datapoint["metadata"]["source_lang"] == "ea"
            and datapoint["source"] != ""
            and datapoint[lKey_or_wordClass] != ""
            and "/" not in datapoint[lKey_or_wordClass]
        ),
        data,
    )

    data = map(
        lambda datapoint: {
            "source": datapoint["source"],
            "target": datapoint[lKey_or_wordClass],
            "metadata": datapoint["metadata"],
        },
        data,
    )

    data = list(data)

    print(f"ea -> {lKey_or_wordClass}: Dopo i filtri abbiamo {len(data)} datapoints.")
    return data


# Extract transliteration as source and lKey/wordClass as target
def extract_data_transliteration_lKey_or_wordClass(data, lKey_or_wordClass):
    assert lKey_or_wordClass in ("lKey", "wordClass")

    # Filter data without tnt -> lKey_or_wordClass
    data = filter(
        lambda datapoint: (
            datapoint["transliteration"] != ""
            and datapoint[lKey_or_wordClass] != ""
            and "/" not in datapoint[lKey_or_wordClass]
        ),
        data,
    )

    data = map(
        lambda datapoint: {
            "source": datapoint["transliteration"],
            "target": datapoint[lKey_or_wordClass],
            "metadata": datapoint["metadata"],
        },
        data,
    )

    data = list(data)

    print(f"tnt -> {lKey_or_wordClass}: Dopo i filtri abbiamo {len(data)} datapoints.")
    return data


# Processing data
def processed_data(data):
    return {
        "ea": {
            "de": extract_data_standard(data, "ea", "de"),
            "en": extract_data_standard(data, "ea", "en"),
            "tnt": extract_data_transliteration_target(data, "ea"),
            "lKey": extract_data_ea_lKey_or_wordClass(data, "lKey"),
            "wordClass": extract_data_ea_lKey_or_wordClass(data, "wordClass"),
        },
        "tnt": {
            "de": extract_data_transliteration_source(data, "de"),
            "en": extract_data_transliteration_source(data, "en"),
            "lKey": extract_data_transliteration_lKey_or_wordClass(data, "lKey"),
            "wordClass": extract_data_transliteration_lKey_or_wordClass(
                data, "wordClass"
            ),
        },
    }


# Cleaning functions defining


# Hieroglyphs cleaning
def clean_graphics(text: str) -> str:
    # Start from double spaces and sentences to delete
    text = " ".join(text.split())
    if "{m1}〈S29〉" in text:
        text = ""
    if "geschrieben" in text:
        text = ""
    if "SandhiForm" in text:
        text = ""
    if "Det.-von" in text:
        text = ""
    if "erhalten" in text:
        text = ""
    if text == "//":
        text = ""
    # Comments
    text = text.replace('"sic"', "")
    text = text.replace('"var"', "")
    text = text.replace('"Var"', "")
    text = text.replace('"var."', "")
    text = text.replace("-var", "")
    text = text.replace("-vae", "")
    text = text.replace("-+lvar+s", "")
    text = text.replace("-+linverted+s", "")
    text = text.replace('"ein Vogel"', "/")
    text = text.replace('"unleserliches Zeichen"', "/")
    text = text.replace('"lb"', "")
    text = text.replace('" lb"', "")
    text = text.replace('"lb', "")
    text = text.replace('"b"', "")
    text = text.replace('"hierat"', "")
    text = text.replace('"monogr"', "")
    text = text.replace('"monogram"', "")
    text = text.replace('"Spuren"', "")
    text = text.replace('"large"', "")
    text = text.replace('"hiero"', "")
    text = text.replace('"mutil"', "")
    text = text.replace('"composite"', "")
    text = text.replace('"vacat"', "")
    text = text.replace('"traces"', "")
    text = text.replace('"senkrechte Zeichenspur"', "")
    text = text.replace('"senkrechtes Zeichen"', "")
    # Jsesh graphic elements
    text = text.replace("**", "-")
    text = text.replace("*", "-")
    text = text.replace("//", "/")
    text = text.replace("h/", "/")
    text = text.replace("v/", "/")
    text = text.replace("#b-/#e", "/")
    text = text.replace("-:", "-")
    text = text.replace(":", "-")
    text = text.replace("[?", "").replace("?]", "")
    text = text.replace('"⸮"', "").replace('"?"', "")
    text = text.replace("\"'⸮'\"", "").replace("\"'?'\"", "")
    text = text.replace("[[", "").replace("]]", "")
    text = text.replace("[{*", "").replace("*}]", "")
    text = text.replace("[{-", "").replace("-}]", "")
    text = text.replace("[[*", "").replace("*]]", "")
    text = text.replace("[[-", "").replace("-]]", "")
    text = text.replace("[(-", "").replace("-)]", "")
    text = text.replace("(", "").replace(")", "")
    text = text.replace("$", "")
    text = text.replace("<1-0>-", "").replace("-<0-2>", "")
    text = text.replace("<1-", "").replace("-2>", "")
    text = text.replace("-<1", "")
    text = text.replace("<2-", "").replace("-1>", "")
    text = text.replace("<0-", "").replace("-0>", "")
    text = text.replace("<-", "").replace("->", "")
    text = text.replace("<", "").replace(">", "")
    text = text.replace('⸮"', "")
    text = text.replace("##", "")
    text = text.replace("v", "")
    # Specific phrase elements
    text = text.replace("ss", "S29")
    text = text.replace("nn", "M22-M22")
    text = text.replace('"lc"', "")
    # text = text.replace('"tr"', '')
    text = text.replace("prwn", "O1")
    text = text.replace("rf", "D21-I9")
    text = text.replace("ZeA", "Z2A")
    text = text.replace("j", "M17")
    text = text.replace("y1", "Y1")
    text = text.replace("z2", "Z2")
    # text = text.replace('-?9', '')
    text = text.replace("b1", "B1")
    text = text.replace("pS", "F22")
    # text = text.replace('-?', '')
    text = text.replace("_", "")
    # text = text.replace('{{89,263,62}}', '')
    # text = text.replace('{{267,6,97}}', '')
    text = text.replace('"⸮h"', "")
    text = text.replace("!", "")
    # [& parenthesis and cleaning residues
    text = text.replace('"', "")
    text = text.replace("[&", "").replace("&]", "")
    text = text.replace("&", "-")
    text = re.sub(r"-+", "-", text)
    text = text.replace("- ", " ")
    text = text.replace(" -", " ")
    text = text.strip("-")
    # \\Rx, cartouche, \\, space at end and beginning
    text = re.sub(r"\\\\R.*?(-|\s|$)", r"\1", text)
    text = re.sub(r"\\\\.*?(-|\s|$)", r"\1", text)
    text = re.sub(r"\\.*?(-|\s|$)", r"\1", text)
    text = re.sub(r"\((.*?)\)\|", r"\1", text)
    text = text.replace("\\", "")
    text = text.strip()
    # Double spaces again and -
    text = text.replace("-", " ")
    text = " ".join(text.split())
    return text


# Traduction cleaning
def clean_traduction(text):
    # Start from double spaces and sentences to delete
    text = " ".join(text.split())
    if text.endswith("..."):
        text = text[:-3].strip()
    if text == "?":
        text = text.replace("?", "")
    if "-??-" in text:
        text = ""
    text = re.sub(r"--.*?--", "--zerstört--", text)
    if "--zerstört--" in text:
        text = ""
    if "..." in text:
        text = ""
    if "…" in text:
        text = ""
    if ". . ." in text:
        text = ""
    if "_" in text:
        text = ""
    if "⸮_?" in text:
        text = ""
    if "?_?" in text:
        text = ""
    if "---?---" in text:
        text = ""
    if "---" in text:
        text = ""
    if "--" in text:
        text = ""
    if "keine Übersetzung vorhanden" in text:
        text = ""
    if "Keine Übersetzung möglich" in text:
        text = ""
    if "--- LEER GEFUNDEN ---" in text:
        text = ""
    if "---LEER GEFUNDEN---" in text:
        text = ""
    text = re.sub(r"\(=.*?\)", "", text)
    # if text == 'The':
    # text = ''
    if "[---]" in text:
        text = ""
    # lhg acronym, other languages, special parenthesis and chapter numbers
    text = re.sub(r"\(\((.*?)\)\)", r"\1", text)
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    text = text.replace('"arbustes à épines"', "dornige Sträucher")
    text = text.replace("rôdeurs", "plünderer")
    text = re.sub('\\"(.*?)"', r"\1", text)
    text = re.sub(r"(\/[\w+ÄäÖöẞßÜü]+)", " ", text)
    text = text.replace("- LHG -", " Leben, Heil, Gesundheit ")
    text = text.replace("- LHG", " Leben, Heil, Gesundheit ")
    text = text.replace("-LHG", " Leben, Heil, Gesundheit ")
    text = text.replace("- {LHG} LHG -", " Leben, Heil, Gesundheit ")
    text = text.replace("LHG", "Leben, Heil, Gesundheit")
    text = text.replace("l.h.g.", "Leben, Heil, Gesundheit")
    text = text.replace("l.h,.g.", "Leben, Heil, Gesundheit")
    text = text.replace("l.h-g", "Leben, Heil, Gesundheit")
    text = text.replace("l.h.g .", "Leben, Heil, Gesundheit")
    text = text.replace("l.h.g -", "Leben, Heil, Gesundheit")
    text = text.replace("l.h.g", "Leben, Heil, Gesundheit")
    text = text.replace("l.p.h.", "Life, Prosperity, Health")
    text = text.replace("LPH", "Life, Prosperity, Health")
    text = text.replace("„", "").replace("“", "").replace("”", "")
    text = text.replace("⸢", "").replace("⸣", "")
    text = re.sub(r"\$\[.*?\]\$", "", text)
    text = text.replace("[", "").replace("]", "")
    text = text.replace("<", "").replace(">", "")
    text = text.replace("𓉘", "").replace("𓊂", "")
    text = text.replace("𓍹", "").replace("𓍺", "")
    text = text.replace("‚", "").replace("‘", "")
    text = re.sub(r"⸮(.*?)\?", r"\1", text)
    # text = re.sub('\((.*?)\)[^\|]', ' ', text) !Attention! Problems with other parenthesis
    text = re.sub(r"\((.*?)\)\|", r"\1", text)
    text = text.replace("|", "")
    text = re.sub(r"\[§[0-9]+\]", "", text)
    text = re.sub(r"\[§[0-9]+\w+\]", "", text)
    text = re.sub(r"§[0-9]+(\s|\.|$|\,|\:|.*?)", r"\1", text)
    text = re.sub(r"§\s[0-9]+(\s|\.|$|\,|\:|.*?)", r"\1", text)
    text = re.sub(r"§\s[0-9]+-[0-9]+(\s|\.|$|\,|\:|.*?)", r"\1", text)
    text = re.sub(r"\-\s(Variante)(.*?)\-", "", text)
    text = re.sub(r"^(Variante)(.*?)$", r"\2", text)
    text = re.sub(r"(Variante)(.*?)$", "", text)
    # und, von, OA, UA acronyms and comments inside parenthesis
    text = text.replace("u.", "und")
    text = text.replace("v.", "von")
    text = text.replace(". ---", "")
    text = text.replace("--NN--", "").replace("|NN|", "").replace("NN", "")
    text = re.sub(r"\(wört.*?\)", "", text)
    text = re.sub(r"\(wört.*?$", "", text)
    text = re.sub(r"\[ältere Fassung.*?\]", "", text)
    text = re.sub(r"\(älterer Text.*?\)", "", text)
    text = re.sub(r"\(oder.*?\)", "", text)
    text = re.sub(r"^\[Beischrift.*?\]:", "", text)
    text = re.sub(r"\[Beischrift.*?\]", "", text)
    text = re.sub(r"\[.*?Beischrift.*?\]", "", text)
    text = re.sub(r"(O.?Äg?\.?)", "Oberägypten", text)
    text = re.sub(r"(U.?Äg?\.?)", "Unterägypten", text)
    text = text.strip("'").strip('"')
    text = text.strip()
    text = text.lstrip(".")
    # 〈〉 and {} parenthesis, and other elements
    text = re.sub(r"\{(.*?)\}\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\{(.*?)\}", r"\2", text)
    text = text.replace("〈〈", "").replace("〉〉", "")
    text = text.replace("{{", "").replace("}}", "")
    text = re.sub(r"(\{.*?\}\s+[\wÄäÖöẞßÜü.,=:]+\s+)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉(\s+[\wÄäÖöẞßÜü.,=:]+\s+\{.*?\})", r"\2", text)
    text = re.sub(
        r"(\{.*?\}[\wÄäÖöẞßÜü.,=:]+\s+[\wÄäÖöẞßÜü.,=:]+\s+)\〈(.*?)\〉", r"\1", text
    )
    text = re.sub(
        r"\〈(.*?)\〉([\wÄäÖöẞßÜü.,=:]+\s+[\wÄäÖöẞßÜü.,=:]+\s+\{.*?\})", r"\2", text
    )
    text = re.sub(
        r"(\{.*?\}\s+[\wÄäÖöẞßÜü.,=:]+\s+[\wÄäÖöẞßÜü.,=:]+\s+)\〈(.*?)\〉", r"\1", text
    )
    text = re.sub(
        r"\〈(.*?)\〉(\s+[\wÄäÖöẞßÜü.,=:]+\s+[\wÄäÖöẞßÜü.,=:]+\s+\{.*?\})", r"\2", text
    )
    text = re.sub(r"\〈(.*?)\〉(\s+[\wÄäÖöẞßÜü.,=:]+\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\}[\wÄäÖöẞßÜü.,=:]+\s+)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉([\wÄäÖöẞßÜü.,=:]+\s+\{.*?\})", r"\2", text)
    text = re.sub(r"\{(.*?)\}\s\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\s\{(.*?)\}", r"\2", text)
    text = re.sub(r'"(.*?)\/(.*?)"', r"\1", text)
    text = text.replace("〈", "").replace("〉", "")
    text = text.replace("{", "").replace("}", "")
    text = text.replace("Ꜥ", "ꜥ")
    text = text.replace("`", "'")
    text = text.replace("#", "")
    text = text.replace("≡", "=")
    text = text.replace("&", "und")
    text = text.replace("$", "")
    text = text.replace("(?)", "")
    text = re.sub(r"\.\s(oder[\s\wÄäÖöẞßÜü.,=:]+)", "", text)
    text = text.replace("*", "")
    text = text.replace('"', "")
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\(d\.h\.\s[\s\wÄäÖöẞßÜü.,=:]+", "", text)
    # Double spaces again
    text = " ".join(text.split())
    return text


# Transliteration cleaning
def clean_wChar(text):
    # Start from double spaces and sentences to delete
    text = " ".join(text.split())
    if "..." in text:
        text = ""
    if "_" in text:
        text = ""
    if "-??-" in text:
        text = ""
    # (()), [[]], ⸮? parenthesis, and two elements
    text = re.sub(r"\(\((.*?)\)\)", r"\1", text)
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    text = text.replace("⸮", "").replace("?", "")
    text = text.replace("~", "")
    text = (
        text.replace(".pl.", "")
        .replace(".pl", "")
        .replace(".{pl}", "")
        .replace("{.pl}", "")
        .replace(",pl", "")
        .replace(".Pl", "")
        .replace("pl", "")
    )
    # text = text.replace('{(ꜥnḫ-wḏꜣ-snb)} ꜥnḫ', 'ꜥnḫ')
    text = text.replace("[", "").replace("]", "")
    text = text.replace("-(Zahl)-", "")
    text = text.replace("oder ḫr =s", "")
    text = text.replace("ON", "").replace("GN", "")
    text = text.replace("a", "")
    text = text.replace("Zahl", "")
    text = text.replace("(", "").replace(")", "")
    text = text.replace("⸢", "").replace("⸣", "")
    text = text.replace("..1Q..", "/")
    text = text.replace("..2Q..", "/ /")
    # Inside 〈〉 and {} parenthesis
    text = re.sub(
        r"(\〈[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\〉.*?\〈[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\〉)(.*?\{[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\}.*?\{[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\})",
        r"\2",
        text,
    )
    text = re.sub(r"(\{.*?\}\s\{.*?\})\s(\〈.*?\〉\s\〈.*?\〉)", r"\1", text)
    text = re.sub(r"(\〈.*?\〉\s\〈.*?\〉)\s(\{.*?\}\s\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\}\s\{.*?\})\s\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\s(\{.*?\}\s\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\})\s(\〈.*?\〉\s\〈.*?\〉)", r"\2", text)
    text = re.sub(r"(\〈.*?\〉\s\〈.*?\〉)\s(\{.*?\})", r"\1", text)
    text = re.sub(r"(\{.*?\}\s.*?\s\{.*?\})\s(\〈.*?\〉)", r"\1", text)
    text = re.sub(r"(\〈.*?\〉\s.*?\s\〈.*?\〉)\s(\{.*?\})", r"\1", text)
    text = re.sub(r"\{(.*?)\}[^\s]\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉[^\s]\{(.*?)\}", r"\2", text)
    text = re.sub(r"\{(.*?)\}\s[^\s]\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\s[^\s]\{(.*?)\}", r"\2", text)
    text = re.sub(r"(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"(\〈.*?\〉)([a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"(\〈.*?\〉)(\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"(\〈.*?\〉)(\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s\{.*?\})", r"\2", text)
    text = re.sub(r"(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"(\〈.*?\〉)([a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s\{.*?\})", r"\2", text)
    text = re.sub(
        r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"(\〈.*?\〉)(\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\{.*?\})",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"(\〈.*?\〉)([a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\{.*?\})",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"(\〈.*?\〉)([a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s\{.*?\})",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"\〈(.*?)\〉(\{.*?\}[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"(\〈.*?\〉)(\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s\{.*?\})",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"(\〈.*?\〉)(\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\{.*?\})",
        r"\2",
        text,
    )
    text = re.sub(
        r"(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)\〈(.*?)\〉",
        r"\1",
        text,
    )
    text = re.sub(
        r"\〈(.*?)\〉(\{.*?\}\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s[a-zA-Z0-9ḤḥḪḫẖꜣꜥḏṯš.,:=i̯]+\s)",
        r"\2",
        text,
    )
    text = re.sub(r"\{(.*?)\}\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\-\{(.*?)\}", r"\2", text)
    text = re.sub(r"\{(.*?)\}\\-〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\s\{(.*?)\}", r"\2", text)
    text = re.sub(r"\{(.*?)\}\s\〈(.*?)\〉", r"\1", text)
    text = re.sub(r"\〈(.*?)\〉\{(.*?)\}", r"\2", text)
    # # Fractions
    # text = re.sub('\〈\w+\/\w+\〉\s\〈\w+\/\w+\〉\s.*?(\{\w+\/\w+\}\s\{\w+\/\w+\})', r'\1', text)
    # 〈〉 and {} parenthesis and other elements
    text = text.replace("〈", "").replace("〉", "")
    text = text.replace("{", "").replace("}", "")
    text = text.replace(":", "")
    text = text.replace(".du", "").replace(",du", "")
    text = text.replace("≡", "=")
    text = text.replace("-Lücke-", "")
    text = text.replace("Lücke", "")
    text = text.replace("-", " ")
    text = text.replace("+", "")
    text = text.replace("!", "")
    text = text.replace("ø", "")
    text = text.replace("𓍹", "").replace("𓍺", "")
    text = text.replace("⁝", "")
    text = text.replace("Präp.", "")
    text = text.replace("𓊆", "").replace("𓊇", "")
    # text = text.replace('ð', '')
    # text = text.replace('ṯb;w,t', 'ṯbw,t')
    text = text.replace("t'", "tꜥ").replace("jmj-r'", "jmj-rꜥ")
    text = text.replace("ʾ", "ꜥ")
    text = text.strip()
    # Double spaces again
    text = " ".join(text.split())
    return text


# # wordClass semplification
# def clean_wordClass(text):
#     text = text.replace('title', 'title_epithet').replace('epith_god', 'title_epithet').replace('epith_king', 'title_epithet').replace('epitheton_title', 'title_epithet')
#     text = text.replace('prepositional_adverb', 'adverb')
#     text = text.replace('nisbe_adjective_preposition', 'adjective').replace('nisbe_adjective_substantive', 'adjective')
#     text = text.replace('substantive_fem', 'substantive').replace('substantive_masc', 'substantive').replace('animal_name', 'substantive').replace('artifact_name', 'substantive')
#     text = text.replace('entity_name', 'substantive').replace('gods_name', 'substantive').replace('kings_name', 'substantive').replace('org_name', 'substantive')
#     text = text.replace('person_name', 'substantive').replace('place_name', 'substantive').replace('root', 'substantive')
#     text = text.replace('cardinal', 'numeral').replace('ordinal', 'numeral')
#     text = text.replace('particle_enclitic', 'particle').replace('particle_nonenclitic', 'particle').replace('interjection', 'particle')
#     text = text.replace('personal_pronoun', 'pronoun').replace('demonstrative_pronoun', 'pronoun').replace('relative_pronoun', 'pronoun').replace('interrogative_pronoun', 'pronoun')
#     text = text.replace('verb_2-gem', 'verb').replace('verb_2-lit', 'verb').replace('verb_3-gem', 'verb').replace('verb_3-inf', 'verb').replace('verb_3-lit', 'verb')
#     text = text.replace('verb_4-inf', 'verb').replace('verb_4-lit', 'verb').replace('verb_5-inf', 'verb').replace('verb_5-lit', 'verb').replace('verb_6-lit', 'verb')
#     text = text.replace('verb_caus_2-gem', 'verb').replace('verb_caus_2-lit', 'verb').replace('verb_caus_3-gem', 'verb').replace('verb_caus_3-inf', 'verb')
#     text = text.replace('verb_caus_3-lit', 'verb').replace('verb_caus_4-inf', 'verb').replace('verb_caus_4-lit', 'verb').replace('verb_caus_5-lit', 'verb')
#     text = text.replace('verb_irr', 'verb')
#     return text


# Clean all data function
def clean_data(data):
    for datapoint in data:
        datapoint["source"] = clean_graphics(datapoint["source"])
        datapoint["transliteration"] = clean_wChar(datapoint["transliteration"])
        datapoint["target"] = clean_traduction(datapoint["target"])
        # datapoint['wordClass'] = clean_wordClass(datapoint['wordClass'])
    return data


# Training functions defining: batch_it, tokenize_batch, training_stes, validations_step
def batch_it(sequence, batch_size=1, return_last=True):
    if batch_size <= 0:
        raise ValueError(
            f"Batch size cannot be nonpositive. Passed `batch_size = {batch_size}`"
        )

    batch = []
    for item in sequence:
        if len(batch) == batch_size:
            yield batch
            batch = []
        batch.append(item)

    if batch and return_last:
        yield batch


def tokenize_batch(model, batch, tokenizer, src_lang, tgt_lang):
    tokenizer.src_lang = src_lang
    tokenizer.tgt_lang = tgt_lang

    tokenized_batch = tokenizer(
        [element["source"] for element in batch],
        text_target=[element["target"] for element in batch],
        max_length=64,
        padding=True,
        truncation=True,
        return_tensors="pt",
    ).to(model.device)

    tokenized_batch["labels"] = torch.where(
        tokenized_batch["labels"] == tokenizer.pad_token_id,
        torch.full_like(tokenized_batch["labels"], -100),
        tokenized_batch["labels"],
    )

    return tokenized_batch


def training_step(batch, model, tokenizer, optimizer, src_lang, tgt_lang):
    with torch.cuda.amp.autocast():
        tokenized_batch = tokenize_batch(model, batch, tokenizer, src_lang, tgt_lang)
        loss = model(**tokenized_batch).loss

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        return loss.item()


def validation_step(batch, model, tokenizer, src_lang, tgt_lang):
    with torch.no_grad():
        with torch.cuda.amp.autocast():
            tokenized_batch = tokenize_batch(
                model, batch, tokenizer, src_lang, tgt_lang
            )
            loss = model(**tokenized_batch).loss

            return loss.item(), (tokenized_batch["labels"] != -100).sum().item()
