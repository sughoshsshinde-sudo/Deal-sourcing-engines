import requests
import pandas as pd
from datetime import datetime
import os
import urllib.parse
import time

# ============================================================
# HUGGING FACE FOUNDER DISCOVERY SCRAPER - VERSION 2
# Purpose:
# Find technically active people / organisations building
# AI products relevant to RegTech, ComplianceTech,
# GovernanceTech and B2B / Enterprise SaaS.
#
# No paid API is required.
# ============================================================

# Broader thesis keywords.
# We deliberately use related terms because a founder may not
# describe their project as "RegTech".
SEARCH_KEYWORDS = [
    # Regulatory / compliance
    "regtech",
    "regulatory technology",
    "regulatory compliance",
    "compliance",
    "compliance ai",
    "compliance agent",
    "compliance automation",
    "regulatory reporting",
    "regulatory intelligence",
    "financial crime",
    "aml",
    "anti-money laundering",
    "kyc",
    "kyb",
    "sanctions",
    "transaction monitoring",
    "fraud detection",

    # Governance / risk / audit
    "governance",
    "ai governance",
    "model governance",
    "model risk",
    "risk management",
    "enterprise risk",
    "grc",
    "internal audit",
    "audit ai",
    "internal controls",
    "third party risk",

    # Legal / privacy
    "legal ai",
    "legaltech",
    "contract ai",
    "contract intelligence",
    "privacy ai",
    "data governance",
    "privacy compliance",
    "legal compliance",

    # Enterprise AI / workflow
    "enterprise ai",
    "enterprise agent",
    "ai agent",
    "agentic ai",
    "workflow automation",
    "enterprise automation",
    "back office ai",
    "business process automation",

    # Infrastructure
    "compliance infrastructure",
    "identity verification",
    "kyc infrastructure",
    "audit trail",
    "ai security",
    "ai observability",
    "ai safety",
    "ai evaluation",
    "policy engine",
]


def get_output_path():
    """Return the fixed RegTech scraper folder."""
    output_dir = r"C:\Users\Sughosh\Downloads\RegTech"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def safe_get_json(url, timeout=20):
    """Make a web request without crashing the whole scraper."""
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Founder-Discovery-Scraper/2.0"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ⚠️ Request failed: {url}")
        print(f"      Reason: {e}")
        return []


