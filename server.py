from flask import Flask, jsonify, redirect, render_template

from src import config
from src.forma_client import AccBuildAPI

ACCOUNT_ID = "51b92711-486c-4b93-b489-81e042ab18aa"
ACCOUNT_NAME = "ACC Build Test"

app = Flask(__name__)


# ── Dashboard Routes ─────────────────────────────────────────────────────────


@app.route("/")
def index():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():
    api = AccBuildAPI(ACCOUNT_ID)
    projects = api.list_projects()

    return render_template(
        "dashboard.html",
        projects=projects,
        account_name=ACCOUNT_NAME,
        user_name="yuxiang ye",
        user_initials="YY",
    )


@app.route("/dashboard/project/<project_id>")
def project_detail(project_id):
    api = AccBuildAPI(ACCOUNT_ID)

    # Get project info
    try:
        project = api.get_project(project_id)
    except Exception:
        project = {"id": project_id, "name": "Unknown", "status": "unknown"}

    # Get RFIs
    rfis = []
    rfi_error = None
    try:
        rfis = api.list_rfis(project_id)
    except Exception:
        rfi_error = "RFI service may not be activated on this project. Activate it in ACC Project Settings."

    # Get Submittals
    submittals = []
    submittal_error = None
    try:
        submittals = api.list_submittals(project_id)
    except Exception:
        submittal_error = "Submittal service may not be activated on this project. Activate it in ACC Project Settings."

    # Get Issues
    issues = []
    issue_error = None
    try:
        issues = api.list_issues(project_id)
    except Exception:
        issue_error = "Issues service may not be activated on this project. Activate it in ACC Project Settings."

    return render_template(
        "project_detail.html",
        project=project,
        rfis=rfis,
        rfi_error=rfi_error,
        submittals=submittals,
        submittal_error=submittal_error,
        issues=issues,
        issue_error=issue_error,
    )


# ── Start server ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n  Autodesk ACC Build Dashboard (2-Legged Auth)")
    print(f"  ---------------------------------------------")
    print(f"  Server running on http://localhost:{config.PORT}")
    print(f"  Dashboard: http://localhost:{config.PORT}/dashboard\n")
    app.run(host="0.0.0.0", port=config.PORT, debug=True)
