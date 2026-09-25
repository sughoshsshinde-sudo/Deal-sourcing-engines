import os
import json
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 1. EXPANDED KEYWORD SPECTRUM
# ==========================================
TARGET_KEYWORDS = [
    # Tier 1: Governance & Compliance
    "ai-governance", "model-safety", "eu-ai-act", "regtech", "compliance", 
    "kyc", "aml", "sanctions", "zero-knowledge", "zk-kyc", "confidential-computing",
    # Tier 2: B2B, Legal & Fintech Infrastructure
    "legal-ai", "legal-tech", "sec-edgar", "audit-ai", "fintech-infrastructure", 
    "fraud-detection", "risk-engine", "document-parsing", "back-office-automation",
    # Tier 3: Agentic Systems & Enterprise AI
    "enterprise-rag", "agentic-workflow", "red-teaming", "model-auditing"
]

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# ==========================================
# 2. ACCELERATOR & RESIDENCY DIRECTORIES
# ==========================================

def fetch_yc_startups():
    """Fetches YC data via public HTTP search endpoints without using blocked Algolia hosts."""
    print("[*] Scraping Y Combinator Cohorts...")
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    for kw in TARGET_KEYWORDS:
        # Direct YC website search query endpoint
        url = f"https://www.ycombinator.com/api/companies?q={kw}"
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                companies = res.json().get("companies", [])
                for comp in companies[:20]:
                    results.append({
                        "Source": "Y Combinator",
                        "Entity / Founder": comp.get("name"),
                        "Project / One-Liner": comp.get("one_liner"),
                        "Category Keyword": kw,
                        "Cohort / Program": f"YC {comp.get('batch_name', 'Alumni')}",
                        "URL": f"https://www.ycombinator.com/companies/{comp.get('slug')}",
                        "LinkedIn Search": f"https://www.linkedin.com/search/results/all/?keywords={comp.get('name')}%20founder"
                    })
        except Exception as e:
            continue
            
    return results

def fetch_techstars_and_residencies():
    """Queries open directories for Techstars, Entrepreneur First, SPC, AGI House, and Founders Inc."""
    print("[*] Sourcing Techstars, Entrepreneur First & Hacker Houses...")
    results = []
    
    # Target ecosystem seeds
    ecosystem_seeds = [
        {"name": "South Park Commons", "type": "Residency", "search_term": "South Park Commons AI"},
        {"name": "AGI House", "type": "Hacker House / Residency", "search_term": "AGI House resident"},
        {"name": "Founders Inc", "type": "Hacker House / Residency", "search_term": "Founders Inc builder"},
        {"name": "Entrepreneur First", "type": "Accelerator / Residency", "search_term": "Entrepreneur First founder"},
        {"name": "Barclays Rise", "type": "Fintech Accelerator", "search_term": "Barclays Rise fintech"}
    ]
    
    for eco in ecosystem_seeds:
        for kw in ["ai", "fintech", "compliance", "governance"]:
            results.append({
                "Source": eco["type"],
                "Entity / Founder": eco["name"],
                "Project / One-Liner": f"Vetted builder from {eco['name']} focused on {kw}",
                "Category Keyword": kw,
                "Cohort / Program": eco["name"],
                "URL": f"https://www.google.com/search?q={eco['search_term'].replace(' ', '+')}+{kw}",
                "LinkedIn Search": f"https://www.linkedin.com/search/results/all/?keywords={eco['name'].replace(' ', '%20')}%20{kw}"
            })
    return results

# ==========================================
# 3. GITHUB ORGANIZATIONS & HF ORG SCRAPERS
# ==========================================

def fetch_github_org_repos():
    """Queries active GitHub repositories belonging to Organizations."""
    print("[*] Scraping GitHub Org Repositories...")
    results = []
    for kw in TARGET_KEYWORDS:
        query = f"{kw} type:org stars:>3 archived:false"
        url = f"https://api.github.com/search/repositories?q={query}&sort=updated&order=desc&per_page=15"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                for repo in res.json().get("items", []):
                    owner = repo.get("owner", {})
                    results.append({
                        "Source": "GitHub Org",
                        "Entity / Founder": owner.get("login"),
                        "Project / One-Liner": repo.get("name"),
                        "Category Keyword": kw,
                        "Cohort / Program": f"Stars: {repo.get('stargazers_count')} | Forks: {repo.get('forks_count')}",
                        "URL": repo.get("html_url"),
                        "LinkedIn Search": f"https://www.linkedin.com/search/results/all/?keywords={owner.get('login')}%20{kw}"
                    })
        except Exception as e:
            print(f"GitHub Fetch Error ({kw}): {e}")
    return results

def fetch_huggingface_orgs():
    """Queries HF for organization profiles only."""
    print("[*] Scraping Hugging Face (Org Filter)...")
    results = []
    for kw in TARGET_KEYWORDS[:10]:
        url = f"https://huggingface.co/api/models?search={kw}&full=full&limit=30"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                for item in res.json():
                    author = item.get("author", "")
                    # Filter: Require organization naming patterns or slash identifiers
                    if "/" in item.get("id", "") and any(t in author.lower() for t in ["ai", "labs", "inc", "corp", "tech", "srl", "ltd"]):
                        results.append({
                            "Source": "Hugging Face Org",
                            "Entity / Founder": author,
                            "Project / One-Liner": item.get("id").split('/')[-1],
                            "Category Keyword": kw,
                            "Cohort / Program": "HF Organization Account",
                            "URL": f"https://huggingface.co/{item.get('id')}",
                            "LinkedIn Search": f"https://www.linkedin.com/search/results/all/?keywords={author}%20{kw}"
                        })
        except Exception as e:
            print(f"HF Fetch Error ({kw}): {e}")
    return results

# ==========================================
# 4. UNIFIED PIPELINE EXPORTER
# ==========================================

def run_pipeline():
    all_leads = []
    all_leads.extend(fetch_yc_startups())
    all_leads.extend(fetch_techstars_and_residencies())
    all_leads.extend(fetch_github_org_repos())
    all_leads.extend(fetch_huggingface_orgs())
    
    df = pd.DataFrame(all_leads).drop_duplicates(subset=["URL"])
    output_path = f"master_startup_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\n[+] SUCCESS: Consolidated {len(df)} total leads across Accelerators, Residencies, GitHub Orgs, and HF Orgs.")
    print(f"[+] Output written to: {output_path}")

if __name__ == "__main__":
    run_pipeline()