def calculate_thesis_score(
    keyword,
    project_name,
    project_type="",
    likes=0,
    downloads=0,
    author=""
):
    """
    Preliminary founder-scouting score.

    This score is NOT an investment recommendation.
    It helps prioritize people/projects for manual research.
    """

    text = (
        f"{keyword} "
        f"{project_name} "
        f"{project_type} "
        f"{author}"
    ).lower()

    score = 0
    matched = []

    # --------------------------------------------------------
    # 1. DIRECT THESIS SIGNALS
    # --------------------------------------------------------

    strong_terms = {
        "regtech": 20,
        "regulatory compliance": 25,
        "compliance": 20,
        "compliance ai": 30,
        "compliance agent": 30,
        "aml": 30,
        "anti-money laundering": 30,
        "kyc": 30,
        "kyb": 25,
        "sanctions": 25,
        "financial crime": 30,
        "transaction monitoring": 30,
        "regulatory reporting": 30,
        "regulatory intelligence": 30,
        "ai governance": 25,
        "model governance": 25,
        "model risk": 25,
        "grc": 25,
        "internal audit": 20,
        "audit ai": 25,
        "legal ai": 20,
        "legaltech": 20,
        "privacy compliance": 25,
        "identity verification": 25,
        "policy engine": 20,
    }

    for term, points in strong_terms.items():

        if term in text:

            score += points

            matched.append(term)

    # --------------------------------------------------------
    # 2. AI / AGENT SIGNAL
    # --------------------------------------------------------

    ai_terms = [
        "ai",
        "agent",
        "agentic",
        "llm",
        "machine learning",
        "generative ai",
        "automation",
    ]

    ai_matches = [
        term for term in ai_terms
        if term in text
    ]

    if ai_matches:

        score += 10

        matched.extend(
            ai_matches[:3]
        )

    # --------------------------------------------------------
    # 3. ENTERPRISE SIGNAL
    # --------------------------------------------------------

    enterprise_terms = [
        "enterprise",
        "b2b",
        "workflow",
        "infrastructure",
        "business process",
        "back office",
        "platform",
        "saas",
    ]

    enterprise_matches = [
        term
        for term in enterprise_terms
        if term in text
    ]

    if enterprise_matches:

        score += 10

        matched.extend(
            enterprise_matches[:3]
        )

    # --------------------------------------------------------
    # 4. PROJECT TYPE
    # --------------------------------------------------------

    if project_type == "Space / Demo":

        # A working demo/application is a stronger
        # startup-building signal than a standalone model.

        score += 10

        matched.append(
            "working demo / application"
        )

    # --------------------------------------------------------
    # 5. GITHUB-LIKE TRACTION SIGNALS
    # --------------------------------------------------------

    try:
        likes = int(likes or 0)
    except (ValueError, TypeError):
        likes = 0

    try:
        downloads = int(downloads or 0)
    except (ValueError, TypeError):
        downloads = 0

    if likes >= 100:

        score += 10
        matched.append("100+ HF likes")

    elif likes >= 25:

        score += 5
        matched.append("25+ HF likes")

    elif likes >= 10:

        score += 3
        matched.append("10+ HF likes")

    # --------------------------------------------------------
    # 6. USAGE / DOWNLOAD SIGNAL
    # --------------------------------------------------------

    if downloads >= 100000:

        score += 10
        matched.append("100k+ downloads")

    elif downloads >= 10000:

        score += 7
        matched.append("10k+ downloads")

    elif downloads >= 1000:

        score += 5
        matched.append("1k+ downloads")

    # --------------------------------------------------------
    # 7. SCORE CAP
    # --------------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------------
    # 8. PRIORITY
    # --------------------------------------------------------

    if score >= 60:

        priority = "HIGH"

    elif score >= 30:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    return (
        score,
        priority,
        ", ".join(dict.fromkeys(matched))
    )

def build_lead(
    author,
    project_type,
    repo_name,
    keyword,
    likes=None,
    downloads=None,
    last_modified=None,
):
    """Create one standard founder-discovery record."""

    score, priority, matched_terms = calculate_thesis_score(
    keyword=keyword,
    project_name=repo_name,
    project_type=project_type,
    likes=likes,
    downloads=downloads,
    author=author,
)

    # Basic creator classification.
    # This is a preliminary signal based on the Hugging Face handle.
    organization_terms = [
        "official",
        "labs",
        "research",
        "ai",
        "inc",
        "corp",
        "company",
        "foundation",
        "team",
        "studio",
        "technologies",
        "technology",
    ]

    author_lower = author.lower()

    if any(
        term in author_lower
        for term in organization_terms
    ):
        creator_type = "Potential Organization"
    else:
        creator_type = "Potential Individual"

    encoded_author = urllib.parse.quote(author)
    linkedin_query = urllib.parse.quote(f'"{author}"')
    x_query = urllib.parse.quote(f'"{author}"')

    return {
        "Founder / Org Handle": author,
        "Creator Type": creator_type,
        "Project Type": project_type,
        "Project Name": repo_name,
        "Keyword Trigger": keyword,

        "Thesis Score": score,
        "Initial Priority": priority,
        "Matched Thesis Signals": matched_terms,

        "HF Likes": likes if likes is not None else "",
        "HF Downloads": downloads if downloads is not None else "",
        "HF Last Modified": last_modified if last_modified else "",

        "Hugging Face Profile": f"https://huggingface.co/{encoded_author}",
        "Project URL": f"https://huggingface.co/{encoded_author}/{urllib.parse.quote(repo_name)}",

        # These are search links, NOT claims that the person owns
        # these accounts.
        "LinkedIn Quick Search": (
            f"https://www.linkedin.com/search/results/all/?keywords={linkedin_query}"
        ),
        "X Quick Search": (
            f"https://x.com/search?q={x_query}"
        ),

        "Source": "Hugging Face",
        "First Seen": datetime.now().strftime("%Y-%m-%d"),
    }


