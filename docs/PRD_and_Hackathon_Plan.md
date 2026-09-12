# PRD — Industrial Emission Leak-Point Detector & Circular Alternative Recommender

## 1. Product Overview

**Product Name:** CircularCarbon AI  
**Theme:** Circular Carbon Ecosystem

### Problem

Small and medium-sized industries often know their total energy/material consumption but cannot easily answer:

> **“Where exactly is our carbon footprint coming from, and what should we change first?”**

Existing carbon accounting can tell a company its emissions, but usually does not turn those numbers into **specific, cost-conscious actions**.

This product converts operational/process data into:

**Process Data → Emission Sources → Hotspots → Circular Alternatives → Cost & CO₂ Savings → Action Plan**

### Product Vision

Build an easy-to-use decision-support platform that allows an SME to enter basic factory/process data and receive an explainable, prioritized plan for reducing emissions through circular interventions.

---

# 2. Goals

### Primary Goals

1. Identify the major sources of CO₂ emissions in an industrial process.
2. Break emissions down into understandable categories.
3. Identify the highest-impact **leak points/hotspots**.
4. Recommend circular interventions for those hotspots.
5. Estimate:
   - Current emissions
   - Potential CO₂ reduction
   - Estimated implementation cost
   - Potential operating savings
   - Payback period
6. Rank recommendations according to **impact vs. cost**.
7. Give SMEs a practical action plan instead of just a carbon number.

### Secondary Goals

- Make results understandable to non-experts.
- Provide explainable recommendations.
- Allow comparison of multiple intervention scenarios.
- Store historical assessments so companies can track improvement.

---

# 3. Non-Goals for the Hackathon MVP

Avoid making the first version excessively ambitious.

The MVP does **not** need:

- Real-time IoT sensor integration
- Automatic factory inspection using cameras
- Full regulatory compliance certification
- Perfect carbon accounting for every industry
- Digital twin simulation
- Fully autonomous AI decisions
- Integration with every ERP/MES system

These can become future extensions.

---

# 4. Target Users

### Primary User — SME Factory Operator

Needs to quickly understand:

> “Which process should I fix first?”

### Secondary User — Sustainability Consultant

Needs:

> “A data-driven assessment and recommendation report for my client.”

### Secondary User — Sustainability/Operations Manager

Needs:

> “How much CO₂ and money can we save by changing this process?”

### Secondary User — Regulator

Needs:

> “Can an organization demonstrate where its emissions originate and what mitigation actions it is taking?”

---

# 5. Core User Journey

```text
           START
             │
             ▼
      Create Factory Profile
             │
             ▼
    Enter Process Information
             │
             ├── Energy
             ├── Materials
             ├── Waste
             ├── Production
             └── Transport (optional)
             │
             ▼
       Calculate Emissions
             │
             ▼
      Detect Emission Hotspots
             │
             ▼
       AI Recommendation Engine
             │
             ▼
   ┌─────────────────────────┐
   │ Circular Alternatives   │
   │ • Material substitution │
   │ • Recycling             │
   │ • Reuse                 │
   │ • Process optimization  │
   │ • Energy switching      │
   └─────────────────────────┘
             │
             ▼
     Cost + CO₂ Simulation
             │
             ▼
      Prioritized Actions
             │
             ▼
        Action Plan
```

---

# 6. Functional Requirements

## FR-01 — Factory Profile

The user should be able to create a factory/project.

### Inputs

```text
Factory Name
Industry
Location
Production Type
Production Volume
Assessment Period
```

Example:

```text
Factory: ABC Manufacturing
Industry: Metal Components
Production: 10,000 units/month
Assessment: Monthly
```

---

# 7. FR-02 — Process Data Input

The system should support a simple form for operational data.

### Energy

```text
Electricity consumed
Natural gas
Diesel
Coal
Other fuels
Renewable electricity
```

### Materials

```text
Raw material
Quantity
Material type
Virgin / recycled
Source
```

### Waste

```text
Waste type
Quantity
Current disposal method
Recycled quantity
Landfilled quantity
Reused quantity
```

### Optional

```text
Transportation
Packaging
Water consumption
Process-specific chemicals
```

For the hackathon, don't make every field mandatory.

