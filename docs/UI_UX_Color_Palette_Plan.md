# CircularCarbon AI — UI/UX + Color Palette Plan

## 1. Overall Design Direction

**Design style:** Modern Industrial / Climate-Tech / Data-Driven

The interface should feel like a combination of:

- Industrial analytics dashboard
- Climate-tech product
- Financial decision tool

The visual message should be:

> **“This system finds measurable problems and tells me what action is worth taking.”**

### Visual characteristics

- Clean
- High information density
- Strong hierarchy
- Large numerical metrics
- Dark navy text/backgrounds
- Off-white surfaces
- Controlled green usage
- Amber/red only for alerts
- Minimal decorative illustrations
- Rounded but not excessively bubble-like
- Subtle borders instead of heavy shadows

---

# 2. Primary Color Palette

Recommended palette: **deep navy + emerald + mint + warm neutral**

| Role | Color | Hex |
|---|---|---|
| Primary | Deep Forest | `#126B5A` |
| Primary Dark | Dark Forest | `#0B4A3F` |
| Secondary | Emerald | `#20A67A` |
| Accent | Mint | `#A7E8D0` |
| Background | Warm White | `#F7F9F7` |
| Surface | White | `#FFFFFF` |
| Main Text | Carbon Black | `#17211F` |
| Secondary Text | Slate | `#66736F` |
| Border | Soft Gray | `#DCE4E0` |
| Success | Green | `#16865B` |
| Warning | Amber | `#D79520` |
| Danger | Red | `#D9534F` |
| Info | Blue | `#3D73C9` |

### Color rationale

**Navy/black** provides the industrial and technical feeling.

**Forest/emerald** communicates sustainability without turning the entire website green.

**Mint** highlights reductions and positive outcomes.

**Amber/red** are reserved for actual problems so they retain semantic meaning.

---

# 3. Dark Mode Palette

A dark dashboard would work particularly well for analytics.

| Role | Hex |
|---|---|
| Background | `#0B1513` |
| Surface | `#101E1B` |
| Surface Elevated | `#162824` |
| Border | `#27403A` |
| Primary Green | `#39C596` |
| Mint | `#8DE2C2` |
| Main Text | `#F0F5F2` |
| Secondary Text | `#94A59F` |
| Warning | `#E5AA3A` |
| Danger | `#EA6B67` |

Recommended UX:

**Light mode for forms/onboarding**  
**Dark mode for analytics/dashboard**

---

# 4. Color Usage Rule

Do not use green everywhere.

Approximate visual balance:

```text
60% Neutral
25% Navy / Dark
10% Green
5% Accent / Alerts
```

### Semantic color usage

Green:

- Reduction achieved
- Recommended action
- Positive impact
- Circularity
- Savings
- Progress

Red:

- High emission hotspot
- Severe inefficiency
- High waste
- Risk

Amber:

- Medium priority
- Moderate impact
- Attention needed

Colors should communicate meaning rather than act as decoration.

---

# 5. Typography

### Primary font

**Inter**

Alternative:

**Manrope**

### Typography scale

| Element | Size |
|---|---:|
| Hero | 52–64px |
| Page heading | 32–40px |
| Section heading | 22–28px |
| Card heading | 16–18px |
| Body | 14–16px |
| Small metadata | 12–13px |
| Metric number | 32–48px |

Example:

```text
TOTAL EMISSIONS

124.6
tCO₂e / month

↓ 18.4% vs previous assessment
```

The **124.6** should dominate visually.

---

# 6. Layout System

Use a 12-column desktop grid.

```text
┌─────────────────────────────────────────────────────────┐
│ Sidebar │                 Main Content                   │
│         │                                                │
│         │                                                │
│         │                                                │
└─────────────────────────────────────────────────────────┘
```

### Desktop

Sidebar:

**240–260px**

Main content:

**Fluid**

### Mobile

Collapse into:

```text
☰
CircularCarbon
```

Use a bottom/mobile navigation where appropriate.

---

# 7. Navigation Structure

Keep navigation compact.

```text
CircularCarbon

Overview
Assessment
Emission Hotspots
Recommendations
Simulator
Action Plan
Reports

────────────

Factory
Settings
```

The core product flow is:

**Assess → Discover → Decide → Act**

The navigation should reflect that.

---

# 8. Landing Page UX

The homepage should not immediately bombard users with forms.

## Hero

