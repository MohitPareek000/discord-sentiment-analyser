# Security Best Practices

## Critical Actions Required NOW

### 1. Regenerate Your Discord Bot Token

**If you have shared or exposed your Discord bot token, you MUST regenerate it immediately:**

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Navigate to the "Bot" section
4. Click "Reset Token"
5. Copy the new token
6. Update your `.env` file with the new token
7. Restart your bot

**Example format:** `MTxxxxxxxxxxxxxxxx.GxxxxX.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
**Status:** If you've exposed your token, regenerate it immediately

### 2. What Happens if a Token is Exposed?

An exposed Discord bot token allows anyone to:
- Control your bot completely
- Send messages as your bot
- Join/leave servers
- Access all data your bot can see
- Potentially abuse rate limits and get your bot banned

## Proper Credential Management

### Environment Variables (.env)

1. **ALWAYS** store sensitive credentials in `.env` file
2. **NEVER** commit `.env` to version control
3. Use `.env.example` as a template (without real values)
4. The `.env` file is already protected by `.gitignore`

### Google Credentials (credentials.json)

1. Download from Google Cloud Console as JSON
2. Store in project root directory
3. Already protected by `.gitignore` (via `*.json` rule)
4. Share Google Sheets only with the service account email

### What NOT to Do

**NEVER:**
- Put credentials directly in code files
- Commit `.env` or `credentials.json` to git
- Share tokens in messages, screenshots, or documentation
- Store credentials in README or other markdown files
- Push credentials to GitHub, GitLab, or any public repository

## Verification Checklist

Before committing any changes, verify:

- [ ] `.env` file exists and contains your actual credentials
- [ ] `.env` is listed in `.gitignore`
- [ ] `credentials.json` is listed in `.gitignore` (via `*.json`)
- [ ] No credentials appear in any committed files
- [ ] Discord bot token has been regenerated if previously exposed
- [ ] Google Sheets is only shared with service account email

## Git Safety Commands

Before committing, check for exposed secrets:

```bash
# Check what will be committed
git status

# Verify .env and credentials.json are NOT listed
git add -n .

# If .env shows up, ensure it's in .gitignore
cat .gitignore | grep .env
```

## If You Accidentally Committed Credentials

1. **Regenerate all exposed credentials immediately**
2. Remove them from git history (consider using tools like `git-filter-repo`)
3. Update `.gitignore` to prevent future commits
4. Push the cleaned history

**Note:** Simply deleting credentials in a new commit is NOT enough - they remain in git history.

## Regular Security Practices

1. **Rotate credentials periodically** (every 90 days recommended)
2. **Monitor bot activity** for unusual behavior
3. **Review Google Sheets access** regularly
4. **Keep dependencies updated** (`pip install --upgrade -r requirements.txt`)
5. **Check logs** (`discord_bot.log`) for security warnings

## Contact

If you suspect a security breach:
1. Immediately regenerate all credentials
2. Check logs for unauthorized access
3. Review Google Sheets for unexpected changes
4. Update and restart the bot

---

**Remember:** Security is not a one-time setup. Regularly review and update your security practices.