Use a **progressive form**:

> Basic information → advanced information

---

# 8. FR-03 — Emission Calculation Engine

The application should convert activity data into estimated emissions.

Conceptually:

```text
Emission = Activity × Emission Factor
```

For example:

```text
Electricity emissions
= electricity consumption × electricity emission factor
```

And:

```text
Fuel emissions
= fuel quantity × fuel emission factor
```

Then:

```text
Total CO₂e
=
Energy emissions
+ Material emissions
+ Waste emissions
+ Transport emissions
```

The exact methodology and emission-factor dataset should be clearly shown in the application so the user understands where estimates originate.

---

# 9. FR-04 — Emission Hotspot Detection

This is one of the most important features.

The system should identify the processes responsible for the largest share of emissions.

Example:

| Source | CO₂e | Contribution |
|---|---:|---:|
| Furnace | 18.2 t | 42% |
| Electricity | 11.3 t | 26% |
| Raw Materials | 8.4 t | 19% |
| Waste | 3.8 t | 9% |
| Transport | 1.7 t | 4% |

The system then labels:

```text
🔥 HIGH IMPACT
Furnace

⚠ MEDIUM IMPACT
Electricity

✓ LOW IMPACT
Transport
```

### Visualization

Use:

- Donut chart
- Horizontal bar chart
- Process flow
- Heatmap
- Emission waterfall

---

# 10. FR-05 — Emission Leak-Point Detection

The term **“leak point”** should not imply a physical gas leak.

In this product, it means:

> **A process step where excessive carbon emissions, material loss, energy inefficiency, or waste generation occurs.**

For example:

```text
Raw Material
     ↓
Cutting ──────→ 18% material waste 🔴
     ↓
Machining ────→ high electricity usage 🟠
     ↓
Finishing
     ↓
Product
```

The system can identify:

### Leak Point #1

**Cutting process**

```text
Material loss: 18%
Estimated CO₂ impact: 7.8 tCO₂e/month
```

Then recommend:

> Optimize cutting pattern + reuse scrap material.

---

# 11. FR-06 — Circular Alternative Recommendation Engine

This is the **AI differentiator**.

The system should map:

```text
Emission Hotspot
       ↓
Cause
       ↓
Circular Strategy
       ↓
Recommended Intervention
```

### Circular Strategy Categories

#### 1. Reduce

Reduce energy/material consumption.

#### 2. Reuse

Reuse process outputs or waste.

#### 3. Recycle

Create internal or external recycling loops.

#### 4. Substitute

Replace carbon-intensive materials/processes.

#### 5. Recover

Recover heat, materials, or energy.

#### 6. Process Optimization

Modify manufacturing processes.

---

# 12. Recommendation Example

Suppose the system detects:

```text
Hotspot:
High virgin aluminum consumption

Impact:
12.4 tCO₂e/month
```

Possible recommendations:

### Recommendation A

**Use recycled aluminum**

```text
Estimated CO₂ reduction: 35%
Implementation cost: Medium
Operational saving: ₹XX/month
Payback: X months
```

### Recommendation B

**Recover and reuse internal aluminum scrap**

```text
Estimated CO₂ reduction: 18%
Implementation cost: Low
Operational saving: ₹XX/month
Payback: X months
```

### Recommendation C

**Optimize cutting layout**

```text
Estimated CO₂ reduction: 8%
Implementation cost: Low
Operational saving: ₹XX/month
Payback: X months
```

Then rank them.

---

# 13. Recommendation Scoring

Instead of blindly asking an LLM:

> “Give me sustainability recommendations.”

Create a **hybrid recommendation system**.

### Score

```text
Recommendation Score =
Impact Score
+ Cost Score
+ Feasibility Score
+ Circularity Score
+ Payback Score
```

For example:

```text
Impact          35%
Cost            20%
Feasibility     20%
Circularity     15%
Payback         10%
```

Result:

| Intervention | CO₂ Reduction | Cost | Payback | Score |
|---|---:|---|---:|---:|
| Scrap reuse | 18% | Low | 4 months | 91 |
| Recycled material | 35% | Medium | 11 months | 88 |
| New equipment | 45% | High | 29 months | 64 |