```text
Find where your factory
is losing carbon efficiency.

CircularCarbon AI analyzes your energy,
materials and waste to identify high-impact
emission hotspots and recommend
cost-effective circular alternatives.

[ Start Free Assessment ]

No sensors required for the initial assessment.
```

### Hero visual

Use a stylized emissions process diagram instead of a generic factory photo:

```text
RAW MATERIAL
     ↓
PROCESSING
     ↓
FINISHING
     ↓
PRODUCT
```

Highlight leak points:

```text
PROCESSING
🔥 42% emissions
```

This immediately explains the product.

---

# 9. Landing Page Sections

### Section 1

Hero.

### Section 2 — How it works

```text
01
Enter factory data

↓

02
Find emission hotspots

↓

03
Get circular alternatives

↓

04
Simulate savings

↓

05
Execute action plan
```

### Section 3

Interactive dashboard preview.

### Section 4

**Why CircularCarbon?**

Show:

```text
CO₂ reduction
Cost savings
Payback period
Circularity score
```

### Section 5

CTA:

> Turn your emissions data into your next business decision.

---

# 10. Onboarding UX

Use a four-step progress system.

```text
① Factory
──●────────────

② Production
────●──────────

③ Energy & Materials
────────●──────

④ Waste
──────────●───
```

## Step 1 — Factory

```text
Factory Name
Industry
Location
Production volume
```

## Step 2 — Production Process

```text
Process

[ Add Process ]

Cutting
Machining
Heating
Finishing
```

## Step 3 — Energy & Materials

```text
Electricity
Natural Gas
Diesel

Raw Materials
Virgin %
Recycled %
```

## Step 4 — Waste

```text
Waste generated
Recycled
Reused
Landfilled
```

For every section, explain why the data is being requested.

Example:

> Electricity usage helps estimate your facility's indirect emissions.

---

# 11. Progress UX

At the top:

```text
Assessment completeness

██████████████░░░░ 78%

You're ready for a preliminary analysis.
```

Don't require every field before showing value.

Allow:

> **Analyze with current data**

Then show:

> Adding fuel consumption could improve this estimate.

---

# 12. Main Dashboard

This should be the centerpiece of the product.

## Header

```text
Good evening, ABC Manufacturing

Monthly Carbon Assessment
September 2026

[ Recalculate ] [ Export Report ]
```

---

# 13. KPI Cards

Use four large cards.

```text
┌───────────────┐ ┌───────────────┐
│ TOTAL CO₂     │ │ CO₂ / UNIT    │
│               │ │               │
│ 124.6         │ │ 12.46 kg      │
│ tCO₂e         │ │ / product     │
│ ↓ 8.4%        │ │ ↓ 5.2%        │
└───────────────┘ └───────────────┘

┌───────────────┐ ┌───────────────┐
│ TOP HOTSPOT   │ │ SAVING        │
│               │ │ OPPORTUNITY   │
│ Furnace       │ │ ₹4.2L/year    │
│ 42%           │ │               │
│ High Impact   │ │ 31.8t CO₂     │
└───────────────┘ └───────────────┘
```

---

# 14. Dashboard Hierarchy

The dashboard should visually answer:

```text
TOTAL IMPACT
     ↓
WHERE?
     ↓
WHY?
     ↓
WHAT SHOULD I DO?
     ↓
HOW MUCH WILL IT HELP?
```

Don't make the dashboard merely a collection of charts.

---

# 15. Emission Hotspot Visualization

Use an interactive process map rather than relying only on a pie chart.

### Left

```text
RAW MATERIAL
      │
      ▼
CUTTING ───────── 🔴 18%
      │
      ▼
MACHINING ─────── 🟠 24%
      │
      ▼
FURNACE ───────── 🔴 42%
      │
      ▼
FINISHING ─────── 🟢 8%
```

### Right

```text
🔥 FURNACE

42%
of total emissions

52.3 tCO₂e/month

Primary cause
Natural gas consumption

[ View recommendations → ]
```

This directly connects **data → diagnosis**.

---

# 16. Hotspot Page

The page should feel like a diagnostic tool.

Header:

```text
Emission Hotspots
3 high-priority opportunities detected
```

Cards:

```text
01  🔴 Furnace
    42% of emissions
    52.3 tCO₂e

02  🟠 Material Processing
    26%
    32.4 tCO₂e

03  🟡 Waste
    14%
    17.4 tCO₂e
```

Sorting options:

```text
Impact
Cost to Fix
CO₂ Reduction Potential
Payback
```

---

