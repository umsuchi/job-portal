"""Seed content, kept apart from the loading logic so it stays readable.

Skill strings use the same spellings as the frontend catalogue
(`frontend/src/lib/skills.ts`). That matters: the suggestion engine matches with
Postgres array overlap, so "PostgreSQL" here and "postgres" there would not meet.
"""
from __future__ import annotations

from typing import Dict, List

# Every seeded account shares this password — it is only ever used locally.
SEED_PASSWORD = "password123"

RECRUITERS: List[Dict] = [
    {"email": "hiring@northwindlabs.example.com", "company_name": "Northwind Labs",
     "company_website": "https://northwindlabs.example.com"},
    {"email": "talent@brightpath.example.com", "company_name": "BrightPath Software",
     "company_website": "https://brightpath.example.com"},
    {"email": "jobs@meridiantech.example.com", "company_name": "Meridian Tech",
     "company_website": "https://meridiantech.example.com"},
    {"email": "careers@lantern.example.com", "company_name": "Lantern Digital",
     "company_website": "https://lantern.example.com"},
    {"email": "people@vellumhq.example.com", "company_name": "Vellum HQ",
     "company_website": "https://vellumhq.example.com"},
    {"email": "hiring@cobaltworks.example.com", "company_name": "Cobalt Works",
     "company_website": "https://cobaltworks.example.com"},
    {"email": "talent@driftwoodapps.example.com", "company_name": "Driftwood Apps",
     "company_website": "https://driftwoodapps.example.com"},
    {"email": "jobs@stonebridgedata.example.com", "company_name": "Stonebridge Data",
     "company_website": "https://stonebridgedata.example.com"},
    {"email": "careers@harborlineai.example.com", "company_name": "Harborline AI",
     "company_website": "https://harborlineai.example.com"},
    {"email": "hiring@keelstudio.example.com", "company_name": "Keel Studio",
     "company_website": "https://keelstudio.example.com"},
    {"email": "people@aurorafintech.example.com", "company_name": "Aurora Fintech",
     "company_website": "https://aurorafintech.example.com"},
    {"email": "talent@pineconecommerce.example.com", "company_name": "Pinecone Commerce",
     "company_website": "https://pineconecommerce.example.com"},
    {"email": "jobs@sablecloud.example.com", "company_name": "Sable Cloud",
     "company_website": "https://sablecloud.example.com"},
    {"email": "careers@tidalhealth.example.com", "company_name": "Tidal Health",
     "company_website": "https://tidalhealth.example.com"},
    {"email": "hiring@quillandcode.example.com", "company_name": "Quill & Code",
     "company_website": "https://quillandcode.example.com"},
]

