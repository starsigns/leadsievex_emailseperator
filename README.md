# Email Separator App

A simple PyQt5 desktop application to help you remove a list of emails from a large main list and export the remainder.

## Features
- Load a main email list (e.g., 200,000 emails) from a text file
- Paste or enter emails to remove in a large text area
- Optionally load an unwanted list from a file
- Click 'Separate' to remove those emails from the main list
- Export and save the remaining emails to a new file

## Requirements
- Python 3.6+
- PyQt5

## Setup
1. Create and activate a virtual environment (already done):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the app with:
```
venv\Scripts\python.exe email_separator.py
```

## How it works
1. **Load Main List:** Click 'Load Main Email List' and select your main email file. **Each email must be on a separate line.**
   - Example:
     ```
     email1@example.com
     email2@example.com
     email3@example.com
     ```
2. **Unwanted List:**
   - Paste emails to remove in the text area (one per line), **or**
   - Click 'Load Unwanted List from File' and select a file (again, one email per line).
   - Both sources are combined for removal.
3. **Separate:** Click 'Separate' to process. The app will remove all emails found in the unwanted list (from both the text area and the file) from the main list.
4. **Export:** Click 'Export Result' to save the remaining emails to a new file. The output will also be one email per line.

## Data Format
- **All input files and pasted lists must have one email per line.**
- Comma-separated or other delimited formats are not supported. If your data is comma-separated, convert it to one email per line before using the app.

## Example
**Main List File:**
```
user1@example.com
user2@example.com
user3@example.com
```
**Unwanted List (pasted or file):**
```
user2@example.com
```
**Result after separation:**
```
user1@example.com
user3@example.com
```

---

Feel free to suggest improvements or request new features!