# 17. Recommendation UX

This is where the product should feel intelligent.

Use a consistent card:

```text
┌─────────────────────────────────────────────┐
│ ♻ 01  REUSE ALUMINUM SCRAP                  │
│                                             │
│ Priority                    HIGH             │
│                                             │
│ Potential CO₂ reduction     7.8 t/month     │
│ Estimated annual saving     ₹1.2L            │
│ Implementation cost         LOW              │
│ Payback                    3.2 months       │
│                                             │
│ Circularity Score           92/100           │
│                                             │
│ [ View recommendation ]                     │
└─────────────────────────────────────────────┘
```

---

# 18. Recommendation Detail Page

Clicking a recommendation opens a detailed view.

## Header

```text
Reuse Internal Aluminum Scrap

HIGH PRIORITY
```

## Impact

```text
CO₂ reduction
7.8 t/month

Annual reduction
93.6 t/year

Annual saving
₹1.2L

Payback
3.2 months
```

## Why?

```text
WHY THIS WAS RECOMMENDED

Your cutting process generates 18%
material waste.

Approximately 64% of this scrap
is currently sent outside the
production loop.

Reusing it could reduce both
material demand and associated
embodied emissions.
```

## Implementation

```text
STEP 1
Segregate aluminum scrap

STEP 2
Install collection point

STEP 3
Validate material quality

STEP 4
Return scrap to production
```

---

# 19. Recommendation Comparison UX

Let users compare interventions.

```text
                    Scrap     Recycled      Heat
                    Reuse     Material      Recovery

CO₂ ↓               18%       35%           14%

Cost                Low       Medium        High

Payback             3 mo      11 mo         8 mo

Feasibility         92        78            61

Circularity         95        88            82
```

Then highlight:

> **Best value: Scrap Reuse**

---

# 20. What-If Simulator

This should be the **hero feature inside the application**.

Use a split screen.

## Left — Controls

```text
SIMULATION

Recycled Material
10% ─────────●──────── 60%

Energy Efficiency
70% ─────●──────────── 100%

Waste Recovery
20% ───────●────────── 90%
```

## Right — Results

```text
CURRENT             SIMULATED

124.6 t             91.2 t
CO₂/month           CO₂/month

                    ↓

                 -26.8%

₹0                 ₹4.3L
                  annual saving
```

Include a chart showing emissions changing dynamically.

---

# 21. Slider Design

Sliders should update values instantly.

Current:

```text
10%
●────────────────────────
```

Selected:

```text
40%
●━━━━━━━━━━━━━━●─────────
```

The experience should feel:

> **Change → See → Decide**

Avoid forcing a separate “Calculate” button for every change.

---

# 22. Action Plan UX

Turn recommendations into execution.

## 90-Day Plan

```text
DAY 0 ───────────────────────── DAY 90

      │          │          │
      ▼          ▼          ▼

    AUDIT      IMPLEMENT    MEASURE
```

Example:

```text
WEEK 1–2
✓ Measure furnace consumption

WEEK 3–4
✓ Optimize operating temperature

MONTH 2
○ Install heat recovery

MONTH 3
○ Measure new emissions
```

Each task can display:

```text
Impact: High
Cost: Low
Owner: Operations
```

---

# 23. Action Priority Matrix

Recommended visualization:

```text
                  HIGH IMPACT
                      ↑
                      │
        DO NOW        │      PLAN
                      │
──────────────────────┼──────────────────
                      │
        QUICK WIN     │      DEFER
                      │
                      ↓
                  LOW IMPACT

     LOW COST  ──────────────→ HIGH COST
```

Plot recommendations as bubbles.

---

# 24. Circularity Score

Introduce one product-level metric:

## Circularity Score

```text
82 / 100

████████████████░░░░

Material reuse      91
Waste recovery      76
Process efficiency  84
Resource loop       77
```

The score must have a transparent calculation rather than being arbitrary.

---

# 25. Emissions Visualization Colors

Use semantic colors rather than random chart colors.

```text
High emissions       #D9534F
Medium emissions     #D79520
Low emissions        #20A67A
Neutral              #94A59F
```

Example:

```text
Furnace       █████████████████ 🔴

Electricity   ███████████       🟠

Materials     ████████          🟡

Waste         ████              🟢
```

Do not use ten unrelated colors.

---

# 26. Dashboard Cards

Recommended:

```text
12–16px radius
1px border
small shadow or no shadow
24px internal padding
```