This makes the recommendation engine much more defensible.

---

# 14. FR-07 — What-If Simulator

This can be one of the strongest hackathon features.

Allow the user to change assumptions.

Example:

```text
Current recycled material: 10%

                    ↓ Slider

Proposed recycled material: 40%
```

The dashboard immediately shows:

```text
CO₂ emissions

Before: 120 t/month
After:   87 t/month

Reduction: 33 t/month
           ↓
        -27.5%
```

Also:

```text
Estimated annual saving: ₹4.2L
Implementation cost: ₹2.1L
Payback: 6 months
```

This transforms the product from a **calculator into a decision-making tool**.

---

# 15. FR-08 — Prioritized Action Plan

Rather than giving users 20 recommendations, give them:

### Now

Low-cost/high-impact actions.

### Next

Medium-investment actions.

### Later

Large capital projects.

Example:

```text
PHASE 1 — 0–3 MONTHS
✓ Optimize material cutting
✓ Segregate production scrap
✓ Reduce idle energy consumption

PHASE 2 — 3–12 MONTHS
→ Increase recycled material usage
→ Recover process heat

PHASE 3 — 12+ MONTHS
→ Replace furnace technology
→ Introduce renewable electricity
```

---

# 16. FR-09 — Dashboard

The main dashboard should answer five questions immediately:

### 1. How much am I emitting?

```text
124.6 tCO₂e/month
```

### 2. Where does it come from?

```text
Furnace       42%
Electricity   26%
Materials     19%
Waste          9%
Transport      4%
```

### 3. What is my biggest problem?

```text
🔥 Furnace
```

### 4. What should I change?

```text
Switch fuel
Recover heat
Optimize operating temperature
```

### 5. How much can I save?

```text
Potential CO₂ reduction
31.8 t/month

Potential annual saving
₹X.X lakh
```

---

# 17. FR-10 — Explainable AI

Every recommendation should answer:

> **“Why did the system recommend this?”**

Example:

```text
WHY THIS RECOMMENDATION?

Your furnace contributes 42% of total emissions.

We detected:
• High fuel consumption
• Low heat recovery
• High operating hours

Therefore:
Heat recovery is predicted to offer
the highest CO₂ reduction per ₹ invested.
```

This is much better than an unexplained AI recommendation.

---

# 18. FR-11 — Reports

Generate a downloadable report containing:

```text
Factory information
↓
Current emissions
↓
Emission breakdown
↓
Top 5 hotspots
↓
Recommended interventions
↓
Cost estimates
↓
CO₂ reduction estimates
↓
Implementation roadmap
```

A PDF export would be a strong hackathon demo feature.

---

# 19. AI Architecture

Don't make the LLM responsible for the actual carbon calculation.

Use:

### Deterministic Engine

For:

- emission calculations
- savings calculations
- scoring
- ranking

### AI/LLM Layer

For:

- interpreting process information
- explaining hotspots
- generating human-readable recommendations
- adapting recommendations to the industry
- creating the action plan

Architecture:

```text
                 USER DATA
                     │
                     ▼
             Data Validation
                     │
                     ▼
          ┌──────────────────┐
          │ Carbon Calculator │
          └──────────────────┘
                     │
                     ▼
             Hotspot Detector
                     │
                     ▼
           Recommendation DB
                     │
             ┌───────┴───────┐
             ▼               ▼
       Rule Engine         AI/LLM
             │               │
             └───────┬───────┘
                     ▼
             Recommendation
                     │
                     ▼
              Cost Simulator
                     │
                     ▼
                 Dashboard
```

---

# 20. Recommended Technical Stack

Since the problem statement itself suggests Python + React:

### Frontend

```text
React
TypeScript
Tailwind CSS
Recharts / D3.js
```

### Backend

```text
Python
FastAPI
Pydantic
Pandas
NumPy
```

### AI

For the hackathon:

```text
LLM API
+
rule-based recommendation engine
```

Potential ML later:

```text
XGBoost
Scikit-learn
LightGBM
```

### Database

```text
PostgreSQL
```

For a very quick MVP:

```text
Supabase
```

### Deployment

```text
Frontend → Vercel
Backend → Render/Railway
Database → Supabase
```

