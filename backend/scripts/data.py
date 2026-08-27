"""Seed content, kept apart from the loading logic so it stays readable.

Skill strings use the same spellings as the frontend catalogue
(`frontend/src/lib/skills.ts`). That matters: the suggestion engine matches with
Postgres array overlap, so "PostgreSQL" here and "postgres" there would not meet.
"""
from __future__ import annotations

from typing import Dict, List, Optional

# Every seeded account shares this password — it is only ever used locally.
SEED_PASSWORD = "password123"

RECRUITERS: List[Dict] = [
    {"email": "hiring@northwindlabs.example.com", "company_name": "Northwind Labs",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=northwind-labs",
     "industry": "Developer tooling",
     "headquarters": "Amsterdam, Netherlands",
     "about": "We build the deploy and observability tooling that ~400 engineering teams rely on. Small teams, long-lived services, and a strong preference for boring technology that works.",
     "company_website": "https://northwindlabs.example.com"},
    {"email": "talent@brightpath.example.com", "company_name": "BrightPath Software",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=brightpath-software",
     "industry": "EdTech",
     "headquarters": "Dhaka, Bangladesh",
     "about": "Learning software used by universities across South and Southeast Asia. Product-led, design-heavy, and closer to our users than most companies our size.",
     "company_website": "https://brightpath.example.com"},
    {"email": "jobs@meridiantech.example.com", "company_name": "Meridian Tech",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=meridian-tech",
     "industry": "Logistics",
     "headquarters": "Singapore",
     "about": "Freight and customs software for operators who still run half their business on spreadsheets. Unglamorous problems, immediate impact.",
     "company_website": "https://meridiantech.example.com"},
    {"email": "careers@lantern.example.com", "company_name": "Lantern Digital",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=lantern-digital",
     "industry": "Consumer apps",
     "headquarters": "London, UK",
     "about": "A consumer product studio. We take a research-first approach and ship in small increments, which means designers and engineers work as one team.",
     "company_website": "https://lantern.example.com"},
    {"email": "people@vellumhq.example.com", "company_name": "Vellum HQ",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=vellum-hq",
     "industry": "SaaS",
     "headquarters": "Remote-first",
     "about": "Document collaboration for regulated industries. Fully distributed across nine timezones, with a written-first culture to match.",
     "company_website": "https://vellumhq.example.com"},
    {"email": "hiring@cobaltworks.example.com", "company_name": "Cobalt Works",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=cobalt-works",
     "industry": "Infrastructure",
     "headquarters": "Berlin, Germany",
     "about": "Managed platform infrastructure. Our customers hand us their Kubernetes so they can stop thinking about it \u2014 which means we think about it a great deal.",
     "company_website": "https://cobaltworks.example.com"},
    {"email": "talent@driftwoodapps.example.com", "company_name": "Driftwood Apps",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=driftwood-apps",
     "industry": "Mobile",
     "headquarters": "Remote-first",
     "about": "A mobile studio building consumer apps for clients and a couple of our own. Two-week release trains and genuine ownership of what you ship.",
     "company_website": "https://driftwoodapps.example.com"},
    {"email": "jobs@stonebridgedata.example.com", "company_name": "Stonebridge Data",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=stonebridge-data",
     "industry": "Data platforms",
     "headquarters": "Toronto, Canada",
     "about": "Analytics infrastructure for mid-market retail. We care about pipelines that fail loudly rather than dashboards that are quietly wrong.",
     "company_website": "https://stonebridgedata.example.com"},
    {"email": "careers@harborlineai.example.com", "company_name": "Harborline AI",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=harborline-ai",
     "industry": "Artificial intelligence",
     "headquarters": "San Francisco, USA",
     "about": "Retrieval and ranking over private document collections. Research-adjacent, but everything we build has to survive contact with production.",
     "company_website": "https://harborlineai.example.com"},
    {"email": "hiring@keelstudio.example.com", "company_name": "Keel Studio",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=keel-studio",
     "industry": "Design & development",
     "headquarters": "Barcelona, Spain",
     "about": "A ten-person studio doing product design and frontend work for European scale-ups. Short feedback loops and unusually good coffee.",
     "company_website": "https://keelstudio.example.com"},
    {"email": "people@aurorafintech.example.com", "company_name": "Aurora Fintech",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=aurora-fintech",
     "industry": "Financial services",
     "headquarters": "Dubai, UAE",
     "about": "Cross-border payments infrastructure. Correctness is not negotiable here, which shapes how we design, review and deploy everything.",
     "company_website": "https://aurorafintech.example.com"},
    {"email": "talent@pineconecommerce.example.com", "company_name": "Pinecone Commerce",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=pinecone-commerce",
     "industry": "E-commerce",
     "headquarters": "Remote-first",
     "about": "Order and fulfilment infrastructure behind several mid-size retail brands. Go services, event streams, and a strong bias toward explicit contracts.",
     "company_website": "https://pineconecommerce.example.com"},
    {"email": "jobs@sablecloud.example.com", "company_name": "Sable Cloud",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=sable-cloud",
     "industry": "Cloud infrastructure",
     "headquarters": "Toronto, Canada",
     "about": "Regional cloud hosting with a decade of customers and a decade of data. Platform work with real migration problems attached.",
     "company_website": "https://sablecloud.example.com"},
    {"email": "careers@tidalhealth.example.com", "company_name": "Tidal Health",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=tidal-health",
     "industry": "Health technology",
     "headquarters": "Remote-first",
     "about": "Patient-facing tools for outpatient clinics. Regulated, audited, and genuinely useful \u2014 a rare combination.",
     "company_website": "https://tidalhealth.example.com"},
    {"email": "hiring@quillandcode.example.com", "company_name": "Quill & Code",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=quill-code",
     "industry": "Content platforms",
     "headquarters": "Dublin, Ireland",
     "about": "Publishing tools for independent writers. Small team, opinionated product, and an unusual amount of care about typography.",
     "company_website": "https://quillandcode.example.com"},
]

