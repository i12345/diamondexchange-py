from typing import Optional
from pydantic import BaseModel
from src.ai.discourse.item_intaker import ItemIndexer, ItemsIndex
from src.db.database import get_session
from src.models.item import Item
from src.models.item_ref import ItemRef
from src.services.item import get_absolute_item_ids, get_items

class PublicationIndexFormatSettings(BaseModel):
    chapters_main_multiple: bool = True
    chapters_intro: list[str] = []
    chapters_conclusion: list[str] = []
    subchapters_main_multiple: bool = True
    subchapters_intro: list[str] = []
    subchapters_conclusion: list[str] = []

    format_publication: str = "{publication}"
    format_publication_chapter_subchapter: str = "{publication} {chapter_subchapter}"
    format_chapter_main_entire_singular: str = "chapter {chapter}"
    format_chapter_main_entire_plural: str = "chapters {chapters}"
    format_chapter_main_entire_plural_range: Optional[str] = "{chapter_start}-{chapter_end}"
    format_chapter_entire_plural_range: Optional[str] = "{chapter_start} through {chapter_end}"
    format_chapter_entire_plural_list_infix: Optional[str] = "{chapters}, {chapter}"
    format_chapter_entire_plural_list_last: Optional[str] = "{chapters}, and {chapter}"
    format_chapter_partial: str = "chapter {chapter}"
    format_subchapter_main_singular: str = "paragraph {subchapter}"
    format_subchapter_main_plural: str = "paragraphs {subchapters}"
    format_subchapter_main_plural_range: Optional[str] = "{subchapter_start}-{subchapter_end}"
    format_subchapter_plural_range: Optional[str] = "{subchapter_start} through {subchapter_end}"
    format_subchapter_plural_list_infix: Optional[str] = "{subchapters}, {subchapter}"
    format_subchapter_plural_list_last: Optional[str] = "{subchapters}, and {subchapter}"
    format_range_through_chapters: str = "{chapter_subchapter_start} through {chapter_subchapter_end}"
    format_chapter_subchapter: str = "{chapter} {subchapter}"
    format_chapter_subchapter_multiple: str = "{0}, {1}"
    format_chapter_subchapter_multiple_last: str = "{0} and {1}"

    format_local_index_chapter: str = "Chapter {chapter}"
    format_local_index_subchapter: str = "({subchapter})"

    def is_main_chapter(self, chapter: str):
        return not (
            (chapter in self.chapters_intro) or
            (chapter in self.chapters_conclusion)
        )
    
    def is_main_subchapter(self, subchapter: str):
        return not (
            (subchapter in self.subchapters_intro) or
            (subchapter in self.subchapters_conclusion)
        )

    def order_index(self, chapter: str, subchapter: Optional[str]) -> int:
        max_items = 0x1_000_000

        def order_index_(item: str, intro_items: list[str], conclusion_items: list[str]) -> int:
            if item in intro_items:
                return intro_items.index(item)
            elif item in conclusion_items:
                return max_items - len(conclusion_items) + conclusion_items.index(item)
            else:
                return len(intro_items) + int(item)

        return (
            (order_index_(chapter, intro_items=self.chapters_intro, conclusion_items=self.chapters_conclusion) * max_items) +
            (order_index_(subchapter, intro_items=self.subchapters_intro, conclusion_items=self.subchapters_conclusion) if subchapter is not None else 0)
        )

class PublicationIndexReferenceSettings(BaseModel):
    name_path: list[str] = []
    chapter_level: int = 0
    subchapter_level: int = 1

class PublicationIndexSettings(BaseModel):
    format_settings: PublicationIndexFormatSettings
    reference_settings: PublicationIndexReferenceSettings