CANDIDATES: List[Dict] = [
    {"email": "arif.rahman@example.com", "full_name": "Arif Rahman",
     "headline": "Frontend engineer, 6 years in React and TypeScript",
     "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS", "TanStack Query", "Vite"]},
    {"email": "nusrat.jahan@example.com", "full_name": "Nusrat Jahan",
     "headline": "Product designer moving into design systems work",
     "skills": ["Figma", "Design Systems", "UI Design", "Accessibility", "Prototyping",
                "Design Tokens"]},
    {"email": "tanvir.hossain@example.com", "full_name": "Tanvir Hossain",
     "headline": "Backend engineer — Python, FastAPI, Postgres",
     "skills": ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Docker", "REST APIs"]},
    {"email": "maya.chowdhury@example.com", "full_name": "Maya Chowdhury",
     "headline": "Full-stack developer who likes shipping small teams' first product",
     "skills": ["TypeScript", "React", "Node.js", "Express", "PostgreSQL", "AWS"]},
    {"email": "samuel.okafor@example.com", "full_name": "Samuel Okafor",
     "headline": "Platform engineer, Kubernetes and Terraform",
     "skills": ["Kubernetes", "Terraform", "Docker", "AWS", "Go", "CI/CD", "Observability"]},
    {"email": "priya.nair@example.com", "full_name": "Priya Nair",
     "headline": "Data engineer building pipelines that people trust",
     "skills": ["Python", "Apache Airflow", "dbt", "Apache Spark", "Snowflake", "SQL", "ETL"]},
    {"email": "daniel.weiss@example.com", "full_name": "Daniel Weiss",
     "headline": "Senior Java engineer, distributed systems",
     "skills": ["Java", "Spring Boot", "Apache Kafka", "PostgreSQL", "Microservices",
                "System Design"]},
    {"email": "farah.siddiqui@example.com", "full_name": "Farah Siddiqui",
     "headline": "UX researcher turning interviews into decisions",
     "skills": ["User Research", "Usability Testing", "User Interviews", "Journey Mapping",
                "Figma", "Information Architecture"]},
    {"email": "kenji.watanabe@example.com", "full_name": "Kenji Watanabe",
     "headline": "Mobile engineer — React Native and native iOS",
     "skills": ["React Native", "TypeScript", "Swift", "SwiftUI", "iOS Development", "Expo"]},
    {"email": "olivia.brennan@example.com", "full_name": "Olivia Brennan",
     "headline": "ML engineer working on retrieval and ranking",
     "skills": ["Python", "PyTorch", "Machine Learning", "LLM Integration",
                "Retrieval-Augmented Generation", "Vector Databases"]},
    {"email": "imran.chowdhury@example.com", "full_name": "Imran Chowdhury",
     "headline": "QA engineer, automation-first",
     "skills": ["Playwright", "Test Automation", "TypeScript", "CI/CD", "pytest",
                "End-to-End Testing"]},
    {"email": "sofia.ricci@example.com", "full_name": "Sofia Ricci",
     "headline": "Frontend engineer with a design background",
     "skills": ["Vue.js", "TypeScript", "CSS", "Figma", "Accessibility", "Storybook"]},
    {"email": "james.mbeki@example.com", "full_name": "James Mbeki",
     "headline": "Backend engineer — Go, gRPC, event-driven systems",
     "skills": ["Go", "gRPC", "PostgreSQL", "Redis", "Docker", "Event-Driven Architecture"]},
    {"email": "hana.park@example.com", "full_name": "Hana Park",
     "headline": ".NET engineer building internal platforms",
     "skills": ["C#", "ASP.NET Core", "Microsoft SQL Server", "Entity Framework",
                "Microsoft Azure", "REST APIs"]},
    {"email": "rakib.islam@example.com", "full_name": "Rakib Islam",
     "headline": "Junior full-stack developer, one year in",
     "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Git"]},
]

