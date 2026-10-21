class PrashikaV8Engine:
    DISPLAY_NAME = "Adarshalipi/Bangla Word/Prashika (v8)"

    def __init__(self):
        self.pre_kar = {'ি', 'ৈ', 'ে'}
        self.post_kar = {'া', 'ো', 'ৌ', 'ৗ', 'ু', 'ূ', 'ী', 'ৃ'}
        self.kar = self.pre_kar.union(self.post_kar)
        self.banjonborno = set("কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমশষসহযরলয়ড়ঢ়ঢ়ংঃঁ")
        self.halant = '্'
        self.space = {' ', '\t', '\n', '\r', '\u00a0'}

        # Updated ANSI to Unicode mapping synchronized with the HTML converter
        self.map_pairs = {
            "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪", "5": "৫",
            "6": "৬", "7": "৭", "8": "৮", "9": "৯", "lÉ": "র‌্য", "ËÉ": "্র্য",
            "rÈ": "ক্ষ্ম", "‚": "ক্ক", "ƒ": "ক্ট", "š²Å": "ক্ত্ব", "š²": "ক্ত",
            "LÅ": "ক্ব", "û": "স্ক্র", "œ²": "ক্র", "LÓ": "ক্ল", "LÁ": "ক্ন",
            "LÈ": "ক্ম", "rÁ": "ক্ষ্ণ", "rÅ": "ক্ষ্ব", "´r": "ঙ্ক্ষ", "r": "ক্ষ",
            "„": "ক্স", "MÅ": "খ্ব", "†": "গ্গ", "³c": "গ্দ", "‡": "গ্ধ",
            "NÀ": "গ্ন", "NÄ": "গ্ব", "NÈ": "গ্ম", "NÔ": "গ্ল", "OÅ": "ঘ্ব",
            "OÀ": "ঘ্ন", "ˆ": "ঙ্ক", "PÈ": "ঙ্ম", "´M": "ঙ্খ", "‰": "ঙ্গ",
            "´": "ঙ্", "µRÅ": "চ্ছ্ব", "µQ": "চ্চ", "µR": "চ্ছ", "Š": "চ্ঞ",
            "RÅ": "ছ্ব", "‹Æ": "জ্জ্ব", "‹": "জ্জ", "Œ": "জ্ঝ", "‘": "জ্ঞ",
            "SÆ": "জ্ব", "SÊ": "জ্র", "’": "ঞ্চ", "“": "ঞ্ছ", "”": "ঞ্জ",
            "•": "ঞ্ঝ", "–": "ট্ট", "VÄ": "ট্ব", "—": "ড্ড", "XÊ": "ড্র",
            "¸V": "ণ্ট", "˜": "ণ্ঠ", "¸Y": "ণ্ঢ", "ZÀ": "ণ্ণ", "ZÈ": "ণ্ম",
            "¾p": "ন্স", "™": "ণ্ড", "ZÄ": "ণ্ব", "šÆ": "ত্ত্ব", "NÎþ": "ক্ত্র",
            "š": "ত্ত", "›": "ত্থ", "aÀ": "ত্ন", "aÈ": "ত্ম", "aÆ": "ত্ব",
            "¿¹Æ": "ন্ত্ব", "Ù¹Æ": "স্ত্ব", "œ": "ত্র", "bË": "থ্র", "¾à": "ন্দ—",
            "ŸÄ": "দ্দ্ব", "Ÿ": "দ্দ", "Þ": "দ্ধ্ব", "Ü": "দ্ধ", "cÀ": "দ্ন",
            "à": "দ্ব", "á": "দ্ভ", "cÈ": "দ্ম", "â": "দ্র", "dÀ": "ধ্ন",
            "dÆ": "ধ্ব", "dÈ": "ধ্ম", "¾V": "ন্ট", "ã": "ন্ঠ", "ä": "ন্ড",
            "¿¹": "ন্ত", "¿»": "ন্ত্র", "¿Û": "ন্থ", "¾c": "ন্দ", "å": "ন্ধ",
            "æ": "ন্ন", "eÄ": "ন্ব", "eÈ": "ন্ম", "¾cÊ": "ন্দ্র", "ÃV": "প্ট",
            "ç": "প্ত", "fÀ": "প্ন", "è": "প্প", "fÔ": "প্ল", "Ãp": "প্স",
            "gÓ": "ফ্ল", "ê": "ব্জ", "ë": "ব্দ", "ì": "ব্ধ", "î": "ব্ব",
            "hÔ": "ব্ল", "ï": "ভ্র", "iÔ": "ভ্ল", "jÀ": "ম্ন", "ØfË": "স্প্র",
            "ÇfË": "ম্প্র", "×fË": "ষ্প্র", "Çf": "ম্প", "Çg": "ম্ফ", "×h": "ষ্ব",
            "ð": "ম্ব", "ñ": "ম্ভ", "Çj": "ম্ম", "Çm": "ম্ল", "ó": "ল্ক",
            "ÒN": "ল্গ", "ÒV": "ল্ট", "ô": "ল্ড", "Òf": "ল্প", "Òg": "ল্ফ",
            "mÄ": "ল্ব", "mÈ": "ল্ম", "õ": "ল্ল", "ö": "শু", "ÕQ": "শ্চ",
            "ÕR": "শ্ছ", "nÀ": "শ্ন", "nÄ": "শ্ব", "nÈ": "শ্ম", "nÔ": "শ্ল",
            "nË": "শ্র", "×L": "ষ্ক", "×œ²": "ষ্ক্র", "ø": "ষ্ট", "ù": "ষ্ঠ",
            "o·": "ষ্ণ", "×f": "ষ্প", "×g": "ষ্ফ", "×j": "ষ্ম", "ú": "স্ক",
            "ØV": "স্ট", "ØM": "স্খ", "Ù¹": "স্ত", "Ù»": "স্ত্র", "ÙÛ": "স্থ",
            "pÀ": "স্ন", "Øf": "স্প", "fË": "প্র", "Øg": "স্ফ", "ü": "স্ব",
            "Øj": "স্ম", "pÔ": "স্ল", "pË": "স্র", "ý": "হু", "qÀ": "হ্ণ",
            "qÄ": "হ্ব", "q²": "হ্ন", "þ": "হ্ম", "jË": "ম্র", "qÓ": "হ্ল",
            "q©": "হৃ", "NË": "গ্র", "…": "গু", "Ñ": "র্", "B": "আ",
            "A": "অ", "C": "ই", "D": "ঈ", "E": "উ", "F": "ঊ",
            "G": "ঋ", "H": "এ", "I": "ঐ", "J": "ও", "K": "ঔ",
            "L": "ক", "M": "খ", "N": "গ", "O": "ঘ", "P": "ঙ",
            "Q": "চ", "R": "ছ", "S": "জ", "T": "ঝ", "U": "ঞ",
            "V": "ট", "W": "ঠ", "s": "ড়", "X": "ড", "t": "ঢ়",
            "ÿ": "়", "Y": "ঢ", "Z": "ণ", "a": "ত", "b": "থ",
            "c": "দ", "d": "ধ", "e": "ন", "f": "প", "g": "ফ",
            "l": "র", "Í": "়", "h": "ব", "i": "ভ", "j": "ম",
            "u": "য়", "k": "য", "m": "ল", "n": "শ", "o": "ষ",
            "p": "স", "q": "হ", "v": "ৎ", "¡": "া", "¢": "ি",
            "£": "ী", "¤": "ু", "¥": "ু", "§": "ূ", "¨": "ূ",
            "ª": "ৃ", "«": "ৃ", "\u00AD": "ে", "®": "ে", "¯": "ৈ",
            "°": "ৈ", "±": "ৗ", "w": "ং", "x": "ঃ", "y": "ঁ",
            "Ê": "্র", "Ë": "্র", "Ì": "্র", "Ð": "্র", "É": "্য",
            "Ú": "্", "z": "।"
        }

    def _apply_mappings(self, text):
        # Sort keys by length descending to maintain correct replacement order without tuples
        sorted_patterns = sorted(self.map_pairs.keys(), key=len, reverse=True)
        for pattern in sorted_patterns:
            if pattern in text:
                text = text.replace(pattern, self.map_pairs[pattern])
        return text

    def rearrange_unicode_converted_phrase(self, text):
        i = 0
        while i < len(text):
            if i < len(text) - 1 and text[i] in self.pre_kar and text[i + 1] not in self.space:
                distance = 1
                while (i + distance < len(text) and text[i + distance] in self.banjonborno):
                    if (i + distance + 1 < len(text) and text[i + distance + 1] == self.halant):
                        distance += 2
                    else:
                        break

                rebuilt = text[:i] + text[i + 1:i + distance + 1]
                extra = 0
                if text[i] == "ে" and i + distance + 1 < len(text) and text[i + distance + 1] in ("া", "ো"):
                    rebuilt += "ো"
                    extra = 1
                elif text[i] == "ে" and i + distance + 1 < len(text) and text[i + distance + 1] in ("ৗ", "ৌ"):
                    rebuilt += "ৌ"
                    extra = 1
                else:
                    rebuilt += text[i]

                rebuilt += text[i + distance + extra + 1:]
                text = rebuilt
                i += distance
            i += 1

        i = 0
        while i < len(text):
            if (i < len(text) - 1 and text[i] == "র" and text[i + 1] == self.halant and text[i - 1:i] != self.halant):
                distance = 1
                while True:
                    if i - distance < 0:
                        break
                    if (text[i - distance] in self.banjonborno and text[i - distance - 1:i - distance] == self.halant):
                        distance += 2
                    elif distance == 1 and text[i - distance] in self.kar:
                        distance += 1
                    else:
                        break
                text = text[:i - distance] + text[i] + text[i + 1] + text[i - distance:i] + text[i + 2:]
                i += 1
                continue
            i += 1

        return text

    def convert_phrase(self, phrase):
        if not phrase:
            return ""
        converted = self._apply_mappings(phrase)
        converted = self.rearrange_unicode_converted_phrase(converted)
        return converted.replace("অা", "আ").replace("্্", "্")