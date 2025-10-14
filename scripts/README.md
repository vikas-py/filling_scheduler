# Admin User Creation

This directory contains the script for creating administrator accounts in the Filling Scheduler application.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install passlib[bcrypt]
```

Or if you're using the project's virtual environment:

```bash
# Activate your virtual environment first, then:
pip install -r requirements.txt
```

## Usage on Ubuntu VM

### Step 1: Ensure the Database Exists

The backend server must have been run at least once to create the database. If you haven't done this:

```bash
cd src
uvicorn fillscheduler.api.main:app --host 0.0.0.0 --port 8000
```

Press `Ctrl+C` after it starts successfully. This creates the `filling_scheduler.db` file.

### Step 2: Run the Admin Creation Script

Navigate to the project root directory and run:

#### Option A: Interactive Mode (Recommended)

```bash
python3 scripts/create_admin.py
```

The script will prompt you for:
- Email address
- Password (hidden input)
- Password confirmation

#### Option B: Command Line Arguments

```bash
python3 scripts/create_admin.py --email admin@example.com --password YourSecurePassword123
```

#### Option C: Quick Test Admin (NOT for production!)

```bash
python3 scripts/create_admin.py --email admin@example.com --password admin123
```

## Features

- ✅ Creates new admin users
- ✅ Upgrades existing users to admin
- ✅ Detects if user is already admin
- ✅ Secure password hashing (bcrypt)
- ✅ Password confirmation in interactive mode
- ✅ Basic email and password validation
- ✅ Works directly with SQLite database

## What is an Administrator?

Administrators (users with `is_superuser=True`) have elevated privileges in the system. Currently, the application uses this flag for:
- Access control to certain features
- Future administrative functions

## Login After Creation

Once you've created the admin user:

1. **Access the frontend:**
   - From VM: `http://<your-vm-ip>:5173`
   - From Windows: `http://192.168.56.101:5173`

2. **Login with your credentials:**
   - Email: The email you provided
   - Password: The password you set

## Troubleshooting

### "Database not found" Error

**Problem:** The script can't find `src/filling_scheduler.db`

**Solution:**
1. Make sure you're running the script from the project root directory
2. Start the backend server at least once to initialize the database:
   ```bash
   cd src
   uvicorn fillscheduler.api.main:app --host 0.0.0.0 --port 8000
   ```

### "passlib is not installed" Error

**Problem:** Missing required dependency

**Solution:**
```bash
pip install passlib[bcrypt]
```

### "Email already registered" Message

**Problem:** User already exists

**Solution:**
- If they're already admin: You can login with that account
- If they're not admin: The script will automatically upgrade them to admin

### Permission Denied Error

**Problem:** No permission to access database file

**Solution:**
```bash
# Check permissions
ls -la src/filling_scheduler.db

# Fix if needed (replace 'your-user' with your username)
sudo chown your-user:your-user src/filling_scheduler.db
```

## Security Notes

⚠️ **IMPORTANT:**

1. **Never use weak passwords in production**
   - Minimum 8 characters (script enforces this)
   - Use combination of uppercase, lowercase, numbers, symbols

2. **Change default passwords immediately**
   - If you used `admin123` for testing, change it after first login

3. **Protect your database file**
   - The SQLite database contains hashed passwords
   - Keep appropriate file permissions: `chmod 600 src/filling_scheduler.db`

4. **Don't commit credentials**
   - Never commit passwords to version control
   - Use environment variables for sensitive data in production

## Database Details

- **Location:** `src/filling_scheduler.db` (SQLite)
- **Admin Flag:** `users.is_superuser = 1`
- **Password Hash:** bcrypt algorithm
- **User Status:** `users.is_active = 1` (active by default)

## Manual Database Method (Advanced)

If the script doesn't work, you can manually update the database:

```bash
# Open SQLite database
sqlite3 src/filling_scheduler.db

# Check existing users
SELECT id, email, is_superuser FROM users;

# Upgrade a user to admin (replace '1' with the user ID)
UPDATE users SET is_superuser = 1 WHERE id = 1;

# Exit
.quit
```

## Support

If you encounter issues:
1. Check that the backend server starts successfully
2. Verify the database file exists
3. Ensure all dependencies are installed
4. Check file permissions
5. Review the error messages carefully
