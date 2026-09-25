"""
GitHub Founder Discovery Engine

Discovers technical builders and repositories relevant to predefined
investment themes using publicly available GitHub data.

The script is designed as a discovery and prioritization tool for
early-stage venture sourcing. Results require manual validation and
should not be interpreted as investment recommendations.

Author: Sughosh Shinde
"""

import os
import urllib.parse
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ GitHub token not found.")
    print("Create a .env file in the project directory containing:")
    print("GITHUB_TOKEN=your_token_here")
    raise SystemExit(1)


# ============================================================
# 2. INVESTMENT-THESIS SEARCH KEYWORDS
# ============================================================

KEYWORDS = [

    # Core RegTech
    "regtech",
    "regulatory-compliance",
    "compliance-automation",
    "compliance-platform",

    # AML / Financial Crime
    "aml",
    "anti-money-laundering",
    "crypto-aml",
    "transaction-monitoring",
    "financial-crime",
    "fraud-detection",
    "fraud-prevention",

    # KYC / Identity
    "kyc",
    "kyb",
    "identity-verification",
    "digital-identity",
    "identity-management",
    "zk-kyc",

    # Sanctions / Screening
    "sanctions",
    "sanction-screening",
    "watchlist-screening",
    "pep-screening",

    # Crypto / VASP
    "travel-rule",
    "vasp",
    "vasp-compliance",
    "crypto-compliance",
    "virtual-asset-compliance",

    # Risk / Governance
    "risk-management",
    "risk-scoring",
    "governance",
    "regulatory-reporting",
]


# ============================================================
# 3. OUTPUT CONFIGURATION
# ============================================================

def get_output_path():
    """
    Create and return a portable output directory.

    Generated data is stored inside /outputs rather than in a
    user-specific local directory.
    """

    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "outputs",
    )

    os.makedirs(output_dir, exist_ok=True)

    return output_dir


# ============================================================
# 4. GITHUB API REQUEST
# ============================================================

def github_get(url, headers, params=None):
    """Safely make an authenticated GitHub API request."""

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20,
        )

        if response.status_code == 200:
            return response.json()

        print(
            f"⚠️ GitHub API error {response.status_code}: "
            f"{response.text[:200]}"
        )

    except requests.exceptions.RequestException as exc:
        print(f"⚠️ Request failed: {exc}")

    return None


# ============================================================
# 5. BUILDER PROFILE ENRICHMENT
# ============================================================

def get_founder_profile(username, headers):
    """
    Retrieve publicly available GitHub profile information
    for a discovered repository owner.
    """

    url = f"https://api.github.com/users/{username}"
    data = github_get(url, headers)

    if not data:
        return {
            "Full Name": username,
            "GitHub Handle": username,
            "GitHub Profile": f"https://github.com/{username}",
            "Company": "",
            "Bio": "",
            "Location": "",
            "Website": "",
            "X Profile": "",
            "Public Repositories": 0,
            "Followers": 0,
        }

    name = data.get("name") or username
    company = data.get("company") or ""
    bio = data.get("bio") or ""
    location = data.get("location") or ""
    website = data.get("blog") or ""
    twitter = data.get("twitter_username") or ""

    x_profile = (
        f"https://x.com/{twitter}"
        if twitter
        else ""
    )

    return {
        "Full Name": name,
        "GitHub Handle": username,
        "GitHub Profile": f"https://github.com/{username}",
        "Company": company,
        "Bio": bio,
        "Location": location,
        "Website": website,
        "X Profile": x_profile,
        "Public Repositories": data.get("public_repos", 0),
        "Followers": data.get("followers", 0),
    }


# ============================================================
# 6. PROFESSIONAL PROFILE SEARCH
# ============================================================

def create_linkedin_search(name, company=""):
    """
    Generate a LinkedIn search URL for manual profile research.

    This does not scrape LinkedIn.
    """

    search_query = f"{name} {company}".strip()
    encoded_query = urllib.parse.quote(search_query)

    return (
        "https://www.linkedin.com/search/results/all/"
        f"?keywords={encoded_query}"
    )


# ============================================================
# 7. BUILDER / STARTUP SIGNAL SCORING
# ============================================================

