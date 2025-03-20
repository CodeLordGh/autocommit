# Security Recommendations

## Handling GitHub Tokens

GitHub tokens have been detected in the repository files, which is a security risk. Here's how to fix this:

### 1. Database Files (scheduler_jobs.db)

The database file contains GitHub tokens which should not be committed to the repository. To fix this:

- Delete the current database file from the repository
- Add `*.db` to your `.gitignore` file (already done)
- Recreate the database without tokens, or modify your application to:
  - Store tokens in environment variables
  - Retrieve tokens from environment variables when needed
  - Store only encrypted references or token IDs in the database

### 2. Script Files (CreateGitHubRepo.ps1)

The PowerShell script has been updated to use environment variables instead of hardcoded tokens.

### Setting Up Environment Variables

#### Windows (PowerShell)
```powershell
$env:GITHUB_TOKEN = "your_github_token"
```

#### Linux/macOS
```bash
export GITHUB_TOKEN="your_github_token"
```

### For Production

Consider using a proper secrets management solution like:
- GitHub Secrets (for GitHub Actions)
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Removing Sensitive Data from Git History

Even after fixing the files, the tokens remain in your Git history. To completely remove them:

1. Use the [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) or [git-filter-repo](https://github.com/newren/git-filter-repo)
2. Follow GitHub's guide: [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

**Important:** After cleaning the history, all collaborators should clone the repository fresh, as force-pushing the cleaned history will cause conflicts with existing clones.

## Revoking Exposed Tokens

Any tokens that have been exposed should be revoked immediately and replaced with new ones.