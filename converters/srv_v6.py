import re

class SrvToUnicodeV6:
    """Version 3 of STM to Unicode Converter Engine with dynamic regex escaping"""

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
            "õþÉ": "র‌্য",
            "èÉ": "্র্য",
            "„": "ক্ষ্ম",
            "!Â˛": "ক্ক",
            "!": "ক্ক",
            "\"": "ক্ট",
            "MW  ": "ক্ত্ব",
            "M": "ক্ত",
            "$Â": "ক্ব",
            "$": "ক্ব",
            "¦ Â": "স্ক্র",
            "S ": "ক্র",
            "ßvÂ": "ক্ল",
            "ßv": "ক্ল",
            "ß®Â": "ক্ন",
            "ß®": "ক্ন",
            "%": "ক্ম",
            "Ž®Â": "ক্ষ্ণ",
            "Ž®": "ক্ষ্ণ",
            "ŽWÂ": "ক্ষ্ব",
            "ŽW": "ক্ষ্ব",
            "ãŽÂ": "ঙ্ক্ষ",
            "ãŽ": "ঙ্ক্ষ",
            "ŽÂ": "ক্ষ",
            "Ž": "ক্ষ",
            "'": "ক্স",
            "àW": "খ্ব",
            "\\)": "গ্গ",
            "¢ð": "গ্দ",
            "\\*": "গ্ধ",
            "¢Ÿ": "গ্ন",
            "¢«": "গ্ব",
            "¢¬": "গ্ম",
            "¢­": "গ্ল",
            "âW": "ঘ্ব",
            "â®": "ঘ্ন",
            "‚Â": "ঙ্ক",
            "‚": "ঙ্ক",
            "\\[": "ঙ্ম",
            "º": "ভ্র",
            "/": "।",
            "Á": "ঙ্",
            "B\\(W": "চ্ছ্ব",
            "BäÂ": "চ্চ",
            "Bä": "চ্চ",
            "B\\(": "চ্ছ",             
            "Žµ": "চ্ঞ",             
            "åW": "ছ্ব",             
            "#;": "জ্জ্ব",             
            "#": "জ্জ",             
            "~": "জ্ঝ",             
            ":": "জ্ঞ",             
            "æW": "জ্ব",             
            "<": "জ্র",             
            "=Â": "ঞ্চ",             
            "=": "ঞ্চ",             
            ">": "ঞ্ছ",             
            "?": "ঞ্জ",             
            "@": "ঞ্ঝ",             
            "A": "ট্ট",             
            "éWÂ": "ট্ব",             
            "éW": "ট্ব",             
            "DÂ": "ড্ড",             
            "D": "ড্ড",             
            "E": "ড্র",             
            "°éÂ": "ণ্ট",             
            "°é": "ণ্ট",             
            "F": "ণ্ঠ",             
            "°ìÂ": "ণ্ঢ",             
            "J": "ণ্ণ",             
            "°¬": "ণ্ম",             
            "k": "ন্স",             
            "GÂ": "ণ্ড",             
            "G": "ণ্ড",            
            "c": "ন্তু",             
            "°«": "ণ্ব",             
            "N": "ত্ত্ব",             
            "M ˜": "ক্ত্র",             
            "M": "ত্ত",             
            "O": "ত্থ",             
            "P": "ত্ন",             
            "R": "ত্ম",             
            "îvÂ": "ত্ল",             
            "îv": "ত্ল",             
            "bLÂ": "ন্ত্ব",             
            "bL": "ন্ত্ব",             
            "b¦Â": "স্ত্ব",             
            "b¦": "স্ত্ব",             
            "Q": "ত্ব",             
            "S": "ত্র",             
            "ïW": "থ্ব",             
            "e": "ন্দ্ব",
            "¢ð": "গ্দ",
            "\\*": "গ্ধ",
            "¢Ÿ": "গ্ন",
            "¢«": "গ্ব",
            "¢¬": "গ্ম",
            "¢­": "গ্ল",
            "âW": "ঘ্ব",
            "â®": "ঘ্ন",
            "‚Â": "ঙ্ক",
            "‚": "ঙ্ক",
            "\\[": "ঙ্ম",
            "º": "ভ্র",
            "/": "।",
            "Á": "ঙ্",
            "B\\(W": "চ্ছ্ব",
            "BäÂ": "চ্চ",
            "Bä": "চ্চ",
            "B\\(": "চ্ছ",
            "¢ð": "গ্দ",
            "\\*": "গ্ধ",
            "¢Ÿ": "গ্ন",
            "¢«": "গ্ব",
            "¢¬": "গ্ম",
            "¢­": "গ্ল",
            "âW": "ঘ্ব",
            "â®": "ঘ্ন",
            "‚Â": "ঙ্ক",
            "‚": "ঙ্ক",
            "\\[": "ঙ্ম",
            "º": "ভ্র",
            "/": "।",
            "Á": "ঙ্",
            "B\\(W": "চ্ছ্ব",
            "BäÂ": "চ্চ",
            "Bä": "চ্চ",
            "B\\(": "চ্ছ",
            "Žµ": "চ্ঞ",
            "åW": "ছ্ব",
            "#;": "জ্জ্ব",
            "#": "জ্জ",
            "~": "জ্ঝ",
            ":": "জ্ঞ",
            "æW": "জ্ব",
            "<": "জ্র",
            "=Â": "ঞ্চ",
            "=": "ঞ্চ",
            ">": "ঞ্ছ",
            "?": "ঞ্জ",
            "@": "ঞ্ঝ",
            "A": "ট্ট",
            "éWÂ": "ট্ব",
            "éW": "ট্ব",
            "DÂ": "ড্ড",
            "D": "ড্ড",
            "E": "ড্র",
            "°éÂ": "ণ্ট",
            "°é": "ণ্ট",
            "F": "ণ্ঠ",
            "°ìÂ": "ণ্ঢ",
            "J": "ণ্ণ",
            "°¬": "ণ্ম",
            "k": "ন্স",
            "GÂ": "ণ্ড",
            "G": "ণ্ড",
            "c": "ন্তু",
            "°«": "ণ্ব",
            "N": "ত্ত্ব",
            "M ˜": "ক্ত্র",
            "M": "ত্ত",
            "O": "ত্থ",
            "P": "ত্ন",
            "R": "ত্ম",
            "îvÂ": "ত্ল",
            "îv": "ত্ল",
            "bLÂ": "ন্ত্ব",
            "bL": "ন্ত্ব",
            "b¦Â": "স্ত্ব",
            "b¦": "স্ত্ব",
            "Q": "ত্ব",
            "S": "ত্র",
            "ïW": "থ্ব",
            "e": "ন্দ্ব",
            "VW": "দ্দ্ব",
            "V": "দ্দ",
            "Y": "দ্ধ্ব",
            "XÂ": "দ্ধ",
            "X": "দ্ধ",
            "ð®": "দ্ন",
            "Z": "দ্ব",
            "\\ž": "দ্ভ্র",
            "¾": "দ্ভ",
            "½": "দ্ম",
            "^": "দ্র",
            "ñ®": "ধ্ন",
            "ñT": "ধ্ব",
            "KéÂ": "ন্ট",
            "Ké": "ন্ট",
            "_": "ন্ঠ",
            "`Â": "ন্ড",
            "`": "ন্ড",
            "\\™L": "ন্ত",
            "La": "ন্ত্র",
            "Lš": "ন্থ",
            "j": "ন্দ",
            "gÂ": "ন্ধ",
            "g": "ন্ধ",
            "i§": "ন্ন",
            "L¤": "ন্ব",
            "iœ": "ন্ম",
            "f": "ন্দ্র",
            "›éÂ": "প্ট",
            "l": "প্ত",
            "›Ÿ": "প্ন",
            "m": "প্প",
            "óv": "প্ল",
            "o": "প্স",
            "ôvÂ": "ফ্ল",
            "ôv": "ফ্ল",
            "r": "ব্জ",
            "s": "ব্দ",
            "t": "ব্ধ",
            "u": "ব্ভ",
            "õT": "ব্ব",
            "õv": "ব্ল",
            "övÂ": "ভ্ল",
            "öv": "ভ্ল",
            "¥¨": "ম্ন",
            "¦x": "স্প্র",
            "¥x": "ম্প্র",
            "©óª": "ষ্প্র",
            "¥ó": "ম্প",
            "¥£Â": "ম্ফ",
            "¥£": "ম্ফ",
            "©¤": "ষ্ব",
            "¥¤": "ম্ব",
            "yÂ": "ম্ভ",
            "y": "ম্ভ",
            "z": "ম্ভ্র",
            "¥œ": "ম্ম",
            "¥": "ম্ল",
            "{¨": "ল্ক",
            "‰": "ল্গ",
            "ŒÂ": "ল্ট",
            "Œ": "ল্ট",
            "‹": "ল্ড",
            "Š": "ল্প",
            "{£Â": "ল্ফ",
            "{£": "ল্ফ",
            "{": "ল্ল",
            "{œ": "ল্ম",
            "q": "শু",
            "}Â": "শ্চ",
            "}": "শ্চ",
            " \\(": "শ্ছ",
            " Ÿ": "শ্ন",
            " «": "শ্ব",
            " ¬": "শ্ম",
            " ­ ­": "শ্ল",
            "|": "শ্র",
            "À": "শ্রী",
            "©¨": "ষ্ক",
            "© Â": "ষ্ক্র",
            "© ": "ষ্ক্র",
            "©†": "ষ্ট",
            "‡Â": "ষ্ঠ",
            "‡": "ষ্ঠ",
            "øž": "ষ্ণ",
            "©ó": "ষ্প",
            "©£Â": "ষ্ফ",
            "©£": "ষ্ফ",
            "ƒ": "ষ্ম",
            "¦¨": "স্ক",
            "ˆÂ": "স্ট",
            "ˆ": "স্ট",
            "…": "স্খ",
            "™¦": "স্ত",
            "d": "স্তু",
            "¦a": "স্ত্র",
            "¦š": "স্থ",
            "¦§": "স্ন",
            "¦ó": "স্প",
            "›¶": "প্র",
            "¦£Â": "স্ফ",
            "¦£": "স্ফ",
            "¦¤": "স্ব",
            "¦œ": "স্ম",
            "¦¡": "স্ল",
            "¦Ú": "স্র",
            "U": "হু",
            "": "হ্ণ",
            "ýW": "হ্ব",
            "ý": "হ্ন",
            "p": "হ্ম",
            "¥Ú": "ম্র",
            "ý+": "হৃ",
            "há": "ড়্গ",
            "¢¶": "গ্র",
            "&": "গু",
            "Ç": "র্",
            "Õ±": "আ",
            "Õ": "অ",
            "ý×": "ই",
            "Ö": "ঈ",
            "ëÂ×": "উ",
            "Ø": "ঊ",
            "Ù": "ঋ",
            "Û": "এ",
            "Ü": "ঐ",
            "Ý": "ও",
            "Þ": "ঔ",
            "ßÂ": "ক",
            "ß": "ক",
            "à": "খ",
            "á": "গ",
            "â": "ঘ",
            "ã": "ঙ",
            "äÂ": "চ",
            "ä": "চ",
            "å": "ছ",
            "æ": "জ",
            "çÂ": "ঝ",
            "ç": "ঝ",
            "Ûž": "ঞ",
            "éÂ": "ট",
            "é": "ট",
            "ê": "ঠ",
            "hÂ": "ড়",
            "ëÂ": "ড",
            "ë": "ড",
            "ìÂÿ": "ঢ়",
            "ÿ": "়",
            "ìÂ": "ঢ",
            "ì": "ঢ",
            "í": "ণ",
            "îÂ": "ত",
            "î": "ত",
            "ï": "থ",
            "ð": "দ",
            "ñ": "ধ",
            "ò": "ন",
            "Âó": "প",
            "ôÂ": "ফ",
            "ô": "ফ",
            "õþ": "র",
            "þ": "়",
            "õ": "ব",
            "öÂ": "ভ",
            "ö": "ভ",
            "÷": "ম",
            "ûþ": "য়",
            "û": "য",
            "ù": "ল",
            "ú": "শ",
            "ø¸": "ষ",
            "ø": "ষ",
            "ü": "স",
            "ý": "হ",
            "È": "ৎ",
            "±": "া",
            "¿": "ি",
            "Ï": "ী",
            "Å": "ু",
            "³": "ু",
            "n": "ু",
            "Ó": "ূ",
            "²": "ূ",
            "+": "ূ",
            "Ô": "ৃ",
            "´": "ৃ",
            "Ë": "ে",
            "Î": "ে",
            "Í": "ৈ",
            "Æ": "ৈ",
            "Ì": "ৗ",
            "Â": "",
            "¯": "!",
            "•": "(",
            "—": ")",
            "\\”": "*",
            "¼": "।",
            "\\\\/": "।",
            "\\\\ ­": ":",
            "€": ";",
            "·": "?",
            "‘": "‘",
            "’": "’",
            "Ñ": "ং",
            "Ð": "ঃ",
            "Ò": "ঁ",
            "è": "্র",
            "¶": "্র",
            "ª": "্র",
            "˜": "্র",
            "Ú": "্র",
            "É": "্য",
            "Ä": "্",
            "\\]": "ৰ",
            "»": "ৱ"
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
        # Using re.escape on keys prevents invalid regex group errors
        for src_key, key_val in char_map.items():
            text = re.sub(re.escape(src_key), key_val, text)
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