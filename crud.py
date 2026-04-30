from sqlalchemy.orm import Session
from models import User, Category, Transaction
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


DEFAULT_CATEGORIES = [
    ("Salary", "income"),
    ("Freelance", "income"),
    ("Investments", "income"),
    ("Other Income", "income"),
    ("Rent", "expense"),
    ("Food & Groceries", "expense"),
    ("Fast Food", "expense"),
    ("Transport", "expense"),
    ("Utilities", "expense"),
    ("Healthcare", "expense"),
    ("Education", "expense"),
    ("Entertainment", "expense"),
    ("Clothing", "expense"),
    ("Travel", "expense"),
    ("Subscriptions", "expense"),
    ("Other Expense", "expense"),
]


# USERS
def create_user(session: Session, username: str, password: str):
    existing_user = session.query(User).filter(User.username == username).first()

    if existing_user:
        return None

    user = User(
        username=username,
        password_hash=generate_password_hash(password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    seed_categories(session, user.id)

    return user


def authenticate_user(session: Session, username: str, password: str):
    user = session.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return user


# CATEGORIES
def seed_categories(session: Session, user_id: int):
    existing = get_all_categories(session, user_id)
    existing_names = [(c.name, c.type) for c in existing]

    for name, type in DEFAULT_CATEGORIES:
        if (name, type) not in existing_names:
            add_category(session, name, type, user_id)


def add_category(session: Session, name: str, type: str, user_id: int):
    category = Category(
        name=name,
        type=type,
        user_id=user_id
    )

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


def get_all_categories(session: Session, user_id: int):
    return (
        session.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.type, Category.name)
        .all()
    )


def delete_category(session: Session, category_id: int, user_id: int):
    category = (
        session.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )

    if category:
        session.delete(category)
        session.commit()
        return True

    return False


# TRANSACTIONS
def add_transaction(
    session: Session,
    amount: float,
    date: date,
    description: str,
    category_id: int,
    user_id: int
):
    transaction = Transaction(
        amount=amount,
        date=date,
        description=description,
        category_id=category_id,
        user_id=user_id
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction


def get_all_transactions(session: Session, user_id: int):
    return (
        session.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .all()
    )


def get_transactions_by_month(session: Session, month: int, year: int, user_id: int):
    start_date = date(year, month, 1)

    if month < 12:
        end_date = date(year, month + 1, 1)
    else:
        end_date = date(year + 1, 1, 1)

    return (
        session.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        .all()
    )


def delete_transaction(session: Session, transaction_id: int, user_id: int):
    transaction = (
        session.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
        .first()
    )

    if transaction:
        session.delete(transaction)
        session.commit()
        return True

    return False