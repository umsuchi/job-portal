/**
 * Skill catalogue used by the tag inputs and the job filter.
 *
 * Skills stay free-text at the API level (spec §18) — this catalogue only makes
 * the common ones easy to pick, so that a candidate typing "postgres" and a
 * recruiter typing "PostgreSQL" end up with the same tag and the array-overlap
 * match in the suggestion engine actually fires.
 *
 * Ranking is drawn from the 2025 Stack Overflow Developer Survey's technology
 * tables, plus standard UI/UX and engineering-practice vocabulary. Editing this
 * list is safe: nothing else derives from it, and unknown skills are still
 * accepted.
 */

export const SKILL_CATEGORIES = [
  'Languages',
  'Frontend',
  'Backend',
  'Mobile',
  'Databases',
  'Cloud & DevOps',
  'Data & AI',
  'Testing',
  'Design (UI/UX)',
  'Practices',
] as const

export type SkillCategory = (typeof SKILL_CATEGORIES)[number]

export interface SkillEntry {
  name: string
  category: SkillCategory
  /** Alternate spellings people actually type. Matched, never displayed. */
  aliases?: string[]
}

/** `s` for short — keeps the table below readable. */
const s = (name: string, category: SkillCategory, ...aliases: string[]): SkillEntry =>
  aliases.length ? { name, category, aliases } : { name, category }