class PublicationChapterSubchapterRange(BaseModel):
    chapter_start: str
    chapter_end: str
    subchapter_start: Optional[str]
    subchapter_end: Optional[str]

    def to_string(self, settings: PublicationIndexFormatSettings):
        chapter_start_main = settings.is_main_chapter(self.chapter_start)
        chapter_end_main   = settings.is_main_chapter(self.chapter_end)

        chapter_not_main = (not chapter_start_main) or (not chapter_end_main)
        chapter_singular = self.chapter_start if (self.chapter_start == self.chapter_end) else None

        if self.subchapter_start is None:
            if chapter_singular is not None:
                return ("{chapter}" if chapter_not_main else settings.format_chapter_main_entire_singular).format(chapter=chapter_singular)
            else:
                if chapter_not_main:
                    chapter_start = settings.format_chapter_main_entire_singular.format(chapter=self.chapter_start) if chapter_start_main else self.chapter_start
                    chapter_end   = settings.format_chapter_main_entire_singular.format(chapter=self.chapter_end)   if chapter_end_main   else self.chapter_end
                    return settings.format_chapter_entire_plural_range.format(chapter_start=chapter_start, chapter_end=chapter_end)
                else:
                    return settings.format_chapter_main_entire_plural_range.format(chapter_start=self.chapter_start, chapter_end=self.chapter_end)
        else:
            def subchapter_range_to_string(
                    subchapter_start: str,
                    subchapter_end: str,
                    settings: PublicationIndexFormatSettings    
                ) -> str:
                subchapter_start_main = settings.is_main_subchapter(subchapter_start)
                subchapter_end_main   = settings.is_main_subchapter(subchapter_end)

                subchapter_not_main = (not subchapter_start_main) or (not subchapter_end_main)
                subchapter_singular = subchapter_start if (subchapter_start == subchapter_end) else None

                if subchapter_singular is not None:
                    return ("{subchapter}" if subchapter_not_main else settings.format_subchapter_main_singular).format(subchapter=subchapter_singular)
                else:
                    subchapter_start_formatted = settings.format_subchapter_main_singular.format(subchapter=subchapter_start) if subchapter_start_main else subchapter_start
                    subchapter_end_formatted   = settings.format_subchapter_main_singular.format(subchapter=subchapter_end)   if subchapter_end_main   else subchapter_end
                    subchapters_formatted = settings.format_subchapter_plural_range.format(subchapter_start=subchapter_start_formatted, subchapter_end=subchapter_end_formatted)
                    return ("{subchapters}" if (subchapter_start_main != subchapter_end_main) else settings.format_subchapter_main_plural).format(subchapters=subchapters_formatted)
            
            if chapter_singular is not None:
                chapter_formatted = settings.format_chapter_partial.format(chapter=chapter_singular)
                subchapter_range_formatted = subchapter_range_to_string(subchapter_start=self.subchapter_start, subchapter_end=self.subchapter_end, settings=settings)
                return settings.format_chapter_subchapter.format(chapter=chapter_formatted, subchapter=subchapter_range_formatted)
            else:
                chapter_start_formatted = (settings.format_chapter_partial if chapter_start_main else "{chapter}").format(chapter=self.chapter_start)
                chapter_end_formatted   = (settings.format_chapter_partial if chapter_end_main   else "{chapter}").format(chapter=self.chapter_end)
                subchapter_start_formatted = subchapter_range_to_string(subchapter_start=self.subchapter_start, subchapter_end=self.subchapter_start, settings=settings)
                subchapter_end_formatted   = subchapter_range_to_string(subchapter_start=self.subchapter_end,   subchapter_end=self.subchapter_end,   settings=settings)
                chapter_subchapter_start_formatted = settings.format_chapter_subchapter.format(chapter=chapter_start_formatted, subchapter=subchapter_start_formatted)
                chapter_subchapter_end_formatted   = settings.format_chapter_subchapter.format(chapter=chapter_end_formatted,   subchapter=subchapter_end_formatted)
                return settings.format_range_through_chapters.format(chapter_subchapter_start=chapter_subchapter_start_formatted, chapter_subchapter_end=chapter_subchapter_end_formatted)

