from database import init_db, get_session
from crud import add_category, get_all_categories

init_db()
session = get_session()

add_category(session, "Food", "Expense")
add_category(session, "Salary", "Income")

categorii = get_all_categories(session)

print("Număr categorii găsite:", len(categorii))
print(categorii)
for c in categorii:
    print(c.id, c.name, c.type)