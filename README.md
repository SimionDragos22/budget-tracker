# Budget Tracker

A simple personal finance web application built with Streamlit.

## Features

- User authentication (register and login)
- Add income and expense transactions
- Custom categories
- Dashboard with:
  - Total balance
  - Total income and expenses
  - Expense breakdown chart
  - Balance over time

## Tech Stack

- Python
- Streamlit
- SQLAlchemy
- SQLite
- Plotly

## Environment variables

Create a `.env` file in the project root:

EMAIL_ADDRESS=your_app_email@gmail.com
EMAIL_PASSWORD=your_google_app_password

Important:

- You must use a Google **App Password**, not your normal Gmail password.
- App Passwords are generated from your Google account (Security → App passwords).
- When copying the password, you can paste it **with or without spaces**:
  
  Example:
  
  Google shows:
  abcd efgh ijkl mnop
  
  You can use:
  abcd efgh ijkl mnop
  OR
  abcdefghijklmnop

- Make sure the App Password is generated from the SAME Gmail account used in `EMAIL_ADDRESS`.

If you get `SMTPAuthenticationError (535)`:
- Check that 2-Step Verification is enabled
- Regenerate your App Password
- Restart the app after updating `.env`

## How to run

1. Clone the repository:

```bash
git clone https://github.com/SimionDragos22/budget-tracker.git
cd budget-tracker
```
2. Install dependencies manually:
```bash
pip install streamlit sqlalchemy plotly pandas werkzeug
```


3. Run the application:
```bash
streamlit run app.py
```
