import re

class StmToUnicodeV3:
    """Version 3 of STM to Unicode Converter Engine"""

    def __init__(self):
        self.pre_conversion_map = {
            r' +': ' ',
            r'yy': 'y',
            r'vv': 'v',
            r'­­': '­',
            r'y&': 'y',
            r'„&': '„',
            r'‡u': 'u‡',
            r'wu': 'uw',
            r' ,': ',',
            r' \|': '\|',
            r'\\ ': '',
            r' \\': '',
            r'\\': '',
            r'\n +': '\n',
            r' +\n': '\n',
            r'\n\n\n\n\n': '\n\n',
            r'\n\n\n\n': '\n\n',
            r'\n\n\n': '\n\n'
        }

        self.conversion_map = {
            "0": "০",
            "1": "১",
            "2": "২",
            "3": "৩",
            "4": "৪",
            "5": "৫",
            "6": "৬",
            "7": "৭",
            "8": "৮",
            "9": "৯",
            "îûÄ": "র‌্য",
            "ÊÄ": "্র্য",
            "\"": "ক্ষ্ম",
            "Eþ": "ক্ক",
            "E": "ক্ক",
            "Q": "ক্ট",
            "_´«": "ক্ত্ব",
            "_«": "ক্ত",
            "ðþ": "ক্ব",
            "ð": "ক্ব",
            "ßþ;": "স্ক্র",
            "ß;": "স্ক্র",
            "e«": "ক্র",
            "ßþÏñ": "স্ক্ল",
            "„Ïþ": "ক্ল",
            "„Ï": "ক্ল",
            "„øþ": "ক্ন",
            "„ø": "ক্ন",
            "©": "ক্ম",
            "Çøþ": "ক্ষ্ণ",
            "Çø": "ক্ষ্ণ",
            "Ç´þ": "ক্ষ্ব",
            "Ç´": "ক্ষ্ব",
            "AÇþ": "ঙ্ক্ষ",
            "AÇ": "ঙ্ক্ষ",
            "A": "ঙ্",
            "Çþ": "ক্ষ",
            "Ç": "ক্ষ",
            ":": "ক্স",
            "…´": "খ্ব",
            ">": "গ্গ",
            "@”": "গ্দ",
            "\\?þ": "গ্ধ",
            "\\?": "গ্ধ",
            "@À": "গ্ন",
            "@»": "গ্ব",
            "@Â": "গ্ম",
            "@Õ": "গ্ল",
            "@Ì": "গ্র",
            "‡´": "ঘ্ব",
            "‡ø": "ঘ্ন",
            "Bþ": "ঙ্ক",
            "B": "ঙ্ক",
            "-": "ঙ্ম",
            "C": "ঙ্খ",
            "D": "ঙ্গ",
            "A‡": "ঙ্ঘ",
            "FŠ´é": "চ্ছ্ব",
            "FŠ´": "চ্ছ্ব",
            "F‰þ": "চ্চ",
            "F‰": "চ্চ",
            "FŠé": "চ্ছ",
            "FŠ": "চ্ছ",
            "Žþ": "চ্ঞ",
            "Ž": "চ্ঞ",
            "Š´é": "ছ্ব",
            "Š´": "ছ্ব",
            "Iµ": "জ্জ্ব",
            "I": "জ্জ",
            "J": "জ্ঝ",
            "Kþé": "জ্ঞ",
            "K": "জ্ঞ",
            "‹µ": "জ্ব",
            "L": "জ্র",
            "Mþé": "ঞ্চ",
            "M": "ঞ্চ",
            "Nþ": "ঞ্ছ",
            "N": "ঞ্ছ",
            "O": "ঞ্জ",
            "P": "ঞ্ঝ",
            "R": "ট্ট",
            "Ý´þ": "ট্ব",
            "Ý´": "ট্ব",
            "Uþ": "ড্ড",
            "U": "ড্ড",
            "\\^ùÝþ": "ণ্ট",
            "\\^ùÝ": "ণ্ট",
            "Zþ": "ণ্ঠ",
            "Z": "ণ্ঠ",
            "\\^éW": "ণ্ঢ",
            "\\]": "ণ্ণ",
            "\\^ùéÂ": "ণ্ম",
            "ª": "ন্স",
            "\\[þ": "ণ্ড",
            "\\[": "ণ্ড",
            "lsþ": "ন্তু",
            "ls": "ন্তু",
            "\\^é»": "ণ্ব",
            "_´": "ত্ত্ব",
            "_É«": "ক্ত্র",
            "_": "ত্ত",
            "a": "ত্থ",
            "b": "ত্ন",
            "d": "ত্ম",
            "“Ïþ": "ত্ল",
            "“Ï": "ত্ল",
            "gsþ": "ন্ত্ব",
            "gs": "ন্ত্ব",
            "gßþ": "স্ত্ব",
            "gß": "স্ত্ব",
            "c": "ত্ব",
            "e": "ত্র",
            "íÏ": "থ্ল",
            "í´": "থ্ব",
            "rm": "ন্দ্ব",
            "å†": "দ্গ",
            "å‡": "দ্ঘ",
            "jµ": "দ্দ্ব",
            "j": "দ্দ",
            "k´þ": "দ্ধ্ব",
            "k´": "দ্ধ্ব",
            "kþ": "দ্ধ",
            "k": "দ্ধ",
            "”ø": "দ্ন",
            "m": "দ্ব",
            "ž": "দ্ভ্র",
            "q": "দ্ভ",
            "p": "দ্ম",
            "o": "দ্র",
            "•ø": "ধ্ন",
            "•¹": "ধ্ব",
            "rÝþ": "ন্ট",
            "rÝ": "ন্ট",
            "tþ": "ন্ঠ",
            "t": "ন্ঠ",
            "uþ": "ন্ড",
            "u": "ন্ড",
            "hsþ": "ন্ত",
            "hs": "ন্ত",
            "sþf": "ন্ত্র",
            "sþi": "ন্থ",
            "¨": "ন্দ",
            "rm": "ন্দ্ব",
            "õþ": "ন্ধ",
            "õ": "ন্ধ",
            "§¬": "ন্ন",
            "§º": "ন্ব",
            "§Ã": "ন্ম",
            "²Wz": "প্ট",
            "®": "প্ত",
            "²À": "প্ন",
            "¯": "প্প",
            "²Õ": "প্ল",
            "°": "প্স",
            "šÏþ": "ফ্ল",
            "šÏ": "ফ্ল",
            "¶": "ব্জ",
            "·": "ব্দ",
            "w": "ন্দ্র",
            "¸þ": "ব্ধ",
            "¸": "ব্ধ",
            "î¹": "ব্ব",
            "îÏ": "ব্ল",
            "¼": "ভ্র",
            "¦Ïþ": "ভ্ল",
            "¦Ï": "ভ্ল",
            "Á¬": "ম্ন",
            "ßþ±": "স্প্র",
            "Á±": "ম্প্র",
            "Ü±": "ষ্প্র",
            "Á™": "ম্প",
            "Á³þ": "ম্ফ",
            "Á³": "ম্ফ",
            "Üº": "ষ্ব",
            "Áº": "ম্ব",
            "½þ": "ম্ভ",
            "½": "ম্ভ",
            "¾": "ম্ভ্র",
            "Á¿": "ম্ম",
            "ÁÔ": "ম্ল",
            "Íñ": "ল্ক",
            "Ñ": "ল্গ",
            "Î¢": "ল্স",
            "ÎÝþ": "ল্ট",
            "ÎÝ": "ল্ট",
            "Óþ": "ল্ড",
            "Ó": "ল্ড",
            "Ò": "ল্প",
            "Í³þ": "ল্ফ",
            "Í³": "ল্ফ",
            "Íº": "ল্ব",
            "ÍÃ": "ল্ম",
            "ÍÔ": "ল্ল",
            "Ö": "শু",
            "Øþ": "শ্চ",
            "Ø": "শ্চ",
            "ÙŠé": "শ্ছ",
            "ÙŠ": "শ্ছ",
            "ÙÀ": "শ্ন",
            "Ù»": "শ্ব",
            "ÙÂ": "শ্ম",
            "ÙÕ": "শ্ল",
            "×": "শ্র",
            "Üñ": "ষ্ক",
            "Ü;þ": "ষ্ক্র",
            "Ü;": "ষ্ক্র",
            "ÜT": "ষ্ট",
            "Ûþ": "ষ্ঠ",
            "Û": "ষ্ঠ",
            "¡Œ": "ষ্ণ",
            "Ü™": "ষ্প",
            "Ü³þ": "ষ্ফ",
            "Ü³": "ষ্ফ",
            "Ü¿": "ষ্ম",
            "ßþñ": "স্ক",
            "ÞÝþ": "স্ট",
            "ÞÝ": "স্ট",
            "ßþ<": "স্খ",
            "hßþ": "স্ত",
            "hß": "স্ত",
            "lßþ": "স্তু",
            "lß": "স্তু",
            "ßþf": "স্ত্র",
            "ßþi": "স্থ",
            "ßþ¬": "স্ন",
            "ßþ™": "স্প",
            "²Ì": "প্র",
            "ßþ³þ": "স্ফ",
            "ßþ³": "স্ফ",
            "ßþº": "স্ব",
            "ßþ¿": "স্ম",
            "ßþÔ": "স্ল",
            "ßþË": "স্র",
            "ßþñ": "স্ক",
            "ý": "হু",
            "ã": "হ্ণ",
            "£¹": "হ্ব",
            "£«": "হ্ন",
            "áþ": "হ্ম",
            "á": "হ্ম",
            "ÁË": "ম্র",
            "â": "হ্ল",
            "£\\*": "হৃ",
            "X†": "ড়্গ",
            "@ùÌ": "গ্র",
            "€": "ল্গু",
            "=": "গু",
            "Å": "র্",
            "xy": "আ",
            "x": "অ",
            "£z": "ই",
            "{": "ঈ",
            "vþz": "উ",
            "\\|": "ঊ",
            "}": "ঋ",
            "~": "এ",
            "ú": "ঐ",
            "ç": "ও",
            "è": "ঔ",
            "Y": "়ু",
            "„þ": "ক",
            "„": "ক",
            "…": "খ",
            "†": "গ",
            "‡": "ঘ",
            "ˆ": "ঙ",
            "‰þ": "চ",
            "‰": "চ",
            "Šé": "ছ",
            "Š": "ছ",
            "‹": "জ",
            "Gþ": "ঝ",
            "G": "ঝ",
            "~Œ": "ঞ",
            "Ýþ": "ট",
            "Ý": "ট",
            "àþ": "ঠ",
            "à": "ঠ",
            "vþü": "ড়",
            "vþ": "ড",
            "v": "ড",
            "‘þü": "ঢ়",
            "‘þ": "ঢ",
            "‘": "ঢ",
            "’": "ণ",
            "“þ": "ত",
            "“": "ত",
            "í": "থ",
            "”": "দ",
            "•": "ধ",
            "˜": "ন",
            "þ™": "প",
            "™": "প",
            "šþ": "ফ",
            "š": "ফ",
            "îû": "র",
            "î": "ব",
            "¦þ": "ভ",
            "¦": "ভ",
            "›": "ম",
            "ëû": "য়",
            "ë": "য",
            "œ": "ল",
            "Ÿ": "শ",
            "¡ì": "ষ",
            "¢": "স",
            "£": "হ",
            "ê": "ৎ",
            "þ": "",
            "é": "",
            "y": "া",
            "!": "ি",
            "#": "ী",
            "%": "ু",
            "\\)": "ূ",
            "\\(": "ূ",
            "&": "ু",
            "\\$": "ু",
            "\\*": "ূ",
            ",": "ৃ",
            "öì": "ে",
            "ö": "ে",
            "÷ì": "ৈ",
            "÷": "ৈ",
            "ï": "ৗ",
            "ì": "",
            "æ": "!",
            "S": "(",
            "V": ")",
            "–": ",",
            "éôé": "-",
            "ô": "-",
            "Ð": "।",
            "­": ":",
            "—": ";",
            "Ú": "?",
            "ò": "‘",
            "ó": "’",
            "‚": "ং",
            "ƒ": "ঃ",
            "¤": "ঁ",
            "Ê": "্র",
            "Æ": "্র",
            "È": "্র",
            "É": "্র",
            "Ä": "্য",
            "ä": "্",
            "r": "ন্"
        }

        self.pro_conversion_map = {'্্': '্'}

        self.post_conversion_map = {
            r'০ঃ': '০:', r'১ঃ': '১:', r'২ঃ': '২:', r'৩ঃ': '৩:', r'৪ঃ': '৪:',
            r'৫ঃ': '৫:', r'৬ঃ': '৬:', r'৭ঃ': '৭:', r'৮ঃ': '৮:', r'৯ঃ': '৯:',
            r' ঃ': ' :', r'\nঃ': '\n:', r']ঃ': ']:', r'\[ঃ': '[:',
            r'  ': ' ', r'অা': 'আ', r'্‌্‌': '্‌'
        }

    def is_bangla_pre_kar(self, c):
        return c in ('ি', 'ৈ', 'ে')

    def is_bangla_post_kar(self, c):
        return c in ('া', 'ো', 'ৌ', 'ৗ', 'ু', 'ূ', 'ী', 'ৃ')

    def is_bangla_kar(self, c):
        return self.is_bangla_pre_kar(c) or self.is_bangla_post_kar(c)

    def is_bangla_banjonborno(self, c):
        return c in (
            'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ',
            'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ',
            'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'
        )

    def is_bangla_nukta(self, c):
        return c == 'ঁ'

    def is_bangla_halant(self, c):
        return c == '্'

    def is_space(self, c):
        return c in (' ', '\t', '\n', '\r')

    def _mb_char_at(self, string, i):
        return string[i] if 0 <= i < len(string) else ''

    def _substring(self, string, start, end):
        return string[start:end]

    def _do_char_map(self, text, char_map):
        for src_key, key_val in char_map.items():
            text = re.sub(src_key, key_val, text)
        return text

    def re_arrange_unicode_converted_text(self, str_val):
        i = 0
        while i < len(str_val):
            if (i < len(str_val) - 1 and self._mb_char_at(str_val, i) == 'র' and
                self.is_bangla_halant(self._mb_char_at(str_val, i + 1)) and
                not self.is_bangla_halant(self._mb_char_at(str_val, i - 1))):
                j = 1
                while True:
                    if i - j < 0: break
                    if (self.is_bangla_banjonborno(self._mb_char_at(str_val, i - j)) and
                        self.is_bangla_halant(self._mb_char_at(str_val, i - j - 1))):
                        j += 2
                    elif j == 1 and self.is_bangla_kar(self._mb_char_at(str_val, i - j)):
                        j += 1
                    else: break

                temp = self._substring(str_val, 0, i - j)
                temp += self._mb_char_at(str_val, i) + self._mb_char_at(str_val, i + 1)
                temp += self._substring(str_val, i - j, i)
                temp += self._substring(str_val, i + 2, len(str_val))
                str_val = temp
                i += 1
                continue
            i += 1

        str_val = self._do_char_map(str_val, self.pro_conversion_map)

        i = 0
        while i < len(str_val):
            if (i < len(str_val) - 1 and self._mb_char_at(str_val, i) == 'র' and
                self.is_bangla_halant(self._mb_char_at(str_val, i + 1)) and
                not self.is_bangla_halant(self._mb_char_at(str_val, i - 1)) and
                self.is_bangla_halant(self._mb_char_at(str_val, i + 2))):
                j = 1
                while True:
                    if i - j < 0: break
                    if (self.is_bangla_banjonborno(self._mb_char_at(str_val, i - j)) and
                        self.is_bangla_halant(self._mb_char_at(str_val, i - j - 1))):
                        j += 2
                    elif j == 1 and self.is_bangla_kar(self._mb_char_at(str_val, i - j)):
                        j += 1
                    else: break

                temp = self._substring(str_val, 0, i - j)
                temp += self._mb_char_at(str_val, i) + self._mb_char_at(str_val, i + 1)
                temp += self._substring(str_val, i - j, i)
                temp += self._substring(str_val, i + 2, len(str_val))
                str_val = temp
                i += 1
                continue

            if (i > 0 and self._mb_char_at(str_val, i) == '\u09CD' and
                (self.is_bangla_kar(self._mb_char_at(str_val, i - 1)) or self.is_bangla_nukta(self._mb_char_at(str_val, i - 1))) and
                i < len(str_val) - 1):
                temp = self._substring(str_val, 0, i - 1)
                temp += self._mb_char_at(str_val, i) + self._mb_char_at(str_val, i + 1) + self._mb_char_at(str_val, i - 1)
                temp += self._substring(str_val, i + 2, len(str_val))
                str_val = temp

            if (i < len(str_val) - 1 and self.is_bangla_pre_kar(self._mb_char_at(str_val, i)) and
                not self.is_space(self._mb_char_at(str_val, i + 1))):
                temp = self._substring(str_val, 0, i)
                j = 1
                while (i + j) < len(str_val) - 1 and self.is_bangla_banjonborno(self._mb_char_at(str_val, i + j)):
                    if (i + j) < len(str_val) and self.is_bangla_halant(self._mb_char_at(str_val, i + j + 1)):
                        j += 2
                    else: break

                temp += self._substring(str_val, i + 1, i + j + 1)
                l = 0
                if self._mb_char_at(str_val, i) == 'ে' and self._mb_char_at(str_val, i + j + 1) == 'া':
                    temp += "ো"; l = 1
                elif self._mb_char_at(str_val, i) == 'ে' and self._mb_char_at(str_val, i + j + 1) == "ৗ":
                    temp += "ৌ"; l = 1
                else:
                    temp += self._mb_char_at(str_val, i)

                temp += self._substring(str_val, i + j + l + 1, len(str_val))
                str_val = temp
                i += j

            i += 1
        return str_val

    def convert(self, src_string):
        if not src_string:
            return ""
        src_string = self._do_char_map(src_string, self.pre_conversion_map)
        src_string = self._do_char_map(src_string, self.conversion_map)
        src_string = self.re_arrange_unicode_converted_text(src_string)
        src_string = self._do_char_map(src_string, self.post_conversion_map)
        return src_string