Avoid:

- Huge shadows
- Glassmorphism everywhere
- Gradient cards everywhere
- Excessively rounded 30px cards

The product should feel **industrial and credible**, not like a consumer wellness app.

---

# 27. Iconography

Use one icon system consistently.

Recommended:

**Lucide Icons**

Examples:

```text
Factory
Zap
Recycle
Flame
TrendingDown
CircleDollarSign
Leaf
Gauge
Settings
FileText
```

Avoid mixing multiple icon systems throughout the interface.

Emojis can be used sparingly in demo callouts, but not as the main icon system.

---

# 28. Microinteractions

Small animations can significantly improve the hackathon demo.

### Analysis

```text
Scanning processes...
↓
Calculating emissions...
↓
Finding hotspots...
↓
Generating recommendations...
```

### Simulation

Animate KPI numbers as inputs change:

```text
124.6
   ↓
118.2
   ↓
107.4
   ↓
91.2
```

### Recommendation selection

Subtle card expansion.

### Task completion

```text
○ → ✓
```

Keep animations around **150–300ms**.

---

# 29. Empty States

Example:

```text
No assessment available.

Run your first assessment to identify
your factory's emission hotspots.

[ Start Assessment ]
```

---

# 30. Loading State

Don't use only:

> Loading...

Use meaningful progress:

```text
ANALYZING YOUR FACTORY

✓ Reading process data
✓ Calculating energy emissions
● Detecting hotspots
○ Ranking interventions
○ Preparing action plan
```

---

# 31. Error Handling

Errors should be actionable.

Bad:

> Error 500.

Good:

> We couldn't calculate emissions because fuel quantity is missing.

```text
[ Add Fuel Data ]
```

---

# 32. Mobile UX

Don't shrink the entire desktop dashboard into mobile.

Prioritize:

```text
Total CO₂
↓
Top hotspot
↓
Top recommendation
↓
Simulation
↓
Action plan
```

Example:

```text
┌──────────────────────┐
│ Total CO₂            │
│                      │
│ 124.6 tCO₂e          │
│ ↓ 8.4%               │
└──────────────────────┘

┌──────────────────────┐
│ 🔴 Top Hotspot       │
│ Furnace              │
│ 42%                  │
│                      │
│ [ Investigate ]      │
└──────────────────────┘
```

---

# 33. Accessibility

Use:

- Minimum 4.5:1 text contrast
- Don't use color alone to convey severity
- Keyboard-accessible controls
- Visible focus state
- Labels on charts
- Tooltips for technical metrics
- Units everywhere

Avoid displaying:

```text
42
```

Prefer:

```text
42 tCO₂e / month
```

---

# 34. Visual Branding

## Logo concept

Avoid an obvious leaf.

Combine:

**Circular arrow + industrial process node**

Concept:

```text
      ↻
   ●────●
   │    │
   ●────●
```

or a circular loop surrounding a subtle factory/process symbol.

### Brand name

**CircularCarbon AI**

Keep “AI” secondary rather than making it the entire identity.

---

# 35. Dashboard Background

Use a subtle light background:

```text
#F7F9F7
```

with white cards.

Structure:

```text
background
   ↓
white card
   ↓
content
```

For dark dashboard mode:

```text
#0B1513
```

with slightly lighter surfaces.

---

# 36. Signature Visual — Carbon Flow

One design element that should become part of the product's visual identity:

```text
INPUTS
   │
   ├── Energy
   ├── Materials
   └── Waste
          ↓
      PROCESS
          ↓
   ┌───────────────┐
   │ CARBON OUTPUT │
   └───────────────┘
          ↓
       HOTSPOTS
          ↓
   CIRCULAR ACTIONS
          ↓
       SAVINGS
```

This can appear across onboarding, dashboards and reports.

---

