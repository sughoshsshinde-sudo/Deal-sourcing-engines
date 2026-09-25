"""
Master Founder Discovery Engine

Combines GitHub and Hugging Face discovery into a unified sourcing
pipeline for identifying technical builders and projects relevant to
predefined early-stage investment themes.

Current thesis areas:
    • RegTech / Compliance
    • Cybersecurity
    • Enterprise SaaS / AI
    • Blockchain / Crypto Infrastructure

The engine performs discovery, profile enrichment, thesis matching,
signal scoring and prioritization.

Discovery scores are designed to prioritize manual research.
They are not investment recommendations.

Author: Sughosh Shinde
"""

import os
import time
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "outputs")

HF_LIMIT = 30
GH_LIMIT = 20

# Useful while testing changes without exporting the full dataset.
TEST_MODE = True
TEST_ROWS_PER_SOURCE = 25

GH_PUSHED_AFTER = "2025-01-01"


# ============================================================
# 2. INVESTMENT THESIS
# ============================================================

THESIS = {

    "RegTech / Compliance": [
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
        "sanction screening",
        "watchlist screening",
        "pep screening",
        "transaction monitoring",
        "fraud detection",
        "fraud prevention",
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
        "legal ai",
        "legaltech",
        "contract ai",
        "contract intelligence",
        "privacy ai",
        "data governance",
        "privacy compliance",
        "legal compliance",
        "identity verification",
        "kyc infrastructure",
        "audit trail",
        "policy engine",
    ],

    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "application security",
        "appsec",
        "cloud security",
        "network security",
        "endpoint security",
        "identity security",
        "access management",
        "iam",
        "zero trust",
        "threat detection",
        "threat intelligence",
        "security automation",
        "security platform",
        "security agent",
        "security ai",
        "ai security",
        "security operations",
        "soc",
        "vulnerability management",
        "penetration testing",
        "devsecops",
        "secrets management",
        "data security",
        "privacy engineering",
        "software supply chain security",
        "api security",
        "container security",
        "cloud posture",
    ],

    "Enterprise SaaS / AI": [
        "enterprise ai",
        "enterprise agent",
        "ai agent",
        "agentic ai",
        "workflow automation",
        "enterprise automation",
        "back office ai",
        "business process automation",
        "enterprise software",
        "enterprise saas",
        "b2b saas",
        "b2b",
        "saas",
        "workflow",
        "business automation",
        "operations automation",
        "developer tools",
        "devtools",
        "productivity platform",
        "knowledge management",
        "data infrastructure",
        "ai infrastructure",
        "llm infrastructure",
        "rag",
        "retrieval augmented generation",
        "ai evaluation",
        "ai observability",
        "model monitoring",
        "document intelligence",
        "document ai",
    ],

    "Blockchain / Crypto Infrastructure": [
        "blockchain",
        "web3 infrastructure",
        "crypto infrastructure",
        "crypto compliance",
        "crypto aml",
        "virtual asset",
        "virtual asset compliance",
        "vasp",
        "vasp compliance",
        "travel rule",
        "on-chain compliance",
        "blockchain analytics",
        "on-chain analytics",
        "wallet security",
        "crypto security",
        "blockchain security",
        "institutional custody",
        "digital assets",
        "digital asset infrastructure",
        "zk-kyc",
        "zero knowledge identity",
        "verifiable credentials",
        "decentralized identity",
    ],
}


TERM_CATEGORY = {
    term: category
    for category, terms in THESIS.items()
    for term in terms
}

KEYWORDS = list(TERM_CATEGORY)


# ============================================================
# 3. CREDENTIALS
# ============================================================

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise SystemExit(
        "GitHub token not found. "
        "Add GITHUB_TOKEN to your local .env file."
    )


GH_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ============================================================
# 4. REQUEST UTILITIES
# ============================================================

def get_json(url, headers=None, params=None):
    """Safely retrieve JSON data from a public API."""

    try:
        response = requests.get(
            url,
            headers=headers or {},
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"   ⚠️ Request failed: {exc}")
        return None


def age_days(date_string):
    """Return the approximate age of a date in days."""

    try:
        date = datetime.strptime(
            str(date_string)[:10],
            "%Y-%m-%d",
        )

        return (datetime.now() - date).days

    except (ValueError, TypeError):
        return None


# ============================================================
# 5. DISCOVERY SCORING
# ============================================================

