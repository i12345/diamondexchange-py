from enum import Enum
import os
from typing import Optional, Union

class USFMMarkerContents:
    name: Optional[str] = None
    level: Optional[int] = None
    number: Optional[int] = None
    text: Optional[str] = None
    nested: bool = False
    descendants: Optional[list["USFMMarkerContents"]] = None
    attributes: Optional[dict[str, str]] = None

class Option(Enum):
    off = "off"
    optional = "optional"
    required = "required"

class USFMMarkerFormat:
    def __init__(
            self,
            name: Optional[str],
            leveled: Option = Option.off,
            closed: Option = Option.off,
            attributes: Option = Option.off,
            default_attribute: Optional[str] = None,
            text: Option = Option.off,
            numbered: Option = Option.off,
            nested: Option = Option.off,
            may_contain: Optional[list[Union["USFMMarkerFormat", str]]] = None
        ):
        self.name = name
        self.leveled = leveled
        self.closed = closed
        self.attributes = attributes
        self.default_attribute = default_attribute
        self.text = text
        self.numbered = numbered
        self.nested = nested
        self.may_contains = may_contain

    def parse(self, text: str, start: int, formats: dict[str, dict[str | None, "USFMMarkerFormat"]]) -> tuple[USFMMarkerContents, int] | None:
        if start == len(text):
            return None

        contents = USFMMarkerContents()

        def skip_whitespace():
            nonlocal start
            while start < len(text) and text[start].isspace():
                start += 1

        opening_marker = None # type: Optional[str]
        start_marker = start

        if self.name is not None:
            if text[start] != '\\':
                return None
            start += 1

            if text[start] == '+':
                if self.nested == Option.off:
                    return None
                contents.nested = True
                start += 1
            
            if contents.nested == Option.required:
                if contents.nested == False:
                    return None

            if not text.startswith(self.name, start):
                return None
            start += len(self.name)

            if not (len(text) == start or (text[start].isspace() or text[start].isdigit())):
                return None

            contents.name = self.name

            if self.leveled == Option.optional or self.leveled == Option.required:
                end_attribute_list = start
                while end_attribute_list < len(text) and text[end_attribute_list].isdigit():
                    end_attribute_list += 1

                if end_attribute_list > start:
                    contents.level = int(text[start:end_attribute_list])
                    start = end_attribute_list
                else:
                    if self.leveled == Option.required:
                        return None
                    else:
                        contents.level = 1

            end_marker = start
            opening_marker = text[start_marker:end_marker]

            skip_whitespace()

        if self.numbered != Option.off:
            end_attribute_list = len(text)

            space_following = text.find(' ', start)
            line_following = text.find('\n', start)
            marker_following = text.find('\\', start)
            attributes_following = text.find('|', start) if self.attributes != Option.off else -1

            if space_following != -1 and space_following < end_attribute_list:
                end_attribute_list = space_following
            if line_following != -1 and line_following < end_attribute_list:
                end_attribute_list = line_following
            if marker_following != -1 and marker_following < end_attribute_list:
                end_attribute_list = marker_following
            if attributes_following != -1 and attributes_following < end_attribute_list:
                end_attribute_list = attributes_following
            
            try:
                contents.number = int(text[start:end_attribute_list])
                start = end_attribute_list
                skip_whitespace()
            except ValueError:
                if self.numbered == Option.required:
                    return None
        
        if self.text != Option.off:
            end_attribute_list = len(text)

            marker_following = text.find('\\', start)
            line_following = text.find('\n', start)
            attributes_following = text.find('|', start) if self.attributes != Option.off else -1

            if marker_following != -1 and marker_following < end_attribute_list:
                end_attribute_list = marker_following
            if line_following != -1 and line_following < end_attribute_list:
                end_attribute_list = line_following
            if attributes_following != -1 and attributes_following < end_attribute_list:
                end_attribute_list = attributes_following

            contents.text = text[start:end_attribute_list].strip()
            if len(contents.text) == 0:
                if self.text == Option.required:
                    return None
            
            start = end_attribute_list
            skip_whitespace()

        if self.may_contains:
            state = True

            while state:
                state = False

                def applyFormat(format: USFMMarkerFormat) -> bool:
                    nonlocal start
                    marker_following_parse = format_parser.parse(text, start, formats=formats)
                    if marker_following_parse != None:
                        marker_following, start = marker_following_parse
                        if contents.descendants is None: 
                            contents.descendants = []
                        contents.descendants.append(marker_following)
                        return True
                    return False

                for format in self.may_contains:
                    if isinstance(format, str):
                        if format.startswith('{') and format.endswith('}'):
                            category = format[1:-1]
                            for format_parser in formats[category].values():
                                if applyFormat(format_parser):
                                    state = True
                                    break
                        else:
                            format_parser = next(format_category for format_category in formats.values() if format in format_category)[format]
                            if applyFormat(format_parser):
                                state = True
                                break
                    else:
                        if applyFormat(format):
                            state = True
                            break
        
        if self.attributes != Option.off:
            if text[start] != '|':
                if self.attributes == Option.required:
                    return None
            
            start += 1
            skip_whitespace()

            start_attribute_list = start
            end_attribute_list = len(text)

            marker_following = text.find('\\', start)

            if marker_following != -1 and marker_following < end_attribute_list:
                end_attribute_list = marker_following
            
            contents.attributes = {}

            while start_attribute_list < end_attribute_list:
                end_attribute_A = end_attribute_list

                space_following = text.find(' ', start_attribute_list, end_attribute_list)
                equal_sign_following = text.find('=', start_attribute_list, end_attribute_list)

                if space_following != -1 and space_following < end_attribute_A:
                    end_attribute_A = space_following
                if equal_sign_following != -1 and equal_sign_following < end_attribute_A:
                    end_attribute_A = equal_sign_following

                if space_following ==  end_attribute_A:
                    contents.attributes[self.default_attribute] = text[start_attribute_list:end_attribute_A]
                    start_attribute_list = end_attribute_A
                else:
                    start_attribute_name = start_attribute_list
                    end_attribute_name = end_attribute_A
                    
                    start_attribute_list = end_attribute_name
                    assert text[start_attribute_list] == '='
                    start_attribute_list += 1
                    assert text[start_attribute_list] == '"'
                    start_attribute_list += 1

                    start_attribute_value = start_attribute_list
                    end_attribute_value = text.find('"', start_attribute_value, end_attribute_list)
                    assert end_attribute_value != -1
                    start_attribute_list = end_attribute_value + 1

                    attribute_name = text[start_attribute_name:end_attribute_name]
                    attribute_value = text[start_attribute_value:end_attribute_value]

                    contents.attributes[attribute_name] = attribute_value

                while start_attribute_list < end_attribute_list and text[start_attribute_list].isspace():
                    start_attribute_list += 1

            start = end_attribute_list
            skip_whitespace()

        if self.closed != Option.off:
            assert opening_marker is not None
            closing_marker = f"{opening_marker}*"
            if not text.startswith(closing_marker, start):
                if self.closed == Option.required:
                    return None
            else:
                start += len(closing_marker)
                skip_whitespace()

        return contents, start