---

# 21. Database Design

### `factories`

```text
id
name
industry
location
production_volume
created_at
```

### `processes`

```text
id
factory_id
name
process_type
production_volume
```

### `energy_consumption`

```text
id
process_id
energy_type
quantity
unit
period
```

### `materials`

```text
id
process_id
material_name
quantity
unit
recycled_percentage
```

### `waste`

```text
id
process_id
waste_type
quantity
disposal_method
```

### `emission_results`

```text
id
process_id
category
activity
emission_factor
co2e
period
```

### `recommendations`

```text
id
hotspot_id
title
description
strategy
estimated_cost
co2_reduction
payback_period
score
```

---

# 22. API Design

### Create factory

```http
POST /api/factories
```

### Add process

```http
POST /api/processes
```

### Add energy data

```http
POST /api/energy
```

### Calculate emissions

```http
POST /api/emissions/calculate
```

### Detect hotspots

```http
GET /api/emissions/hotspots/{factory_id}
```

### Generate recommendations

```http
POST /api/recommendations/generate
```

### Simulate intervention

```http
POST /api/simulation
```

### Generate report

```http
GET /api/reports/{factory_id}
```

---

# 23. MVP Scope

For a hackathon, I would **strongly limit the initial scope**.

### Support only 2–3 industries.

For example:

```text
Metal Manufacturing
Textile Manufacturing
Food Processing
```

Why?

Because trying to support every industry will make your recommendation engine shallow.

### MVP input

```text
Industry
Production
Electricity
Fuel
Raw materials
Waste
```

### MVP output

```text
Total CO₂
Emission breakdown
Top 3 hotspots
Top 5 recommendations
Cost
CO₂ saving
Payback
Action plan
```

### MVP killer feature

**What-if simulator**

---

# 24. Suggested UI

## Screen 1 — Landing Page

```text
────────────────────────────────────

        CIRCULAR CARBON AI

Find where your factory
is losing carbon efficiency.

        [ Start Assessment ]

────────────────────────────────────
```

---

## Screen 2 — Factory Setup

```text
Factory Name       [____________]

Industry           [Manufacturing ▼]

Production/month   [____________]

          [ Continue → ]
```

---

# 25. Screen 4 — Carbon Dashboard

```text
┌─────────────────────────────────────┐
│ TOTAL EMISSIONS                     │
│                                     │
│ 124.6 tCO₂e / month                 │
│                                     │
│ Potential reduction                 │
│ 31.8 tCO₂e / month                  │
└─────────────────────────────────────┘


EMISSION SOURCES

Furnace       █████████████████ 42%
Electricity   ███████████       26%
Materials     ████████          19%
Waste         ████               9%
Transport     ██                 4%


🔥 TOP LEAK POINT

FURNACE

42% of total emissions
```

---

# 26. Screen 5 — Recommendations

```text
TOP RECOMMENDATIONS

┌─────────────────────────────────────┐
│ 01  RECOVER WASTE HEAT              │
│                                     │
│ CO₂ reduction     14.2 t/month      │
│ Cost              Medium            │
│ Payback           8 months          │
│                                     │
│ [ View Details ]                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 02  REUSE PRODUCTION SCRAP          │
│                                     │
│ CO₂ reduction      7.8 t/month      │
│ Cost              Low               │
│ Payback           3 months           │
│                                     │
│ [ View Details ]                    │
└─────────────────────────────────────┘
```

---

# 27. Screen 6 — What-If Simulator

This should be visually impressive during the hackathon.

```text
INCREASE RECYCLED MATERIAL

Current          ███░░░░░░  20%
Proposed         ███████░░  60%


          CURRENT       NEW

CO₂        124.6        94.2 t
Cost       ₹0           ₹X

Reduction               ↓24.4%
Annual saving           ₹X.X L
```

The user moves the slider and the graphs update instantly.

---

# 28. Screen 7 — Action Plan

```text
YOUR 90-DAY CARBON PLAN

WEEK 1–2
✓ Waste segregation

WEEK 3–4
✓ Process optimization

MONTH 2
→ Increase recycled material

MONTH 3
→ Install heat recovery system


EXPECTED RESULT

CO₂ ↓ 25%
Operating Cost ↓ 11%
```

