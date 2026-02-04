# Fashion Trend Tracker MVP - Implementation Guide (Indonesia, MarkdownV2)

## Overview

An automated system that collects real-time fashion trends from Instagram and Pinterest, analyzes them with AI, and delivers actionable content recommendations daily.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FASHION TREND TRACKER MVP                               │
│                     Daily Automated Workflow                                │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │  SCHEDULER  │
                              │  (07:00)    │
                              │  WIB (UTC+7)│
                              │ GitHub      │
                              │ Actions     │
                              │ (FREE)      │
                              └──────┬──────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          PHASE 1: DATA COLLECTION                           │
│                                                                             │
│  ┌─────────────────────────┐         ┌─────────────────────────┐           │
│  │                         │         │                         │           │
│  │   PINTEREST TRENDS      │         │   INSTAGRAM GRAPH       │           │
│  │   API (v5)              │         │   API                   │           │
│  │                         │         │                         │           │
│  │   ┌─────────────────┐   │         │   ┌─────────────────┐   │           │
│  │   │ Trending        │   │         │   │ Your Posts      │   │           │
│  │   │ Keywords        │   │         │   │ Performance     │   │           │
│  │   │ (Fashion)       │   │         │   │ (Last 30 days)  │   │           │
│  │   └─────────────────┘   │         │   └─────────────────┘   │           │
│  │                         │         │                         │           │
│  │   ┌─────────────────┐   │         │   ┌─────────────────┐   │           │
│  │   │ Demographics    │   │         │   │ Hashtag         │   │           │
│  │   │ & Predictions   │   │         │   │ Research        │   │           │
│  │   └─────────────────┘   │         │   │ (Top Posts)     │   │           │
│  │                         │         │   └─────────────────┘   │           │
│  │   Cost: FREE            │         │                         │           │
│  │   Rate: 100 req/sec     │         │   ┌─────────────────┐   │           │
│  │                         │         │   │ Competitor      │   │           │
│  └─────────────────────────┘         │   │ Analysis        │   │           │
│                                      │   │ (Optional)      │   │           │
│                                      │   └─────────────────┘   │           │
│                                      │                         │           │
│                                      │   Cost: FREE            │           │
│                                      │   Limits:               │           │
│                                      │   - 30 hashtags/week    │           │
│                                      │   - 200 requests/hour   │           │
│                                      └─────────────────────────┘           │
│                                                                             │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   MERGE DATA    │
                          │                 │
                          │ • Pinterest     │
                          │   trends        │
                          │ • Instagram     │
                          │   hashtags      │
                          │ • Your stats    │
                          │ • Competitors   │
                          └────────┬────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          PHASE 2: AI ANALYSIS                               │
│                                                                             │
│                         ┌─────────────────────┐                             │
│                         │                     │                             │
│                         │   OPENROUTER API    │                             │
│                         │                     │                             │
│                         │  ┌───────────────┐  │                             │
│                         │  │ Model Options │  │                             │
│                         │  │               │  │                             │
│                         │  │ • DeepSeek    │◀─── Recommended ($0.14/M)      │
│                         │  │ • GPT-4o-mini │    Good balance ($0.15/M)      │
│                         │  │ • Llama 3.1   │    Free tier available         │
│                         │  │ • Claude 3.5  │    Best quality ($3/M)         │
│                         │  └───────────────┘  │                             │
│                         │                     │                             │
│                         │  Structured Prompts │                             │
│                         │  ┌───────────────┐  │                             │
│                         │  │ 1. Daily      │  │                             │
│                         │  │    Trends     │  │                             │
│                         │  │ 2. Lifecycle  │  │                             │
│                         │  │    Prediction │  │                             │
│                         │  │ 3. Content    │  │                             │
│                         │  │    Ideas      │  │                             │
│                         │  │ 4. Weekly     │  │                             │
│                         │  │    Calendar   │  │                             │
│                         │  └───────────────┘  │                             │
│                         │                     │                             │
│                         │  Cost: ~$0.50/month │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          PHASE 3: DELIVERY                                  │
│                                                                             │
│                         ┌─────────────────────┐                             │
│                         │                     │                             │
│                         │   TELEGRAM BOT      │                             │
│                         │                     │                             │
│                         │   Daily Report      │                             │
│                         │   to Your Phone     │                             │
│                         │                     │                             │
│                         │   Includes:         │                             │
│                         │   • Top 3 trends    │                             │
│                         │   • 5 content ideas │                             │
│                         │   • Quick win       │                             │
│                         │   • Trends to skip  │                             │
│                         │                     │                             │
│                         │   Cost: FREE        │                             │
│                         └─────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   OPTIONAL:     │
                              │   Google Sheets │
                              │   for tracking  │
                              │   over time     │
                              └─────────────────┘
