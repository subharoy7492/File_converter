import re

class BijoyToUnicodeV1:
    """Version 1 of Bijoy to Unicode Converter Engine (Fixed)"""
    
    def __init__(self):
        # Maps ordered longest-key-first
        self.pre_conversion_map = [
            (r' +', ' '),
            (r'yy', 'y'),
            (r'vv', 'v'),
            (r'­­', '­'),
            (r'y&', 'y'),
            (r'„&', '„'),
            (r'‡u', 'u‡'),
            (r'wu', 'uw'),
            (r' ,', ','),
            (r' \|', '|'),
            (r'\\ ', ''),
            (r' \\', ''),
            (r'\\', ''),
            (r'\n +', '\n'),
            (r' +\n', '\n'),
            (r'\n{3,}', '\n\n')
        ]

        # Key-value mapping array (sorted by key length descending to prevent sub-string collision)
        raw_conversion_map = {
            'Av': 'আ', 'A': 'অ', 'B': 'ই', 'C': 'ঈ', 'D': 'উ', 'E': 'ঊ',
            'F': 'ঋ', 'G': 'এ', 'H': 'ঐ', 'I': 'ও', 'J': 'ঔ',
            'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ', 'P': 'চ',
            'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ', 'U': 'ট', 'V': 'ঠ',
            'W': 'ড', 'X': 'ঢ', 'Y': 'ণ', 'Z': 'ত', '_': 'থ', '`': 'দ',
            'a': 'ধ', 'b': 'ন', 'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ',
            'g': 'ম', 'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ',
            'm': 'স', 'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়', 'r': 'ৎ',
            's': 'ং', 't': 'ঃ', 'u': 'ঁ',
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫',
            '6': '৬', '7': '৭', '8': '৮', '9': '৯',
            '•': 'ঙ্', 'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ু',
            '“': 'ু', '–': 'ু', '~': 'ূ', 'ƒ': 'ূ', '‚': 'ূ', '„„': 'ৃ',
            '„': 'ৃ', '…': 'ৃ', '†': 'ে', '‡': 'ে', 'ˆ': 'ৈ', '‰': 'ৈ',
            'Š': 'ৗ', '|': '।', '&': '্‌', '^': '্ব', '‘': '্তু',
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

        # Sort keys by length descending so longer tokens match first
        self.conversion_map = sorted(
            [(re.escape(k), v) for k, v in raw_conversion_map.items()],
            key=lambda item: len(item[0]),
            reverse=True
        )

        self.post_conversion_map = [
            (r'০ঃ', '০:'), (r'১ঃ', '১:'), (r'২ঃ', '২:'), (r'৩ঃ', '৩:'), (r'৪ঃ', '৪:'),
            (r'৫ঃ', '৫:'), (r'৬ঃ', '৬:'), (r'৭ঃ', '৭:'), (r'৮ঃ', '৮:'), (r'৯ঃ', '৯:'),
            (r' ঃ', ' :'), (r'\nঃ', '\n:'), (r']ঃ', ']:'), (r'\[ঃ', '[:'),
            (r'  ', ' '), (r'অা', 'আ'), (r'্‌্‌', '্‌')
        ]

    def is_bangla_pre_kar(self, c):
        return c in ('ি', 'ৈ', 'ে')

    def is_bangla_banjonborno(self, c):
        return c in (
            'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 
            'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 
            'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'
        )

    def is_bangla_halant(self, c):
        return c == '্'

    def re_arrange_unicode_converted_text(self, text):
        chars = list(text)
        i = 0
        n = len(chars)

        # Step 1: Shift pre-kars (ি, ে, ৈ) after consonant cluster/conjuncts
        res = []
        while i < n:
            c = chars[i]
            if self.is_bangla_pre_kar(c) and (i + 1 < n) and self.is_bangla_banjonborno(chars[i + 1]):
                kar = c
                i += 1
                cluster = []
                
                # Consume the consonant cluster (e.g. ক + ্ + ষ)
                while i < n and self.is_bangla_banjonborno(chars[i]):
                    cluster.append(chars[i])
                    if i + 1 < n and self.is_bangla_halant(chars[i + 1]):
                        cluster.append(chars[i + 1])
                        i += 2
                    else:
                        i += 1
                        break
                
                # Check for combined vowel signs (ে + া -> ো / ে + ৗ -> ৌ)
                if kar == 'ে' and i < n:
                    if chars[i] == 'া':
                        kar = 'ো'
                        i += 1
                    elif chars[i] == 'ৗ':
                        kar = 'ৌ'
                        i += 1

                res.extend(cluster)
                res.append(kar)
            else:
                res.append(c)
                i += 1

        text = "".join(res)

        # Step 2: Handle Ref (র্) shifting
        # Move 'র' + '্' behind consonant cluster
        chars = list(text)
        i = 0
        n = len(chars)
        res = []
        while i < n:
            if i + 1 < n and chars[i] == 'র' and chars[i + 1] == '্':
                # Check if it's a ref (followed by a consonant)
                if i + 2 < n and self.is_bangla_banjonborno(chars[i + 2]):
                    ref = ['র', '্']
                    i += 2
                    cluster = []
                    while i < n and self.is_bangla_banjonborno(chars[i]):
                        cluster.append(chars[i])
                        if i + 1 < n and self.is_bangla_halant(chars[i + 1]):
                            cluster.append(chars[i + 1])
                            i += 2
                        else:
                            i += 1
                            break
                    # Append kar if present right after consonant
                    if i < n and chars[i] in ('ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ', 'া'):
                        cluster.append(chars[i])
                        i += 1
                    
                    res.extend(ref)
                    res.extend(cluster)
                    continue

            res.append(chars[i])
            i += 1

        return "".join(res)

    def convert(self, src_string):
        if not src_string:
            return ""

        # Pre-conversion replacements
        for pattern, replacement in self.pre_conversion_map:
            src_string = re.sub(pattern, replacement, src_string)

        # Primary character mapping
        for pattern, replacement in self.conversion_map:
            src_string = re.sub(pattern, replacement, src_string)

        # Structural rearrangement (Pre-kar and Ref handling)
        src_string = self.re_arrange_unicode_converted_text(src_string)

        # Post-conversion replacements
        for pattern, replacement in self.post_conversion_map:
            src_string = re.sub(pattern, replacement, src_string)

        return src_string