# 37. Main Dashboard Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ CircularCarbon                         ABC Manufacturing ▼   │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│ Overview      │  Good evening, ABC Manufacturing             │
│ Assessment    │  September 2026                              │
│ Hotspots      │                                              │
│ Recommendations ─────────────────────────────────────────── │
│ Simulator     │                                              │
│ Action Plan   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│ Reports       │  │124.6 t │ │12.4 kg │ │Furnace │ │₹4.2L │ │
│               │  │ CO₂    │ │ /unit  │ │ 42%    │ │save  │ │
│ ────────────  │  └────────┘ └────────┘ └────────┘ └──────┘ │
│ Factory       │                                              │
│ Settings      │  ┌─────────────────────┐ ┌────────────────┐ │
│               │  │ EMISSION HOTSPOTS   │ │ TOP ACTION     │ │
│               │  │                     │ │                │ │
│               │  │ Furnace       42%   │ │ Recover heat   │ │
│               │  │ Electricity   26%   │ │                │ │
│               │  │ Materials     19%   │ │ CO₂ ↓ 14.2t    │ │
│               │  │ Waste          9%   │ │ Payback 8mo    │ │
│               │  └─────────────────────┘ └────────────────┘ │
│               │                                              │
│               │  ┌─────────────────────────────────────────┐ │
│               │  │        WHAT-IF SIMULATION                │ │
│               │  │                                         │ │
│               │  │  Recycled material  10% ─────●── 40%  │ │
│               │  │                                         │ │
│               │  │  CO₂ 124.6 → 94.2 tCO₂e               │ │
│               │  └─────────────────────────────────────────┘ │
└───────────────┴──────────────────────────────────────────────┘
```

---

# 38. User Flow to Design Around

The entire website should revolve around:

```text
LANDING
   ↓
START ASSESSMENT
   ↓
FACTORY SETUP
   ↓
DATA INPUT
   ↓
ANALYSIS
   ↓
CARBON DASHBOARD
   ↓
HOTSPOT
   ↓
RECOMMENDATION
   ↓
WHAT-IF
   ↓
ACTION PLAN
   ↓
REPORT
```

A user should be able to complete this journey in **under 5 minutes for a demo**.

---

# 39. Most Important UX Principle

Don't make the user think like a sustainability expert.

Instead of:

> “Enter Scope 1 and Scope 2 emissions.”

Ask:

> **“How much natural gas does your factory use each month?”**

Then calculate the technical metric in the background.

Instead of:

> “Enter waste diversion rate.”

Ask:

> **“What happens to your production waste?”**

```text
○ Reused
○ Recycled
○ Sold
○ Landfilled
○ Other
```

This is a much better SME experience.

---

# 40. Hackathon Visual Priority

Spend most design effort on these four screens:

### 1. Carbon Dashboard

Should look immediately impressive.

### 2. Hotspot Investigation

Should make the problem obvious.

### 3. Recommendation

Should communicate **CO₂ + money + feasibility**.

### 4. What-If Simulator

Should have the strongest interaction and animation.

Everything else can be simpler.

---

# 41. Final Design System

### Brand

**CircularCarbon AI**

### Personality

```text
Technical
Credible
Action-oriented
Modern
Sustainable
Industrial
```

### Colors

```text
Primary       #126B5A
Dark          #0B4A3F
Secondary     #20A67A
Mint          #A7E8D0
Background    #F7F9F7
Text          #17211F
Muted         #66736F
Border        #DCE4E0
Success       #16865B
Warning       #D79520
Danger        #D9534F
Info          #3D73C9
```

### Font

**Inter**

### Icon set

**Lucide**

### UI style

**Clean analytics + industrial climate-tech**

### Core UX narrative

> **Measure → Find → Understand → Simulate → Act**

### Signature feature

> **Interactive Carbon Flow + What-If Simulator**

---

# 42. Recommended Frontend Structure

```text
src/
├── components/
│   ├── ui/
│   ├── dashboard/
│   ├── hotspots/
│   ├── recommendations/
│   ├── simulator/
│   └── action-plan/
│
├── pages/
│   ├── Landing.tsx
│   ├── Onboarding.tsx
│   ├── Dashboard.tsx
│   ├── Hotspots.tsx
│   ├── Recommendations.tsx
│   ├── Simulator.tsx
│   ├── ActionPlan.tsx
│   └── Reports.tsx
│
├── data/
│   ├── emissionFactors.ts
│   └── recommendations.ts
│
├── lib/
│   ├── calculations.ts
│   ├── scoring.ts
│   └── simulation.ts
│
└── styles/
    └── globals.css
```

Recommended reusable components:

```text
<MetricCard />
<HotspotCard />
<RecommendationCard />
<SimulationResult />
```

---

# 43. Key Design Decision

Make **green represent opportunity**, not merely “environment.”

The most important visual transition in the product should be:

**🔴 “This is where you're losing carbon efficiency.”**

→

**🟢 “This is what you can do about it.”**

→

**📉 “This is exactly how much CO₂ and money you could save.”**

This gives the UI a clear story and makes the product much more compelling in a hackathon demo.