---

# 29. Hackathon Development Plan

Assuming a **24–48 hour hackathon**, divide the work into four phases.

## Phase 1 — Foundation

### Hours 0–4

Build:

```text
Project architecture
React frontend
FastAPI backend
Database
Basic UI
```

At the same time, define the supported industry/process model.

### Deliverable

User can create a factory and enter data.

---

# 30. Phase 2 — Carbon Engine

### Hours 4–10

Implement:

```text
Emission-factor dataset
Emission calculations
Category aggregation
Hotspot calculation
CO₂ breakdown
```

Create a deterministic pipeline:

```python
activity
→ emission factor
→ emissions
→ process total
→ factory total
→ percentage contribution
```

### Deliverable

Dashboard showing accurate and explainable emission estimates.

---

# 31. Phase 3 — Recommendation Engine

### Hours 10–18

Create a curated recommendation knowledge base.

Example:

```json
{
  "hotspot": "high_material_waste",
  "interventions": [
    {
      "name": "Scrap Reuse",
      "cost": "low",
      "impact": "high",
      "circularity": 5
    }
  ]
}
```

Then build the ranking engine.

After ranking, use the LLM to generate the explanation:

```text
Why?
What should be done?
Expected benefit?
What assumptions were made?
```

### Deliverable

User gets personalized recommendations instead of generic sustainability advice.

---

# 32. Phase 4 — What-If Simulator + Polish

### Hours 18–28

Build the feature that will probably have the highest demo value:

```text
Slider/Input
       ↓
Recalculate
       ↓
CO₂ reduction
       ↓
Cost
       ↓
Payback
       ↓
Updated recommendation
```

Then polish:

```text
Charts
animations
responsive UI
loading states
error handling
report generation
```

---

# 33. Phase 5 — Demo Preparation

### Final 4–6 hours

Do **not** spend this time adding random features.

Use it for:

```text
Seed realistic demo data
Fix UI bugs
Improve graphs
Test calculations
Prepare presentation
Prepare fallback data
Practice demo
```

A reliable product with 5 strong features will beat a broken product with 20 features.

---

# 34. Team Structure

For a 4-person team:

### Person 1 — Frontend

```text
React
Dashboard
Charts
Forms
Simulator
```

### Person 2 — Backend

```text
FastAPI
Database
APIs
Validation
```

### Person 3 — AI/Carbon Engine

```text
Emission calculations
Emission factors
Hotspot detection
Recommendation engine
LLM integration
```

### Person 4 — Product/Integration

```text
Database seed data
Testing
Report generation
UI integration
Pitch
Demo flow
```

For a 3-person team, combine Person 2 + Person 4.

---

# 35. Recommendation Engine — Important Design Decision

I would **not** make this:

```text
User data → LLM → recommendations
```

That introduces too much unpredictability.

Instead:

```text
User Data
    ↓
Carbon Calculation
    ↓
Hotspot Detection
    ↓
Rule/Knowledge Base
    ↓
Candidate Recommendations
    ↓
Scoring
    ↓
Top 3–5
    ↓
LLM explanation
```

This gives you both:

**Reliability + AI**

which is much stronger for a hackathon judge.

---

# 36. Example End-to-End Demo

Your demo could use a fictional textile factory.

### Input

```text
Production:
100,000 garments/month

Electricity:
70,000 kWh

Diesel:
4,000 L

Cotton:
20 tonnes

Recycled cotton:
10%

Textile waste:
3 tonnes

Recycled:
40%
```

### System discovers

```text
TOTAL:
~XXX tCO₂e/month

TOP HOTSPOTS

1. Electricity       37%
2. Virgin cotton     31%
3. Diesel            18%
4. Textile waste     9%
```

### AI recommends

```text
#1 Increase recycled cotton
CO₂ ↓ 22%
Cost: Medium

#2 Reuse textile cutting waste
CO₂ ↓ 11%
Cost: Low

#3 Improve machinery efficiency
CO₂ ↓ 8%
Cost: Medium
```

### User opens simulator

```text
Recycled cotton

10% ──────────────→ 50%

CO₂:
134 → 105 tCO₂e

Reduction:
21.6%

Annual saving:
₹X.X lakh

Payback:
7 months
```