def score(
    category,
    keyword,
    project,
    desc="",
    bio="",
    topics="",
    stars=0,
    likes=0,
    downloads=0,
    updated="",
    ptype="",
    **kwargs,
):
    """
    Calculate a heuristic discovery score.

    The score prioritizes profiles for further manual research.
    It should not be interpreted as a measure of investment quality.
    """

    text = " ".join(
        map(
            str,
            [
                keyword,
                project,
                desc,
                bio,
                topics,
            ],
        )
    ).lower()

    discovery_score = 15

    signals = [
        f"keyword: {keyword}"
    ]

    # --------------------------------------------------------
    # Thesis overlap
    # --------------------------------------------------------

    thesis_hits = [
        term
        for term in THESIS[category]
        if term.lower() in text
        and term.lower() != keyword.lower()
    ]

    discovery_score += min(
        5 * len(thesis_hits[:4]),
        20,
    )

    signals += [
        f"thesis: {term}"
        for term in thesis_hits[:4]
    ]

    # --------------------------------------------------------
    # Builder / product signals
    # --------------------------------------------------------

    builder_terms = [
        "building",
        "builder",
        "founder",
        "startup",
        "product",
        "platform",
        "api",
        "application",
        "software",
        "saas",
        "agent",
        "automation",
        "infrastructure",
    ]

    builder_hits = [
        term
        for term in builder_terms
        if term in text
    ]

    if builder_hits:
        discovery_score += min(
            2 * len(builder_hits),
            8,
        )

        signals.append(
            "builder/product: "
            + ", ".join(builder_hits[:4])
        )

    # --------------------------------------------------------
    # Technical signals
    # --------------------------------------------------------

    technical_terms = [
        "python",
        "pytorch",
        "tensorflow",
        "transformers",
        "llm",
        "machine learning",
        "deep learning",
        "api",
        "agent",
        "rag",
        "kubernetes",
        "docker",
        "postgres",
        "redis",
    ]

    technical_hits = [
        term
        for term in technical_terms
        if term in text
    ]

    if technical_hits:
        discovery_score += min(
            2 * len(technical_hits),
            8,
        )

        signals.append(
            "technical: "
            + ", ".join(technical_hits[:5])
        )

    # --------------------------------------------------------
    # Recency
    # --------------------------------------------------------

    age = age_days(updated)

    if age is not None:

        if age <= 90:
            discovery_score += 8
            signals.append(
                "updated <=90 days"
            )

        elif age <= 180:
            discovery_score += 4
            signals.append(
                "updated <=6 months"
            )

        elif age <= 365:
            discovery_score += 1
            signals.append(
                "updated <=12 months"
            )

    # --------------------------------------------------------
    # Normalize engagement values
    # --------------------------------------------------------

    try:
        stars = int(stars or 0)
    except (ValueError, TypeError):
        stars = 0

    try:
        likes = int(likes or 0)
    except (ValueError, TypeError):
        likes = 0

    try:
        downloads = int(downloads or 0)
    except (ValueError, TypeError):
        downloads = 0

    # --------------------------------------------------------
    # GitHub traction
    # --------------------------------------------------------

    if stars >= 100:
        discovery_score += 8
        signals.append("100+ stars")

    elif stars >= 25:
        discovery_score += 5
        signals.append("25+ stars")

    elif stars >= 10:
        discovery_score += 2
        signals.append("10+ stars")

    # --------------------------------------------------------
    # Hugging Face engagement
    # --------------------------------------------------------

    if likes >= 100:
        discovery_score += 6
        signals.append("100+ HF likes")

    elif likes >= 25:
        discovery_score += 3
        signals.append("25+ HF likes")

    elif likes >= 10:
        discovery_score += 1
        signals.append("10+ HF likes")

    if downloads >= 100000:
        discovery_score += 6
        signals.append("100k+ downloads")

    elif downloads >= 10000:
        discovery_score += 4
        signals.append("10k+ downloads")

    elif downloads >= 1000:
        discovery_score += 2
        signals.append("1k+ downloads")

    # A working Hugging Face Space can represent a stronger
    # product-building signal than a standalone model.

    if ptype == "HF Space":
        discovery_score += 5
        signals.append("HF Space")

    discovery_score = min(
        discovery_score,
        100,
    )

    if discovery_score >= 55:
        priority = "HIGH"

    elif discovery_score >= 30:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    return (
        discovery_score,
        priority,
        "; ".join(signals),
    )


# ============================================================
# 6. STANDARDIZED DISCOVERY RECORD
# ============================================================