def scrape_huggingface():
    print("🚀 Starting Hugging Face Founder Discovery Scraper v2...\n")
    print(f"🔎 Searching {len(SEARCH_KEYWORDS)} thesis keywords.\n")

    # Key = author + project so we don't accidentally lose
    # multiple relevant projects from the same builder.
    found_projects = {}

    for number, keyword in enumerate(SEARCH_KEYWORDS, start=1):
        print(f"[{number}/{len(SEARCH_KEYWORDS)}] 🔍 {keyword}")

        # ----------------------------------------------------
        # MODELS
        # ----------------------------------------------------
        model_url = (
            "https://huggingface.co/api/models"
            f"?search={urllib.parse.quote(keyword)}&limit=30"
        )

        models = safe_get_json(model_url)

        if isinstance(models, list):
            for model in models:
                item_id = model.get("id", "")

                if "/" not in item_id:
                    continue

                author, repo = item_id.split("/", 1)

                key = f"{author.lower()}::{repo.lower()}::model"

                if key not in found_projects:
                    found_projects[key] = build_lead(
                        author=author,
                        project_type="Model",
                        repo_name=repo,
                        keyword=keyword,
                        likes=model.get("likes"),
                        downloads=model.get("downloads"),
                        last_modified=model.get("lastModified"),
                    )

        # ----------------------------------------------------
        # SPACES
        # ----------------------------------------------------
        space_url = (
            "https://huggingface.co/api/spaces"
            f"?search={urllib.parse.quote(keyword)}&limit=30"
        )

        spaces = safe_get_json(space_url)

        if isinstance(spaces, list):
            for space in spaces:
                item_id = space.get("id", "")

                if "/" not in item_id:
                    continue

                author, repo = item_id.split("/", 1)

                key = f"{author.lower()}::{repo.lower()}::space"

                if key not in found_projects:
                    found_projects[key] = build_lead(
                        author=author,
                        project_type="Space / Demo",
                        repo_name=repo,
                        keyword=keyword,
                        likes=space.get("likes"),
                        last_modified=space.get("lastModified"),
                    )

        # Small pause to be polite to the public API.
        time.sleep(0.25)

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------
    results = list(found_projects.values())

    if not results:
        print("\n❌ No matching results found.")
        return

    df = pd.DataFrame(results)

    # Count how many relevant HF projects each creator has.
    project_counts = df.groupby("Founder / Org Handle")["Project Name"].transform("nunique")
    df["Project Count"] = project_counts

    # Highest-value records first.
    df = df.sort_values(
        by=["Thesis Score", "HF Likes", "HF Downloads"],
        ascending=[False, False, False],
        na_position="last",
    )

    target_dir = get_output_path()

    filename = os.path.join(
        target_dir,
        f"hf_founder_discovery_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    )

    df.to_csv(filename, index=False, encoding="utf-8-sig")

    # Also create a smaller "Scout Queue" containing HIGH priority.
    scout_df = df[df["Initial Priority"] == "HIGH"].copy()

    scout_filename = os.path.join(
        target_dir,
        f"hf_scout_queue_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    )

    scout_df.to_csv(
        scout_filename,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("✅ SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Projects found: {len(df)}")
    print(f"High-priority records: {len(scout_df)}")
    print(f"\n📁 Master file:")
    print(filename)
    print(f"\n🔥 Scout Queue:")
    print(scout_filename)
    print("=" * 60)


if __name__ == "__main__":
    scrape_huggingface()
