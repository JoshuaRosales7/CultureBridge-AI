# Demo Script — 2 Minutes

## Pre-Demo Checklist

- [ ] Frontend running at http://localhost:3000 (or deployed URL)
- [ ] API running at http://localhost:8000 (or deployed URL)
- [ ] Azure OpenAI endpoint configured and accessible
- [ ] Application Insights portal open in a separate tab
- [ ] Screen recording software ready (OBS, Loom, or similar)
- [ ] Browser zoom at 110% for readability
- [ ] Clear browser cache for clean demo state

---

## Storyboard

### Act 1: The Problem (0:00 – 0:20)

**Script:**
> "When an e-commerce brand expands internationally, they face a hidden conversion killer: cultural behavioral mismatch. The same checkout flow that works in one market fails in another — not because of language, but because of different trust patterns, decision flows, and communication styles.
>
> CultureBridge AI solves this using multi-agent AI to generate region-adapted storefront variants."

**Screen Actions:**
1. Show the CultureBridge AI landing page
2. Briefly highlight the "same product, three regions" concept

---

### Act 2: Live Demo (0:20 – 1:10)

**Script:**
> "Let's adapt an electronics product for three markets: Japan, Guatemala, and Germany."

**Screen Actions:**

1. **[0:20–0:30]** Select product category: "Electronics", price band: "Mid", audience: "General Consumer"
2. **[0:30–0:40]** Click "Generate Variants" — show loading state with agent pipeline visualization
3. **[0:40–0:55]** Show the **side-by-side comparison**:
   - **Japan variant**: Point out enhanced trust modules, structured multi-step flow, community reviews placement, consensus-oriented CTAs
   - **Guatemala variant**: Point out streamlined checkout (fewer steps), installment payment options, value framing, mobile-optimized flow
   - **Germany variant**: Point out detailed specifications upfront, explicit pricing breakdown, institutional trust badges, precise technical copy
4. **[0:55–1:10]** Click on one variant to expand details:
   - Show the adapted flow diagram
   - Highlight specific copy changes with rationale tooltips
   - Show the cultural dimension scores that drove the adaptation

---

### Act 3: Compliance & Audit (1:10 – 1:35)

**Script:**
> "Every variant is automatically audited by our Compliance & Bias Auditor agent."

**Screen Actions:**

1. **[1:10–1:20]** Navigate to the Audit tab — show the audit score (e.g., 87/100)
2. **[1:20–1:25]** Show risk flags:
   - Example: "Medium risk: Social proof emphasis for JP variant may over-index on conformity pressure"
   - Each flag shows the affected element and recommended change
3. **[1:25–1:35]** Demonstrate **dimension override**: adjust Japan's "collectivism" slider down → click "Regenerate" → show the variant updates in real-time

---

### Act 4: Azure + Observability (1:35 – 1:55)

**Script:**
> "Everything runs on Azure with full observability."

**Screen Actions:**

1. **[1:35–1:45]** Switch to Azure Portal / Application Insights tab
   - Show the trace for the request we just made
   - Highlight the correlation ID linking frontend → API → each agent call
2. **[1:45–1:55]** Quick flash of:
   - Architecture diagram showing Azure services
   - Key Vault integration (no hardcoded secrets)
   - GitHub Actions CI/CD pipeline

---

### Act 5: Close (1:55 – 2:00)

**Script:**
> "CultureBridge AI: culturally intelligent e-commerce adaptation powered by Microsoft Agent Framework and Azure AI Foundry. Our multi-agent system delivers an average predicted lift of 25-35% in conversion rate — with full transparency, compliance auditing, and responsible AI built in."

**Screen Action:**
- Show the predicted lift summary for all three variants
- Quick zoom on "Predicted – Transparent Assumptions" disclosure

---

## Recording Tips

1. **Resolution**: Record at 1920x1080 minimum
2. **Narration**: Use clear, measured pace — practice 2-3 times before recording
3. **Transitions**: Use smooth scroll, avoid abrupt jumps
4. **Fallback**: If Azure OpenAI is slow, pre-generate variants and have them cached
5. **Time management**: Acts 2 and 3 are the core — prioritize those if running short

## Post-Production

1. Add title card: "CultureBridge AI — Cultural Behavior Adaptation for Global E-Commerce"
2. Add team name card at the end
3. Keep total runtime ≤ 2:00
4. Export as MP4, 1080p, ≤ 100MB