class USFMMarkerFormatsCharacter:
    _category = "character"
    text = USFMMarkerFormat(None, text=Option.required)
    word = USFMMarkerFormat("w", text=Option.required, closed=Option.required, attributes=Option.optional, default_attribute="lemma", nested=Option.optional)
    addition = USFMMarkerFormat("add", text=Option.required, closed=Option.required, may_contain=["{character}"])
    verse = USFMMarkerFormat("v", numbered=Option.required)
    selah = USFMMarkerFormat("qs", closed=Option.required, may_contain=['{character}'])
    footnote = USFMMarkerFormat("f", text=Option.optional, closed=Option.optional, may_contain=["{character}", "{footnote}"])

class USFMMarkerFormatsFootnote:
    _category = "footnote"
    footnote_origin_reference = USFMMarkerFormat("fr", text=Option.required, closed=Option.optional)
    footnote_text = USFMMarkerFormat("ft", text=Option.required, closed=Option.optional)
    footnote_translation = USFMMarkerFormat("fq", text=Option.required, closed=Option.optional)
    footnote_translation_alternative = USFMMarkerFormat("fqa", text=Option.required, closed=Option.optional)
    footnote_keyword = USFMMarkerFormat("fk", text=Option.required, closed=Option.optional)
    footnote_label = USFMMarkerFormat("fl", text=Option.required, closed=Option.optional)
    footnote_paragraph = USFMMarkerFormat("fp")
    footnote_verse_number = USFMMarkerFormat("fv", numbered=Option.required, closed=Option.optional)

class USFMMarkerFormatsParagraph:
    _category = "paragraph"

    qc = USFMMarkerFormat("qc", text=Option.required)
    poetic_line = USFMMarkerFormat("q", leveled=Option.optional)

    descriptive_title = USFMMarkerFormat("d", may_contain=["{character}"])
    major_section_heading = USFMMarkerFormat("ms", leveled=Option.optional, may_contain=["{character}"])
    no_break = USFMMarkerFormat("nb")
    paragraph = USFMMarkerFormat("p")
    paragraph_embedded = USFMMarkerFormat("pm")
    paragraph_indented = USFMMarkerFormat("pi", leveled=Option.optional)
    blank_line = USFMMarkerFormat("b")
    margin_paragraph = USFMMarkerFormat("m")
    
class USFMMarkerFormatsFile:
    _category = "file"

    chapter = USFMMarkerFormat("c", numbered=Option.required, may_contain=["{character}", "{paragraph}"])
    title_major = USFMMarkerFormat("mt", leveled=Option.optional, text=Option.required)
    table_of_contents = USFMMarkerFormat("toc", leveled=Option.optional, text=Option.required)
    header = USFMMarkerFormat("h", text=Option.required)
    id = USFMMarkerFormat("id", text=Option.required)

class USFMFile:
    def __init__(
            self,
            filename: str,
            contents: list[USFMMarkerContents]
        ):
        self.filename = filename
        self.contents = contents

def read_Bible_USFM(directory: str, skip: Optional[list[str]] = None) -> list[USFMFile]:
    
    def formatCategory(formats) -> str:
        return next(category for key, category in vars(formats).items() if key.endswith("_category"))

    def formatMap(formats):
        return { format.name: format for format in vars(formats).values() if isinstance(format, USFMMarkerFormat) }
    
    formats = { formatCategory(formats): formatMap(formats) for formats in [USFMMarkerFormatsCharacter, USFMMarkerFormatsParagraph, USFMMarkerFormatsFootnote, USFMMarkerFormatsFile] }

    files = [] # type: list[USFMFile]

    for filename in os.listdir(directory):
        if not filename.endswith(".usfm") or (skip is not None and filename in skip):
            continue

        contents = [] # type: list[USFMMarkerContents]

        text: str
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            text = file.read()

        start = 0
        
        while start < len(text):
            parsed = False

            for format in formats[USFMMarkerFormatsFile._category].values():
                result = format.parse(text, start, formats=formats)
                if result is not None:
                    parsed = True
                    content, start = result
                    contents.append(content)
                    break

            if not parsed:
                raise NotImplementedError()
        
        files.append(USFMFile(filename=filename, contents=contents))
    
    return files
