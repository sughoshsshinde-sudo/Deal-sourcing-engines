"""
Hugging Face Founder Discovery Engine

Discovers technically active builders and organizations working on
AI products relevant to predefined early-stage investment themes.

Current areas of interest include RegTech, ComplianceTech, Governance,
Risk, Enterprise AI and related infrastructure.

The engine is designed for founder discovery and research prioritization.
Scores are heuristic signals and should not be interpreted as investment
recommendations.

Author: Sughosh Shinde
"""

import os
import time
import urllib.parse
from datetime import datetime

import pandas as pd
import requests


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Broader thesis keywords are intentionally used because builders
# may be working on relevant problems without describing themselves
# explicitly as "RegTech" or "ComplianceTech".

SEARCH_KEYWORDS = [

    # Regulatory / Compliance
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

    # Governance / Risk / Audit
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

    # Legal / Privacy
    "legal ai",
    "legaltech",
    "contract ai",
    "contract intelligence",
    "privacy ai",
    "data governance",
    "privacy compliance",
    "legal compliance",

    # Enterprise AI / Workflow
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


# ============================================================
# 2. OUTPUT CONFIGURATION
# ============================================================

def get_output_path():
    """
    Create and return a portable output directory.

    Generated datasets are stored inside /outputs so they remain
    separate from the source code and can be excluded from Git.
    """

    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "outputs",
    )

    os.makedirs(output_dir, exist_ok=True)

    return output_dir


# ============================================================
# 3. API REQUEST HANDLING
# ============================================================

def safe_get_json(url, timeout=20):
    """
    Make a request to a public endpoint without allowing an
    individual request failure to terminate the entire discovery run.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent":
                    "Founder-Discovery-Engine/2.0"
            },
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:

        print(f"   ⚠️ Request failed: {url}")
        print(f"      Reason: {exc}")

        return []


# ============================================================
# 4. THESIS SCORING
# ============================================================

def calculate_thesis_score(
    keyword,
    project_name,
    project_type="",
    likes=0,
    downloads=0,
    author="",
):
    """
    Calculate a preliminary discovery score.

    The score is designed to prioritize projects for manual
    founder and company research.

    It is not intended to predict investment quality.
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
    # 4.1 DIRECT THESIS SIGNALS
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
    # 4.2 AI / AGENT SIGNALS
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
        term
        for term in ai_terms
        if term in text
    ]

    if ai_matches:

        score += 10

        matched.extend(
            ai_matches[:3]
        )

    # --------------------------------------------------------
    # 4.3 ENTERPRISE SIGNALS
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
    # 4.4 PRODUCT / DEMO SIGNAL
    # --------------------------------------------------------

    if project_type == "Space / Demo":

        # A deployed application or demo can be a stronger
        # company-building signal than a standalone model.

        score += 10

        matched.append(
            "working demo / application"
        )

    # --------------------------------------------------------
    # 4.5 COMMUNITY TRACTION
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
    # 4.6 USAGE / DOWNLOAD SIGNAL
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
    # 4.7 SCORE CAP
    # --------------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------------
    # 4.8 PRIORITY CLASSIFICATION
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
        ", ".join(
            dict.fromkeys(matched)
        ),
    )


# ============================================================
# 5. STANDARDIZE DISCOVERY RECORD
# ============================================================

def build_lead(
    author,
    project_type,
    repo_name,
    keyword,
    likes=None,
    downloads=None,
    last_modified=None,
):
    """
    Convert a discovered Hugging Face project into a standardized
    founder / organization research record.
    """

    score, priority, matched_terms = (
        calculate_thesis_score(
            keyword=keyword,
            project_name=repo_name,
            project_type=project_type,
            likes=likes,
            downloads=downloads,
            author=author,
        )
    )

    # --------------------------------------------------------
    # Preliminary creator classification
    # --------------------------------------------------------
    #
    # Hugging Face handles do not always reveal whether an
    # account represents an individual or an organization.
    #
    # This is therefore only a discovery heuristic and should
    # be manually validated during research.

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

    # --------------------------------------------------------
    # Research links
    # --------------------------------------------------------

    encoded_author = urllib.parse.quote(author)

    encoded_repo = urllib.parse.quote(repo_name)

    linkedin_query = urllib.parse.quote(
        f'"{author}"'
    )

    x_query = urllib.parse.quote(
        f'"{author}"'
    )

    return {

        # CREATOR
        "Founder / Org Handle":
            author,

        "Creator Type":
            creator_type,

        # PROJECT
        "Project Type":
            project_type,

        "Project Name":
            repo_name,

        "Keyword Trigger":
            keyword,

        # DISCOVERY SCORING
        "Thesis Score":
            score,

        "Initial Priority":
            priority,

        "Matched Thesis Signals":
            matched_terms,

        # PLATFORM SIGNALS
        "HF Likes":
            likes if likes is not None else "",

        "HF Downloads":
            downloads if downloads is not None else "",

        "HF Last Modified":
            last_modified if last_modified else "",

        # RESEARCH LINKS
        "Hugging Face Profile":
            f"https://huggingface.co/{encoded_author}",

        "Project URL":
            (
                "https://huggingface.co/"
                f"{encoded_author}/{encoded_repo}"
            ),

        # These URLs generate manual searches.
        # They do not claim that the resulting account belongs
        # to the discovered Hugging Face creator.

        "LinkedIn Quick Search":
            (
                "https://www.linkedin.com/"
                "search/results/all/"
                f"?keywords={linkedin_query}"
            ),

        "X Quick Search":
            (
                "https://x.com/search"
                f"?q={x_query}"
            ),

        # METADATA
        "Source":
            "Hugging Face",

        "First Seen":
            datetime.now().strftime(
                "%Y-%m-%d"
            ),
    }


