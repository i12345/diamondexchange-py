from src import db
from src.ai.teacher.learning_outcome import LearningOutcome
from src.db.database import get_session
from src.models.item import Item

item_id = ""
item = None # type: Item

with get_session() as session:
    item = session.get(Item, item_id)
    
    
def main():
    
    