export const SKILLS: SkillEntry[] = [
  // ---------------------------------------------------------------- Languages
  s('JavaScript', 'Languages', 'js', 'ecmascript'),
  s('TypeScript', 'Languages', 'ts'),
  s('Python', 'Languages', 'py'),
  s('Java', 'Languages'),
  s('C#', 'Languages', 'csharp', 'c sharp', 'dotnet language'),
  s('C++', 'Languages', 'cpp', 'cplusplus'),
  s('C', 'Languages'),
  s('Go', 'Languages', 'golang'),
  s('Rust', 'Languages'),
  s('PHP', 'Languages'),
  s('Ruby', 'Languages'),
  s('Kotlin', 'Languages'),
  s('Swift', 'Languages'),
  s('Dart', 'Languages'),
  s('Scala', 'Languages'),
  s('Elixir', 'Languages'),
  s('Erlang', 'Languages'),
  s('Clojure', 'Languages'),
  s('Haskell', 'Languages'),
  s('Lua', 'Languages'),
  s('R', 'Languages'),
  s('MATLAB', 'Languages'),
  s('Perl', 'Languages'),
  s('Groovy', 'Languages'),
  s('Objective-C', 'Languages', 'objc'),
  s('Zig', 'Languages'),
  s('F#', 'Languages', 'fsharp'),
  s('OCaml', 'Languages'),
  s('COBOL', 'Languages'),
  s('Assembly', 'Languages', 'asm'),
  s('SQL', 'Languages'),
  s('Bash', 'Languages', 'shell', 'sh', 'shell scripting'),
  s('PowerShell', 'Languages', 'pwsh'),
  s('HTML', 'Languages', 'html5'),
  s('CSS', 'Languages', 'css3'),

  // ----------------------------------------------------------------- Frontend
  s('React', 'Frontend', 'reactjs', 'react.js'),
  s('Next.js', 'Frontend', 'nextjs', 'next'),
  s('Vue.js', 'Frontend', 'vue', 'vuejs'),
  s('Nuxt.js', 'Frontend', 'nuxt', 'nuxtjs'),
  s('Angular', 'Frontend', 'angular2+'),
  s('Svelte', 'Frontend'),
  s('SvelteKit', 'Frontend'),
  s('Astro', 'Frontend'),
  s('Remix', 'Frontend'),
  s('SolidJS', 'Frontend', 'solid'),
  s('Qwik', 'Frontend'),
  s('Alpine.js', 'Frontend', 'alpinejs'),
  s('HTMX', 'Frontend'),
  s('jQuery', 'Frontend'),
  s('Redux', 'Frontend'),
  s('Zustand', 'Frontend'),
  s('TanStack Query', 'Frontend', 'react query', 'react-query'),
  s('React Router', 'Frontend'),
  s('Tailwind CSS', 'Frontend', 'tailwind', 'tailwindcss'),
  s('shadcn/ui', 'Frontend', 'shadcn'),
  s('Material UI', 'Frontend', 'mui'),
  s('Chakra UI', 'Frontend', 'chakra'),
  s('Bootstrap', 'Frontend'),
  s('Sass', 'Frontend', 'scss'),
  s('CSS Modules', 'Frontend'),
  s('styled-components', 'Frontend'),
  s('Vite', 'Frontend'),
  s('Webpack', 'Frontend'),
  s('Rollup', 'Frontend'),
  s('esbuild', 'Frontend'),
  s('Turbopack', 'Frontend'),
  s('Storybook', 'Frontend'),
  s('Three.js', 'Frontend', 'threejs', 'webgl'),
  s('D3.js', 'Frontend', 'd3'),
  s('GSAP', 'Frontend'),
  s('Framer Motion', 'Frontend'),
  s('Web Components', 'Frontend'),
  s('Progressive Web Apps', 'Frontend', 'pwa'),
  s('Web Performance', 'Frontend', 'core web vitals', 'lighthouse'),
  s('Responsive Design', 'Frontend'),
  s('Server-Side Rendering', 'Frontend', 'ssr'),
  s('WebAssembly', 'Frontend', 'wasm'),

  // ------------------------------------------------------------------ Backend
  s('Node.js', 'Backend', 'node', 'nodejs'),
  s('Express', 'Backend', 'expressjs', 'express.js'),
  s('NestJS', 'Backend', 'nest'),
  s('Fastify', 'Backend'),
  s('Deno', 'Backend'),
  s('Bun', 'Backend'),
  s('FastAPI', 'Backend'),
  s('Django', 'Backend'),
  s('Flask', 'Backend'),
  s('Django REST Framework', 'Backend', 'drf'),
  s('Celery', 'Backend'),
  s('SQLAlchemy', 'Backend'),
  s('Pydantic', 'Backend'),
  s('Spring Boot', 'Backend', 'spring'),
  s('Hibernate', 'Backend'),
  s('ASP.NET Core', 'Backend', 'aspnet', 'asp.net', '.net'),
  s('Entity Framework', 'Backend', 'ef core'),
  s('Laravel', 'Backend'),
  s('Symfony', 'Backend'),
  s('Ruby on Rails', 'Backend', 'rails'),
  s('Phoenix', 'Backend'),
  s('Gin', 'Backend'),
  s('Actix', 'Backend'),
  s('Axum', 'Backend'),
  s('REST APIs', 'Backend', 'rest', 'restful'),
  s('GraphQL', 'Backend'),
  s('gRPC', 'Backend'),
  s('WebSockets', 'Backend', 'websocket'),
  s('Microservices', 'Backend'),
  s('Event-Driven Architecture', 'Backend'),
  s('Message Queues', 'Backend', 'queue'),
  s('RabbitMQ', 'Backend'),
  s('Apache Kafka', 'Backend', 'kafka'),
  s('OAuth 2.0', 'Backend', 'oauth'),
  s('JWT', 'Backend', 'json web token'),
  s('OpenAPI', 'Backend', 'swagger'),
  s('API Design', 'Backend'),
  s('Caching', 'Backend'),

  // ------------------------------------------------------------------- Mobile
  s('React Native', 'Mobile'),
  s('Flutter', 'Mobile'),
  s('SwiftUI', 'Mobile'),
  s('UIKit', 'Mobile'),
  s('Jetpack Compose', 'Mobile'),
  s('Android Development', 'Mobile', 'android'),
  s('iOS Development', 'Mobile', 'ios'),
  s('Expo', 'Mobile'),
  s('Ionic', 'Mobile'),
  s('Mobile App Architecture', 'Mobile'),

  // ---------------------------------------------------------------- Databases
  s('PostgreSQL', 'Databases', 'postgres', 'psql'),
  s('MySQL', 'Databases'),
  s('SQLite', 'Databases'),
  s('MariaDB', 'Databases'),
  s('Microsoft SQL Server', 'Databases', 'mssql', 'sql server'),
  s('Oracle Database', 'Databases', 'oracle'),
  s('MongoDB', 'Databases', 'mongo'),
  s('Redis', 'Databases'),
  s('Elasticsearch', 'Databases', 'elastic', 'opensearch'),
  s('DynamoDB', 'Databases'),
  s('Cassandra', 'Databases'),
  s('Neo4j', 'Databases'),
  s('ClickHouse', 'Databases'),
  s('Snowflake', 'Databases'),
  s('BigQuery', 'Databases'),
  s('Supabase', 'Databases'),
  s('Firebase', 'Databases'),
  s('Prisma', 'Databases'),
  s('Drizzle ORM', 'Databases', 'drizzle'),
  s('pgvector', 'Databases'),
  s('Database Design', 'Databases', 'schema design'),
  s('Query Optimization', 'Databases'),
  s('Data Modeling', 'Databases'),

  // ----------------------------------------------------------- Cloud & DevOps
  s('AWS', 'Cloud & DevOps', 'amazon web services'),
  s('Microsoft Azure', 'Cloud & DevOps', 'azure'),
  s('Google Cloud', 'Cloud & DevOps', 'gcp', 'google cloud platform'),
  s('Docker', 'Cloud & DevOps'),
  s('Kubernetes', 'Cloud & DevOps', 'k8s'),
  s('Terraform', 'Cloud & DevOps'),
  s('Pulumi', 'Cloud & DevOps'),
  s('Ansible', 'Cloud & DevOps'),
  s('CI/CD', 'Cloud & DevOps', 'continuous integration', 'continuous delivery'),
  s('GitHub Actions', 'Cloud & DevOps'),
  s('GitLab CI', 'Cloud & DevOps'),
  s('Jenkins', 'Cloud & DevOps'),
  s('ArgoCD', 'Cloud & DevOps'),
  s('Helm', 'Cloud & DevOps'),
  s('Nginx', 'Cloud & DevOps'),
  s('Linux', 'Cloud & DevOps'),
  s('Git', 'Cloud & DevOps'),
  s('Vercel', 'Cloud & DevOps'),
  s('Netlify', 'Cloud & DevOps'),
  s('Cloudflare Workers', 'Cloud & DevOps', 'cloudflare'),
  s('Serverless', 'Cloud & DevOps', 'lambda', 'aws lambda'),
  s('Prometheus', 'Cloud & DevOps'),
  s('Grafana', 'Cloud & DevOps'),
  s('Datadog', 'Cloud & DevOps'),
  s('OpenTelemetry', 'Cloud & DevOps', 'otel'),
  s('Observability', 'Cloud & DevOps', 'monitoring'),
  s('Infrastructure as Code', 'Cloud & DevOps', 'iac'),
  s('Site Reliability Engineering', 'Cloud & DevOps', 'sre'),
  s('Application Security', 'Cloud & DevOps', 'appsec', 'security'),

  // -------------------------------------------------------------- Data & AI
  s('Pandas', 'Data & AI'),
  s('NumPy', 'Data & AI'),
  s('Polars', 'Data & AI'),
  s('Apache Spark', 'Data & AI', 'spark', 'pyspark'),
  s('Apache Airflow', 'Data & AI', 'airflow'),
  s('dbt', 'Data & AI'),
  s('ETL', 'Data & AI', 'elt', 'data pipelines'),
  s('Data Warehousing', 'Data & AI'),
  s('PyTorch', 'Data & AI'),
  s('TensorFlow', 'Data & AI'),
  s('scikit-learn', 'Data & AI', 'sklearn'),
  s('Machine Learning', 'Data & AI', 'ml'),
  s('Deep Learning', 'Data & AI'),
  s('Natural Language Processing', 'Data & AI', 'nlp'),
  s('Computer Vision', 'Data & AI', 'cv'),
  s('LLM Integration', 'Data & AI', 'llm', 'large language models'),
  s('Prompt Engineering', 'Data & AI'),
  s('Retrieval-Augmented Generation', 'Data & AI', 'rag'),
  s('LangChain', 'Data & AI'),
  s('Vector Databases', 'Data & AI', 'embeddings'),
  s('MLOps', 'Data & AI'),
  s('Data Analysis', 'Data & AI', 'analytics'),
  s('Data Visualization', 'Data & AI', 'dataviz'),

  // ------------------------------------------------------------------ Testing
  s('Unit Testing', 'Testing'),
  s('Integration Testing', 'Testing'),
  s('End-to-End Testing', 'Testing', 'e2e'),
  s('Jest', 'Testing'),
  s('Vitest', 'Testing'),
  s('Playwright', 'Testing'),
  s('Cypress', 'Testing'),
  s('Selenium', 'Testing'),
  s('pytest', 'Testing'),
  s('JUnit', 'Testing'),
  s('React Testing Library', 'Testing', 'testing library'),
  s('Test-Driven Development', 'Testing', 'tdd'),
  s('Load Testing', 'Testing', 'performance testing'),
  s('Test Automation', 'Testing', 'qa automation'),

  // ----------------------------------------------------------- Design (UI/UX)
  s('Figma', 'Design (UI/UX)'),
  s('FigJam', 'Design (UI/UX)'),
  s('Sketch', 'Design (UI/UX)'),
  s('Adobe XD', 'Design (UI/UX)'),
  s('Framer', 'Design (UI/UX)'),
  s('Penpot', 'Design (UI/UX)'),
  s('Adobe Photoshop', 'Design (UI/UX)', 'photoshop'),
  s('Adobe Illustrator', 'Design (UI/UX)', 'illustrator'),
  s('UI Design', 'Design (UI/UX)', 'user interface design'),
  s('UX Design', 'Design (UI/UX)', 'user experience design'),
  s('Interaction Design', 'Design (UI/UX)', 'ixd'),
  s('Visual Design', 'Design (UI/UX)'),
  s('Design Systems', 'Design (UI/UX)'),
  s('Design Tokens', 'Design (UI/UX)'),
  s('Wireframing', 'Design (UI/UX)'),
  s('Prototyping', 'Design (UI/UX)'),
  s('User Research', 'Design (UI/UX)'),
  s('Usability Testing', 'Design (UI/UX)'),
  s('User Interviews', 'Design (UI/UX)'),
  s('Card Sorting', 'Design (UI/UX)'),
  s('Information Architecture', 'Design (UI/UX)', 'ia'),
  s('User Flows', 'Design (UI/UX)'),
  s('Journey Mapping', 'Design (UI/UX)', 'customer journey'),
  s('Personas', 'Design (UI/UX)'),
  s('Typography', 'Design (UI/UX)'),
  s('Color Theory', 'Design (UI/UX)', 'color systems'),
  s('Accessibility', 'Design (UI/UX)', 'a11y', 'wcag', 'aria'),
  s('Motion Design', 'Design (UI/UX)', 'micro-interactions'),
  s('Design Handoff', 'Design (UI/UX)', 'dev mode', 'zeplin'),
  s('Material Design', 'Design (UI/UX)'),
  s('Human Interface Guidelines', 'Design (UI/UX)', 'apple hig'),
  s('Content Design', 'Design (UI/UX)', 'ux writing'),
  s('A/B Testing', 'Design (UI/UX)'),

  // ---------------------------------------------------------------- Practices
  s('Agile', 'Practices', 'scrum'),
  s('Kanban', 'Practices'),
  s('Code Review', 'Practices'),
  s('Pair Programming', 'Practices'),
  s('System Design', 'Practices', 'architecture'),
  s('Domain-Driven Design', 'Practices', 'ddd'),
  s('Refactoring', 'Practices'),
  s('Technical Writing', 'Practices', 'documentation'),
  s('Mentoring', 'Practices', 'coaching'),
  s('Technical Leadership', 'Practices', 'tech lead'),
  s('Stakeholder Management', 'Practices'),
  s('Product Thinking', 'Practices'),
  s('Jira', 'Practices'),
  s('Notion', 'Practices'),
  s('Communication', 'Practices'),
  s('Problem Solving', 'Practices'),
]