def calculate_builder_signal(row):
    """
    Assign a heuristic discovery score to a repository/profile.

    The score is intended only to prioritize manual research.
    It is not an investment-quality score.
    """

    score = 0
    reasons = []

    description = str(row.get("Description", "")).lower()
    bio = str(row.get("Bio", "")).lower()
    company = str(row.get("Company", "")).lower()
    topics = str(row.get("Topics", "")).lower()

    combined_text = (
        f"{description} {bio} {company} {topics}"
    )

    # --------------------------------------------------------
    # Founder / builder signals
    # --------------------------------------------------------

    founder_words = [
        "founder",
        "co-founder",
        "startup",
        "building",
        "builder",
        "founding",
        "founding engineer",
        "ceo",
        "entrepreneur",
        "entrepreneurship",
        "indie hacker",
        "indiehackers",
        "product builder",
        "stealth startup",
    ]

    for word in founder_words:
        if word in combined_text:
            score += 2
            reasons.append(
                f"Contains '{word}' builder signal"
            )
            break

    # --------------------------------------------------------
    # Thesis relevance
    # --------------------------------------------------------

    thesis_words = [
        "regtech",
        "compliance",
        "kyc",
        "kyb",
        "aml",
        "sanctions",
        "identity",
        "fraud",
        "transaction-monitoring",
        "financial-crime",
        "vasp",
        "crypto-compliance",
        "travel-rule",
    ]

    for word in thesis_words:
        if word in combined_text:
            score += 2
            reasons.append(
                f"Relevant thesis signal: '{word}'"
            )
            break

    # --------------------------------------------------------
    # Product / company-building language
    # --------------------------------------------------------

    product_words = [
        "product",
        "platform",
        "saas",
        "api",
        "application",
        "software",
        "protocol",
    ]

    for word in product_words:
        if word in description:
            score += 1
            reasons.append(
                f"Project appears to be a {word}"
            )
            break

    # --------------------------------------------------------
    # GitHub traction
    # --------------------------------------------------------

    try:
        stars = int(row.get("Stars", 0))
    except (TypeError, ValueError):
        stars = 0

    if stars >= 100:
        score += 3
        reasons.append("100+ GitHub stars")

    elif stars >= 25:
        score += 2
        reasons.append("25+ GitHub stars")

    elif stars >= 10:
        score += 1
        reasons.append("10+ GitHub stars")

    # --------------------------------------------------------
    # Recent technical activity
    # --------------------------------------------------------

    last_updated = str(
        row.get("Last Updated", "")
    )

    if last_updated:

        try:
            updated_date = datetime.strptime(
                last_updated,
                "%Y-%m-%d",
            )

            days_old = (
                datetime.now() - updated_date
            ).days

            if days_old <= 90:
                score += 2
                reasons.append(
                    "Active within last 90 days"
                )

            elif days_old <= 180:
                score += 1
                reasons.append(
                    "Active within last 6 months"
                )

        except ValueError:
            pass

    # --------------------------------------------------------
    # Priority classification
    # --------------------------------------------------------

    if score >= 5:
        status = "SCOUT"

    elif score >= 3:
        status = "MONITOR"

    else:
        status = "LOW PRIORITY"

    return (
        score,
        status,
        "; ".join(reasons),
    )


# ============================================================
# 8. MAIN DISCOVERY ENGINE
# ============================================================

