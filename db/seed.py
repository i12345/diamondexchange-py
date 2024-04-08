# db/seed.py
from sqlmodel import SQLModel, Session
from src.db.database import get_session, engine, init_db
from src.models import NoteItem, CollectionItem, CollectionChildDisplayClass

from dataclasses import dataclass
from typing import List, Callable, Iterable, Optional, Tuple
import re
import asyncio
import os
import aiofiles

from src.models.item_collection import CollectionItemChild

def reset_all():
    SQLModel.metadata.drop_all(engine)

async def load_initial_data(reset: bool = True):
    if reset:
        reset_all()
    init_db()

    with get_session() as session:
        await load_KJ(session=session)

async def load_KJ(session: Session):
    @dataclass
    class Verse:
        index: int
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

    async def save(books: list[Book], rendering: str):
        child_books = [] # type: list[CollectionItemChild]

        for book in books:
            child_chapters = [] # type: list[CollectionItemChild]

            for chapter in book.chapters:
                child_paragraphs = [] # type: list[CollectionItemChild]

                for paragraph in chapter.paragraphs:
                    child_verses = [] # type: list[CollectionItemChild]

                    for verse in paragraph.verses:
                        verse_note = NoteItem(text=verse.text)
                        session.add(verse_note)
                        child_verses.append(CollectionItemChild(local_label="{verse.index}", child=verse_note))

                    paragraph_collection = CollectionItem(child_display_class=CollectionChildDisplayClass.INLINE, children=child_verses)
                    session.add(paragraph_collection)
                    child_paragraphs.append(CollectionItemChild(child=paragraph_collection))

                chapter_collection = CollectionItem(name=f"{chapter.index}", child_display_class=CollectionChildDisplayClass.BLOCK, children=child_paragraphs)
                session.add(chapter_collection)
                child_chapters.append(CollectionItemChild(child=chapter_collection))

            book_collection = CollectionItem(name=book.title, child_display_class=CollectionChildDisplayClass.PAGINATION, children=child_chapters)
            session.add(book_collection)
            session.commit()
            child_books.append(CollectionItemChild(local_label=book.title, child=book_collection))

        Bible_collection = CollectionItem(name=f"Bible ({rendering})", child_display_class=CollectionChildDisplayClass.ACCORDION, children=child_books)
        session.add(Bible_collection)
        session.commit()
        return Bible_collection

    # This generator function yields paragraphs formatted from unformatted verses
    def format_verses(verses_unformatted: List[str], short_title_callback: Callable[[str], None]) -> Iterable[Paragraph]:
        paragraph_sign = "¶"
        
        current_paragraph: List[Verse] = []
        verse_index_prev = 0

        for verse in verses_unformatted:
            verse_index_matches = re.search(r'\d+', verse)
            if not verse_index_matches:
                raise ValueError("Verse index not found")

            verse_index = int(verse_index_matches.group(0))
            text_index = len(verse_index_matches.group(0))

            if not ((verse_index == verse_index_prev + 1) or (verse_index > verse_index_prev and verse_index < verse_index_prev + 5) or (verse_index_prev == 0)):
                short_title_callback(verse)
                break

            verse_index_prev = verse_index

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

    async def process_books(folder: str) -> CollectionItem:
        books = [] # type: list[Book]

        async for book_filename in os.listdir(folder):
            title = ""
            chapters: List[Chapter] = []
            
            async with aiofiles.open(os.path.join(folder, book_filename), mode='r', encoding='utf-8') as file:
                contents = await file.read()
                lines = contents.split('\n')
                title_lines = []

                def set_title(short_title: str):
                    nonlocal title
                    title = short_title

                title_finished = False
                chapter_index = -1
                chapter_verses_unformatted = []

                async def finish_chapter():
                    nonlocal chapter_verses_unformatted, chapters, chapter_index
                    if not chapter_verses_unformatted:
                        return

                    paragraphs = [p for p in format_verses(chapter_verses_unformatted, set_title)]

                    chapters.append(Chapter(index=chapter_index, paragraphs=paragraphs))
                    chapter_verses_unformatted = []

                for line_untrimmed in lines:
                    line = line_untrimmed.strip()

                    if not title_finished:
                        if line:
                            title_lines.append(line)
                        else:
                            title_finished = True
                            title = ' '.join(title_lines).strip()
                    else:
                        chapter_match = re.match(r'^((CHAPTER)|(PSALM))\W+(\d+)', line)
                        if chapter_match:
                            finish_chapter()
                            chapter_index = int(chapter_match.group(4))
                        elif chapter_index > 0:
                            chapter_verses_unformatted.append(line)
                        else:
                            print(f"Skipping line: {line}")

                finish_chapter()
            
            books.append(Book(title=title, chapters=chapters))
        
        return await save(books, "King James version")

    Bible = await process_books("content/Bible_KJ/")
    print(f"King James Bible: {Bible.id}")

if __name__ == "__main__":
    load_initial_data()