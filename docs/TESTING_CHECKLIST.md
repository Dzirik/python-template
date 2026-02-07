# Repository Testing Checklist

**Purpose:** Comprehensive end-to-end testing checklist for deploying the Python Minimal Template to a new repository
**Version:** 1.0
**Last Updated:** 2026-02-06

---

## 📋 Overview

This checklist ensures complete functionality verification when deploying the template to a new repository. Follow each step in order, checking off items as you complete them.

**Estimated Time:** 2-3 hours for complete testing
**Prerequisites:** Git, GitHub account, Python 3.11+ installed

---

## ✅ Phase 1: Repository Setup (15 minutes)

### 1.1 Create New GitHub Repository

**📍 Where:** GitHub website (https://github.com)

**🔧 How to do it:**
1. Click "+" in top right → "New repository"
2. Enter repository name (e.g., `my-python-project`)
3. Choose public or private
4. **IMPORTANT:** Do NOT check "Add a README file", "Add .gitignore", or "Choose a license"
5. Click "Create repository"
6. Copy the repository URL (e.g., `https://github.com/username/my-python-project.git`)

**✅ Checklist:**
- [ ] Create new repository on GitHub (public or private)
- [ ] Repository name: `___________`
- [ ] Initialize WITHOUT README, .gitignore, or license (we'll push our own)
- [ ] Copy repository URL: `____________`

### 1.2 Clone Template Code

**📍 Where:** Your local machine (command line)

**🔧 How to do it:**
```bash
# Option 1: Copy from existing template directory
cp -r /path/to/template-repo /path/to/new-project-directory

# Option 2: On Windows (PowerShell)
Copy-Item -Path "C:\path\to\template-repo\*" -Destination "C:\path\to\new-project-directory" -Recurse

# Option 3: Manual copy
# Just copy all files and folders from template to new directory using file explorer
```

**✅ Checklist:**
- [ ] Navigate to local directory where you want to work
- [ ] Copy all files from template to new directory
- [ ] Verify all files copied (use `tree` or `ls -R`)
- [ ] Verify hidden files copied (`.env.example`, `.gitignore`, `.gitattributes`, `.editorconfig`)

### 1.3 Initialize Git Repository

**📍 Where:** New project directory (command line)

**🔧 How to do it:**
```bash
# Navigate to your new project directory
cd /path/to/new-project-directory

# Initialize Git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Python minimal template"

# Rename branch to main
git branch -M main

# Add remote (replace with your repository URL)
git remote add origin https://github.com/username/my-python-project.git

# Push to GitHub
git push -u origin main
```

**✅ Verification:**
- [ ] All files pushed to GitHub
- [ ] Repository shows correct file count on GitHub
- [ ] `.github/workflows/ci.yml` visible in repository
- [ ] `docs/` folder with all documentation files visible

---

## ✅ Phase 2: Local Environment Setup (20 minutes)

### 2.1 Verify Python Installation

Note: Not necessary - UV will install python library based on .python-version file.

### 2.2 Install UV Package Manager

**📍 Where:** Any directory (command line)

**🔧 How to do it:**

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS (Terminal):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**After installation, verify:**
```bash
uv --version
```

**✅ Checklist:**
- [ ] UV installed successfully
- [ ] UV version displayed (should be 0.1.0 or higher)

### 2.3 NOTHING HERE

### 2.4 Create Virtual Environment & Set Up repository

**📍 Where:** Project directory (command line)

**🔧 How to do it:**

**Windows:**
```bash
make create-venv
```

**Linux/macOS:**
```bash
make create-venv-linux
```

**What this does:**
- Creates `.venv/` directory
- Installs all 13 dependencies (7 runtime + 6 dev)
- Sets up Python environment

**Verify installation:**
```bash
# Activate virtual environment first (if needed)
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# List installed packages
uv pip list
```

**✅ Checklist:**
- [ ] `make_config.mk` created from template
- [ ] `configurations/python_personal.conf` created from `python_repo.conf`
- [ ] `.env` file created from `.env.example`
- [ ] Success message displayed

- [ ] `.venv/` directory created
- [ ] All dependencies installed

---

## ✅ Phase 3: Configuration Testing (15 minutes)

### 3.1 Test Environment Variables

**📍 Where:** Project root directory

**🔧 How to do it:**
```bash
# Open .env file in your text editor
# Windows: notepad .env
# Linux/macOS: nano .env  or  vim .env  or  code .env

# Or just view it:
cat .env
```

**What to check:**
- File should contain 4 environment variables
- Each variable should have a value (no empty values)

**✅ Checklist:**
- [ ] Open `.env` file
- [ ] Verify all variables present:
  - [ ] `ENV_CONFIG=python_personal`
  - [ ] `ENV_LOGGER=logger_file_limit_console`
  - [ ] `ENV_RUNNING_UNIT_TESTS=False`

### 3.2 Test Configuration Files

**📍 Where:** `configurations/` directory

**🔧 How to do it:**
```bash
# Check if file exists
ls configurations/python_personal.conf

# View the file
cat configurations/python_personal.conf
```

**What to check:**
- File should be in HOCON format
- Should contain project name and paths

**✅ Checklist:**
- [ ] Verify `configurations/python_personal.conf` exists
- [ ] Open and verify structure:
  - [ ] `name = "python_personal"`
  - [ ] `path.data = "../../data"`

### 3.3 Test Makefile Configuration

**📍 Where:** Project root directory

**🔧 How to do it:**
```bash
# View the file
cat make_config.mk

# Or open in editor
# Windows: notepad make_config.mk
# Linux/macOS: nano make_config.mk  or  code make_config.mk
```

**What to check:**
- File should contain default file folder and name for single-file operations

**✅ Checklist:**
- [ ] Open `make_config.mk`
- [ ] Verify default values:
  - [ ] `FILE_FOLDER = utils`
  - [ ] `FILE_NAME = leap_year`

---

## ✅ Phase 4: Code Quality Checks (30 minutes)

### 4.1 Type Checking (MyPy)

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make mypy
```

**What this does:**
- Runs MyPy type checker on all files in `src/`
- Checks for type errors and inconsistencies

**Expected output:**
- Green "Success" message
- No type errors

**✅ Checklist:**
- [ ] MyPy runs without errors
- [ ] All source files type-checked
- [ ] Success message displayed
- [ ] No type errors reported

### 4.2 Code Formatting Check (Ruff)

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make format-check
```

**What this does:**
- Checks if all Python files follow formatting standards
- Does NOT modify files (just checks)

**Expected output:**
- Green "Success" message
- No formatting issues

**✅ Checklist:**
- [ ] Ruff format check runs without errors
- [ ] All files properly formatted
- [ ] Success message displayed
- [ ] No formatting issues reported

### 4.3 Code Linting (Ruff)

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make lint-check
```

**What this does:**
- Checks code for style violations, unused imports, etc.
- Enforces coding standards

**Expected output:**
- Green "Success" message
- No linting violations

**✅ Checklist:**
- [ ] Ruff lint check runs without errors
- [ ] All linting rules pass
- [ ] Success message displayed
- [ ] No linting violations reported

### 4.4 Docstring Check (Ruff)

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make docstring-check
```

**What this does:**
- Checks that all functions/classes have proper docstrings
- Verifies docstring format

**Expected output:**
- Green "Success" message
- No docstring issues

**✅ Checklist:**
- [ ] Docstring check runs without errors
- [ ] All docstrings properly formatted
- [ ] Success message displayed
- [ ] No docstring issues reported

### 4.5 Run All Quality Checks

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make all -i
```

**What this does:**
- Runs ALL quality checks in sequence:
  1. MyPy type checking
  2. Format check
  3. Lint check
  4. Docstring check
  5. All tests
- The `-i` flag means "ignore errors and continue"

**Expected output:**
- All checks pass with green "Success" messages
- Final summary showing all checks passed

**✅ Checklist:**
- [ ] MyPy passes
- [ ] Format check passes
- [ ] Lint check passes
- [ ] Docstring check passes
- [ ] All tests pass
- [ ] Overall success message displayed

---

## ✅ Phase 5: Testing (20 minutes)

### 5.1 Run All Tests

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make test
```

**What this does:**
- Runs all tests in `tests/` directory using pytest
- Shows test summary

**Expected output:**
- All tests pass (green dots or checkmarks)
- Summary: "X passed in Y seconds"

**✅ Checklist:**
- [ ] Pytest runs successfully
- [ ] All tests pass
- [ ] Test summary displayed
- [ ] No test failures
- [ ] `tests/tests_utils/test_leap_year.py` - All tests pass
- [ ] `tests/tests_utils/test_meta_class.py` - All tests pass
- [ ] `tests/tests_utils/test_date_time_functions.py` - All tests pass
- [ ] `tests/tests_transformations/test_datetime_one_hot_transformer.py` - All tests pass

### 5.2 Run Tests with Detailed Output

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make test-detailed
```

**What this does:**
- Runs tests with verbose output
- Shows each individual test case name

**Expected output:**
- Each test listed with PASSED status
- More detailed information than `make test`

**✅ Checklist:**
- [ ] Detailed test output displayed
- [ ] Each test case shown individually
- [ ] All tests pass

### 5.3 Test Single File

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
# Uses default file from make_config.mk (test_leap_year.py)
make test-f

# To test a different file, edit make_config.mk first:
# FILE_FOLDER = utils
# FILE_NAME = meta_class
```

**What this does:**
- Runs tests for a single file only
- Faster than running all tests

**✅ Checklist:**
- [ ] Single file test runs (default: `test_leap_year.py`)
- [ ] Tests pass
- [ ] Success message displayed

### 5.4 Generate Coverage Report

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make cover
```

**What this does:**
- Runs tests with coverage tracking
- Generates HTML report in `coverage/` directory

**How to view:**
```bash
# Open in browser
# Windows: start coverage/index.html
# Linux: xdg-open coverage/index.html
# macOS: open coverage/index.html
```

**✅ Checklist:**
- [ ] Coverage report generated
- [ ] `coverage/` directory created
- [ ] HTML report available at `coverage/index.html`
- [ ] Open `coverage/index.html` in browser and verify

### 5.5 Coverage with Log

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make cover-log
```

**What this does:**
- Runs coverage and saves ratio to CSV file
- Creates `reports/` directory if it doesn't exist
- Appends coverage data to `reports/cover_log.csv`

**How to view:**
```bash
cat reports/cover_log.csv
```

**✅ Checklist:**
- [ ] Coverage report generated
- [ ] Coverage ratio logged to `reports/cover_log.csv`
- [ ] File contains coverage percentage

---

## ✅ Phase 6: Security Checks (15 minutes)

### 6.1 Run Security Checks

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make security-check
```

**What this does:**
- Runs **Bandit** - scans source code for security issues
- Runs **pip-audit** - checks dependencies for known vulnerabilities

**Expected output:**
- Bandit: "No issues identified"
- pip-audit: "No known vulnerabilities found"
- Green success message

**✅ Checklist:**
- [ ] Bandit runs successfully
- [ ] pip-audit runs successfully
- [ ] No security vulnerabilities found
- [ ] Success message displayed (green)
- [ ] Bandit scans all Python files in `src/`
- [ ] Bandit excludes `tests/` directory
- [ ] pip-audit checks all installed packages
- [ ] No high or medium severity issues reported

### 6.2 Run All Checks with Security

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
make all-secure -i
```

**What this does:**
- Runs ALL quality checks (mypy, format, lint, docstring, test)
- PLUS security checks (bandit, pip-audit)
- The `-i` flag means "ignore errors and continue"

**Expected output:**
- All checks pass with green success messages
- Final summary showing everything passed

**This is the MOST comprehensive check available!**

**✅ Checklist:**
- [ ] All quality checks pass (mypy, format, lint, docstring, test)
- [ ] Security checks pass (bandit, pip-audit)
- [ ] Overall success message displayed
- [ ] No errors or warnings

---

## ✅ Phase 7: Core Functionality Testing (30 minutes)

Testing the core components of the repository to ensure they work as expected. This includes the logger, configuration management, timer, transformers, and exception hierarchy.

The tests are included in the `tests/` directory and can be run using `make test`. However, we will also perform some manual tests to verify the core functionality.

```
# Windows / Linux / macOS
make test
make test-detailed
```


**✅ Checklist:**
- [ ] All automatic tests run and pass successfully in compressed form.
- [ ] All automatic tests run and pass successfully in detailed form.
---

## ✅ Phase 8: Git Hooks Testing (20 minutes)

### 8.1 Install Git Hooks

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**

```
# Windows
make install-hooks

# Linux/macOS
make install-hooks-linux
```

**What this does:**
- Copies pre-commit hook to `.git/hooks/pre-commit`
- Copies pre-push hook to `.git/hooks/pre-push`
- Makes hooks executable (Linux/macOS)

**Verify installation:**
```bash
# Check if hooks exist
ls .git/hooks/

# You should see:
# - pre-commit
# - pre-push
```

**✅ Checklist:**
- [ ] Pre-commit hook installed to `.git/hooks/pre-commit`
- [ ] Pre-push hook installed to `.git/hooks/pre-push`
- [ ] Success message displayed


### 8.2 Test Pre-Commit Hook (Branch Protection)

**📍 Where:** Project root directory (command line)

**🔧 Test 1: Try to commit to main branch (should be BLOCKED)**

```bash
# Make sure you're on main branch
git checkout main

# Create a test file
echo "# Test" >> test_file.txt

# Try to commit (this should FAIL)
git add test_file.txt
git commit -m "Test commit on main"
```

**Expected behavior:**
- ❌ Commit is **BLOCKED**
- Error message: "Commits to main branch are not allowed"
- File is NOT committed

**Cleanup:**
```bash
git reset HEAD test_file.txt
rm test_file.txt
```

**✅ Checklist:**
- [ ] Commit is BLOCKED
- [ ] Error message displayed: "Commits to main branch are not allowed"
- [ ] File not committed

**🔧 Test 2: Try to commit to develop branch (should be BLOCKED)**

```bash
# Create and switch to develop branch
git checkout -b develop

# Create a test file
echo "# Test" >> test_file.txt

# Try to commit (this should FAIL)
git add test_file.txt
git commit -m "Test commit on develop"
```

**Expected behavior:**
- ❌ Commit is **BLOCKED**
- Error message: "Commits to develop branch are not allowed"
- File is NOT committed

**Cleanup:**
```bash
git reset HEAD test_file.txt
rm test_file.txt
git checkout main
git branch -D develop
```

**✅ Checklist:**
- [ ] Commit is BLOCKED
- [ ] Error message displayed: "Commits to develop branch are not allowed"
- [ ] File not committed

**🔧 Test 3: Commit to feature branch (should WORK)**

```bash
# Create and switch to feature branch
git checkout -b feature/test-hooks

# Create a test file
echo "# Test" >> test_file.txt

# Try to commit (this should SUCCEED)
git add test_file.txt
git commit -m "Test commit on feature branch"
```

**Expected behavior:**
- ✅ Commit is **ALLOWED**
- Commit successful
- File is committed

**Cleanup:**
```bash
# Undo the commit
git reset --hard HEAD~1

# Switch back to main and delete feature branch
git checkout main
git branch -D feature/test-hooks
```

**✅ Checklist:**
- [ ] Commit is ALLOWED
- [ ] Commit successful
- [ ] File committed

### 8.3 Test Pre-Push Hook (Security Checks)

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**

**Step 1: Create feature branch with changes**
```bash
# Create and switch to feature branch
git checkout -b feature/test-security

# Make a small change to README
echo "# Test change" >> README.md

# Commit the change
git add README.md
git commit -m "Test: minor README change"
```

**Step 2: Try to push (this triggers security checks)**
```bash
git push -u origin feature/test-security
```

**What happens:**
1. Pre-push hook runs automatically
2. Bandit scans the changed files (README.md in this case)
3. pip-audit checks all dependencies
4. If no issues: Push proceeds
5. If issues found: Push is blocked

**Expected output:**
```
Running security checks on changed files...
[bandit] Running Bandit security scanner...
[bandit] No issues identified.
[pip-audit] Checking dependencies for vulnerabilities...
[pip-audit] No known vulnerabilities found.
Pushing to origin...
```

**✅ Checklist:**
- [ ] Pre-push hook runs automatically
- [ ] Bandit scans changed files
- [ ] pip-audit checks dependencies
- [ ] If no issues: Push proceeds
- [ ] If issues found: Push is blocked
- [ ] Security checks run before push
- [ ] Output shows "Running security checks on changed files..."
- [ ] Bandit results displayed
- [ ] pip-audit results displayed
- [ ] Push completes successfully (if no security issues)

**Step 3: Cleanup**
```bash
# Switch back to main
git checkout main

# Delete local branch
git branch -D feature/test-security

# Delete remote branch (if it was pushed)
git push origin --delete feature/test-security
```

---

## ✅ Phase 9: GitHub Integration Testing (15 minutes)

### 9.1 Test GitHub Actions CI/CD

**📍 Where:** Project root directory (command line) + GitHub website

**🔧 How to do it:**

**Step 1: Create feature branch**
```bash
# Create and switch to feature branch
git checkout -b feature/test-ci
```

**Step 2: Make a small change**
```bash
# Create a test file
echo "# CI Test" >> test_ci.txt

# Commit and push
git add test_ci.txt
git commit -m "Test: trigger CI pipeline"
git push -u origin feature/test-ci
```

**Step 3: Create Pull Request on GitHub**

**📍 Where:** GitHub website (https://github.com/your-username/your-repo)

1. Go to your GitHub repository
2. You should see a yellow banner: "feature/test-ci had recent pushes"
3. Click "Compare & pull request" button

   **OR manually:**
   - Click "Pull requests" tab
   - Click "New pull request"
   - Base: `main`, Compare: `feature/test-ci`
   - Click "Create pull request"

4. Add title: "Test: CI Pipeline"
5. Click "Create pull request"

**✅ Checklist:**
- [ ] Go to GitHub repository
- [ ] Click "Pull requests" tab
- [ ] Click "New pull request"
- [ ] Base: `main`, Compare: `feature/test-ci`
- [ ] Click "Create pull request"
- [ ] Add title: "Test: CI Pipeline"
- [ ] Click "Create pull request"

**Step 4: Monitor CI/CD Pipeline**

**📍 Where:** GitHub Pull Request page

**🔧 How to monitor:**
1. On the PR page, scroll down to "Checks" section
2. You should see "CI - Pull Request Checks" workflow running
3. Click "Details" to see the workflow run
4. You'll see 3 jobs running in parallel (Python 3.11, 3.12, 3.13)

**✅ Checklist:**
- [ ] GitHub Actions workflow starts automatically
- [ ] Workflow name: "CI - Pull Request Checks"
- [ ] Matrix testing runs for Python 3.11, 3.12, 3.13
- [ ] All jobs start

**Step 5: Verify Each Job**

**📍 Where:** GitHub Actions workflow run page

**🔧 How to verify:**
- Click on each job (e.g., "test (3.11)")
- Expand each step to see details
- All steps should have green checkmarks

**For each Python version (3.11, 3.12, 3.13):**
- [ ] Checkout code - Success ✅
- [ ] Set up Python - Success ✅
- [ ] Install uv - Success ✅
- [ ] Install dependencies - Success ✅
- [ ] Run all quality checks with security - Success ✅
- [ ] Upload coverage reports - Success ✅

**Step 6: Verify All Checks Pass**

**📍 Where:** GitHub Pull Request page

**🔧 What to check:**
- All 3 jobs should show green checkmarks
- PR should show "All checks have passed" at the bottom

**✅ Checklist:**
- [ ] All 3 matrix jobs complete successfully (green checkmarks)
- [ ] No failed jobs
- [ ] Coverage artifacts uploaded
- [ ] PR shows "All checks have passed"

**Step 7: Cleanup**

**📍 Where:** GitHub website + command line

**🔧 How to cleanup:**

**On GitHub:**
1. Go to the Pull Request
2. Click "Close pull request" (don't merge)
3. Click "Delete branch" button that appears

**On command line:**
```bash
# Switch back to main
git checkout main

# Delete local branch
git branch -D feature/test-ci
```

**✅ Checklist:**
- [ ] Close pull request (don't merge)
- [ ] Delete branch on GitHub
- [ ] Delete local branch

---

## ✅ Phase 10: Documentation Verification (15 minutes)

### 10.1 Verify README Accuracy

**📍 Where:** Project root directory

**🔧 How to do it:**
```bash
# Open README in your editor or browser
# Windows: start README.md
# Linux: xdg-open README.md
# macOS: open README.md

# Or view in terminal
cat README.md | less
```

**What to check:**
- Try running a few commands from README to verify they work
- Check that file paths mentioned actually exist
- Verify table of contents links work (if viewing on GitHub)

**✅ Checklist:**
- [ ] Open README.md
- [ ] Verify all commands work as documented
- [ ] Verify all file paths are correct
- [ ] Verify all examples run successfully
- [ ] Verify table of contents links work

### 10.2 Verify Specialized Documentation

**📍 Where:** `docs/` directory

**🔧 How to do it:**
```bash
# View each documentation file
cat docs/EVALUATION.md | less
cat docs/EVALUATION_SUMMARY.md | less

# Or open in editor
code docs/  # VS Code
```

**What to check:**
- Verify information is accurate and up-to-date
- Check line counts match what's documented
- Verify commands in documentation actually work

**✅ Checklist:**
- [ ] Open `docs/EVALUATION.md`
- [ ] Verify rating and metrics are accurate
- [ ] Verify improvement roadmap is clear
- [ ] Open `docs/EVALUATION_SUMMARY.md`
- [ ] Verify all sections are accurate
- [ ] Verify line counts are correct

---

## ✅ Phase 11: Makefile Command Testing (20 minutes)

### 11.1 Test Help Commands

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**

**Test help command:**
```bash
make help
```

**Expected output:**
- List of all available make commands
- Commands grouped by category (Setup, Quality Checks, Testing, etc.)
- Brief description for each command

**Test hello command:**
```bash
make hello
```

**Expected output:**
- Greeting message
- Repository name and information
- Current configuration

**✅ Checklist:**
- [ ] Help displayed with all available commands
- [ ] Commands organized by category
- [ ] Descriptions are clear
- [ ] Greeting message displayed
- [ ] Repository information shown

### 11.2 Test File-Specific Commands

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**

**Step 1: Configure file in make_config.mk**
```bash
# Open make_config.mk in editor
# Windows: notepad make_config.mk
# Linux/macOS: nano make_config.mk

# Set these values:
FILE_FOLDER = utils
FILE_NAME = leap_year
```

**Step 2: Test each file-specific command**

```bash
# Type check single file
make mypy-f
```
**Expected:** Type checks only `src/utils/leap_year.py`

```bash
# Format check single file
make format-check-f
```
**Expected:** Checks formatting for single file only

```bash
# Lint check single file
make lint-check-f
```
**Expected:** Lints single file only

```bash
# Docstring check single file
make docstring-check-f
```
**Expected:** Checks docstrings for single file only

```bash
# Test single file
make test-f
```
**Expected:** Runs tests for `tests/tests_utils/test_leap_year.py` only

```bash
# Run all checks for single file
make all-f
```
**Expected:** Runs all checks (mypy, format, lint, docstring, test) for single file

**✅ Checklist:**
- [ ] Type checks single file
- [ ] No errors reported
- [ ] Checks formatting for single file
- [ ] No issues reported
- [ ] Lints single file
- [ ] No violations reported
- [ ] Checks docstrings for single file
- [ ] No issues reported
- [ ] Runs tests for single file
- [ ] All tests pass
- [ ] Runs all checks for single file
- [ ] All checks pass

---

## ✅ Phase 12: Final Verification (10 minutes)

### 12.1 Repository Health Check

**📍 Where:** Project root directory

**🔧 How to do it:**

**Check repository structure:**
```bash
# List all files
tree  # or ls -R

# Check for unwanted files
find . -name "__pycache__" -type d
find . -name "*.pyc"

# Verify .gitignore is working
git status  # Should not show ignored files
```

**Verify Git status:**
```bash
git status
# Should show: "nothing to commit, working tree clean"
# Or only intentional changes
```

**✅ Checklist:**
- [ ] All files present in repository
- [ ] No unnecessary files (e.g., `__pycache__`, `.pyc`, test files)
- [ ] `.gitignore` working correctly
- [ ] All documentation up-to-date
- [ ] All tests passing
- [ ] All quality checks passing
- [ ] Security checks passing
- [ ] Git hooks installed and working
- [ ] CI/CD pipeline working

### 12.2 Dependency Verification

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
# List all installed packages
uv pip list

# Count external libraries (excluding pip, setuptools, etc.)
uv pip list | grep -v "pip\|setuptools\|wheel" | wc -l
```

**Expected number of libraries can vary:**

**✅ Checklist:**
- [ ] No unexpected dependencies
- [ ] All versions compatible

### 12.3 Coverage Verification

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
# Run coverage with log
make cover-log

# View the coverage log
cat reports/cover_log.csv

# Or view HTML report
# Windows: start coverage/index.html
# Linux: xdg-open coverage/index.html
# macOS: open coverage/index.html
```

**Expected output:**
- Coverage percentage >= 80%
- CSV file created in `reports/cover_log.csv`
- HTML report in `coverage/index.html`

**✅ Checklist:**
- [ ] Coverage >= 80%
- [ ] Coverage report generated
- [ ] Coverage log saved to `reports/cover_log.csv`

### 12.4 Final Quality Check

**📍 Where:** Project root directory (command line)

**🔧 How to do it:**
```bash
# Run the most comprehensive check
make all-secure -i
```

**What this does:**
- Runs ALL quality checks (mypy, format, lint, docstring, test)
- Runs ALL security checks (bandit, pip-audit)
- The `-i` flag continues even if one check fails

**Expected output:**
- All checks pass with green success messages
- Final summary showing everything passed
- No errors or warnings

**This is your final "go/no-go" check!**

**✅ Checklist:**
- [ ] All quality checks pass
- [ ] Security checks pass
- [ ] No errors or warnings
- [ ] Success message displayed


---

## ✅ Phase 13: Cleanup and Documentation (10 minutes)

### 13.1 Clean Up Test Artifacts

**📍 Where:** Project root directory

**🔧 How to do it:**

**Remove test files:**
```bash
# List any test files you created
ls test_*.py

# Remove them
rm test_*.py  # If any exist

# Remove any other test artifacts
rm test_ci.txt  # If it exists
```

**Check for temporary branches:**
```bash
# List all branches
git branch -a

# Delete any test branches locally
git branch -D feature/test-ci  # If it exists
git branch -D feature/test-security  # If it exists
git branch -D feature/test-hooks  # If it exists
```

**Clean up Git:**
```bash
# Make sure working directory is clean
git status

# If there are uncommitted changes you don't want:
git reset --hard HEAD
git clean -fd  # Remove untracked files (be careful!)
```

**✅ Checklist:**
- [ ] Remove any test files created during manual testing
- [ ] Remove any temporary branches
- [ ] Remove any test commits (if needed)

### 13.2 Update Repository Documentation

**📍 Where:** Project root directory

**🔧 How to do it:**

**Update README.md:**
```bash
# Open in editor
# Windows: notepad README.md
# Linux/macOS: nano README.md  or  code README.md

# Update:
# - Project name/title
# - Project description
# - Author information
# - Any project-specific details
```

**Update pyproject.toml:**
```bash
# Open in editor
# Windows: notepad pyproject.toml
# Linux/macOS: nano pyproject.toml

# Update these fields:
# [project]
# name = "your-project-name"
# description = "Your project description"
# authors = [{name = "Your Name", email = "your.email@example.com"}]
```

**Update configurations/python_personal.conf:**
```bash
# Open in editor
nano configurations/python_personal.conf

# Update:
# name = "your_project_name"
# Any other project-specific settings
```

**Update .env:**
```bash
# Open in editor
nano .env

# Update environment variables if needed:
# ENV_DATA_FOLDER=../../data  # Or your data location
# ENV_LOGS_FOLDER=../../logs  # Or your logs location
```

**Commit changes:**
```bash
git add README.md pyproject.toml configurations/python_personal.conf .env
git commit -m "docs: Update project-specific information"
git push origin main
```

**✅ Checklist:**
- [ ] Update README.md with repository-specific information
- [ ] Update `pyproject.toml` with correct project name, author, email
- [ ] Update `configurations/python_personal.conf` with project-specific settings
- [ ] Update `.env` with project-specific environment variables

### 13.3 Create Initial Release (Optional)

**📍 Where:** Project root directory (command line) + GitHub website

**🔧 How to do it:**

**Step 1: Create and push tag**
```bash
# Create annotated tag
git tag -a v1.0.0 -m "Initial release"

# Push tag to GitHub
git push origin v1.0.0
```

**Step 2: Create GitHub release**
1. Go to your GitHub repository
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Select tag: `v1.0.0`
5. Release title: `v1.0.0 - Initial Release`
6. Description: Add release notes, e.g.:
   ```
   ## Initial Release

   - Python minimal template with full functionality
   - Comprehensive testing and quality checks
   - CI/CD pipeline with GitHub Actions
   - Git hooks for branch protection and security
   - 80%+ test coverage
   ```
7. Click "Publish release"

**✅ Checklist:**
- [ ] Tag initial release: `git tag -a v1.0.0 -m "Initial release"`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub release from tag
- [ ] Add release notes

---

## 📊 Testing Summary

### Completion Checklist
- [ ] Phase 1: Repository Setup (15 min)
- [ ] Phase 2: Local Environment Setup (20 min)
- [ ] Phase 3: Configuration Testing (15 min)
- [ ] Phase 4: Code Quality Checks (30 min)
- [ ] Phase 5: Testing (20 min)
- [ ] Phase 6: Security Checks (15 min)
- [ ] Phase 7: Core Functionality Testing (30 min)
- [ ] Phase 8: Git Hooks Testing (20 min)
- [ ] Phase 9: GitHub Integration Testing (15 min)
- [ ] Phase 10: Cross-Platform Testing (30 min) - Optional
- [ ] Phase 11: Documentation Verification (15 min)
- [ ] Phase 12: Makefile Command Testing (20 min)
- [ ] Phase 13: Final Verification (10 min)
- [ ] Phase 14: Cleanup and Documentation (10 min)

### Total Time
- **Required phases:** ~2 hours 15 minutes
- **With optional cross-platform testing:** ~2 hours 45 minutes

### Issues Found
Document any issues found during testing:

| Phase | Issue Description | Severity | Resolution |
|-------|------------------|----------|------------|
|       |                  |          |            |
|       |                  |          |            |
|       |                  |          |            |

### Final Status
- [ ] ✅ All required tests passed
- [ ] ✅ Repository is production-ready
- [ ] ✅ Documentation is accurate
- [ ] ✅ CI/CD pipeline working
- [ ] ✅ Git hooks working
- [ ] ✅ All functionality verified

---

## 🎯 Success Criteria

The repository is considered **fully tested and production-ready** when:

1. ✅ All quality checks pass (`make all-secure -i`)
2. ✅ All tests pass with >= 80% coverage
3. ✅ Security checks pass (no vulnerabilities)
4. ✅ Git hooks installed and working correctly
5. ✅ CI/CD pipeline passes for all Python versions (3.11, 3.12, 3.13)
6. ✅ Core functionality verified (Logger, Config, Timer, Transformers, Exceptions)
7. ✅ Documentation is accurate and complete
8. ✅ Cross-platform compatibility verified (at least 2 platforms)

---

**Testing Completed By:** `_________________`
**Date:** `_________________`
**Repository URL:** `_________________`
**Final Status:** ✅ PASSED / ❌ FAILED
**Notes:** `_________________`

---

# Appendix

## ✅ A1: Cross-Platform Testing (Optional, 30 minutes)

**📍 Purpose:** Verify the repository works on different operating systems

### A1.1 Windows Testing

**📍 Where:** Windows machine (PowerShell or Command Prompt)

**🔧 How to do it:**
```powershell
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Set up repository
make set-up-repo

# Create virtual environment (Windows version)
make create-venv

# Run all checks
make all-secure -i

# Install Git hooks
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1

# Test pre-commit hook (try to commit to main - should fail)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test"  # Should be BLOCKED

# Clean up
git reset HEAD test.txt
rm test.txt
```

**✅ Checklist:**
- [ ] Clone repository on Windows
- [ ] Run `make set-up-repo`
- [ ] Run `make create-venv`
- [ ] Run `make all-secure -i`
- [ ] All checks pass
- [ ] Install hooks: `powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1`
- [ ] Test pre-commit hook
- [ ] Test pre-push hook

### A1.2 Linux Testing

**📍 Where:** Linux machine (Terminal)

**🔧 How to do it:**
```bash
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Set up repository
make set-up-repo

# Create virtual environment (Linux version)
make create-venv-linux

# Run all checks
make all-secure -i

# Install Git hooks
bash scripts/install-hooks.sh

# Test pre-commit hook (try to commit to main - should fail)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test"  # Should be BLOCKED

# Clean up
git reset HEAD test.txt
rm test.txt
```

**✅ Checklist:**
- [ ] Clone repository on Linux
- [ ] Run `make set-up-repo`
- [ ] Run `make create-venv-linux`
- [ ] Run `make all-secure -i`
- [ ] All checks pass
- [ ] Install hooks: `bash scripts/install-hooks.sh`
- [ ] Test pre-commit hook
- [ ] Test pre-push hook

### A1.3 macOS Testing

**📍 Where:** macOS machine (Terminal)

**🔧 How to do it:**
```bash
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Set up repository
make set-up-repo

# Create virtual environment (macOS uses Linux version)
make create-venv-linux

# Run all checks
make all-secure -i

# Install Git hooks
bash scripts/install-hooks.sh

# Test pre-commit hook (try to commit to main - should fail)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test"  # Should be BLOCKED

# Clean up
git reset HEAD test.txt
rm test.txt
```

**✅ Checklist:**
- [ ] Clone repository on macOS
- [ ] Run `make set-up-repo`
- [ ] Run `make create-venv-linux`
- [ ] Run `make all-secure -i`
- [ ] All checks pass
- [ ] Install hooks: `bash scripts/install-hooks.sh`
- [ ] Test pre-commit hook
- [ ] Test pre-push hook

---

# ✅ A2 GitHub Branch Protection Testing Guide

## Overview

This guide covers testing and verifying GitHub branch protection rules in combination with local Git hooks to ensure a comprehensive protection system for your repository.

---

## A2.1 Test GitHub Branch Protection Rules

**📍 Where:** GitHub website + Project root directory (command line)

### A2.1.1 Configure Branch Protection on GitHub

**📍 Where:** GitHub repository settings

1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Branches" in the left sidebar
4. Under "Branch protection rules", click "Add rule"
5. Configure the rule:
   - **Pattern name:** `main`
   - **Require a pull request before merging:** ✅ Check
   - **Require approvals:** ✅ Check (set to 1)
   - **Dismiss stale pull request approvals when new commits are pushed:** ✅ Check
   - **Require status checks to pass before merging:** ✅ Check
   - **Status checks that must pass:**
     - `test (3.11)` ✅
     - `test (3.12)` ✅
     - `test (3.13)` ✅
   - **Require branches to be up to date before merging:** ✅ Check
   - **Require code reviews before merging:** ✅ Check
   - **Require conversation resolution before merging:** ✅ Check
6. Click "Create" button

**✅ Verification Checklist:**
- [ ] Navigate to Settings → Branches
- [ ] Create new branch protection rule for `main`
- [ ] Require pull request before merging
- [ ] Require status checks (all 3 Python versions)
- [ ] Require code review
- [ ] Rule successfully created

---

### A2.1.2 Test Branch Protection - Verify Main Branch is Protected

**📍 Where:** Project root directory (command line)

**Purpose:** Verify that direct pushes to `main` are blocked

**Steps:**

```bash
# Try to push directly to main (should be BLOCKED at GitHub)
git checkout main

# Create a test file
echo "# Direct push test" >> test_protection.txt

# Commit it
git add test_protection.txt
git commit -m "Test: attempt direct push to main"

# Try to push (this should fail at GitHub if you have push protection enabled)
git push origin main
```

**Expected behavior:**
- ❌ Push is **REJECTED** by GitHub
- Error message: "Pushing to `main` is not allowed" or similar
- If not rejected at push, it will be rejected when trying to merge the PR

**Cleanup:**
```bash
# Undo the commit
git reset --hard HEAD~1
```

**✅ Verification Checklist:**
- [ ] Attempt direct push to `main`
- [ ] Push is blocked (either at push time or merge time)
- [ ] Error message displayed
- [ ] Branch protection is working
- [ ] Local changes cleaned up

---

### A2.1.3 Test Branch Protection - Create PR with Required Approvals

**📍 Where:** GitHub website + Project root directory (command line)

**Purpose:** Verify that pull requests require status checks and approvals

#### Step 1: Create feature branch and PR

**On command line:**
```bash
# Create and switch to feature branch
git checkout -b feature/test-branch-protection

# Create a test file
echo "# Protection test" >> test_protection.txt

# Commit and push
git add test_protection.txt
git commit -m "feat: Add protection test file"
git push -u origin feature/test-branch-protection
```

**On GitHub:**
1. Go to your repository
2. Click "Pull requests" tab
3. Click "New pull request"
4. Base: `main`, Compare: `feature/test-branch-protection`
5. Click "Create pull request"
6. Add title: "Test: Branch Protection with PR"

#### Step 2: Verify PR Status Checks

1. On the PR page, scroll down to "Checks" section
2. Verify that status checks are running:
   - `test (3.11)` - should show as pending/running
   - `test (3.12)` - should show as pending/running
   - `test (3.13)` - should show as pending/running
3. Wait for all checks to complete (should all pass ✅)

**Expected outcome:**
- All three Python version tests run in parallel
- All tests should pass (green checkmarks)
- Timeline shows test completion

**✅ Verification Checklist:**
- [ ] Create feature branch
- [ ] Create pull request to `main`
- [ ] Status checks start running
- [ ] All 3 status checks (Python 3.11, 3.12, 3.13) visible
- [ ] All status checks pass

#### Step 3: Verify Merge Button is Disabled Without Approval

1. On the PR page, look at "Merge pull request" button
2. It should be **disabled** (greyed out)
3. Error message should show one or both:
   - "At least 1 review approval is required"
   - "Pending status checks..."

**✅ Verification Checklist:**
- [ ] All status checks pass (green checkmarks)
- [ ] Merge button is disabled/greyed out
- [ ] Error message indicates approvals required or checks pending
- [ ] Cannot merge without approval and passing checks

---

### A2.1.4 Test Branch Protection - Approve and Merge

**📍 Where:** GitHub website

**Purpose:** Verify that merge is allowed only after approval

**Option A: If you want to test the approval process**

1. On the PR page, scroll to "Reviewers" section
2. Click "Review changes" button (as a reviewer)
3. Select "Approve"
4. Click "Submit review"
5. Verify all checks pass (green checkmarks)
6. Now "Merge pull request" button should be **enabled**
7. Click "Merge pull request"

**Option B: Skip approval and just verify you cannot merge without it (RECOMMENDED FOR THIS TEST)**

1. Try clicking "Merge pull request" button
2. It should remain **disabled**
3. Hover over it to see why: "Requires at least 1 approval"

**For this test, we recommend Option B** to avoid actually merging test code.

**✅ Verification Checklist:**
- [ ] All status checks pass (green checkmarks)
- [ ] Merge button becomes enabled ONLY after approval (if using Option A)
- [ ] Merge button remains disabled without approval (if using Option B)
- [ ] Branch protection rules are enforced

---

### A2.1.5 Cleanup

**📍 Where:** GitHub website + Project root directory (command line)

**Purpose:** Remove test artifacts and branches

**On GitHub:**
1. Go back to the PR
2. Click "Close pull request" button (don't merge)
3. Click "Delete branch" to remove the feature branch from GitHub

**On command line:**
```bash
# Switch back to main
git checkout main

# Delete local feature branch
git branch -D feature/test-branch-protection
```

**✅ Verification Checklist:**
- [ ] Close pull request (don't merge)
- [ ] Delete branch on GitHub
- [ ] Delete local branch
- [ ] No test files remain in repository

---

## Summary: Complete Protection System

### What This Test Verifies

✅ **Direct pushes to `main` are blocked** - Cannot push directly without pull request

✅ **All changes must go through pull requests** - Enforced by branch protection rules

✅ **Status checks (CI/CD) must pass before merging** - Tests must pass on all Python versions (3.11, 3.12, 3.13)

✅ **Code reviews/approvals are required before merging** - At least 1 approval needed

✅ **Branch protection rules are properly configured** - All settings correctly applied on GitHub

✅ **Local git hooks work with remote protection** - Comprehensive layered protection

### Layered Protection Architecture

This creates a **three-layer protection system:**

**Layer 1: Local Git Hooks**
- `pre-commit` hook: Prevents accidental commits to protected branches
- `pre-push` hook: Runs security checks before pushing
- Location: `.git/hooks/`
- Benefit: Immediate feedback, prevents local mistakes

**Layer 2: GitHub Branch Protection**
- Enforces pull request requirement
- Requires status checks (CI/CD) to pass
- Requires code reviews/approvals
- Location: GitHub repository settings
- Benefit: Prevents merging of non-compliant changes

**Layer 3: GitHub Actions CI/CD**
- Runs automated tests on all Python versions
- Runs code quality checks (mypy, ruff, bandit)
- Reports results back to PR
- Location: `.github/workflows/ci.yml`
- Benefit: Automated validation of code quality and functionality

### How They Work Together

```
Developer commits code
         ↓
Local pre-commit hook checks branch
  (blocks commits to main/develop)
         ↓
Developer pushes to feature branch
         ↓
Local pre-push hook runs security checks
  (bandit scans for vulnerabilities)
         ↓
Developer creates Pull Request
         ↓
GitHub Actions CI starts automatically
  (tests on Python 3.11, 3.12, 3.13)
         ↓
GitHub branch protection evaluates PR
  - Status checks must pass ✅
  - Approval required ✅
         ↓
Developer/Reviewer approves PR
         ↓
Merge button becomes enabled
         ↓
Code is merged to main/develop
         ↓
✅ Codebase stays stable and secure
```

### Result

Only **approved, tested, and security-scanned code** reaches production branches (`main`, `develop`).

---

## Troubleshooting

### Issue: Branch Protection Rule Not Applied

**Solution:** 
- Ensure you're an admin of the repository
- Check that you created the rule for the correct branch pattern (`main`)
- Refresh the GitHub page to see updated settings

### Issue: Status Checks Not Appearing in PR

**Solution:**
- Ensure `.github/workflows/ci.yml` is in the repository
- Push the workflow file to `main` first (it only runs on branches)
- Wait for the workflow to trigger (may take a few seconds)
- Check "Actions" tab in GitHub to see workflow status

### Issue: Pre-Push Hook Fails Locally

**Solution:**
- Ensure git hooks are installed: `make install-hooks` (Windows) or `make install-hooks-linux` (Linux/macOS)
- Check that bandit is installed: `uv run --no-project bandit --version`
- Run `make security-check` to test bandit separately

### Issue: Cannot Delete Feature Branch

**Solution:**
- Ensure the branch is closed/not merged
- In PR, click "Delete branch" button
- Locally, use `git branch -D feature/test-branch-protection` to force delete

---

## Best Practices

✅ **Always create feature branches** for new work

✅ **Never commit directly to `main` or `develop`** - use feature branches

✅ **Wait for all status checks to pass** before reviewing/merging

✅ **Get at least one approval** before merging (ideally from a different developer)

✅ **Keep commit messages descriptive** for future reference

✅ **Delete feature branches after merging** to keep repository clean

❌ **Avoid bypassing checks** - only use `--no-verify` in emergencies, never merge without checks

❌ **Never force-push to `main` or `develop`** - can corrupt repository

❌ **Don't merge your own code** - always have someone else review

---

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