# recruiter index -> job. Two recruiters post twice, so 15 jobs across 13 firms.
JOBS: List[Dict] = [
    {"recruiter": 0, "title": "Senior Frontend Engineer",
     "description": "You will own the customer-facing web application end to end — the "
                    "component library, the performance budget, and the release process. "
                    "We care more about how you reason through a tradeoff than about how "
                    "many frameworks you have used.",
     "required_skills": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
     "location": "Remote", "job_type": "remote", "salary_min": 95000, "salary_max": 140000},
    {"recruiter": 0, "title": "Backend Engineer, Platform",
     "description": "Our platform team keeps the API fast and the deploys boring. You will "
                    "work on the service layer, the query patterns behind it, and the tooling "
                    "that lets fifteen engineers ship without stepping on each other.",
     "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
     "location": "Remote", "job_type": "remote", "salary_min": 90000, "salary_max": 135000},
    {"recruiter": 1, "title": "Product Designer",
     "description": "We are a small team with a large surface area, so you will move between "
                    "research, interface design, and the design system that holds it together. "
                    "Comfort with ambiguity matters more than pixel perfection.",
     "required_skills": ["Figma", "UI Design", "Design Systems", "Prototyping"],
     "location": "Dhaka, Bangladesh", "job_type": "full_time",
     "salary_min": 45000, "salary_max": 70000},
    {"recruiter": 2, "title": "Full-Stack Engineer",
     "description": "Join a four-person product team building tools for logistics operators. "
                    "You will write TypeScript on both sides of the wire and talk to the "
                    "people who use what you build.",
     "required_skills": ["TypeScript", "React", "Node.js", "PostgreSQL"],
     "location": "Singapore", "job_type": "full_time",
     "salary_min": 80000, "salary_max": 120000},
    {"recruiter": 3, "title": "UX Researcher",
     "description": "You will run the studies that decide what we build next — interviews, "
                    "usability sessions, and the synthesis that turns them into something a "
                    "product team can act on.",
     "required_skills": ["User Research", "Usability Testing", "User Interviews",
                         "Journey Mapping"],
     "location": "London, UK", "job_type": "full_time",
     "salary_min": 60000, "salary_max": 85000},
    {"recruiter": 4, "title": "Design Systems Engineer",
     "description": "The bridge role between design and frontend: you will maintain our "
                    "component library, keep tokens in sync with Figma, and make "
                    "accessibility a default rather than a review step.",
     "required_skills": ["React", "TypeScript", "Design Systems", "Accessibility",
                         "Storybook"],
     "location": "Remote", "job_type": "remote", "salary_min": 100000, "salary_max": 145000},
    {"recruiter": 5, "title": "Site Reliability Engineer",
     "description": "You will own the reliability of a platform serving a few million "
                    "requests a day — the Kubernetes footprint, the Terraform that describes "
                    "it, and the alerting that decides whether anyone's evening is ruined.",
     "required_skills": ["Kubernetes", "Terraform", "AWS", "Observability", "Go"],
     "location": "Berlin, Germany", "job_type": "full_time",
     "salary_min": 85000, "salary_max": 125000},
    {"recruiter": 6, "title": "Mobile Engineer (React Native)",
     "description": "One codebase, two stores, and a release train that leaves every "
                    "fortnight. You will work close to the design team and own features from "
                    "spec to App Store.",
     "required_skills": ["React Native", "TypeScript", "iOS Development", "Expo"],
     "location": "Remote", "job_type": "contract",
     "salary_min": 70000, "salary_max": 110000},
    {"recruiter": 7, "title": "Data Engineer",
     "description": "You will build and own the pipelines feeding our analytics warehouse, "
                    "and the tests that tell us when a source has quietly changed shape.",
     "required_skills": ["Python", "Apache Airflow", "dbt", "SQL", "Snowflake"],
     "location": "Remote", "job_type": "remote", "salary_min": 95000, "salary_max": 140000},
    {"recruiter": 8, "title": "Machine Learning Engineer",
     "description": "We are building retrieval and ranking for a document product. You will "
                    "work on the embedding pipeline, the evaluation harness, and the "
                    "unglamorous work of making a model behave in production.",
     "required_skills": ["Python", "PyTorch", "Machine Learning",
                         "Retrieval-Augmented Generation", "Vector Databases"],
     "location": "Remote", "job_type": "remote", "salary_min": 120000, "salary_max": 180000},
    {"recruiter": 9, "title": "Frontend Engineer (Vue)",
     "description": "A studio role: several client products, short feedback loops, and real "
                    "ownership of the frontend on each. Design literacy is a genuine "
                    "advantage here.",
     "required_skills": ["Vue.js", "TypeScript", "CSS", "Accessibility"],
     "location": "Barcelona, Spain", "job_type": "full_time",
     "salary_min": 55000, "salary_max": 80000},
    {"recruiter": 10, "title": "Senior Backend Engineer, Payments",
     "description": "Payments is where correctness stops being negotiable. You will work on "
                    "the ledger, the reconciliation jobs, and the event stream that ties them "
                    "together.",
     "required_skills": ["Java", "Spring Boot", "Apache Kafka", "PostgreSQL",
                         "Microservices"],
     "location": "Dubai, UAE", "job_type": "full_time",
     "salary_min": 110000, "salary_max": 160000},
    {"recruiter": 11, "title": "Go Backend Engineer",
     "description": "Our order pipeline is Go services talking over gRPC. You will add to it, "
                    "and help us keep the seams between services honest.",
     "required_skills": ["Go", "gRPC", "PostgreSQL", "Redis", "Docker"],
     "location": "Remote", "job_type": "remote", "salary_min": 100000, "salary_max": 150000},
    {"recruiter": 12, "title": ".NET Engineer",
     "description": "Internal platform work for a cloud infrastructure company — the "
                    "services, the admin tooling, and the migrations that keep a decade of "
                    "data usable.",
     "required_skills": ["C#", "ASP.NET Core", "Microsoft Azure", "Microsoft SQL Server"],
     "location": "Toronto, Canada", "job_type": "full_time",
     "salary_min": 90000, "salary_max": 130000},
    {"recruiter": 13, "title": "QA Automation Engineer",
     "description": "You will own the end-to-end suite for a regulated health product, and "
                    "the CI setup that runs it on every pull request.",
     "required_skills": ["Playwright", "Test Automation", "TypeScript", "CI/CD"],
     "location": "Remote", "job_type": "part_time",
     "salary_min": 50000, "salary_max": 75000},
]

