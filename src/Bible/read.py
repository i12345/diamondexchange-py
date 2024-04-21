from sqlmodel import Session
from dspy import Signature, InputField, OutputField, TypedPredictor
from src.ai.discourse.discourse import DiscourseFeatures
from src.ai.discourse.ingestor import BackingDiscourseChunkIngestor, DiscourseChunkIngestorDiscourseTextualContextUpdaterWithLLM, DiscourseIngestor
from src.ai.discourse.item_intaker import ItemIntaker
from src.models.item import Item
from src.models.item_ref import ItemRef
from src.publications.publication_items import PublicationIndexFormatSettings, PublicationIndexReferenceSettings, PublicationIndexSettings, PublicationItemsIndexer
from src.services.item import get_items

indexSettings = PublicationIndexSettings(
    format_settings=PublicationIndexFormatSettings(
        chapters_main_multiple=True,
        chapters_intro=[],
        chapters_conclusion=[],
        subchapters_main_multiple=True,
        subchapters_intro=["superscript"],
        subchapters_conclusion=[],
        format_chapter_main_entire_singular="{chapter}",
        format_chapter_main_entire_plural="{chapters}",
        format_chapter_partial="{chapter}",
        format_subchapter_main_singular="{subchapter}",
        format_subchapter_main_plural="{subchapters}",
        format_range_through_chapters="{chapter_subchapter_start}-{chapter_subchapter_end}",
        format_chapter_subchapter="{chapter}:{subchapter}",
    ),
    reference_settings=PublicationIndexReferenceSettings()
)

def readBible(Bible: Item, session: Session):
    class GuessDiscourseFeatures(Signature):
        """Answers the discourse features for a book of the Bible"""
        book: str = InputField()
        features: DiscourseFeatures = OutputField()

    guess_features = TypedPredictor(GuessDiscourseFeatures)

    for book in Bible.children:
        name = next(get_items(ItemRef(root=book.child_id, path=indexSettings.reference_settings.name_path), session)).text
        print(name)

        features = guess_features(book=name).features

        backing = BackingDiscourseChunkIngestor(features=features, new_chunk_receiver=print)

        intaker = ItemIntaker(
            item_indexer=PublicationItemsIndexer(settings=indexSettings),
            discourse_ingestor=DiscourseIngestor(
                discourse_features=features,
                ingestors=[
                    # DiscourseChunkIngestorDiscourseTextualContextUpdaterWithLLM(),
                    backing
                ],
            )
        )


        intaker.intake(book.child, ItemRef(root=book.child_id))

        for chunk in backing.discourse.chunks:
            print(chunk.index)
            print(chunk.context_at_start)
            print(chunk.communicator)
            print(chunk.text)
            print()

        input("")