# ============================================================
# 6. DISCOVERY ENGINE
# ============================================================

def scrape_huggingface():

    print("=" * 60)
    print("🚀 HUGGING FACE FOUNDER DISCOVERY ENGINE")
    print("=" * 60)

    print(
        f"\n🔎 Searching "
        f"{len(SEARCH_KEYWORDS)} "
        "thesis keywords.\n"
    )

    # Key = creator + project + project type.
    #
    # This allows one creator to have multiple relevant
    # projects while preventing duplicate records caused
    # by overlapping keyword searches.

    found_projects = {}

    for number, keyword in enumerate(
        SEARCH_KEYWORDS,
        start=1,
    ):

        print(
            f"[{number}/"
            f"{len(SEARCH_KEYWORDS)}] "
            f"🔍 {keyword}"
        )

        # ----------------------------------------------------
        # MODELS
        # ----------------------------------------------------

        model_url = (
            "https://huggingface.co/api/models"
            f"?search="
            f"{urllib.parse.quote(keyword)}"
            "&limit=30"
        )

        models = safe_get_json(
            model_url
        )

        if isinstance(models, list):

            for model in models:

                item_id = model.get(
                    "id",
                    "",
                )

                if "/" not in item_id:
                    continue

                author, repo = (
                    item_id.split("/", 1)
                )

                key = (
                    f"{author.lower()}::"
                    f"{repo.lower()}::model"
                )

                if key not in found_projects:

                    found_projects[key] = (
                        build_lead(
                            author=author,
                            project_type="Model",
                            repo_name=repo,
                            keyword=keyword,
                            likes=model.get(
                                "likes"
                            ),
                            downloads=model.get(
                                "downloads"
                            ),
                            last_modified=model.get(
                                "lastModified"
                            ),
                        )
                    )

        # ----------------------------------------------------
        # SPACES / DEMOS
        # ----------------------------------------------------

        space_url = (
            "https://huggingface.co/api/spaces"
            f"?search="
            f"{urllib.parse.quote(keyword)}"
            "&limit=30"
        )

        spaces = safe_get_json(
            space_url
        )

        if isinstance(spaces, list):

            for space in spaces:

                item_id = space.get(
                    "id",
                    "",
                )

                if "/" not in item_id:
                    continue

                author, repo = (
                    item_id.split("/", 1)
                )

                key = (
                    f"{author.lower()}::"
                    f"{repo.lower()}::space"
                )

                if key not in found_projects:

                    found_projects[key] = (
                        build_lead(
                            author=author,
                            project_type=(
                                "Space / Demo"
                            ),
                            repo_name=repo,
                            keyword=keyword,
                            likes=space.get(
                                "likes"
                            ),
                            last_modified=space.get(
                                "lastModified"
                            ),
                        )
                    )

        # Small delay to avoid unnecessarily aggressive
        # requests to the public Hugging Face endpoints.

        time.sleep(0.25)

    # ========================================================
    # 7. BUILD DATASET
    # ========================================================

    results = list(
        found_projects.values()
    )

    if not results:

        print(
            "\n❌ No matching results found."
        )

        return

    df = pd.DataFrame(results)

    # Count the number of unique thesis-relevant projects
    # associated with each discovered creator.

    project_counts = (
        df.groupby(
            "Founder / Org Handle"
        )["Project Name"]
        .transform("nunique")
    )

    df["Project Count"] = project_counts

    # Highest-priority discovery records appear first.

    df = df.sort_values(
        by=[
            "Thesis Score",
            "HF Likes",
            "HF Downloads",
        ],
        ascending=[
            False,
            False,
            False,
        ],
        na_position="last",
    )

    # ========================================================
    # 8. EXPORT
    # ========================================================

    target_dir = get_output_path()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M"
    )

    master_filename = os.path.join(
        target_dir,
        f"hf_founder_discovery_{timestamp}.csv",
    )

    df.to_csv(
        master_filename,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # HIGH-PRIORITY SCOUT QUEUE
    # --------------------------------------------------------

    scout_df = df[
        df["Initial Priority"] == "HIGH"
    ].copy()

    scout_filename = os.path.join(
        target_dir,
        f"hf_scout_queue_{timestamp}.csv",
    )

    scout_df.to_csv(
        scout_filename,
        index=False,
        encoding="utf-8-sig",
    )

    # ========================================================
    # 9. SUMMARY
    # ========================================================

    unique_creators = (
        df["Founder / Org Handle"]
        .nunique()
    )

    print()
    print("=" * 60)
    print("✅ DISCOVERY COMPLETE")
    print("=" * 60)

    print(
        f"Projects found: "
        f"{len(df)}"
    )

    print(
        f"Unique creators: "
        f"{unique_creators}"
    )

    print(
        f"High-priority records: "
        f"{len(scout_df)}"
    )

    print(
        "\n📁 Master discovery file:"
    )

    print(master_filename)

    print(
        "\n🔥 High-priority scout queue:"
    )

    print(scout_filename)

    print("=" * 60)


# ============================================================
# 10. RUN
# ============================================================

if __name__ == "__main__":
    scrape_huggingface()
