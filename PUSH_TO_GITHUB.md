# Push Test-Data-Hub to GitHub

Your project is committed locally. Follow these steps to create a new repo on GitHub and push.

## Step 1: Create a new repository on GitHub

1. Open **https://github.com/new** in your browser.
2. **Repository name:** `Test-Data-Hub` (or any name you prefer).
3. **Description (optional):** e.g. "AI-powered synthetic data generation and validation".
4. Choose **Public** (or Private).
5. **Do not** add a README, .gitignore, or license (the project already has them).
6. Click **Create repository**.

## Step 2: Add remote and push

In a terminal, from the project root (`C:\Users\User\Desktop\Codingyay\Crayon Data\Test-Data-Hub`), run:

```powershell
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/Test-Data-Hub.git

# Push to GitHub
git push -u origin main
```

If you used a different repo name than `Test-Data-Hub`, use that name in the URL instead.

Example (if your username is `johndoe` and repo name is `Test-Data-Hub`):

```powershell
git remote add origin https://github.com/johndoe/Test-Data-Hub.git
git push -u origin main
```

## Step 3: Authenticate if prompted

- **HTTPS:** GitHub may ask for your username and a **Personal Access Token** (not your password). Create one at: https://github.com/settings/tokens
- **SSH:** If you use SSH keys, use: `git@github.com:YOUR_USERNAME/Test-Data-Hub.git` instead of the `https://` URL.

---

**Done.** Your code will be on GitHub at `https://github.com/YOUR_USERNAME/Test-Data-Hub`.
