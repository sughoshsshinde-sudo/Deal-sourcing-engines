# Founder Discovery & Deal-Sourcing Engine

An experimental sourcing system for discovering early-stage technical founders and emerging startups through public digital ecosystems.

The project explores whether signals from platforms such as GitHub and Hugging Face can help surface builders **before they enter conventional venture sourcing pipelines**.

## 🎯 The Problem

Traditional venture sourcing often becomes easier once a startup already has visible signals — accelerator participation, fundraising announcements, media coverage, investor networks, or database presence.

But technical founders frequently leave signals much earlier.

They build repositories, publish models, contribute to open-source projects, participate in technical communities, and experiment publicly before formally launching or raising capital.

The question behind this project is:

> **Can public builder activity be systematically used as an additional discovery layer for identifying promising founders earlier?**

This engine is my attempt to explore that question.

## ⚙️ What I'm Building

The engine combines multiple sourcing channels into a structured discovery workflow:

**Public ecosystem → Builder discovery → Signal extraction → Thesis matching → Scoring → Shortlist → Manual investment research**

The current version uses separate discovery engines for:

- **GitHub** — repositories, contributors and technical projects
- **Hugging Face** — models, datasets and AI builders
- **Company discovery** — emerging companies matching predefined investment themes
- **Profile enrichment** — connecting fragmented public signals for further research

The objective is not to automate investment decisions.

It is to expand the top of the sourcing funnel, reduce repetitive discovery work, and allow more time to be spent on understanding the founders and companies that surface.

## 🔄 How It Works

The system follows a funnel-based approach to founder discovery:

### 1. Discovery

Search public ecosystems using keywords and themes related to the investment thesis.

Current themes include:

- RegTech & ComplianceTech
- GRC & Continuous Control Monitoring
- FinTech & Financial Infrastructure
- Enterprise SaaS
- AI-native enterprise workflows
- Cybersecurity
- Legacy modernization

### 2. Signal Extraction

For each discovered project or profile, the engine captures relevant public signals such as:

- Repository or model information
- Project descriptions
- Topics and keywords
- Creator / contributor information
- Activity indicators
- Available profile and company information

### 3. Thesis Matching

The collected information is compared against predefined thesis signals to identify builders and projects relevant to areas I'm actively researching.

Rather than treating every keyword match equally, the system attempts to distinguish between broad matches and stronger indicators of thesis relevance.

### 4. Scoring & Prioritization

Profiles are assigned discovery scores based on the strength and combination of relevant signals.

The score is used for **prioritization, not investment evaluation**.

Its purpose is to answer:

> "Which profiles should I research first?"

rather than:

> "Which company should I invest in?"

### 5. Enrichment & Manual Research

High-priority results can then be enriched using additional publicly available information.

From this point, the process becomes primarily manual:

**Founder → Company → Problem → Market → Product → Differentiation → Traction → Risks → Investment hypothesis**

This separates automated discovery from human investment judgment.

## 🏗️ System Architecture

The current engine uses multiple discovery modules that can operate independently and feed into a broader founder-sourcing workflow.

                         ┌─────────────────────┐
                         │  Investment Thesis  │
                         │   & Search Signals  │
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   │                │                │
                   ▼                ▼                ▼
              GitHub           Hugging Face      Company
             Discovery          Discovery         Discovery
                   │                │                │
                   └────────────────┼────────────────┘
                                    ▼
                          Candidate Profiles
                                    │
                                    ▼
                         Signal Enrichment
                                    │
                                    ▼
                         Thesis-Based Scoring
                                    │
                                    ▼
                          Founder Shortlist
                                    │
                                    ▼
                      Manual Investment Research


## 🧭 Investment Thesis

The discovery engine is thesis-driven. Instead of searching broadly for "startups", I define areas where I believe structural or technological shifts could create new company-building opportunities and then look for early builder signals within them.

My current areas of exploration include:

### AI-Native RegTech & Compliance

Regulatory and compliance workflows remain fragmented, manual and heavily dependent on periodic reviews.

I'm interested in companies moving these workflows toward continuous, exception-based monitoring — particularly where AI can help interpret regulatory change, identify control gaps and integrate compliance directly into operational workflows.

### GRC & Continuous Control Monitoring

I'm exploring infrastructure that moves governance, risk and control functions from periodic testing toward continuous monitoring of transactions, systems and business processes.

I am particularly interested in products that become embedded within enterprise workflows rather than functioning as standalone AI interfaces.

### FinTech & Financial Inclusion

I'm interested in infrastructure and products that expand access to financial services, particularly where alternative data and AI can improve underwriting, insurance, credit assessment or financial-product distribution for underserved users.

### Enterprise AI & Legacy Modernization

Many large enterprises continue to operate critical systems built on legacy technology.

I'm exploring AI-native tools that can help enterprises understand, maintain, modernize and eventually migrate these systems while reducing implementation risk.

## 📊 Scoring Philosophy

The scoring system is designed to prioritize discovery results, not predict startup success.