```

---

## Data Flow Specification

### Input Sources

```
┌──────────────────────────────────────────────────────────────────┐
│                        INPUT SOURCES                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. PINTEREST TRENDS API (v5)                                    │
│     ─────────────────────────                                    │
│     Endpoint: GET /trends/keywords/{region}/top/{trend_type}     │
│                                                                   │
│     Parameters:                                                   │
│     • region: "ID" (Indonesia)                                   │
│     • trend_type: "growing" (emerging) or "monthly" (seasonal)   │
│     • interests: "womens_fashion,mens_fashion,beauty"            │
│     • include_demographics: true                                 │
│     • include_prediction: true                                   │
│     • limit: 20                                                  │
│                                                                   │
│     Returns:                                                      │
│     {                                                            │
│       "trends": [                                                │
│         {                                                        │
│           "keyword": "quiet luxury outfit",                      │
│           "volume": 125000,                                      │
│           "volume_change": 0.45,  // 45% growth                  │
│           "demographics": {                                      │
│             "age_groups": ["25-34", "35-44"],                    │
│             "gender": {"female": 0.78, "male": 0.22}             │
│           },                                                     │
│           "prediction": {                                        │
│             "direction": "up",                                   │
│             "confidence": 0.85                                   │
│           }                                                      │
│         }                                                        │
│       ]                                                          │
│     }                                                            │
│                                                                   │
│     Rate Limits: 100 requests/second                             │
│     Cost: FREE                                                   │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  2. INSTAGRAM GRAPH API                                          │
│     ───────────────────────                                      │
│                                                                   │
│     A. Your Media Performance                                    │
│        Endpoint: GET /{user-id}/media                            │
│        Fields: id, caption, media_type, timestamp,               │
│                like_count, comments_count,                       │
│                insights.metric(impressions,reach,saved,shares)   │
│                                                                   │
│     B. Hashtag Research                                          │
│        Step 1: GET /ig_hashtag_search?q={hashtag}               │
│        Step 2: GET /{hashtag-id}/top_media                      │
│                                                                   │
│        IMPORTANT LIMIT: 30 unique hashtags per 7 days           │
│                                                                   │
│     C. Competitor Analysis (Business Discovery)                  │
│        Endpoint: GET /{user-id}?fields=business_discovery...    │
│        Returns: Public metrics for business/creator accounts     │
│                                                                   │
│     Rate Limits: 200 requests/hour per user                      │
│     Cost: FREE (requires Business/Creator account)               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### AI Processing