def scrape_github_founders():

    print("=" * 60)
    print("🚀 GITHUB FOUNDER DISCOVERY ENGINE")
    print("=" * 60)
    print()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    raw_items = []

    # --------------------------------------------------------
    # SEARCH REPOSITORIES
    # --------------------------------------------------------

    for keyword in KEYWORDS:

        print(
            f"🔍 Searching GitHub for "
            f"'{keyword}'..."
        )

        url = (
            "https://api.github.com/"
            "search/repositories"
        )

        params = {
            "q": f"{keyword} pushed:>2025-01-01",
            "sort": "updated",
            "order": "desc",
            "per_page": 20,
        }

        data = github_get(
            url,
            headers,
            params=params,
        )

        if not data:
            continue

        items = data.get("items", [])

        print(
            f"   Found {len(items)} repositories"
        )

        for item in items:

            owner = item.get("owner", {})

            # Focus on individual builders rather than
            # organization-owned repositories.
            if owner.get("type") != "User":
                continue

            raw_items.append(
                {
                    "Repo URL":
                        item.get("html_url", ""),

                    "Repository Name":
                        item.get("name", ""),

                    "Founder Handle":
                        owner.get("login", ""),

                    "Keyword Trigger":
                        keyword,

                    "Description":
                        item.get("description")
                        or "No description provided",

                    "Stars":
                        item.get(
                            "stargazers_count",
                            0,
                        ),

                    "Forks":
                        item.get(
                            "forks_count",
                            0,
                        ),

                    "Language":
                        item.get("language")
                        or "N/A",

                    "Topics":
                        ", ".join(
                            item.get(
                                "topics",
                                [],
                            )
                        ),

                    "Created At":
                        item.get(
                            "created_at",
                            "",
                        )[:10],

                    "Last Updated":
                        item.get(
                            "updated_at",
                            "",
                        )[:10],
                }
            )

    # --------------------------------------------------------
    # CHECK RESULTS
    # --------------------------------------------------------

    if not raw_items:
        print("\n❌ No repositories found.")
        return

    # --------------------------------------------------------
    # DEDUPLICATE REPOSITORIES
    # --------------------------------------------------------

    df_repos = pd.DataFrame(raw_items)

    df_repos = df_repos.drop_duplicates(
        subset=["Repo URL"]
    )

    print()
    print(
        f"📦 Unique repositories found: "
        f"{len(df_repos)}"
    )

    # --------------------------------------------------------
    # IDENTIFY UNIQUE BUILDERS
    # --------------------------------------------------------

    founders = (
        df_repos["Founder Handle"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        f"👤 Unique builders found: "
        f"{len(founders)}"
    )

    print()

    # --------------------------------------------------------
    # ENRICH BUILDER PROFILES
    # --------------------------------------------------------

    profile_cache = {}
    enriched_rows = []

    for number, handle in enumerate(
        founders,
        start=1,
    ):

        print(
            f"👤 [{number}/{len(founders)}] "
            f"Enriching @{handle}..."
        )

        if handle not in profile_cache:

            profile_cache[handle] = (
                get_founder_profile(
                    handle,
                    headers,
                )
            )

        profile = profile_cache[handle]

        founder_repos = df_repos[
            df_repos["Founder Handle"]
            == handle
        ]

        for _, repo in founder_repos.iterrows():

            linkedin = create_linkedin_search(
                profile["Full Name"],
                profile["Company"],
            )

            row = {

                # PERSON
                "Full Name":
                    profile["Full Name"],

                "GitHub Handle":
                    profile["GitHub Handle"],

                "GitHub Profile":
                    profile["GitHub Profile"],

                "Company":
                    profile["Company"],

                "Bio":
                    profile["Bio"],

                "Location":
                    profile["Location"],

                "Website":
                    profile["Website"],

                "X Profile":
                    profile["X Profile"],

                "LinkedIn Search":
                    linkedin,

                "Followers":
                    profile["Followers"],

                "Public Repositories":
                    profile[
                        "Public Repositories"
                    ],

                # PROJECT
                "Repository Name":
                    repo["Repository Name"],

                "Repository URL":
                    repo["Repo URL"],

                "Description":
                    repo["Description"],

                "Keyword Trigger":
                    repo["Keyword Trigger"],

                "Stars":
                    repo["Stars"],

                "Forks":
                    repo["Forks"],

                "Language":
                    repo["Language"],

                "Topics":
                    repo["Topics"],

                "Created At":
                    repo["Created At"],

                "Last Updated":
                    repo["Last Updated"],
            }

            score, status, reasons = (
                calculate_builder_signal(row)
            )

            row["Builder Score"] = score
            row["Scout Status"] = status
            row["Scout Signals"] = reasons

            enriched_rows.append(row)

    # --------------------------------------------------------
    # CREATE FINAL DATASET
    # --------------------------------------------------------

    if not enriched_rows:
        print(
            "\n❌ No builder profiles "
            "were successfully enriched."
        )
        return

    df_final = pd.DataFrame(enriched_rows)

    # Prioritize strongest discovery candidates.
    df_final = df_final.sort_values(
        by=[
            "Builder Score",
            "Stars",
            "Followers",
        ],
        ascending=False,
    )

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    target_dir = get_output_path()

    filename = os.path.join(
        target_dir,
        "github_founder_scouting_"
        f"{datetime.now().strftime('%Y%m%d')}.csv",
    )

    df_final.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    scout_count = (
        df_final["Scout Status"]
        == "SCOUT"
    ).sum()

    monitor_count = (
        df_final["Scout Status"]
        == "MONITOR"
    ).sum()

    print()
    print("=" * 60)
    print("✅ DISCOVERY COMPLETE")
    print("=" * 60)

    print(
        f"Repositories: "
        f"{len(df_repos)}"
    )

    print(
        f"Builders: "
        f"{len(founders)}"
    )

    print(
        f"SCOUT candidates: "
        f"{scout_count}"
    )

    print(
        f"MONITOR candidates: "
        f"{monitor_count}"
    )

    print()
    print("📁 Results saved to:")
    print(filename)
    print()


# ============================================================
# 9. RUN
# ============================================================

if __name__ == "__main__":
    scrape_github_founders()
