from src.Bible.read import readBible
from src.db.database import get_session
from src.models.item import Item

import dspy
from dspy import OpenAI


def main():
    dspy.settings.configure(lm=OpenAI(model="gpt-3.5-turbo"))
    item_id = 36600
    with get_session() as session:
        item = session.get(Item, item_id)
        readBible(item, session)

if __name__ == "__main__":
    main()