```
┌──────────────────────────────────────────────────────────────────┐
│                     AI PROCESSING (OpenRouter)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PROMPT STRUCTURE: Role + Context + Data + Deliverables          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  SYSTEM PROMPT                                             │  │
│  │  ──────────────                                            │  │
│  │  "You are TrendAnalyst, an expert fashion/lifestyle        │  │
│  │   content strategist specializing in Instagram and         │  │
│  │   Pinterest. Your communication style: specific,           │  │
│  │   actionable, data-driven, with clear prioritization."     │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  USER PROMPT STRUCTURE                                     │  │
│  │  ─────────────────────                                     │  │
│  │                                                            │  │
│  │  ## DATA PROVIDED                                          │  │
│  │  • Pinterest Trends (JSON)                                 │  │
│  │  • Instagram Hashtag Data (JSON)                           │  │
│  │  • Your Performance Stats (JSON)                           │  │
│  │                                                            │  │
│  │  ## DELIVERABLES REQUESTED                                 │  │
│  │  1. Top 3 Trends with urgency scores                       │  │
│  │  2. 5 Content Ideas with hooks and hashtags                │  │
│  │  3. Quick Win (< 30 min content)                           │  │
│  │  4. Trends to avoid                                        │  │
│  │  5. Pattern insight from your data                         │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  MODEL SELECTION                                                 │
│  ───────────────                                                 │
│  Daily Analysis: deepseek/deepseek-chat (cheapest, good)         │
│  Quality Mode:   anthropic/claude-3.5-sonnet (best)              │
│  Free Backup:    meta-llama/llama-3.1-8b-instruct:free          │
│                                                                   │
│  API: POST https://openrouter.ai/api/v1/chat/completions        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Output Format (Telegram MarkdownV2)

Telegram requires `parse_mode=MarkdownV2` and escaping special characters. The template below already escapes MarkdownV2 symbols.

```
DAILY TREND REPORT
Date: [Day], [Month] [Date], [Year]
Time: [HH:MM] WIB

TOP 3 TRENDS TO ACT ON TODAY

1\. [Trend Name]
Platform: Instagram / Pinterest / Both
Evidence: [Data points]
Urgency: Today / This week / Next week
Fit Score: X/10
Content Angle: [Recommendation]

5 CONTENT IDEAS

IDEA 1: [Title]
Platform: [Instagram Reel]
Hook: "[Exact first 3 seconds]"
Concept: [Description]
Effort: Quick / Medium / Involved
Hashtags: #tag1 #tag2 #tag3

QUICK WIN
[Specific content to create in 30 min]

SKIP THESE
[Trends to avoid and why]

Reply with trend name for deeper analysis
```

---

## Setup Instructions

### Step 1: Create Required Accounts

```
┌──────────────────────────────────────────────────────────────────┐
│                     ACCOUNTS TO CREATE                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. OPENROUTER (Required)                                        │
│     ─────────────────────                                        │
│     URL: https://openrouter.ai                                   │
│     Time: 2 minutes                                              │
│     Cost: Free $5 credit to start                                │
│                                                                   │
│     Steps:                                                       │
│     a. Sign up with Google/GitHub                                │
│     b. Go to Keys section                                        │
│     c. Create new API key                                        │
│     d. Save key starting with "sk-or-v1-..."                     │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  2. INSTAGRAM GRAPH API (Required)                               │
│     ───────────────────────────────                              │
│     URL: https://developers.facebook.com                         │
│     Time: 15-30 minutes                                          │
│     Cost: Free                                                   │
│                                                                   │
│     Prerequisites:                                               │
│     • Instagram Business or Creator account                      │
│     • Facebook Page connected to Instagram                       │
│                                                                   │
│     Steps:                                                       │
│     a. Go to developers.facebook.com                             │
│     b. Create new App → Select "Business"                        │
│     c. Add "Instagram Graph API" product                         │
│     d. Add Instagram Business account                            │
│     e. Generate User Access Token with permissions:              │
│        - instagram_basic                                         │
│        - instagram_manage_insights                               │
│        - pages_read_engagement                                   │
│     f. Convert to Long-Lived Token (60 days)                     │
│     g. Note your Instagram User ID                               │
│                                                                   │
│     Token Refresh:                                               │
│     Set calendar reminder every 50 days to refresh token         │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  3. TELEGRAM BOT (Required)                                      │
│     ───────────────────────                                      │
│     Time: 2 minutes                                              │
│     Cost: Free                                                   │
│                                                                   │
│     Steps:                                                       │
│     a. Open Telegram, search @BotFather                          │
│     b. Send: /newbot                                             │
│     c. Name: "My Trend Tracker" (any name)                       │
│     d. Username: mytrendtracker_bot (must be unique)             │
│     e. Copy the token (format: 123456789:ABC...)                │
│     f. Send any message to YOUR new bot                          │
│     g. Get chat ID:                                              │
│        Visit: https://api.telegram.org/bot<TOKEN>/getUpdates    │
│        Find: "chat":{"id": YOUR_CHAT_ID}                        │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  4. PINTEREST API (Optional but Recommended)                     │
│     ────────────────────────────────────────                     │
│     URL: https://developers.pinterest.com                        │
│     Time: 5 minutes                                              │
│     Cost: Free                                                   │
│                                                                   │
│     Prerequisites:                                               │
│     • Pinterest Business account                                 │
│                                                                   │
│     Steps:                                                       │
│     a. Go to developers.pinterest.com                            │
│     b. Create new app                                            │
│     c. Request access to Trends API                              │
│     d. Generate access token                                     │
│     e. Token expires in 60 days (set reminder)                   │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  5. GITHUB (For Automation)                                      │
│     ───────────────────────                                      │
│     URL: https://github.com                                      │
│     Time: 5 minutes if no account                                │
│     Cost: Free (GitHub Actions free tier: 2000 min/month)       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Step 2: Environment Configuration (.env)