class PublicationItemsIndex(ItemsIndex):
    def __init__(self, settings: PublicationIndexSettings,
                 publication: str, publication_ID: int,
                 ranges: list[PublicationChapterSubchapterRange]):
        self.settings = settings
        self.publication = publication
        self.publication_ID = publication_ID
        self.ranges = ranges
        assert len(ranges) <= 1

    def follows(self,
                chapter_start: str, chapter_end: str,
                subchapter_start: Optional[str], subchapter_end: Optional[str]) -> bool:
        return (
            self.settings.format_settings.order_index(chapter=chapter_start, subchapter=subchapter_start) <=
            self.settings.format_settings.order_index(chapter=chapter_end, subchapter=subchapter_end)
        )

    def extend(self, item: ItemRef) -> bool:
        publication_ID = item.root
        chapter = item.path[self.settings.reference_settings.chapter_level] if item.path is not None and self.settings.reference_settings.chapter_level < len(item.path) else None
        subchapter = item.path[self.settings.reference_settings.subchapter_level] if item.path is not None and self.settings.reference_settings.subchapter_level < len(item.path) else None

        if publication_ID != self.publication_ID:
            return False
        
        if len(self.ranges) == 0:
            if chapter is not None:
                self.ranges = [PublicationChapterSubchapterRange(chapter_start=chapter, chapter_end=chapter, subchapter_start=subchapter, subchapter_end=subchapter)]
            return True
        else:
            assert len(self.ranges) == 1

            self.ranges[0].chapter_end = chapter
            self.ranges[0].subchapter_end = subchapter

            if self.ranges[0].chapter_start == chapter and self.ranges[0].subchapter_start is None:
                self.ranges[0].subchapter_start = subchapter

            return True

    def to_string(self):
        publication_formatted = self.settings.format_settings.format_publication.format(publication=self.publication)
        if len(self.ranges) == 0:
            return publication_formatted
        else:
            assert len(self.ranges) == 1
            chapter_subchapter_formatted = self.ranges[0].to_string(settings=self.settings.format_settings)
            return self.settings.format_settings.format_publication_chapter_subchapter.format(publication=publication_formatted, chapter_subchapter=chapter_subchapter_formatted)

class PublicationItemsIndexer(ItemIndexer):
    def __init__(self, settings: PublicationIndexSettings):
        super().__init__()
        self.settings = settings

    def index_new(self, ref: ItemRef) -> ItemsIndex:
        name: str
        id = ref.root
        chapter: Optional[str]
        subchapter: Optional[str]

        with get_session() as session:
            name = next(iter(get_items(ItemRef(root=id, path=self.settings.reference_settings.name_path), session=session))).text
        
        chapter = ref.path[self.settings.reference_settings.chapter_level] if ref.path is not None and self.settings.reference_settings.chapter_level < len(ref.path) else None
        subchapter = ref.path[self.settings.reference_settings.subchapter_level] if ref.path is not None and self.settings.reference_settings.subchapter_level < len(ref.path) else None
        ranges = [PublicationChapterSubchapterRange(chapter_start=chapter, chapter_end=chapter, subchapter_start=subchapter, subchapter_end=subchapter)] if chapter is not None else []

        return PublicationItemsIndex(settings=self.settings, publication=name, publication_ID=id, ranges=ranges)

    def index_child_local(self, ref: ItemRef) -> str:
        if ref.path is None:
            raise "Not supported"
        
        if len(ref.path) - 1 == self.settings.reference_settings.chapter_level:
            return self.settings.format_settings.format_local_index_chapter.format(chapter=ref.path[self.settings.reference_settings.chapter_level])
        elif len(ref.path) - 1 == self.settings.reference_settings.subchapter_level:
            return self.settings.format_settings.format_local_index_subchapter.format(subchapter=ref.path[self.settings.reference_settings.subchapter_level])
        else:
            return ""

    def index_parse(self, format: str) -> ItemsIndex:
        pass