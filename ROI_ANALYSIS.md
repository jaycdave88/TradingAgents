# TradingAgents: Model Evaluation & ROI Analysis

> **Last updated:** March 2026 | **Disclaimer:** This analysis is for informational and research purposes only. It is not financial, investment, or trading advice. Projected returns are estimates based on reasoning benchmark quality and assumed market edge — actual results will vary significantly based on market conditions, model behavior, data quality, and execution.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [LLM Call Budget Per Run](#llm-call-budget-per-run)
- [Supported Models & Pricing](#supported-models--pricing-march-2026)
- [Cloud Configuration Costs](#cloud-configuration-costs-per-run)
- [Model Quality Rankings](#model-quality-rankings)
- [Projected Signal Accuracy & Returns](#projected-signal-accuracy--returns)
- [ROI by Portfolio Size](#roi-by-portfolio-size)
- [Best Cloud Configuration](#best-cloud-configuration)
- [Local LLM Support](#local-llm-support-ollama)
- [Hybrid Strategy](#hybrid-strategy-local--cloud)
- [Recommendations Summary](#recommendations-summary)
- [Security Notes](#security-notes)

---

## Architecture Overview

TradingAgents decomposes trading analysis into specialized agent roles that collaborate through structured debate:

```
┌─────────────────────────────────┐
│  ANALYST TEAM (configurable)    │
│  Market → Social → News →      │
│  Fundamentals                   │
│  (Each uses tool-calling LLM)   │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  RESEARCH TEAM                  │
│  Bull Researcher ⟷ Bear        │
│  (Multi-round debate)           │
│  → Research Manager (judge)     │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  TRADER AGENT                   │
│  Creates investment plan        │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  RISK MANAGEMENT TEAM           │
│  Aggressive ⟷ Conservative ⟷   │
│  Neutral (multi-round debate)   │
│  → Portfolio Manager (judge)    │
└──────────────┬──────────────────┘
               ▼
  FINAL DECISION: Buy / Overweight / Hold / Underweight / Sell
```

Two LLM tiers are used throughout:
- **Quick-think LLM**: Analysts, researchers, trader, risk analysts, reflection, signal processing
- **Deep-think LLM**: Research Manager and Portfolio Manager (final decision-makers)

---

## LLM Call Budget Per Run

With default configuration (`max_debate_rounds: 1`, `max_risk_discuss_rounds: 1`, all 4 analysts enabled):

| Phase | Agent | Calls | LLM Tier |
|-------|-------|-------|----------|
| Analysts | Market Analyst | 2 | Quick |
| Analysts | Social Media Analyst | 2 | Quick |
| Analysts | News Analyst | 2 | Quick |
| Analysts | Fundamentals Analyst | 2 | Quick |
| Research Debate | Bull Researcher | 2 | Quick |
| Research Debate | Bear Researcher | 2 | Quick |
| Research Synthesis | Research Manager | 1 | **Deep** |
| Trading | Trader | 1 | Quick |
| Risk Debate | Aggressive Analyst | 3 | Quick |
| Risk Debate | Conservative Analyst | 3 | Quick |
| Risk Debate | Neutral Analyst | 3 | Quick |
| Risk Synthesis | Portfolio Manager | 1 | **Deep** |
| Post-Processing | Signal Processor | 1 | Quick |
| Reflection | 5 agent reflections | 5 | Quick |
| **Total** | | **30** | **28 Quick + 2 Deep** |

### Estimated Token Usage Per Run

| Component | Input Tokens | Output Tokens |
|-----------|-------------|---------------|
| Quick-think calls (28) | ~70,000 | ~28,000 |
| Deep-think calls (2) | ~13,000 | ~5,000 |
| **Total** | **~83,000** | **~33,000** |

---

## Supported Models & Pricing (March 2026)

### OpenAI

| Model | Input/1M | Output/1M | Cached Input/1M | Notes |
|-------|----------|-----------|-----------------|-------|
| GPT-5-nano | $0.05 | $0.40 | $0.005 | Budget, limited reasoning |
| GPT-5-mini | $0.25 | $2.00 | $0.025 | Good balance of speed and cost |
| GPT-5 | $1.25 | $10.00 | $0.125 | Strong general reasoning |
| GPT-5.2 | $1.75 | $14.00 | $0.175 | Frontier reasoning |
| GPT-5.4 | $2.50 | $15.00 | $1.25 | Latest frontier, 1M context |
| GPT-5.4-Pro | $30.00 | $180.00 | — | Maximum capability, very expensive |

### Anthropic Claude

| Model | Input/1M | Output/1M | Notes |
|-------|----------|-----------|-------|
| Haiku 4.5 | $1.00 | $5.00 | Fast, near-instant responses |
| Sonnet 4.6 | $3.00 | $15.00 | Best speed/intelligence balance |
| Opus 4.6 | $5.00 | $25.00 | Most capable, best tool-augmented reasoning |

### Google Gemini

| Model | Input/1M | Output/1M | Notes |
|-------|----------|-----------|-------|
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Ultra-budget |
| Gemini 2.5 Flash | $0.30 | $2.50 | Best budget option |
| Gemini 2.5 Pro | $1.25 | $10.00 | Strong reasoning, excellent value |
| Gemini 3.1 Pro (preview) | $2.00 | $12.00 | Highest pure reasoning benchmarks |

### xAI Grok

| Model | Input/1M | Output/1M | Notes |
|-------|----------|-----------|-------|
| Grok 4.1 Fast | $0.20 | $0.50 | Cheapest non-trivial model |
| Grok 4 | $3.00 | $15.00 | Frontier tier, low hallucination |

### Cost Optimization

All providers offer **Batch API** (50% discount) for non-real-time workloads. OpenAI and Google offer **prompt caching** (up to 90% savings on repeated prompts). Google has a **free tier** with up to 1,000 daily requests.

---

## Cloud Configuration Costs Per Run

| # | Configuration | Quick Model | Deep Model | Cost/Run | Daily (10 stocks) | Annual (252 days) |
|---|--------------|-------------|------------|----------|-------------------|-------------------|
| 1 | Ultra Budget | Gemini Flash-Lite | Gemini Flash | $0.02 | $0.18 | **$45** |
| 2 | Budget | Grok 4.1 Fast | Grok 4.1 Fast | $0.03 | $0.28 | **$70** |
| 3 | Budget+ | GPT-5-nano | GPT-5-mini | $0.02 | $0.16 | **$40** |
| 4 | **Value King** | Gemini 2.5 Flash | Gemini 2.5 Pro | $0.09 | $0.92 | **$232** |
| 5 | **Sweet Spot** | GPT-5-mini | GPT-5.2 | $0.13 | $1.30 | **$328** |
| 6 | Balanced | Grok 4.1 Fast | Grok 4 | $0.11 | $1.10 | **$277** |
| 7 | Quality | Haiku 4.5 | Sonnet 4.6 | $0.29 | $2.87 | **$724** |
| 8 | Premium | Sonnet 4.6 | Opus 4.6 | $0.67 | $6.72 | **$1,694** |
| 9 | Max Cloud | GPT-5.4 | GPT-5.4-Pro | $6.17 | $61.70 | **$15,549** |

---

## Model Quality Rankings

Based on March 2026 benchmarks (GPQA Diamond, SWE-bench Verified, ARC-AGI-2):

| Rank | Model | GPQA Diamond | SWE-bench | Tool Use | Trading Suitability |
|------|-------|-------------|-----------|----------|-------------------|
| 1 | GPT-5.4-Pro | ~95% | ~75% | Excellent | Overkill for most portfolios |
| 2 | GPT-5.4 | 92.8% | 74.9% | Excellent | Top tier |
| 3 | Gemini 3.1 Pro | 94.3% | 80.6% | Good | Best reasoning/price ratio |
| 4 | Claude Opus 4.6 | 91.3% | 80.8% | Best w/tools | Best tool-augmented reasoning |
| 5 | Grok 4 | ~90% | 75% | Good | Strong, low hallucination |
| 6 | GPT-5.2 | ~90% | 80% | Excellent | Best value frontier |
| 7 | Claude Sonnet 4.6 | ~87% | ~77% | Strong | Great balanced option |
| 8 | Gemini 2.5 Pro | ~86% | ~72% | Good | Best price/performance |
| 9 | GPT-5-mini | ~82% | ~65% | Good | Solid quick-think |
| 10 | Gemini 2.5 Flash | ~80% | ~60% | Good | Best budget option |
| 11 | Grok 4.1 Fast | ~78% | ~55% | OK | Cheapest viable |
| 12 | Haiku 4.5 | ~78% | ~55% | OK | Fast, decent |
| 13 | Qwen3 235B (local) | ~75% | ~50% | OK | Best local option |
| 14 | GPT-5-nano | ~72% | ~45% | Weak | Too weak for deep analysis |

### What Matters for TradingAgents

The multi-agent debate architecture **amplifies model quality differences**:

1. **Tool calling reliability** (analysts) — A model that botches tool calls breaks the entire pipeline. This is pass/fail.
2. **Reasoning depth** (debates) — Weak models repeat the same points. Strong models find new angles each round.
3. **Synthesis ability** (managers) — Final decision-makers must weigh contradictory arguments. Weak models default to "hold" or echo the last speaker.
4. **Risk assessment** (risk team) — Requires genuine reasoning about tail risks, correlations, and position sizing. Small models produce generic boilerplate.

---

## Projected Signal Accuracy & Returns

> **Important:** These are estimates based on reasoning benchmark quality mapped to assumed market edge. Actual trading results depend on market conditions, data quality, execution, and many other factors.

| Config | Configuration | Est. Accuracy | Market Edge | $100K Annual | $500K Annual |
|--------|--------------|--------------|-------------|-------------|-------------|
| 9 | Max Cloud (5.4-Pro) | 57-59% | ~8% | $8,000 | $40,000 |
| 8 | Premium (Opus+Sonnet) | 56-58% | ~7% | $7,000 | $35,000 |
| 5 | Sweet Spot (5-mini+5.2) | 55-57% | ~6% | $6,000 | $30,000 |
| 4 | Value King (Flash+Pro) | 54-56% | ~5% | $5,000 | $25,000 |
| 6 | Balanced (Grok mix) | 54-55% | ~4.5% | $4,500 | $22,500 |
| 7 | Quality (Haiku+Sonnet) | 53-55% | ~4% | $4,000 | $20,000 |
| 10 | Local (Qwen3 235B) | 51-53% | ~2% | $2,000 | $10,000 |
| 3 | Budget+ (nano+mini) | 50-52% | ~1% | $1,000 | $5,000 |
| 1 | Ultra Budget | 49-51% | ~0.5% | $500 | $2,500 |

---

## ROI by Portfolio Size

### $100K Portfolio — 10 stocks/day, 252 trading days/year

| Configuration | Annual Cost | Est. Return | Net Profit | ROI % |
|--------------|------------|------------|------------|-------|
| Local (Qwen3 235B) | $38 | $2,000 | **$1,962** | 5,063% |
| Ultra Budget | $45 | $500 | **$455** | 911% |
| Budget+ (nano+mini) | $40 | $1,000 | **$960** | 2,400% |
| **Value King (Flash+Pro)** | $232 | $5,000 | **$4,768** | 2,055% |
| Balanced (Grok) | $277 | $4,500 | **$4,223** | 1,524% |
| **Sweet Spot (5-mini+5.2)** | $328 | $6,000 | **$5,672** | 1,729% |
| Quality (Haiku+Sonnet) | $724 | $4,000 | **$3,276** | 452% |
| Premium (Opus+Sonnet) | $1,694 | $7,000 | **$5,306** | 313% |
| Max Cloud (5.4-Pro) | $15,549 | $8,000 | **-$7,549** | -49% |

### $500K Portfolio — 10 stocks/day

| Configuration | Annual Cost | Est. Return | Net Profit | ROI % |
|--------------|------------|------------|------------|-------|
| Local (Qwen3 235B) | $38 | $10,000 | **$9,962** | 26,216% |
| **Value King (Flash+Pro)** | $232 | $25,000 | **$24,768** | 10,676% |
| **Sweet Spot (5-mini+5.2)** | $328 | $30,000 | **$29,672** | 9,046% |
| Balanced (Grok) | $277 | $22,500 | **$22,223** | 8,023% |
| Quality (Haiku+Sonnet) | $724 | $20,000 | **$19,276** | 2,663% |
| Premium (Opus+Sonnet) | $1,694 | $35,000 | **$33,306** | 1,966% |
| Max Cloud (5.4-Pro) | $15,549 | $40,000 | **$24,451** | 157% |

### $1M+ Portfolio — 10 stocks/day

| Configuration | Annual Cost | Est. Return | Net Profit |
|--------------|------------|------------|------------|
| Value King (Flash+Pro) | $232 | $50,000 | **$49,768** |
| Sweet Spot (5-mini+5.2) | $328 | $60,000 | **$59,672** |
| Premium (Opus+Sonnet) | $1,694 | $70,000 | **$68,306** |
| Max Cloud (5.4-Pro) | $15,549 | $80,000 | **$64,451** |

### Break-Even Portfolio Size

| Configuration | Minimum Portfolio to Break Even |
|--------------|-------------------------------|
| Local (Qwen3 235B) | ~$2,500 |
| Value King (Flash+Pro) | ~$10,000 |
| Sweet Spot (5-mini+5.2) | ~$15,000 |
| Quality (Haiku+Sonnet) | ~$40,000 |
| Premium (Opus+Sonnet) | ~$285,000 |
| Max Cloud (5.4-Pro) | ~$2,000,000+ |

---

## Best Cloud Configuration

### For Portfolios Under $500K: "Value King"

```python
config["llm_provider"] = "google"
config["quick_think_llm"] = "gemini-2.5-flash"
config["deep_think_llm"] = "gemini-2.5-pro"
```

- **$0.09/run, $232/year** (10 stocks daily)
- Best ROI at every portfolio size under $500K
- Google free tier (1,000 req/day) can further reduce costs
- Batch API drops cost to ~$116/year

### For Portfolios $500K+: "Sweet Spot"

```python
config["llm_provider"] = "openai"
config["quick_think_llm"] = "gpt-5-mini"
config["deep_think_llm"] = "gpt-5.2"
```

- **$0.13/run, $328/year** (10 stocks daily)
- The extra ~1-2% accuracy edge over Gemini pays for itself above $500K
- Best absolute net profit at the $500K-$1M range

### Never Use GPT-5.4-Pro Unless...

Your portfolio exceeds **$2M+**. The $15K/year cost destroys ROI on anything smaller. The marginal accuracy gain (1-2%) over GPT-5.2 does not justify the 47x cost increase.

---

## Local LLM Support (Ollama)

TradingAgents fully supports local models via Ollama's OpenAI-compatible API.

### Configuration

```python
config["llm_provider"] = "ollama"
config["quick_think_llm"] = "qwen3:32b"
config["deep_think_llm"] = "qwen3:235b-a22b"
```

No API key required. Ollama must be running at `http://localhost:11434`.

### Recommended Local Models

| Model | Parameters | RAM (Q4) | Speed (M3 Max) | Quality | Role |
|-------|-----------|----------|----------------|---------|------|
| Qwen 3 8B | 8B | ~6GB | ~45 tok/s | Adequate | Quick-think only |
| Qwen 3 32B | 32B | ~20GB | ~20 tok/s | Good | Quick-think |
| Qwen 3 72B | 72B | ~45GB | ~10 tok/s | Strong | Quick or deep |
| Llama 4 Scout | 109B | ~65GB | ~7 tok/s | Excellent | Deep-think |
| **Qwen 3 235B (MoE)** | 235B (22B active) | ~140GB | ~12 tok/s | **Best local** | Deep-think |

### Hardware Requirements

| Setup | Min VRAM/RAM | Run Time/Analysis |
|-------|-------------|-------------------|
| Qwen3 8B + 32B | 26GB | ~5-8 min |
| Qwen3 32B + 72B | 65GB | ~10-15 min |
| Qwen3 32B + 235B MoE | 160GB | ~8-12 min |
| Full 72B + 235B MoE | 185GB | ~12-18 min |

**256GB Apple Silicon Mac Studio**: Can run Qwen3 235B (MoE) + Qwen3 32B comfortably with room for macOS overhead. Cost: ~$0.02/run in electricity.

### Critical Requirement

The local model **must support tool/function calling** via Ollama. Models with reliable tool calling:
- **Qwen 3** (all sizes) — best tool calling support
- **Llama 3.3 / Llama 4** — solid tool calling
- **Mistral** models — good tool calling

**Avoid** for this use case: DeepSeek-R1 (inconsistent tool calling), any model under 8B parameters.

### Any OpenAI-Compatible Server Works

Since the Ollama provider uses `ChatOpenAI` with a custom base URL, any OpenAI-compatible server works:

```python
config["llm_provider"] = "ollama"
config["backend_url"] = "http://your-server:port/v1"
```

Compatible servers: vLLM, llama.cpp, text-generation-inference (TGI), LM Studio.

---

## Hybrid Strategy (Local + Cloud)

The optimal approach for users with local GPU/Apple Silicon hardware:

| Stage | Purpose | Model | Cost | Timing |
|-------|---------|-------|------|--------|
| 1. Screen | Scan 30-50 watchlist stocks | Local Qwen3 235B | $0.00 | Overnight |
| 2. Confirm | Re-analyze top 10 candidates | Gemini 2.5 Flash + Pro | $0.90/day | Morning |
| 3. Decide | Final 2-3 trade candidates | GPT-5-mini + GPT-5.2 | $0.39/day | Pre-market |

### Hybrid Costs & Returns

| Metric | Value |
|--------|-------|
| Annual cost | ~$325 |
| Stock coverage | 50 stocks screened (vs 10 cloud-only) |
| Signal quality on trades | Near-frontier (GPT-5.2 on final decisions) |
| Projected accuracy | 55-57% on executed trades |
| Est. return on $100K | ~$6,000 |
| **Net profit on $100K** | **~$5,675** |
| Est. return on $500K | ~$30,000 |
| **Net profit on $500K** | **~$29,675** |

### Why Hybrid Wins

- **3-5x the stock coverage** at the same cost as cloud-only (free local screening)
- **Same quality on actual trades** (final decisions use frontier cloud models)
- **Better diversification** from broader screening = better risk-adjusted returns
- **Resilience** — if cloud APIs go down, local screening continues

---

## Recommendations Summary

| Portfolio Size | Best Strategy | Annual Cost | Expected Net Return |
|---------------|--------------|-------------|-------------------|
| < $50K | Local only (Qwen3 235B) | ~$38 | ~$500-$1,000 |
| $50-200K | Hybrid (local screen + Gemini confirm) | ~$150 | ~$3,000-$6,000 |
| $200-500K | Hybrid (local + Gemini + GPT-5.2 final) | ~$325 | ~$10,000-$25,000 |
| $500K-1M | Sweet Spot cloud (GPT-5-mini + GPT-5.2) | ~$328 | ~$25,000-$55,000 |
| $1M+ | Premium cloud (Sonnet 4.6 + Opus 4.6) | ~$1,694 | ~$60,000-$130,000 |
| $2M+ | Max Cloud (GPT-5.4 + GPT-5.4-Pro) | ~$15,549 | ~$120,000+ |

**Single best value across all scenarios:** Gemini 2.5 Flash + Gemini 2.5 Pro at $232/year — 5x cheaper than GPT with only ~1-2% less accuracy.

---

## Security Notes

The codebase has an overall **LOW risk** security posture:

- All API keys are managed via environment variables (no hardcoded secrets)
- HTTPS is used for all external API calls
- No `eval()`, `exec()`, `pickle`, `subprocess`, or `os.system` usage
- No SQL injection vectors (no SQL used)
- SSL certificate verification is never disabled
- `.env` files are properly gitignored

### Minor Items to Be Aware Of

- Ollama connections use unencrypted HTTP (localhost only — acceptable for local use)
- `ast.literal_eval()` is used on LLM output in the CLI (`cli/main.py`) for emptiness checking — low risk but unnecessary
- Broad `except Exception` blocks in some data fetching code may mask errors silently

---

## Pricing Sources

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [Anthropic Claude Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [xAI Grok Pricing](https://docs.x.ai/developers/models)
- [LLM Benchmark Comparisons (March 2026)](https://lmcouncil.ai/benchmarks)

---

*This analysis was generated in March 2026. Model pricing and capabilities change frequently — verify current rates before making decisions.*