```
┌──────────────────────────────────────────────────────────────────┐
│                  ENVIRONMENT VARIABLES                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Create .env file with these variables:                          │
│                                                                   │
│  # ============================================================   │
│  # REQUIRED                                                      │
│  # ============================================================   │
│                                                                   │
│  # OpenRouter API                                                │
│  OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx            │
│                                                                   │
│  # Instagram Graph API (Indonesia account)                       │
│  INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxx             │
│  INSTAGRAM_USER_ID=17841400000000000                             │
│  INSTAGRAM_ACCOUNT_COUNTRY=ID                                    │
│  GRAPH_API_VERSION=v19.0                                         │
│                                                                   │
│  # Telegram Bot                                                  │
│  TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz         │
│  TELEGRAM_CHAT_ID=123456789,987654321                           │
│  TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook   │
│  TELEGRAM_WEBHOOK_SECRET=your_webhook_secret                     │
│                                                                   │
│  # ============================================================   │
│  # OPTIONAL                                                      │
│  # ============================================================   │
│                                                                   │
│  # Pinterest API (Indonesia)                                     │
│  PINTEREST_ACCESS_TOKEN=pina_xxxxxxxxxxxxxxxxxx                  │
│  PINTEREST_REGION=ID                                             │
│                                                                   │
│  # Apify (for advanced Instagram scraping)                       │
│  APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxx                        │
│  APIFY_DATASET_ID=xxxxxxxxxxxxxxxxxxxx                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Step 3: Configure Tracking Parameters (Indonesia)

```
┌──────────────────────────────────────────────────────────────────┐
│                  TRACKING CONFIGURATION                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  HASHTAGS TO MONITOR                                             │
│  ────────────────────                                            │
│  Customize these for Indonesia. Remember: Instagram limits        │
│  to 30 unique hashtag lookups per 7 days.                        │
│                                                                   │
│  Recommended structure (pick 8-10 total):                        │
│                                                                   │
│  High-Volume General (3-4):                                      │
│  • ootd                                                          │
│  • outfitoftheday                                                │
│  • fashionblogger                                                │
│  • streetstyle                                                   │
│                                                                   │
│  Local Trends (2-3, update monthly):                             │
│  • fashionindonesia                                              │
│  • ootdindonesia                                                 │
│  • hijabfashion                                                  │
│                                                                   │
│  Your Specific Niche (2-3):                                      │
│  • sustainablefashion                                            │
│  • capsulewardrobe                                               │
│  • thrifthaul                                                    │
│                                                                   │
│  COMPETITOR ACCOUNTS                                             │
│  ───────────────────                                             │
│  Add 3-5 Indonesia-based accounts in your niche:                 │
│  • Must be Business or Creator accounts                          │
│  • Choose accounts slightly bigger than you                      │
│  • Mix of direct competitors and aspirational                    │
│                                                                   │
│  PINTEREST CATEGORIES                                            │
│  ────────────────────                                            │
│  Available categories for fashion:                               │
│  • womens_fashion                                                │
│  • mens_fashion                                                  │
│  • beauty                                                        │
│  • wedding                                                       │
│  • home_decor (for lifestyle content)                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Workflow Execution