const SKILL_BY_KEY = new Map<string, SkillEntry>()
for (const entry of SKILLS) {
  SKILL_BY_KEY.set(normalize(entry.name), entry)
  for (const alias of entry.aliases ?? []) SKILL_BY_KEY.set(normalize(alias), entry)
}

export function normalize(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, ' ')
}

/**
 * Map a typed value onto its catalogue spelling — "postgres" becomes
 * "PostgreSQL" — so both sides of a match agree. Unknown skills pass through
 * with only whitespace tidied, because the catalogue is a convenience, not a
 * whitelist.
 */
export function canonicalize(value: string): string {
  const hit = SKILL_BY_KEY.get(normalize(value))
  return hit ? hit.name : value.trim().replace(/\s+/g, ' ')
}

interface SearchOptions {
  /** Skills already chosen — filtered out of the results. */
  exclude?: string[]
  limit?: number
}

/**
 * Rank catalogue entries against what the user has typed.
 *
 * Order: exact match, then name prefix, then a prefix at any word boundary in
 * the name, then an alias prefix, then anything containing the query. Ties break
 * on the shorter name, so "Go" beats "GraphQL" for "go".
 */
export function searchSkills(query: string, options: SearchOptions = {}): SkillEntry[] {
  const { exclude = [], limit = 8 } = options
  const q = normalize(query)
  const taken = new Set(exclude.map(normalize))

  const available = SKILLS.filter((entry) => !taken.has(normalize(entry.name)))
  if (!q) return available.slice(0, limit)

  const scored: Array<{ entry: SkillEntry; score: number }> = []

  for (const entry of available) {
    const name = normalize(entry.name)
    const aliases = (entry.aliases ?? []).map(normalize)

    let score = -1
    if (name === q || aliases.includes(q)) score = 0
    else if (name.startsWith(q)) score = 1
    else if (name.split(/[\s./-]+/).some((word) => word.startsWith(q))) score = 2
    else if (aliases.some((a) => a.startsWith(q))) score = 3
    else if (name.includes(q) || aliases.some((a) => a.includes(q))) score = 4

    if (score >= 0) scored.push({ entry, score })
  }

  scored.sort(
    (a, b) => a.score - b.score || a.entry.name.length - b.entry.name.length
      || a.entry.name.localeCompare(b.entry.name),
  )
  return scored.slice(0, limit).map((x) => x.entry)
}