# (candidate index, job index, status, cover note)
APPLICATIONS = [
    (0, 0, "shortlisted", "Six years of React, the last three in Next.js. I have run a "
                          "performance budget before and would like to do it again."),
    (0, 5, "reviewed", "The design-systems half of this role is what I want to grow into."),
    (0, 3, "applied", "Happy to talk about the full-stack side — I have shipped Node "
                      "services alongside the frontend work."),
    (1, 2, "hired", "My portfolio is mostly design-system work, which looks like what you "
                    "need here."),
    (1, 5, "rejected", "I know this leans engineering; applying anyway in case the balance "
                       "is flexible."),
    (2, 1, "shortlisted", "FastAPI and Postgres are my day job. I have done the boring "
                          "deploy work too."),
    (2, 8, "applied", None),
    (3, 3, "reviewed", "Small teams are where I do my best work."),
    (3, 0, "applied", "Frontend is the half I enjoy most."),
    (4, 6, "shortlisted", "I have run Kubernetes in anger, including the night someone "
                          "deleted a namespace."),
    (5, 8, "reviewed", "Airflow and dbt daily for the last two years."),
    (6, 11, "applied", "Kafka and ledger work is exactly the problem I want."),
    (7, 4, "shortlisted", "I would bring a research practice, not just individual studies."),
    (8, 7, "reviewed", "One codebase, two stores — that has been my last three years."),
    (9, 9, "applied", "The evaluation-harness part of this is what interests me most."),
    (10, 14, "shortlisted", "Playwright plus CI is precisely my setup."),
    (11, 10, "hired", "Vue with a design background — that is the combination I have."),
    (12, 12, "reviewed", "Go and gRPC, with a Postgres bias."),
    (13, 13, "applied", None),
    (14, 3, "rejected", "A year in, so this is a stretch — worth asking."),
    (14, 0, "withdrawn", "Withdrawing; I accepted something else."),
]

# (application index, [(sender, body), ...]) — sender is "candidate" or "recruiter"
THREADS = [
    (0, [
        ("recruiter", "Thanks for applying, Arif. Are you open to a 45-minute technical "
                      "conversation next week?"),
        ("candidate", "Yes — Tuesday or Thursday afternoon works, Asia/Dhaka time."),
        ("recruiter", "Thursday it is. I will send an invite shortly."),
    ]),
    (5, [
        ("candidate", "Is the platform team's on-call rotation weekly or fortnightly?"),
        ("recruiter", "Fortnightly, and only during business hours in your timezone."),
    ]),
    (9, [
        ("recruiter", "Your Kubernetes experience stood out. What was the namespace "
                      "incident, out of curiosity?"),
    ]),
    (12, [
        ("candidate", "Would this role own the research repository, or contribute to an "
                      "existing one?"),
        ("recruiter", "Own it — we do not have one yet, which is part of why we are hiring."),
    ]),
]