### Daily Workflow Sequence (WIB)

```
┌──────────────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW SEQUENCE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  07:00 WIB ─── TRIGGER ───────────────────────────────────────    │
│            │                                                      │
│            │  GitHub Actions cron: '0 0 * * *'                   │
│            │  (Runs at 07:00 WIB daily)                          │
│            │                                                      │
│  07:00 WIB ─── STEP 1: Initialize ────────────────────────────    │
│            │                                                      │
│            │  • Load environment variables                       │
│            │  • Validate API credentials                         │
│            │  • Log start time                                   │
│            │                                                      │
│  07:01 WIB ─── STEP 2: Collect Pinterest Trends ─────────────     │
│            │                                                      │
│            │  API Calls:                                         │
│            │  • GET /trends/keywords/ID/top/growing              │
│            │    - womens_fashion (20 trends)                     │
│            │    - mens_fashion (20 trends)                       │
│            │    - beauty (20 trends)                             │
│            │                                                      │
│            │  Expected: 60 trends with demographics              │
│            │  Time: ~5 seconds                                   │
│            │                                                      │
│  07:02 WIB ─── STEP 3: Collect Instagram Data ────────────────    │
│            │                                                      │
│            │  A. Your Posts (30 recent)                          │
│            │     GET /{user-id}/media?limit=30                   │
│            │                                                      │
│            │  B. Hashtag Research (8 hashtags)                   │
│            │     For each hashtag:                               │
│            │     - GET /ig_hashtag_search?q={hashtag}           │
│            │     - GET /{hashtag-id}/top_media?limit=15         │
│            │     - 1 second delay between requests               │
│            │                                                      │
│            │  C. Competitor Analysis (if configured)             │
│            │     GET /{user-id}?fields=business_discovery...    │
│            │                                                      │
│            │  Time: ~30 seconds                                  │
│            │                                                      │
│  07:03 WIB ─── STEP 4: Process & Merge Data ─────────────────     │
│            │                                                      │
│            │  • Calculate engagement rates                       │
│            │  • Identify top performing posts                    │
│            │  • Extract content patterns                         │
│            │  • Structure data for AI prompt                     │
│            │                                                      │
│            │  Time: ~2 seconds                                   │
│            │                                                      │
│  07:03 WIB ─── STEP 5: AI Analysis ───────────────────────────    │
│            │                                                      │
│            │  POST https://openrouter.ai/api/v1/chat/completions│
│            │                                                      │
│            │  Model: deepseek/deepseek-chat                      │
│            │  Max tokens: 3000                                   │
│            │  Temperature: 0.7                                   │
│            │                                                      │
│            │  Prompt includes:                                   │
│            │  • Pinterest trends JSON                            │
│            │  • Instagram hashtag data JSON                      │
│            │  • Your performance stats JSON                      │
│            │  • Deliverables specification                       │
│            │                                                      │
│            │  Time: ~15-30 seconds                               │
│            │                                                      │
│  07:04 WIB ─── STEP 6: Format Report ─────────────────────────    │
│            │                                                      │
│            │  • Add header with date/time                        │
│            │  • Format for Telegram (MarkdownV2)                 │
│            │  • Escape special characters                        │
│            │  • Split if > 4000 characters                       │
│            │                                                      │
│  07:04 WIB ─── STEP 7: Deliver ───────────────────────────────    │
│            │                                                      │
│            │  POST https://api.telegram.org/bot{token}/sendMessage│
│            │                                                      │
│            │  • Send to your Telegram                            │
│            │  • Confirm delivery                                 │
│            │                                                      │
│  07:05 WIB ─── COMPLETE ──────────────────────────────────────    │
│                                                                   │
│            Total execution time: ~2-3 minutes                    │
│            Total API cost: ~$0.01-0.02                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Error Handling Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     ERROR HANDLING                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Pinterest API Failure                                           │
│  ─────────────────────                                           │
│  IF Pinterest API fails:                                         │
│    → Use fallback curated trends list                            │
│    → Continue workflow                                           │
│    → Note in report: "Using cached Pinterest data"               │
│                                                                   │
│  Instagram API Failure                                           │
│  ─────────────────────                                           │
│  IF Instagram API fails:                                         │
│    → Skip hashtag research                                       │
│    → Use basic performance placeholder                           │
│    → Continue with Pinterest data only                           │
│    → Note in report: "Instagram data unavailable"                │
│                                                                   │
│  OpenRouter API Failure                                          │
│  ──────────────────────                                          │
│  IF primary model fails:                                         │
│    → Try fallback: meta-llama/llama-3.1-8b-instruct:free        │
│  IF fallback fails:                                              │
│    → Send error notification via Telegram                        │
│    → Log error for debugging                                     │
│                                                                   │
│  Telegram Delivery Failure                                       │
│  ─────────────────────────                                       │
│  IF Telegram fails:                                              │
│    → Retry 3 times with 5 second delay                          │
│    → Log to GitHub Actions output                                │
│                                                                   │
│  Rate Limit Handling                                             │
│  ───────────────────                                             │
│  Instagram 30 hashtag/week limit:                                │
│    → Track usage in workflow                                     │
│    → Prioritize most important hashtags                          │
│    → Skip if quota exhausted                                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions Setup

### Workflow File Structure (uses .env variable names)

```
┌──────────────────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS WORKFLOW                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  File: .github/workflows/daily-trends.yml                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  name: Daily Trend Analysis                                │  │
│  │                                                            │  │
│  │  on:                                                       │  │
│  │    schedule:                                               │  │
│  │      - cron: '0 0 * * *'     # 07:00 WIB daily             │  │
│  │    workflow_dispatch:       # Manual trigger button        │  │
│  │                                                            │  │
│  │  jobs:                                                     │  │
│  │    analyze:                                                │  │
│  │      runs-on: ubuntu-latest                                │  │
│  │      timeout-minutes: 10                                   │  │
│  │                                                            │  │
│  │      steps:                                                │  │
│  │        - uses: actions/checkout@v4                         │  │
│  │                                                            │  │
│  │        - name: Set up Python                               │  │
│  │          uses: actions/setup-python@v5                     │  │
│  │          with:                                             │  │
│  │            python-version: '3.11'                          │  │
│  │                                                            │  │
│  │        - name: Install dependencies                        │  │
│  │          run: uv sync --dev                                │  │
│  │                                                            │  │
│  │        - name: Run trend analysis                          │  │
│  │          env:                                              │  │
│  │            OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}│
│  │            INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}│
│  │            INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}│
│  │            INSTAGRAM_ACCOUNT_COUNTRY: ${{ secrets.INSTAGRAM_ACCOUNT_COUNTRY }}│
│  │            PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}│
│  │            PINTEREST_REGION: ${{ secrets.PINTEREST_REGION }}│
│  │            TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}│
│  │            TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}│
│  │          run: python main.py                               │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  SECRETS TO ADD IN GITHUB                                        │
│  ─────────────────────────                                       │
│  Go to: Repository → Settings → Secrets → Actions                │
│                                                                   │
│  Add these secrets (match .env names):                           │
│  • OPENROUTER_API_KEY                                            │
│  • INSTAGRAM_ACCESS_TOKEN                                        │
│  • INSTAGRAM_USER_ID                                             │
│  • INSTAGRAM_ACCOUNT_COUNTRY                                     │
│  • PINTEREST_ACCESS_TOKEN (optional)                             │
│  • PINTEREST_REGION                                              │
│  • TELEGRAM_BOT_TOKEN                                            │
│  • TELEGRAM_CHAT_ID                                              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Cost Analysis

