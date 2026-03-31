"""List all projects and their RFIs/Submittals from your ACC account."""

import json
from src.forma_client import AccBuildAPI

ACCOUNT_ID = "51b92711-486c-4b93-b489-81e042ab18aa"


def main():
    api = AccBuildAPI(ACCOUNT_ID)

    print("Fetching projects...\n")
    projects = api.list_projects()

    if not projects:
        print("No projects found.")
        return

    for p in projects:
        print(f"Project: {p['name']}")
        print(f"  ID:     {p['id']}")
        print(f"  Status: {p['status']}")

        # Try to fetch RFIs
        try:
            rfis = api.list_rfis(p["id"])
            print(f"  RFIs:   {len(rfis)}")
            for rfi in rfis:
                title = rfi.get("title") or rfi.get("subject", "Untitled")
                status = rfi.get("status", "unknown")
                print(f"    - [{status}] {title}")
        except Exception as e:
            print(f"  RFIs:   (not available - {e})")

        # Try to fetch Submittals
        try:
            submittals = api.list_submittals(p["id"])
            print(f"  Submittals: {len(submittals)}")
            for sub in submittals:
                title = sub.get("title") or sub.get("description", "Untitled")
                status = sub.get("status", "unknown")
                print(f"    - [{status}] {title}")
        except Exception as e:
            print(f"  Submittals: (not available - {e})")

        print()


if __name__ == "__main__":
    main()