def base_row(
    source,
    category,
    keyword,
    person,
    project,
    ptype,
    profile,
    project_url,
    **kwargs,
):
    """Create a standardized record across discovery sources."""

    discovery_score, priority, signals = score(
        category,
        keyword,
        project,
        ptype=ptype,
        **kwargs,
    )

    return {
        "Source": source,
        "Category": category,
        "Discovery Keyword": keyword,
        "Person / Handle": person,
        "Project": project,
        "Project Type": ptype,

        "Description":
            kwargs.get("desc", "") or "",

        "Bio":
            kwargs.get("bio", "") or "",

        "Company":
            kwargs.get("company", "") or "",

        "Location":
            kwargs.get("location", "") or "",

        "Website":
            kwargs.get("website", "") or "",

        "Profile URL": profile,
        "Project URL": project_url,

        "Language":
            kwargs.get("language", "") or "",

        "Framework / Library":
            kwargs.get("framework", "") or "",

        "Model / Pipeline":
            kwargs.get("model", "") or "",

        "Topics / Tags":
            kwargs.get("topics", "") or "",

        "Stars / Likes":
            kwargs.get(
                "stars",
                kwargs.get("likes", 0),
            ) or 0,

        "Downloads":
            kwargs.get("downloads", "") or "",

        "Forks":
            kwargs.get("forks", "") or "",

        "Created At":
            kwargs.get("created", "") or "",

        "Last Updated":
            kwargs.get("updated", "") or "",

        "Discovery Score":
            discovery_score,

        "Discovery Priority":
            priority,

        "Discovery Signals":
            signals,

        # Reserved for later stages of the research workflow.
        "Technical Analysis":
            "NOT ANALYSED",

        "LinkedIn":
            "",

        "LinkedIn Confidence":
            "",

        "Outreach Status":
            "",
    }


# ============================================================
# 7. HUGGING FACE DISCOVERY
# ============================================================

def hf_discovery():
    """Discover relevant models and Spaces on Hugging Face."""

    rows = {}

    for index, keyword in enumerate(
        KEYWORDS,
        start=1,
    ):

        category = TERM_CATEGORY[keyword]

        print(
            f"[HF {index}/{len(KEYWORDS)}] "
            f"{keyword}"
        )

        # ----------------------------------------------------
        # Models
        # ----------------------------------------------------

        models = get_json(
            "https://huggingface.co/api/models",
            params={
                "search": keyword,
                "limit": HF_LIMIT,
            },
        ) or []

        for model in models:

            item = model.get("id", "")

            if "/" not in item:
                continue

            author, repo = item.split(
                "/",
                1,
            )

            key = (
                author.lower(),
                repo.lower(),
                "model",
            )

            if key in rows:
                continue

            rows[key] = base_row(
                "Hugging Face",
                category,
                keyword,
                author,
                repo,
                "HF Model",
                f"https://huggingface.co/{author}",
                f"https://huggingface.co/{item}",
                likes=model.get("likes", 0),
                downloads=model.get(
                    "downloads",
                    0,
                ),
                updated=model.get(
                    "lastModified",
                    "",
                ),
                topics=", ".join(
                    model.get(
                        "tags",
                        [],
                    ) or []
                ),
                framework=model.get(
                    "library_name",
                    "",
                ) or "",
                model=model.get(
                    "pipeline_tag",
                    "",
                ) or "",
            )

        # ----------------------------------------------------
        # Spaces
        # ----------------------------------------------------

        spaces = get_json(
            "https://huggingface.co/api/spaces",
            params={
                "search": keyword,
                "limit": HF_LIMIT,
            },
        ) or []

        for space in spaces:

            item = space.get("id", "")

            if "/" not in item:
                continue

            author, repo = item.split(
                "/",
                1,
            )

            key = (
                author.lower(),
                repo.lower(),
                "space",
            )

            if key in rows:
                continue

            rows[key] = base_row(
                "Hugging Face",
                category,
                keyword,
                author,
                repo,
                "HF Space",
                f"https://huggingface.co/{author}",
                f"https://huggingface.co/spaces/{item}",
                likes=space.get(
                    "likes",
                    0,
                ),
                updated=space.get(
                    "lastModified",
                    "",
                ),
            )

        time.sleep(0.15)

    return list(rows.values())


# ============================================================
# 8. GITHUB DISCOVERY
# ============================================================

