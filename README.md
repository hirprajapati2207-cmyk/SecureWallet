# SecureVault

A web-based personal password and credential management system built with Python, Flask, and SQLite.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```
   *(The database `securevault.db` will be initialized automatically on first run)*

3. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:5000/`

## Pushing to GitHub

1. Initialize Git in the project directory:
   ```bash
   git init
   ```
2. Create a `.gitignore` file to ignore the database and virtual environment:
   ```bash
   echo "securevault.db" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo ".env" >> .gitignore
   ```
3. Commit the code:
   ```bash
   git add .
   git commit -m "Initial commit of SecureVault"
   ```
4. Link to your GitHub repository and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

## Deploying to Render

1. Go to [Render](https://render.com/) and create a new **Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:create_app()`
4. Add Environment Variables:
   - `SECRET_KEY`: A strong random string.
   - `ENCRYPTION_KEY`: A Fernet key generated using `cryptography.fernet.Fernet.generate_key()`.
5. Render uses ephemeral storage for standard web services, so for a production-ready SQLite database you will need to attach a **Render Disk** or switch to PostgreSQL. If you want to use PostgreSQL, you can update `config.py` to read `DATABASE_URL` and use `psycopg2` or `SQLAlchemy` instead of SQLite.
