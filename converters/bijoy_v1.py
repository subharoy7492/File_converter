import re

class BijoyToUnicodeV1:
    """Version 1 of Bijoy to Unicode Converter Engine"""
    
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
            'Av': 'আ', 'A': 'অ', 'B': 'ই', 'C': 'ঈ', 'D': 'উ', 'E': 'ঊ',
            'F': 'ঋ', 'G': 'এ', 'H': 'ঐ', 'I': 'ও', 'J': 'ঔ',
            'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ', 'P': 'চ',
            'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ', 'U': 'ট', 'V': 'ঠ',
            'W': 'ড', 'X': 'ঢ', 'Y': 'ণ', 'Z': 'ত', '_': 'থ', '`': 'দ',
            'a': 'ধ', 'b': 'ন', 'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ',
            'g': 'ম', 'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ',
            'm': 'স', 'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়', 'r': 'ৎ',
            's': 'ং', 't': 'ঃ', 'u': 'ঁ',
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫',
            '6': '৬', '7': '৭', '8': '৮', '9': '৯',
            '•': 'ঙ্', 'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ু',
            '“': 'ু', '–': 'ু', '~': 'ূ', 'ƒ': 'ূ', '‚': 'ূ', '„„': 'ৃ',
            '„': 'ৃ', '…': 'ৃ', '†': 'ে', '‡': 'ে', 'ˆ': 'ৈ', '‰': 'ৈ',
            'Š': 'ৗ', r'\|': '।', r'\&': '্‌', r'\^': '্ব', '‘': '্তু',
            '’': '্থ', '‹': '্ক', 'Œ': '্ক্র', '”': 'চ্', '—': '্ত',
            '˜': 'দ্', '™': 'দ্', 'š': 'ন্', '›': 'ন্', 'œ': '্ন',
            'Ÿ': '্ব', '¡': '্ব', '¢': '্ভ', '£': '্ভ্র', '¤': 'ম্',
            '¥': '্ম', '¦': '্ব', '§': '্ম', '¨': '্য', '©': 'র্',
            'ª': '্র', '«': '্র', '¬': '্ল', '­': '্ল', '®': 'ষ্',
            '¯': 'স্', '°': 'ক্ক', '±': 'ক্ট', '²': 'ক্ষ্ণ', '³': 'ক্ত',
            '´': 'ক্ম', 'µ': 'ক্র', '¶': 'ক্ষ', '·': 'ক্স', '¸': 'গু',
            '¹': 'জ্ঞ', 'º': 'গ্দ', '»': 'গ্ধ', '¼': 'ঙ্ক', '½': 'ঙ্গ',
            '¾': 'জ্জ', '¿': '্ত্র', 'À': 'জ্ঝ', 'Á': 'জ্ঞ', 'Â': 'ঞ্চ',
            'Ã': 'ঞ্ছ', 'Ä': 'ঞ্জ', 'Å': 'ঞ্ঝ', 'Æ': 'ট্ট', 'Ç': 'ড্ড',
            'È': 'ণ্ট', 'É': 'ণ্ঠ', 'Ê': 'ণ্ড', 'Ë': 'ত্ত', 'Ì': 'ত্থ',
            'Í': 'ত্ম', 'Î': 'ত্র', 'Ï': 'দ্দ', 'Ð': '-', 'Ñ': '-',
            'Ò': '"', 'Ó': '"', 'Ô': "'", 'Õ': "'", 'Ö': '্র',
            '×': 'দ্ধ', 'Ø': 'দ্ব', 'Ù': 'দ্ম', 'Ú': 'ন্ঠ', 'Û': 'ন্ড',
            'Ü': 'ন্ধ', 'Ý': 'ন্স', 'Þ': 'প্ট', 'ß': 'প্ত', 'à': 'প্প',
            'á': 'প্স', 'â': 'ব্জ', 'ã': 'ব্দ', 'ä': 'ব্ধ', 'å': 'ভ্র',
            'æ': 'ম্ন', 'ç': 'ম্ফ', 'è': '্ন', 'é': 'ল্ক', 'ê': 'ল্গ',
            'ë': 'ল্ট', 'ì': 'ল্ড', 'í': 'ল্প', 'î': 'ল্ফ', 'ï': 'শু',
            'ð': 'শ্চ', 'ñ': 'শ্ছ', 'ò': 'ষ্ণ', 'ó': 'ষ্ট', 'ô': 'ষ্ঠ',
            'õ': 'ষ্ফ', 'ö': 'স্খ', '÷': 'স্ট', 'ø': 'স্ন', 'ù': 'স্ফ',
            'ú': '্প', 'û': 'হু', 'ü': 'হৃ', 'ý': 'হ্ন', 'þ': 'হ্ম'
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