A profile can receive a higher priority when multiple relevant signals appear together, such as:

**Thesis relevance + technical activity + project relevance + builder signals + recency**

This helps reduce a large universe of public profiles into a smaller research queue.

The scoring methodology will continue to evolve as I learn which signals produce useful sourcing outcomes.

Importantly:

> **A high discovery score is a reason to investigate — not an investment recommendation.**

Investment evaluation still requires qualitative research into the founder, problem, market, product, differentiation, traction and potential risks.

## 📋 Example Output

The engine converts fragmented public signals into a structured research queue.

A simplified example:

| Candidate | Source | Observed Signal | Thesis Match | Priority |
|---|---|---|---|---|
| Founder A | GitHub | Building AML / transaction-monitoring infrastructure | RegTech | High |
| Founder B | Hugging Face | Publishing models related to document intelligence | Enterprise AI | Medium |
| Founder C | GitHub | Building tooling around legacy code modernization | Legacy Modernization | High |
| Founder D | Hugging Face | Experimenting with governance / evaluation tooling | AI Governance | Medium |

*Example data is illustrative and does not represent an investment recommendation.*

The intended workflow is:

**Large public universe → Automated discovery → Prioritized shortlist → Manual research → Founder / company evaluation**

The value of the system is therefore not eliminating research, but reducing the amount of low-value manual discovery required before deeper research begins.

## ⚠️ Current Limitations

This is an experimental project and the current system has several limitations.

### Noise

Keyword-based discovery can surface repositories, models and profiles that technically match a search term but have little relevance to startup formation.

### Founder Identification

A strong technical project does not necessarily mean its creator intends to build a company. Founder intent often requires additional research and direct interaction.

### Public Data Bias

The engine can only discover signals that builders choose to make public. Strong founders with limited public technical activity may therefore be missed entirely.

### Scoring

Current scores are heuristic prioritization mechanisms rather than statistically validated predictors of founder or startup quality.

### Data Fragmentation

Founder signals are distributed across developer platforms, company websites, professional networks, accelerators, universities and other communities. Connecting these signals reliably remains difficult.

### Human Judgment

The engine can help answer **where should I look?**

It cannot independently answer **should I invest?**

That requires understanding the founder, market, product, competitive environment, business model, traction and risks.

## 🗺️ Roadmap

The current version focuses primarily on public developer ecosystems. The next stage is to expand discovery beyond code and model platforms while improving the quality of the signals already collected.

### Near Term

- [x] GitHub-based founder discovery
- [x] Hugging Face-based founder discovery
- [x] Thesis-based keyword matching
- [x] Basic prioritization and scoring
- [ ] Improve signal weighting and reduce false positives
- [ ] Standardize outputs across discovery engines
- [ ] Improve founder and company enrichment
- [ ] Create a unified research pipeline across sources

### Expanding the Sourcing Universe

Future discovery channels I'm exploring include:

- Accelerator, fellowship and residency alumni
- University founder and technical communities
- Hacker houses and builder communities
- Startup events and technical conferences
- Professional networks
- Open-source ecosystems
- Portfolio and ecosystem mapping

The longer-term objective is to combine these channels into a sourcing system where different signals reinforce each other.

For example:

**Technical activity + accelerator participation + company formation + thesis relevance**

could represent a stronger research signal than any one data point independently.

### Closing the Feedback Loop

The most important next step is not simply adding more data sources.

It is measuring whether the system actually improves sourcing.

Over time, I want to track:

**Profiles surfaced → Profiles researched → Relevant founders → Companies identified → Founder conversations → Investment-worthy opportunities**

This feedback can then be used to refine which signals deserve greater weight and which discovery channels actually produce useful opportunities.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sughoshsshinde-sudo/Deal-sourcing-engines.git
cd Deal-sourcing-engines
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure GitHub access

Create a local `.env` file in the project directory:

```text
GITHUB_TOKEN=your_github_token_here
```

The `.env` file is excluded from version control through `.gitignore`.

### 4. Run a discovery engine

For the combined discovery pipeline:

```bash
python master_founder_scraper.py
```

Or run an individual discovery engine:

```bash
python github_scraper.py
python hf_scraper.py
```

Generated results are stored locally in the `outputs/` directory and are not committed to the repository.

## 🧪 Current Status

The **Master Founder Discovery Engine** is the current combined version of the project, bringing GitHub and Hugging Face discovery into a standardized research pipeline.

`github_scraper.py` and `hf_scraper.py` can also be run independently for source-specific discovery.

The project remains experimental and is being iterated as I learn which public signals are genuinely useful for identifying interesting early-stage builders.


---

## About This Project

This is a personal research and experimentation project built to explore alternative approaches to early-stage venture sourcing.

The system uses publicly available information for discovery and research purposes. It is not intended to provide investment advice or automatically make investment decisions.

The project is continuously evolving as I test new sourcing channels, refine my investment theses and learn from the quality of the founders and companies surfaced.