CANDIDATES: List[Dict] = [
    {"email": "arif.rahman@example.com", "full_name": "Arif Rahman",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=arif-rahman",
     "headline": "Frontend engineer, 6 years in React and TypeScript",
     "bio": "I have spent the last three years on one large Next.js application — "
            "owning the component library, the performance budget and the release "
            "process. I care most about the boring parts: bundle size, error rates, "
            "and making a design system that other engineers actually use.",
     "location": "Dhaka, Bangladesh", "years_experience": 6, "experience_level": "senior",
     "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS", "TanStack Query", "Vite"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["remote", "hybrid"],
     "preferred_locations": ["Remote", "Dhaka"], "desired_salary_min": 90000},

    {"email": "nusrat.jahan@example.com", "full_name": "Nusrat Jahan",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=nusrat-jahan",
     "headline": "Product designer moving into design systems work",
     "bio": "Four years designing product interfaces, the last eighteen months "
            "building and maintaining a design system across three products. "
            "Comfortable in code enough to argue with engineers productively.",
     "location": "Dhaka, Bangladesh", "years_experience": 4, "experience_level": "mid",
     "skills": ["Figma", "Design Systems", "UI Design", "Accessibility", "Prototyping",
                "Design Tokens"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["hybrid", "onsite"],
     "preferred_locations": ["Dhaka", "Remote"], "desired_salary_min": 45000},

    {"email": "tanvir.hossain@example.com", "full_name": "Tanvir Hossain",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=tanvir-hossain",
     "headline": "Backend engineer — Python, FastAPI, Postgres",
     "bio": "Async Python for the last four years, mostly APIs with Postgres behind "
            "them. I have done enough deployment work to have opinions about it, and "
            "I would rather delete code than add it.",
     "location": "Chittagong, Bangladesh", "years_experience": 5, "experience_level": "mid",
     "skills": ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Docker", "REST APIs"],
     "preferred_job_types": ["full_time", "contract"],
     "preferred_work_modes": ["remote"], "preferred_locations": ["Remote"],
     "desired_salary_min": 80000},

    {"email": "maya.chowdhury@example.com", "full_name": "Maya Chowdhury",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=maya-chowdhury",
     "headline": "Full-stack developer who likes shipping small teams' first product",
     "bio": "Three zero-to-one products in four years, all TypeScript on both sides. "
            "I am at my best when the spec is thin and I get to talk to the people "
            "who will use the thing.",
     "location": "Singapore", "years_experience": 4, "experience_level": "mid",
     "skills": ["TypeScript", "React", "Node.js", "Express", "PostgreSQL", "AWS"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["hybrid", "onsite"],
     "preferred_locations": ["Singapore", "Remote"], "desired_salary_min": 85000},

    {"email": "samuel.okafor@example.com", "full_name": "Samuel Okafor",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=samuel-okafor",
     "headline": "Platform engineer, Kubernetes and Terraform",
     "bio": "Nine years in infrastructure, the last five running production "
            "Kubernetes for teams who would rather not. I have been on call for "
            "systems that mattered, which shapes how I design them.",
     "location": "Berlin, Germany", "years_experience": 9, "experience_level": "lead",
     "skills": ["Kubernetes", "Terraform", "Docker", "AWS", "Go", "CI/CD", "Observability"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["hybrid", "remote"],
     "preferred_locations": ["Berlin", "Remote"], "desired_salary_min": 95000},

    {"email": "priya.nair@example.com", "full_name": "Priya Nair",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=priya-nair",
     "headline": "Data engineer building pipelines that people trust",
     "bio": "Airflow and dbt daily for two years, Spark before that. Most of my work "
            "is making failures loud and schemas explicit, so nobody builds a "
            "dashboard on a source that quietly changed shape.",
     "location": "Bengaluru, India", "years_experience": 6, "experience_level": "senior",
     "skills": ["Python", "Apache Airflow", "dbt", "Apache Spark", "Snowflake", "SQL", "ETL"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["remote"],
     "preferred_locations": ["Remote"], "desired_salary_min": 100000},

    {"email": "daniel.weiss@example.com", "full_name": "Daniel Weiss",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=daniel-weiss",
     "headline": "Senior Java engineer, distributed systems",
     "bio": "Eleven years of JVM work, most recently on a payments ledger where "
            "being approximately right was not an option. I like problems where "
            "correctness is checkable.",
     "location": "Dubai, UAE", "years_experience": 11, "experience_level": "lead",
     "skills": ["Java", "Spring Boot", "Apache Kafka", "PostgreSQL", "Microservices",
                "System Design"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["onsite", "hybrid"],
     "preferred_locations": ["Dubai", "Berlin"], "desired_salary_min": 120000},

    {"email": "farah.siddiqui@example.com", "full_name": "Farah Siddiqui",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=farah-siddiqui",
     "headline": "UX researcher turning interviews into decisions",
     "bio": "Five years of mixed-methods research. The part I am good at is the "
            "synthesis — turning twelve messy interviews into three things a product "
            "team can actually act on this quarter.",
     "location": "London, UK", "years_experience": 5, "experience_level": "senior",
     "skills": ["User Research", "Usability Testing", "User Interviews", "Journey Mapping",
                "Figma", "Information Architecture"],
     "preferred_job_types": ["full_time", "contract"],
     "preferred_work_modes": ["hybrid"], "preferred_locations": ["London", "Remote"],
     "desired_salary_min": 65000},

    {"email": "kenji.watanabe@example.com", "full_name": "Kenji Watanabe",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=kenji-watanabe",
     "headline": "Mobile engineer — React Native and native iOS",
     "bio": "One codebase, two stores, three years. I have shipped through enough "
            "App Store review cycles to plan around them, and I work closely with "
            "designers rather than waiting for handoff.",
     "location": "Tokyo, Japan", "years_experience": 7, "experience_level": "senior",
     "skills": ["React Native", "TypeScript", "Swift", "SwiftUI", "iOS Development", "Expo"],
     "preferred_job_types": ["contract", "full_time"],
     "preferred_work_modes": ["remote"], "preferred_locations": ["Remote", "Tokyo"],
     "desired_salary_min": 85000},

    {"email": "olivia.brennan@example.com", "full_name": "Olivia Brennan",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=olivia-brennan",
     "headline": "ML engineer working on retrieval and ranking",
     "bio": "Six years between research and production, currently on retrieval over "
            "private document sets. Most of the value I add is in the evaluation "
            "harness, not the model.",
     "location": "Dublin, Ireland", "years_experience": 6, "experience_level": "senior",
     "skills": ["Python", "PyTorch", "Machine Learning", "LLM Integration",
                "Retrieval-Augmented Generation", "Vector Databases"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["remote"],
     "preferred_locations": ["Remote", "Dublin"], "desired_salary_min": 130000},

    {"email": "imran.chowdhury@example.com", "full_name": "Imran Chowdhury",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=imran-chowdhury",
     "headline": "QA engineer, automation-first",
     "bio": "I do not write manual test plans. Four years of Playwright suites wired "
            "into CI, with a focus on tests that fail for one reason and tell you "
            "what it was.",
     "location": "Dhaka, Bangladesh", "years_experience": 4, "experience_level": "mid",
     "skills": ["Playwright", "Test Automation", "TypeScript", "CI/CD", "pytest",
                "End-to-End Testing"],
     "preferred_job_types": ["part_time", "contract"],
     "preferred_work_modes": ["remote"], "preferred_locations": ["Remote"],
     "desired_salary_min": 45000},

    {"email": "sofia.ricci@example.com", "full_name": "Sofia Ricci",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=sofia-ricci",
     "headline": "Frontend engineer with a design background",
     "bio": "I trained as a designer and moved into frontend, which means I argue "
            "about spacing and can also fix it. Vue for the last three years, plus "
            "the accessibility work nobody else volunteers for.",
     "location": "Barcelona, Spain", "years_experience": 5, "experience_level": "mid",
     "skills": ["Vue.js", "TypeScript", "CSS", "Figma", "Accessibility", "Storybook"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["hybrid", "onsite"],
     "preferred_locations": ["Barcelona", "Remote"], "desired_salary_min": 55000},

    {"email": "james.mbeki@example.com", "full_name": "James Mbeki",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=james-mbeki",
     "headline": "Backend engineer — Go, gRPC, event-driven systems",
     "bio": "Seven years of backend work, four in Go. I like explicit contracts "
            "between services and I am suspicious of anything that requires a "
            "diagram to explain the happy path.",
     "location": "Cape Town, South Africa", "years_experience": 7, "experience_level": "senior",
     "skills": ["Go", "gRPC", "PostgreSQL", "Redis", "Docker", "Event-Driven Architecture"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["remote"],
     "preferred_locations": ["Remote"], "desired_salary_min": 105000},

    {"email": "hana.park@example.com", "full_name": "Hana Park",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=hana-park",
     "headline": ".NET engineer building internal platforms",
     "bio": "Eight years on internal tooling and platform services in .NET. A lot of "
            "my work has been migrations — moving a decade of data without anyone "
            "noticing.",
     "location": "Toronto, Canada", "years_experience": 8, "experience_level": "senior",
     "skills": ["C#", "ASP.NET Core", "Microsoft SQL Server", "Entity Framework",
                "Microsoft Azure", "REST APIs"],
     "preferred_job_types": ["full_time"], "preferred_work_modes": ["hybrid"],
     "preferred_locations": ["Toronto"], "desired_salary_min": 95000},

    {"email": "rakib.islam@example.com", "full_name": "Rakib Islam",
     "avatar_url": "https://api.dicebear.com/9.x/initials/svg?seed=rakib-islam",
     "headline": "Junior full-stack developer, one year in",
     "bio": "One year professionally, plus a lot of side projects before that. "
            "Currently strongest in React; learning the backend properly rather than "
            "just enough to get by.",
     "location": "Dhaka, Bangladesh", "years_experience": 1, "experience_level": "junior",
     "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
     "preferred_job_types": ["full_time", "internship"],
     "preferred_work_modes": ["onsite", "hybrid"],
     "preferred_locations": ["Dhaka"], "desired_salary_min": 20000},
]

# recruiter index -> job. Two recruiters post twice, so 15 jobs across 13 firms.
JOBS: List[Dict] = [
    {"recruiter": 0, "title": "Senior Frontend Engineer",
     "description": "You will own the customer-facing web application end to end — the "
                    "component library, the performance budget, and the release process. "
                    "We care more about how you reason through a tradeoff than about how "
                    "many frameworks you have used.",
     "responsibilities": [
         "Own the architecture and performance of our main React application",
         "Maintain the shared component library other teams build on",
         "Work directly with design on what is feasible and what is worth it",
         "Mentor two mid-level engineers through code review"],
     "requirements": [
         "5+ years building production React applications",
         "Fluent TypeScript, including where its type system stops helping",
         "Have owned a performance budget, not just read about one"],
     "benefits": ["Fully remote within ±3 hours of CET", "Four-day release weeks",
                  "€2,000 annual learning budget"],
     "required_skills": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
     "nice_to_have_skills": ["Storybook", "Web Performance", "Design Systems"],
     "experience_level": "senior", "min_years_experience": 5,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 95000, "salary_max": 140000},

    {"recruiter": 0, "title": "Backend Engineer, Platform",
     "description": "Our platform team keeps the API fast and the deploys boring. You will "
                    "work on the service layer, the query patterns behind it, and the tooling "
                    "that lets fifteen engineers ship without stepping on each other.",
     "responsibilities": [
         "Design and build async Python services",
         "Own query performance against a Postgres database that is no longer small",
         "Improve the deploy pipeline so releases stay uneventful"],
     "requirements": [
         "3+ years of Python in production",
         "Comfortable reading an EXPLAIN plan and acting on it",
         "Have run something you built, not just handed it over"],
     "benefits": ["Fully remote", "On-call is fortnightly and business hours only",
                  "Conference travel"],
     "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
     "nice_to_have_skills": ["SQLAlchemy", "Kubernetes", "Observability"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 90000, "salary_max": 135000},

    {"recruiter": 1, "title": "Product Designer",
     "description": "We are a small team with a large surface area, so you will move between "
                    "research, interface design, and the design system that holds it together. "
                    "Comfort with ambiguity matters more than pixel perfection.",
     "responsibilities": [
         "Design end-to-end flows, from first sketch to shipped interface",
         "Grow and maintain the design system across three products",
         "Run lightweight research when a decision needs evidence"],
     "requirements": [
         "3+ years designing software products, not marketing pages",
         "A portfolio showing your reasoning, not only your final screens",
         "Fluent in Figma, including components and variables"],
     "benefits": ["Hybrid — two days in the Dhaka office", "Annual design conference budget",
                  "Real influence on the roadmap"],
     "required_skills": ["Figma", "UI Design", "Design Systems", "Prototyping"],
     "nice_to_have_skills": ["User Research", "Accessibility", "Design Tokens"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Dhaka, Bangladesh", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 45000, "salary_max": 70000},

    {"recruiter": 2, "title": "Full-Stack Engineer",
     "description": "Join a four-person product team building tools for logistics operators. "
                    "You will write TypeScript on both sides of the wire and talk to the "
                    "people who use what you build.",
     "responsibilities": [
         "Build features end to end, from schema to interface",
         "Sit in on customer calls — we do not have a product manager buffer",
         "Keep the Postgres schema honest as the product grows"],
     "requirements": [
         "3+ years shipping full-stack TypeScript",
         "Comfortable owning a feature without a detailed spec"],
     "benefits": ["Hybrid in Singapore", "Equity", "Direct customer contact"],
     "required_skills": ["TypeScript", "React", "Node.js", "PostgreSQL"],
     "nice_to_have_skills": ["AWS", "Express", "Database Design"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Singapore", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 80000, "salary_max": 120000},

    {"recruiter": 3, "title": "UX Researcher",
     "description": "You will run the studies that decide what we build next — interviews, "
                    "usability sessions, and the synthesis that turns them into something a "
                    "product team can act on.",
     "responsibilities": [
         "Plan and run generative and evaluative studies",
         "Build the research repository from nothing — we do not have one",
         "Present findings to teams who will argue with them"],
     "requirements": [
         "4+ years of applied UX research",
         "Mixed methods, and the judgement to know which one fits",
         "Writing clear enough that findings survive being forwarded"],
     "benefits": ["Hybrid in London", "Dedicated research tooling budget",
                  "A team that acts on findings"],
     "required_skills": ["User Research", "Usability Testing", "User Interviews",
                         "Journey Mapping"],
     "nice_to_have_skills": ["Information Architecture", "Figma", "Card Sorting"],
     "experience_level": "senior", "min_years_experience": 4,
     "location": "London, UK", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 60000, "salary_max": 85000},

    {"recruiter": 4, "title": "Design Systems Engineer",
     "description": "The bridge role between design and frontend: you will maintain our "
                    "component library, keep tokens in sync with Figma, and make "
                    "accessibility a default rather than a review step.",
     "responsibilities": [
         "Own the component library and its documentation",
         "Keep design tokens synchronised between Figma and code",
         "Make WCAG 2.2 AA the default rather than a retrofit"],
     "requirements": [
         "4+ years of frontend engineering",
         "Have maintained a design system used by other teams",
         "Genuine accessibility knowledge, not a checklist"],
     "benefits": ["Fully remote, nine timezones", "Written-first culture",
                  "Home office budget"],
     "required_skills": ["React", "TypeScript", "Design Systems", "Accessibility",
                         "Storybook"],
     "nice_to_have_skills": ["Design Tokens", "Figma", "CSS"],
     "experience_level": "senior", "min_years_experience": 4,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 100000, "salary_max": 145000},

    {"recruiter": 5, "title": "Site Reliability Engineer",
     "description": "You will own the reliability of a platform serving a few million "
                    "requests a day — the Kubernetes footprint, the Terraform that describes "
                    "it, and the alerting that decides whether anyone's evening is ruined.",
     "responsibilities": [
         "Own our multi-cluster Kubernetes estate",
         "Describe all of it in Terraform, with no manual drift",
         "Tune alerting so pages mean something"],
     "requirements": [
         "5+ years in infrastructure or SRE",
         "Production Kubernetes, including the incidents",
         "Have written Terraform someone else had to maintain"],
     "benefits": ["Hybrid in Berlin", "Compensated on-call", "Relocation support"],
     "required_skills": ["Kubernetes", "Terraform", "AWS", "Observability", "Go"],
     "nice_to_have_skills": ["Prometheus", "Grafana", "CI/CD"],
     "experience_level": "senior", "min_years_experience": 5,
     "location": "Berlin, Germany", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 85000, "salary_max": 125000},

    {"recruiter": 6, "title": "Mobile Engineer (React Native)",
     "description": "One codebase, two stores, and a release train that leaves every "
                    "fortnight. You will work close to the design team and own features from "
                    "spec to App Store.",
     "responsibilities": [
         "Build features across iOS and Android from one codebase",
         "Own the release train, including store review",
         "Drop into native when React Native runs out of road"],
     "requirements": [
         "3+ years of React Native in production",
         "Have shipped to both stores and handled a rejection"],
     "benefits": ["Fully remote", "Six-month contract with extension likely",
                  "Device budget"],
     "required_skills": ["React Native", "TypeScript", "iOS Development", "Expo"],
     "nice_to_have_skills": ["Swift", "Jetpack Compose", "Mobile App Architecture"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Remote", "job_type": "contract", "work_mode": "remote",
     "salary_min": 70000, "salary_max": 110000},

    {"recruiter": 7, "title": "Data Engineer",
     "description": "You will build and own the pipelines feeding our analytics warehouse, "
                    "and the tests that tell us when a source has quietly changed shape.",
     "responsibilities": [
         "Build and own Airflow pipelines into Snowflake",
         "Model the warehouse in dbt, with tests that actually fail",
         "Make upstream schema changes loud instead of silent"],
     "requirements": [
         "4+ years in data engineering",
         "Airflow and dbt in production, not in a tutorial",
         "SQL good enough to be the person others ask"],
     "benefits": ["Fully remote", "No on-call", "Annual conference budget"],
     "required_skills": ["Python", "Apache Airflow", "dbt", "SQL", "Snowflake"],
     "nice_to_have_skills": ["Apache Spark", "ETL", "Data Modeling"],
     "experience_level": "senior", "min_years_experience": 4,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 95000, "salary_max": 140000},

    {"recruiter": 8, "title": "Machine Learning Engineer",
     "description": "We are building retrieval and ranking for a document product. You will "
                    "work on the embedding pipeline, the evaluation harness, and the "
                    "unglamorous work of making a model behave in production.",
     "responsibilities": [
         "Own the retrieval and ranking pipeline end to end",
         "Build the evaluation harness the team trusts",
         "Take models to production and keep them there"],
     "requirements": [
         "4+ years applying ML to a real product",
         "Comfortable with PyTorch and with reading recent papers",
         "Have shipped a retrieval system, not only trained a model"],
     "benefits": ["Fully remote", "Compute budget", "Publication support"],
     "required_skills": ["Python", "PyTorch", "Machine Learning",
                         "Retrieval-Augmented Generation", "Vector Databases"],
     "nice_to_have_skills": ["LLM Integration", "MLOps", "pgvector"],
     "experience_level": "senior", "min_years_experience": 4,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 120000, "salary_max": 180000},

    {"recruiter": 9, "title": "Frontend Engineer (Vue)",
     "description": "A studio role: several client products, short feedback loops, and real "
                    "ownership of the frontend on each. Design literacy is a genuine "
                    "advantage here.",
     "responsibilities": [
         "Own the frontend on two or three client products at a time",
         "Work directly with our designers, not from a handoff file",
         "Keep accessibility in scope from the start"],
     "requirements": [
         "3+ years of Vue in production",
         "CSS skills beyond a utility framework"],
     "benefits": ["Hybrid in Barcelona", "Friday afternoons for personal projects",
                  "Genuinely good coffee"],
     "required_skills": ["Vue.js", "TypeScript", "CSS", "Accessibility"],
     "nice_to_have_skills": ["Figma", "Nuxt.js", "Storybook"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Barcelona, Spain", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 55000, "salary_max": 80000},

    {"recruiter": 10, "title": "Senior Backend Engineer, Payments",
     "description": "Payments is where correctness stops being negotiable. You will work on "
                    "the ledger, the reconciliation jobs, and the event stream that ties them "
                    "together.",
     "responsibilities": [
         "Build and maintain the double-entry ledger",
         "Own reconciliation between our records and the banks'",
         "Design event schemas that stay compatible as we grow"],
     "requirements": [
         "6+ years of JVM backend work",
         "Kafka or a comparable event platform in production",
         "Have worked somewhere correctness was audited"],
     "benefits": ["Onsite in Dubai", "Relocation and visa support", "Tax-free salary"],
     "required_skills": ["Java", "Spring Boot", "Apache Kafka", "PostgreSQL",
                         "Microservices"],
     "nice_to_have_skills": ["System Design", "Event-Driven Architecture", "Kotlin"],
     "experience_level": "lead", "min_years_experience": 6,
     "location": "Dubai, UAE", "job_type": "full_time", "work_mode": "onsite",
     "salary_min": 110000, "salary_max": 160000},

    {"recruiter": 11, "title": "Go Backend Engineer",
     "description": "Our order pipeline is Go services talking over gRPC. You will add to it, "
                    "and help us keep the seams between services honest.",
     "responsibilities": [
         "Build Go services in the order and fulfilment pipeline",
         "Define gRPC contracts other teams depend on",
         "Keep latency predictable under seasonal load"],
     "requirements": [
         "4+ years of Go in production",
         "gRPC or another schema-first RPC system",
         "Postgres knowledge beyond basic queries"],
     "benefits": ["Fully remote", "Async-first", "Quarterly team offsites"],
     "required_skills": ["Go", "gRPC", "PostgreSQL", "Redis", "Docker"],
     "nice_to_have_skills": ["Event-Driven Architecture", "Kubernetes", "Observability"],
     "experience_level": "senior", "min_years_experience": 4,
     "location": "Remote", "job_type": "full_time", "work_mode": "remote",
     "salary_min": 100000, "salary_max": 150000},

    {"recruiter": 12, "title": ".NET Engineer",
     "description": "Internal platform work for a cloud infrastructure company — the "
                    "services, the admin tooling, and the migrations that keep a decade of "
                    "data usable.",
     "responsibilities": [
         "Build internal platform services in .NET",
         "Run data migrations against a decade of production data",
         "Improve the admin tooling our support team lives in"],
     "requirements": [
         "5+ years of C# and .NET",
         "SQL Server experience including migrations",
         "Patience for legacy code that pays the bills"],
     "benefits": ["Hybrid in Toronto", "Pension matching", "Education allowance"],
     "required_skills": ["C#", "ASP.NET Core", "Microsoft Azure", "Microsoft SQL Server"],
     "nice_to_have_skills": ["Entity Framework", "REST APIs", "Docker"],
     "experience_level": "senior", "min_years_experience": 5,
     "location": "Toronto, Canada", "job_type": "full_time", "work_mode": "hybrid",
     "salary_min": 90000, "salary_max": 130000},

    {"recruiter": 13, "title": "QA Automation Engineer",
     "description": "You will own the end-to-end suite for a regulated health product, and "
                    "the CI setup that runs it on every pull request.",
     "responsibilities": [
         "Own the Playwright end-to-end suite",
         "Keep it fast enough to run on every pull request",
         "Produce the test evidence our audits require"],
     "requirements": [
         "3+ years of test automation",
         "Playwright or Cypress at scale",
         "Comfortable in a CI pipeline, not just a local runner"],
     "benefits": ["Fully remote", "Part-time, 24 hours a week", "Flexible hours"],
     "required_skills": ["Playwright", "Test Automation", "TypeScript", "CI/CD"],
     "nice_to_have_skills": ["End-to-End Testing", "pytest", "GitHub Actions"],
     "experience_level": "mid", "min_years_experience": 3,
     "location": "Remote", "job_type": "part_time", "work_mode": "remote",
     "salary_min": 50000, "salary_max": 75000},
]


# Application deadlines, as days from the seed run so the demo never goes
# stale. Negative means already expired; 0 means closing today; None means
# no deadline. The spread is deliberate — it makes the live, closing-soon
# and expired states all visible without editing anything.
JOB_DEADLINE_DAYS: Dict[int, Optional[int]] = {
    0: 21,
    1: 45,
    2: 3,
    3: None,
    4: 10,
    5: None,
    6: -4,
    7: 6,
    8: 30,
    9: None,
    10: 14,
    11: -12,
    12: 60,
    13: None,
    14: 0,
}

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