Then the system generates:

> **Recommended priority: Increase recycled cotton from 10% to 50%, because it provides the largest emissions reduction with a moderate implementation cost.**

That is a strong 3–5 minute demo story.

---

# 37. Key Metrics / Success Criteria

### Product Metrics

```text
Emission calculation completion rate
Recommendation generation time
Number of actionable recommendations
```

### Impact Metrics

```text
Potential CO₂ reduction
Potential cost reduction
Average payback period
Percentage of waste diverted from disposal
```

### Technical

```text
API response < 2 sec
Dashboard loads < 3 sec
Recommendation generation < 10 sec
```

---

# 38. Risks

### Risk 1 — Inaccurate emission factors

**Solution:** Store every factor with:

```text
Source
Unit
Version
Date
```

And clearly label outputs as estimates.

---

### Risk 2 — AI hallucination

**Solution:**

Never allow the LLM to invent:

```text
emission factors
costs
savings
technical specifications
```

Feed it verified values from your database and instruct it to explain only those values.

---

### Risk 3 — Too much user input

An SME won't want to fill a 50-field environmental form.

Use:

```text
Quick Assessment
        ↓
Detailed Assessment
```

---

### Risk 4 — Generic recommendations

Avoid:

> “Use renewable energy.”

Instead:

> “Electricity contributes 26% of your emissions. Based on your consumption profile, reducing electricity demand by X% would reduce approximately Y tCO₂e/month.”

Specificity makes the product feel intelligent.

---

# 39. Future Roadmap

### V2

```text
IoT sensor integration
Live emissions monitoring
Supplier carbon data
ERP integration
Automated data import
```

### V3

```text
Predictive optimization
Digital twin
Computer vision for waste detection
Supply-chain carbon analysis
Industry benchmarking
```

### V4

```text
Carbon marketplace
Circular material exchange
Supplier matching
Carbon-credit integration
```

The long-term vision can become:

> **Not just “Where are my emissions?” but “What circular action should I take next?”**

---

# 40. Final Product Architecture

```text
                    ┌───────────────────┐
                    │      React        │
                    │     Frontend      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      FastAPI      │
                    │       API         │
                    └─────────┬─────────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
       ┌─────────────┐ ┌────────────┐ ┌─────────────┐
       │   Carbon    │ │ Hotspot    │ │Recommendation│
       │   Engine    │ │  Engine    │ │    Engine    │
       └──────┬──────┘ └─────┬──────┘ └──────┬──────┘
              │              │               │
              └──────────────┼───────────────┘
                             ▼
                    ┌─────────────────┐
                    │   AI / LLM      │
                    │ Explanation     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ What-if Engine  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

# 41. What I Would Prioritize for the Hackathon

Build the project around **three standout capabilities** rather than trying to implement everything:

### 1. 🔥 Emission Leak-Point Map

Show exactly **which process is responsible for the emissions** and why.

### 2. 🤖 Circular Recommendation Engine

Turn the hotspot into **specific, ranked, cost-aware interventions**.

### 3. 📊 What-If Simulator

Let the judge change a parameter and immediately see:

**CO₂ ↓ + Cost ↓ + Payback ↓**

That third feature gives you a very strong live demonstration because the result changes in front of the judges.

---

## One-line pitch

> **“CircularCarbon AI helps SMEs find exactly where their emissions originate and tells them which circular intervention will reduce the most CO₂ for the least cost.”**

## 48-hour MVP target

```text
                    ┌───────────────────────────┐
                    │   FACTORY DATA INPUT      │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │   CARBON CALCULATION       │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │  TOP 3 EMISSION HOTSPOTS   │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │ AI CIRCULAR RECOMMENDATIONS│
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │ COST / CO₂ / PAYBACK       │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │    WHAT-IF SIMULATOR       │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │     90-DAY ACTION PLAN     │
                    └───────────────────────────┘
```

## Final Product Strategy

The real differentiator should not be the carbon calculator—**that part is relatively straightforward**. The competitive advantage is the chain:

**hotspot detection → circular intervention → quantified impact → interactive what-if decision**

That is what to optimize the hackathon build around.