```
┌──────────────────────────────────────────────────────────────────┐
│                     MONTHLY COST BREAKDOWN                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Component              │ Daily Use    │ Monthly Cost             │
│  ───────────────────────┼──────────────┼────────────────────────  │
│  Instagram Graph API    │ ~50 requests │ FREE                     │
│  Pinterest Trends API   │ ~5 requests  │ FREE                     │
│  OpenRouter (DeepSeek)  │ ~3000 tokens │ $0.01-0.02/day          │
│  Telegram Bot           │ 1-2 messages │ FREE                     │
│  GitHub Actions         │ ~3 minutes   │ FREE (2000 min/mo)      │
│  ───────────────────────┼──────────────┼────────────────────────  │
│  TOTAL                  │              │ $0.30-0.60/month        │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  OPTIONAL UPGRADES                                               │
│  ─────────────────                                               │
│                                                                   │
│  Better AI (Claude 3.5)                                          │
│  • Cost: ~$1-2/month                                             │
│  • Benefit: Higher quality analysis                              │
│                                                                   │
│  Apify Instagram Scraper                                         │
│  • Cost: ~$5/month                                               │
│  • Benefit: Trending Reels audio, more hashtag data              │
│                                                                   │
│  Google Sheets Integration                                       │
│  • Cost: FREE                                                    │
│  • Benefit: Track trends over time                               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Maintenance Schedule

```
┌──────────────────────────────────────────────────────────────────┐
│                   MAINTENANCE SCHEDULE                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DAILY (Automatic)                                               │
│  ─────────────────                                               │
│  • Workflow runs at 07:00 WIB (UTC+7)                            │
│  • Report delivered to Telegram                                  │
│  • No action needed                                              │
│                                                                   │
│  WEEKLY (5 minutes)                                              │
│  ─────────────────                                               │
│  □ Review which trends you acted on                              │
│  □ Note which content ideas performed well                       │
│  □ Update trending aesthetics hashtags if needed                 │
│                                                                   │
│  MONTHLY (15 minutes)                                            │
│  ──────────────────                                              │
│  □ Update TRACKED_HASHTAGS list                                  │
│    - Remove declining hashtags                                   │
│    - Add new trending aesthetics                                 │
│  □ Review competitor list                                        │
│    - Add new relevant accounts                                   │
│    - Remove inactive accounts                                    │
│  □ Check API usage stats                                         │
│                                                                   │
│  EVERY 50 DAYS (Important!)                                      │
│  ──────────────────────────                                      │
│  □ Refresh Instagram Access Token                                │
│    - Tokens expire after 60 days                                 │
│    - Set calendar reminder                                       │
│  □ Refresh Pinterest Access Token (if using)                     │
│                                                                   │
│  QUARTERLY (30 minutes)                                          │
│  ─────────────────────                                           │
│  □ Review overall system performance                             │
│  □ Update seasonal hashtag tracking                              │
│  □ Adjust posting time based on analytics                        │
│  □ Consider upgrading AI model if budget allows                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### API Endpoints

