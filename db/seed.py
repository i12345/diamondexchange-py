# db/seed.py
import io
from sqlmodel import SQLModel, Session
from src.db.database import get_session, engine, init_db
from src.models import Item, ItemChildrenDisplayClass, ItemChild

from dataclasses import dataclass
from typing import List, Callable, Iterable
import re
import os

def reset_all():
    SQLModel.metadata.drop_all(engine)

def load_initial_data(reset: bool = True):
    if reset:
        reset_all()
    init_db()

    with get_session() as session:
        load_KJ(session=session)

def load_KJ(session: Session):
    @dataclass
    class Verse:
        index: str
        text: str

    @dataclass
    class Paragraph:
        verses: list[Verse]

    @dataclass
    class Chapter:
        index: int
        paragraphs: list[Paragraph]

    @dataclass
    class Book:
        title: str
        chapters: list[Chapter]

    def save(item_book: list[Book], rendering: str):
        child_books = [] # type: list[ItemChild]

        local_index_book = 0
        for book in item_book:
            child_chapters = [] # type: list[ItemChild]

            local_index_chapter = 0
            for chapter in book.chapters:
                child_paragraphs = [] # type: list[ItemChild]

                local_index_paragraph = 0
                for paragraph in chapter.paragraphs:
                    child_verses = [] # type: list[ItemChild]

                    local_index_verse = 0
                    for verse in paragraph.verses:
                        verse_note = Item(text=verse.text)
                        session.add(verse_note)
                        child_verses.append(ItemChild(local_index=local_index_verse, local_label=verse.index, child=verse_note))
                        local_index_verse += 1

                    item_paragraph = Item(child_display_class=ItemChildrenDisplayClass.INLINE, children=child_verses)
                    session.add(item_paragraph)
                    child_paragraphs.append(ItemChild(local_index=local_index_paragraph, child=item_paragraph))
                    local_index_paragraph += 1

                item_chapter = Item(text=f"{chapter.index}", child_display_class=ItemChildrenDisplayClass.BLOCK, children=child_paragraphs)
                session.add(item_chapter)
                child_chapters.append(ItemChild(local_index=local_index_chapter, label=f"{chapter.index}", child=item_chapter))
                local_index_chapter += 1

            item_book = Item(text=book.title, child_display_class=ItemChildrenDisplayClass.PAGINATION, children=child_chapters)
            session.add(item_book)
            session.commit()
            child_books.append(ItemChild(local_index=local_index_book, local_label=book.title, child=item_book))
            local_index_book += 1

        Bible = Item(text=f"Bible ({rendering})", child_display_class=ItemChildrenDisplayClass.ACCORDION, children=child_books)
        session.add(Bible)
        session.commit()
        # session.refresh(Bible)
        return Bible

    # This generator function yields paragraphs formatted from unformatted verses
    def format_verses(verses_unformatted: List[str], short_title_callback: Callable[[str], None], chapter_reference_str: str) -> Iterable[Paragraph]:
        paragraph_sign = "¶"
        SUPERSCRIPT = "superscript"
        
        current_paragraph: List[Verse] = []
        verse_index_prev = 0
        verse_index = 0
        text_index = 0

        for verse in verses_unformatted:
            verse_index_matches = re.search(r'\d+', verse)
            if not verse_index_matches:
                if verse_index_prev > 0:
                    print(f"Unexpected line in {chapter_reference_str}: {verse}")
                    continue
                else:
                    verse_index = SUPERSCRIPT
                    text_index = 0
            else:
                verse_index = int(verse_index_matches.group(0))
                text_index = len(verse_index_matches.group(0))

            if not ((verse_index_prev == 0) or (verse_index == verse_index_prev + 1) or (verse_index > verse_index_prev and verse_index < verse_index_prev + 5)):
                short_title_callback(verse)
                break

            verse_index_prev = verse_index if verse_index != SUPERSCRIPT else 0 

            if paragraph_sign in verse:
                split = verse.split(paragraph_sign)
                split[0] = split[0][text_index:].strip()

                if len(split[0]) > 0:
                    current_paragraph.append(Verse(index=verse_index, text=split[0]))

                yield Paragraph(verses=current_paragraph)

                for split_i in range(1, len(split) - 1):
                    yield Paragraph(verses=[Verse(index=verse_index, text=split[split_i].strip())])

                current_paragraph = [Verse(index=verse_index, text=split[-1].strip())]
            else:
                current_paragraph.append(Verse(index=verse_index, text=verse[text_index:].lstrip()))

        if current_paragraph:
            yield Paragraph(verses=current_paragraph)

    def process_books(folder: str) -> Item:
        books = [] # type: list[Book]

        for book_filename in os.listdir(folder):
            if book_filename == "Preface.txt":
                continue

            title = ""
            chapters: List[Chapter] = []
            
            with io.open(os.path.join(folder, book_filename), mode='r', encoding='utf-8') as file:
                contents = file.read()
                lines = contents.split('\n')
                title_lines = []

                def set_title(short_title: str):
                    nonlocal title
                    title = short_title

                title_finished = False
                chapter_likely_finished = False
                chapter_index = -1
                chapter_verses_unformatted = []

                def finish_chapter():
                    nonlocal chapter_verses_unformatted, chapters, chapter_index, chapter_likely_finished
                    if not chapter_verses_unformatted:
                        return

                    paragraphs = [p for p in format_verses(chapter_verses_unformatted, set_title, f"{title} chapter {chapter_index}")]

                    chapters.append(Chapter(index=chapter_index, paragraphs=paragraphs))
                    chapter_verses_unformatted = []
                    chapter_likely_finished = False

                for line_untrimmed in lines:
                    line = line_untrimmed.strip()

                    if not title_finished:
                        if line:
                            title_lines.append(line)
                        else:
                            title_finished = True
                            title = ' '.join(title_lines).strip()
                    elif chapter_likely_finished == False:
                        chapter_match = re.match(r'^((CHAPTER)|(PSALM))\W+(\d+)', line)
                        if chapter_match:
                            print("chapter finish not expected")
                            finish_chapter()
                            chapter_index = int(chapter_match.group(4))
                        elif chapter_index > 0:
                            if len(line) > 0:
                                chapter_verses_unformatted.append(line)
                            else:
                                chapter_likely_finished = True
                        else:
                            print(f"Skipping line: {line}")
                    else: # chapter_likely_finished == True
                        chapter_match = re.match(r'^((CHAPTER)|(PSALM))\W+(\d+)', line)
                        if chapter_match:
                            print("chapter finish not expected")
                            finish_chapter()
                            chapter_index = int(chapter_match.group(4))
                        elif len(line) > 0:
                            print(f"Unexpected line in {title} chapter {chapter_index}: {line}")

                finish_chapter()
            
            books.append(Book(title=title, chapters=chapters))
        
        return save(books, "King James version")

    Bible = process_books("content/Bible_KJ/")
    print(f"King James Bible: {Bible.id}")

if __name__ == "__main__":
    load_initial_data()

    # reset_all()
    # init_db()

    # with get_session() as session:
    #     item1 = Item(text="Hi")
    #     session.add(item1)
    #     session.commit()
    #     print(item1)
    #     print("")
