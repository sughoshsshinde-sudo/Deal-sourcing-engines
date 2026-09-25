import csv
import glob
import os
import urllib.parse
import webbrowser
from datetime import datetime

BASE_DIR = r"C:\Users\Sughosh\Downloads\RegTech"
HF_DIR = os.path.join(BASE_DIR, "HF Scraper Results")
GITHUB_DIR = os.path.join(BASE_DIR, "GitHub Scraper Results")

TEST_LIMIT = 10


def latest_file(folder, pattern):
    files = glob.glob(os.path.join(folder, pattern))

    if not files:
        raise FileNotFoundError(
            f"No file found in {folder} matching {pattern}"
        )

    return max(files, key=os.path.getmtime)


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def make_hf_candidates(rows):
    candidates = []

    for row in rows:
        candidates.append({
            "Source": "Hugging Face",
            "Name": row.get("Founder / Org Handle", ""),
            "Handle": row.get("Founder / Org Handle", ""),
            "Project": row.get("Project Name", ""),
            "Description": row.get("Matched Thesis Signals", ""),
            "Bio": "",
            "Company": "",
            "Location": "",
            "Website": "",
            "Profile": row.get("Hugging Face Profile", ""),
            "Project URL": row.get("Project URL", ""),
            "Score": row.get("Thesis Score", ""),
        })

    return candidates


def make_github_candidates(rows):
    candidates = []

    for row in rows:
        candidates.append({
            "Source": "GitHub",
            "Name": row.get("Full Name", "") or row.get("GitHub Handle", ""),
            "Handle": row.get("GitHub Handle", ""),
            "Project": row.get("Repository Name", ""),
            "Description": row.get("Description", ""),
            "Bio": row.get("Bio", ""),
            "Company": row.get("Company", ""),
            "Location": row.get("Location", ""),
            "Website": row.get("Website", ""),
            "Profile": row.get("GitHub Profile", ""),
            "Project URL": row.get("Repository URL", ""),
            "Score": row.get("Builder Score", ""),
        })

    return candidates


def create_searches(candidate):

    name = candidate["Name"]
    handle = candidate["Handle"]
    project = candidate["Project"]
    company = candidate["Company"]
    location = candidate["Location"]

    searches = []

    # Search using the person's name
    if name:
        searches.append(
            f'site:linkedin.com/in "{name}"'
        )

    # Name + project
    if name and project:
        searches.append(
            f'site:linkedin.com/in "{name}" "{project}"'
        )

    # Handle + LinkedIn
    if handle:
        searches.append(
            f'site:linkedin.com/in "{handle}"'
        )

    # Name + company
    if name and company:
        searches.append(
            f'site:linkedin.com/in "{name}" "{company}"'
        )

    # Name + location
    if name and location:
        searches.append(
            f'site:linkedin.com/in "{name}" "{location}"'
        )

    return searches


def google_url(query):
    encoded = urllib.parse.quote_plus(query)

    return (
        "https://www.google.com/search?q="
        + encoded
    )


hf_file = latest_file(
    HF_DIR,
    "hf_founder_discovery_*.csv"
)

github_file = latest_file(
    GITHUB_DIR,
    "github_founder_scouting_*.csv"
)

print("=" * 70)
print("LINKEDIN FINDER — TEST MODE")
print("=" * 70)

print(f"\nHF file:")
print(os.path.basename(hf_file))

print(f"\nGitHub file:")
print(os.path.basename(github_file))

hf_rows = read_csv(hf_file)
github_rows = read_csv(github_file)

candidates = (
    make_hf_candidates(hf_rows)
    + make_github_candidates(github_rows)
)

print(f"\nHF candidates:      {len(hf_rows)}")
print(f"GitHub candidates:  {len(github_rows)}")
print(f"Total candidates:   {len(candidates)}")

# Take first TEST_LIMIT for initial test
test_candidates = candidates[:TEST_LIMIT]

results = []

print("\n")
print("=" * 70)
print(f"GENERATING LINKEDIN SEARCHES FOR {len(test_candidates)} PEOPLE")
print("=" * 70)

for index, candidate in enumerate(test_candidates, start=1):

    searches = create_searches(candidate)

    print("\n" + "-" * 70)
    print(f"[{index}/{len(test_candidates)}]")
    print(f"Name:      {candidate['Name']}")
    print(f"Handle:    {candidate['Handle']}")
    print(f"Project:   {candidate['Project']}")
    print(f"Source:    {candidate['Source']}")

    print("\nSearch options:")

    for search_number, query in enumerate(searches, start=1):

        url = google_url(query)

        print(f"\n{search_number}. {query}")
        print(f"   {url}")

    results.append({
        "Source": candidate["Source"],
        "Name": candidate["Name"],
        "Handle": candidate["Handle"],
        "Project": candidate["Project"],
        "GitHub/HF Profile": candidate["Profile"],
        "Project URL": candidate["Project URL"],
        "Score": candidate["Score"],
        "Search 1": google_url(searches[0])
            if len(searches) > 0 else "",
        "Search 2": google_url(searches[1])
            if len(searches) > 1 else "",
        "Search 3": google_url(searches[2])
            if len(searches) > 2 else "",
        "Search 4": google_url(searches[3])
            if len(searches) > 3 else "",
        "Search 5": google_url(searches[4])
            if len(searches) > 4 else "",
    })


timestamp = datetime.now().strftime("%Y%m%d_%H%M")

output_file = os.path.join(
    BASE_DIR,
    f"linkedin_finder_test_{timestamp}.csv"
)

with open(
    output_file,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    fieldnames = [
        "Source",
        "Name",
        "Handle",
        "Project",
        "GitHub/HF Profile",
        "Project URL",
        "Score",
        "Search 1",
        "Search 2",
        "Search 3",
        "Search 4",
        "Search 5",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print("\n")
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)

print(f"\nSaved file:")
print(output_file)

print("\nIMPORTANT:")
print("This first version ONLY generates targeted searches.")
print("We will NOT scale it yet.")