def github_discovery():
    """Discover repositories and enrich their individual owners."""

    rows = {}
    profiles = {}

    for index, keyword in enumerate(
        KEYWORDS,
        start=1,
    ):

        category = TERM_CATEGORY[keyword]

        print(
            f"[GH {index}/{len(KEYWORDS)}] "
            f"{keyword}"
        )

        data = get_json(
            "https://api.github.com/search/repositories",
            headers=GH_HEADERS,
            params={
                "q":
                    f"{keyword} "
                    f"pushed:>{GH_PUSHED_AFTER}",

                "sort":
                    "updated",

                "order":
                    "desc",

                "per_page":
                    GH_LIMIT,
            },
        ) or {}

        for item in data.get(
            "items",
            [],
        ):

            owner = item.get(
                "owner",
                {},
            )

            # Focus the discovery layer on individual
            # technical builders rather than organization
            # accounts.
            if owner.get("type") != "User":
                continue

            handle = owner.get(
                "login",
                "",
            )

            repo = item.get(
                "name",
                "",
            )

            key = (
                handle.lower(),
                repo.lower(),
            )

            if key in rows:
                continue

            rows[key] = base_row(
                "GitHub",
                category,
                keyword,
                handle,
                repo,
                "GitHub Repository",

                owner.get(
                    "html_url",
                    f"https://github.com/{handle}",
                ),

                item.get(
                    "html_url",
                    "",
                ),

                desc=item.get(
                    "description",
                    "",
                ) or "",

                stars=item.get(
                    "stargazers_count",
                    0,
                ),

                forks=item.get(
                    "forks_count",
                    0,
                ),

                language=item.get(
                    "language",
                    "",
                ) or "",

                topics=", ".join(
                    item.get(
                        "topics",
                        [],
                    ) or []
                ),

                created=item.get(
                    "created_at",
                    "",
                )[:10],

                updated=item.get(
                    "updated_at",
                    "",
                )[:10],
            )

    # --------------------------------------------------------
    # GitHub profile enrichment
    # --------------------------------------------------------

    for row in rows.values():

        handle = row[
            "Person / Handle"
        ]

        if handle not in profiles:

            profiles[handle] = (
                get_json(
                    (
                        "https://api.github.com/"
                        f"users/{handle}"
                    ),
                    headers=GH_HEADERS,
                )
                or {}
            )

        profile = profiles[handle]

        row.update(
            {
                "Bio":
                    profile.get(
                        "bio",
                        "",
                    ) or "",

                "Company":
                    profile.get(
                        "company",
                        "",
                    ) or "",

                "Location":
                    profile.get(
                        "location",
                        "",
                    ) or "",

                "Website":
                    profile.get(
                        "blog",
                        "",
                    ) or "",
            }
        )

        # Recalculate after profile enrichment so bio/company
        # information can contribute to discovery signals.

        discovery_score, priority, signals = score(
            row["Category"],
            row["Discovery Keyword"],
            row["Project"],
            row["Description"],
            row["Bio"],
            row["Topics / Tags"],
            row["Stars / Likes"],
            updated=row[
                "Last Updated"
            ],
            ptype=row[
                "Project Type"
            ],
        )

        row.update(
            {
                "Discovery Score":
                    discovery_score,

                "Discovery Priority":
                    priority,

                "Discovery Signals":
                    signals,
            }
        )

    return list(rows.values())


# ============================================================
# 9. MASTER PIPELINE
# ============================================================

def main():

    print("=" * 70)

    print(
        "MASTER FOUNDER DISCOVERY ENGINE "
        "— HUGGING FACE + GITHUB"
    )

    print("=" * 70)

    print(
        "Thesis: RegTech/Compliance + "
        "Cybersecurity + Enterprise SaaS/AI + "
        "Blockchain/Crypto Infrastructure"
    )

    # --------------------------------------------------------
    # Discovery
    # --------------------------------------------------------

    hf_rows = hf_discovery()

    print(
        f"\nHugging Face rows: "
        f"{len(hf_rows)}"
    )

    github_rows = github_discovery()

    print(
        f"GitHub rows: "
        f"{len(github_rows)}"
    )

    # --------------------------------------------------------
    # Optional test export
    # --------------------------------------------------------

    if TEST_MODE:

        hf_rows = hf_rows[
            :TEST_ROWS_PER_SOURCE
        ]

        github_rows = github_rows[
            :TEST_ROWS_PER_SOURCE
        ]

        print(
            "\nTEST MODE: exporting up to "
            f"{TEST_ROWS_PER_SOURCE} rows "
            "from each source."
        )

    # --------------------------------------------------------
    # Unified research queue
    # --------------------------------------------------------

    df = pd.DataFrame(
        hf_rows + github_rows
    )

    if df.empty:

        print(
            "\nNo discovery results found."
        )

        return

    df = df.drop_duplicates(
        subset=[
            "Source",
            "Person / Handle",
            "Project",
            "Project Type",
        ]
    )

    df = df.sort_values(
        [
            "Discovery Score",
            "Stars / Likes",
        ],
        ascending=False,
        na_position="last",
    )

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    os.makedirs(
        OUT_DIR,
        exist_ok=True,
    )

    filename = os.path.join(
        OUT_DIR,
        (
            "master_founder_discovery_"
            f"{datetime.now().strftime('%Y%m%d_%H%M')}"
            ".csv"
        ),
    )

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print("DISCOVERY COMPLETE")

    print("=" * 70)

    print(
        f"Rows exported: "
        f"{len(df)}"
    )

    print(
        "\nSources:\n"
        + df["Source"]
        .value_counts()
        .to_string()
    )

    print(
        "\nCategories:\n"
        + df["Category"]
        .value_counts()
        .to_string()
    )

    print(
        "\nPriorities:\n"
        + df["Discovery Priority"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nSaved: {filename}"
    )

    print(
        "\nNext stage: deeper technical and company "
        "research on prioritized candidates."
    )


# ============================================================
# 10. RUN
# ============================================================

if __name__ == "__main__":
    main()
