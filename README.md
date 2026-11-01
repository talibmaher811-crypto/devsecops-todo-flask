# DevSecOps TODO Flask — Stage 1

A small Flask TODO API used to practice a **shift-left DevSecOps pipeline** with GitHub Actions.

## Stage 1 pipeline

Seven independent checks run in parallel on pushes to `main`, pull requests targeting `main`, and manual workflow dispatch:

| Job | Purpose |
|---|---|
| Gitleaks | Detect accidentally committed secrets |
| Semgrep | Static application security analysis (SAST) |
| Bandit | Python security linting |
| Hadolint | Dockerfile linting |
| Pylint | Python code quality |
| pip-audit | Check Python dependencies for known vulnerabilities |
| pytest | Automated tests with an 80% coverage minimum |

The **Stage 1 Summary** job always runs after the seven checks and publishes a score in the Actions run summary. The PR score gate (such as a minimum score of 80) is intentionally left for Stage 2.

## Stage 2 and Stage 3

- **Security Score Gate** (Stage 2): weighted score 0-100; passes at >= 80 and only if Gitleaks is green. Posts a PR comment.
- **Stage 3** (runs only if the gate passes): Docker Build + smoke test, Trivy image scan, Syft SBOM, and on `main` a push to GHCR with Cosign keyless signing and SBOM attestation.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
pylint app.py --fail-under=8.0
bandit -r app.py -ll
pip-audit -r requirements.txt
```

Semgrep and Hadolint can also be installed locally; GitHub Actions runs them in their respective jobs.

## Run the Flask app

```bash
python app.py
```

Open `http://127.0.0.1:5000`. The app binds to `127.0.0.1` by default; set `FLASK_HOST` (the Dockerfile sets it to `0.0.0.0`) to change that.

## Push to GitHub

Create an empty GitHub repository, then from this project directory:

```bash
git init -b main
git add .
git commit -m "feat: stage 1 shift-left pipeline"
git remote add origin https://github.com/USERNAME/devsecops-todo-flask.git
git push -u origin main
```

Replace `USERNAME` with your GitHub username.

## Important

- Do not commit `.env`, passwords, API keys, tokens, or other secrets.
- The sample `fail/*` scenarios described in the lab guide should be tested on separate branches and pull requests, not committed to `main`.
- This is a learning starter project, not a production-ready TODO service. It uses in-memory storage and has no authentication or database.
