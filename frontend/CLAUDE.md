# CrowdTest Frontend

## Tech Stack
- Next.js 14 (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Framer Motion (animations)
- Recharts (charts)

## Directory Structure
```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx            # Testing Lab (main page)
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   └── insights/
│       └── [testId]/
│           └── page.tsx    # Insights dashboard
├── components/
│   ├── lab/                # Testing Lab components
│   │   ├── ChatSidebar.tsx
│   │   ├── Character.tsx
│   │   ├── ThoughtBubble.tsx
│   │   └── CrowdScene.tsx
│   ├── insights/           # Insights Dashboard components
│   │   ├── ExecutiveSummary.tsx
│   │   ├── SentimentChart.tsx
│   │   ├── SegmentAnalysis.tsx
│   │   ├── ThemeExtractor.tsx
│   │   └── ResponseDrillDown.tsx
│   └── common/             # Shared components
├── hooks/
│   ├── useSSE.ts           # SSE connection hook
│   └── useTestSession.ts   # Test lifecycle hook
└── lib/
    ├── api.ts              # API client
    └── types.ts            # TypeScript interfaces
```

## Code Style
- Prefer `interface` over `type`
- Named exports for utilities, default exports for components
- Functional components with hooks
- Tailwind utility classes only — no custom CSS files
- ES modules (import/export)

## Environment Variables
- `NEXT_PUBLIC_API_URL` — Backend URL (default: http://localhost:8000)
