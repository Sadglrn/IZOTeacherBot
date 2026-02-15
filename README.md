# IZOTeacherBot
Telegram-bot written in Python. Bot offers the user to guess the painter of a picture.
Add bot in Telegram: @IZOTeacherBot

## Local run on Windows (PowerShell)

### 1) Install Python
Install Python 3.10 (or newer compatible version) and verify:

```powershell
py -0p
```

If 3.10 is missing:

```powershell
winget install -e --id Python.Python.3.10
```

### 2) Create and activate virtual environment

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Note: this project uses `psycopg2-binary` to avoid local PostgreSQL build tooling (`pg_config`) errors on Windows.

### 3) Configure bot token
Edit `config.py`:

```python
TOKEN = 'YOUR-TELEGRAM-BOT-TOKEN'
TYPE_PROXY = None
IP = None
```

### 4) Configure database URL for current shell

```powershell
$env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/izoteacherbot"
```

### 5) Create table `pic_infos` (one-time)

```sql
CREATE TABLE IF NOT EXISTS pic_infos (
  id SERIAL PRIMARY KEY,
  file_id TEXT NOT NULL,
  author_name TEXT NOT NULL
);
```

### 6) Run

```powershell
python main.py
```


## Reset local picture database (delete old and create new)

If you want a completely fresh local DB for images:

```powershell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/izoteacherbot"
python reset_local_db.py
```

What this does:
- drops old table `pic_infos`
- creates a new empty table `pic_infos`
- removes local shelve game-state files (`shelve.db.*`)

If you want to keep local shelve state files:

```powershell
python reset_local_db.py --keep-state
```

### Troubleshooting: "connection refused" on localhost:5432
If `python reset_local_db.py` shows `connection refused`, PostgreSQL service is not running or listens on another port.

PowerShell checks:

```powershell
Test-NetConnection localhost -Port 5432
Get-Service *postgres*
```

Start service (service name may differ):

```powershell
Start-Service postgresql-x64-16
```

If your PostgreSQL uses another port, update `DATABASE_URL` accordingly.

Optional SSL mode override:

```powershell
$env:DB_SSLMODE = "disable"   # for most local installs
# or
$env:DB_SSLMODE = "require"   # for managed/remote DB with SSL
```