```
┌──────────────────────────────────────────────────────────────────┐
│                    API QUICK REFERENCE                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PINTEREST                                                       │
│  Base: https://api.pinterest.com/v5                              │
│  • GET /trends/keywords/{region}/top/{trend_type}                │
│  • Auth: Bearer token in header                                  │
│                                                                   │
│  INSTAGRAM GRAPH                                                 │
│  Base: https://graph.facebook.com/v19.0                          │
│  • GET /{user-id}/media                                          │
│  • GET /ig_hashtag_search?q={hashtag}                           │
│  • GET /{hashtag-id}/top_media                                   │
│  • Auth: access_token query parameter                            │
│                                                                   │
│  OPENROUTER                                                      │
│  Base: https://openrouter.ai/api/v1                              │
│  • POST /chat/completions                                        │
│  • GET /models (list available models)                           │
│  • GET /auth/key (check credits)                                 │
│  • Auth: Bearer token in header                                  │
│                                                                   │
│  TELEGRAM                                                        │
│  Base: https://api.telegram.org/bot{token}                       │
│  • POST /sendMessage                                             │
│  • GET /getUpdates (to find chat_id)                            │
│  • Use parse_mode=MarkdownV2                                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Troubleshooting

```
┌──────────────────────────────────────────────────────────────────┐
│                    TROUBLESHOOTING                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  "Instagram API Error: Invalid token"                            │
│  → Token expired. Generate new long-lived token.                 │
│                                                                   │
│  "Instagram API Error: (#30) rate limit"                         │
│  → Exceeded 30 hashtags/week. Wait or reduce hashtag count.      │
│                                                                   │
│  "OpenRouter Error 401"                                          │
│  → Invalid API key. Check key in environment variables.          │
│                                                                   │
│  "OpenRouter Error 402"                                          │
│  → Out of credits. Add credits at openrouter.ai/credits          │
│                                                                   │
│  "Telegram Error: chat not found"                                │
│  → Wrong chat_id. Re-check with /getUpdates endpoint.            │
│                                                                   │
│  "GitHub Actions: workflow not running"                          │
│  → Check if Actions enabled in repo settings                     │
│  → Verify cron syntax                                            │
│  → Check secrets are set correctly                               │
│                                                                   │
│  "No trends in report"                                           │
│  → Pinterest API may be down. Fallback should activate.          │
│  → Check Pinterest token hasn't expired.                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
fashion-trend-tracker/
│
├── .github/
│   └── workflows/
│       └── daily-trends.yml      # GitHub Actions automation
│
├── config.py                     # Configuration and constants
├── instagram_api.py              # Instagram Graph API wrapper
├── pinterest_api.py              # Pinterest Trends API wrapper
├── apify_client.py               # Apify API wrapper
├── mcp_adapters.py               # Local MCP-style adapters
├── openrouter_ai.py              # OpenRouter AI analyzer
├── prompting.py                  # Prompt templates + schema validation
├── utils.py                      # Summaries + Telegram formatting utils
├── orchestrator.py               # LangGraph orchestration
├── telegram_bot.py               # Telegram chatbot (server mode)
├── main.py                       # One-off runner (optional)
│
├── pyproject.toml                # Python dependencies (uv)
├── requirements.txt              # Legacy fallback (optional)
├── .env.example                  # Environment template
├── .env                          # Your credentials (gitignored)
├── .gitignore                    # Git ignore file
│
└── IMPLEMENTATION_GUIDE_FIXED.md # This document
```

---

## Next Steps After Setup

1. Test manually first: Run `python telegram_bot.py` locally to verify everything works
2. Check Telegram: Confirm you receive a response
3. Set token refresh reminders: Calendar alerts for 50-day token renewal
4. Iterate on hashtags: After first week, adjust tracked hashtags based on relevance

---

## Server Mode (Telegram Chatbot)

For a server-based chatbot (user asks: “what should I post today”), you can run either long polling or webhook.

Long polling (simple):

```
uv run python telegram_bot.py
```

This mode fetches fresh Instagram + Pinterest + Apify data on each request and generates a bilingual response.

Webhook mode (recommended for servers with public HTTPS):

1. Run the server:
```
uv run uvicorn telegram_webhook:app --host 0.0.0.0 --port 8000
```

2. Set your webhook URL (must be public HTTPS):
```
uv run python -c "from telegram_webhook import set_webhook; set_webhook()"
```

### Local Development (uv + Make)

Install dependencies:
```
make setup
```

Run tests:
```
make test
```

Run bot:
```
make run-bot
```

Run webhook server:
```
make run-webhook
```

### Logging

Logs are written to:
- `logs/telegram_bot.log` (long polling)
- `logs/telegram_webhook.log` (webhook server)

---

Last updated: February 2026
Version: 2.1 (Indonesia, MarkdownV2, unified env names)
