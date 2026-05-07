# HubSpot CRM Agent — Azure OpenAI + MCP (Phase 1)

A CLI AI agent with full HubSpot CRM access via 8 universal MCP tools.

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
# or
uv sync
```

### 2. Fill in .env
```
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...        # https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=... # your GPT-4o deployment name
HUBSPOT_TOKEN=...                # HubSpot → Settings → Integrations → Private Apps
```

### 3. Run
```bash
python main.py
```

---

## 8 Universal Tools

| Tool | Handles | Key actions |
|------|---------|-------------|
| `crm_object_action` | contacts, companies, deals, tickets, leads, quotes, invoices, orders, products, line_items, subscriptions, goals, appointments, marketing_events, services, courses, carts | search, get, list, create, update, delete, associate, merge |
| `engagement_action` | notes, calls, emails, meetings, tasks | create, update, list, get_timeline |
| `automation_action` | workflows, sequences | list, enroll, unenroll, get_enrollments |
| `marketing_action` | campaigns, lists, forms | list, get, create, add_contacts, submissions |
| `conversation_action` | inbox threads, communication preferences | list, get, send, archive, update |
| `analytics_action` | reports, behavioral events, GraphQL, forecasts | query, send_event, list_defs, get |
| `cms_action` | knowledge base, domains, files | list, get, create, update, publish, archive |
| `settings_action` | users, teams, owners, properties, pipelines, currencies | list, get, create |

## 5 Resources (auto-injected context)
- `hubspot://pipelines` — deal pipeline stage IDs
- `hubspot://ticket-pipelines` — ticket pipeline stage IDs
- `hubspot://owners` — owner IDs and emails
- `hubspot://contact-properties` — valid contact property names
- `hubspot://deal-properties` — valid deal property names

## 7 Slash Commands (Prompts)
| Command | What it does |
|---------|-------------|
| `/find_contact <name or email>` | Search and show contact card |
| `/deal_report [stage]` | Pipeline deals table with totals |
| `/create_contact_flow <email>` | Guided contact creation with duplicate check |
| `/contact_summary <contact_id>` | 360° view — deals, tickets, timeline |
| `/pipeline_overview` | Full pipeline breakdown by stage |
| `/log_call_flow <name or email>` | Guided call logging + follow-up task |
| `/ticket_triage [priority]` | List and act on open tickets |

## HubSpot Private App Scopes needed
Enable these when creating your Private App:
- crm.objects.contacts.read / write
- crm.objects.companies.read / write
- crm.objects.deals.read / write
- crm.objects.tickets.read / write (tickets)
- crm.objects.leads.read / write
- crm.objects.quotes.read / write
- crm.objects.invoices.read / write
- crm.objects.orders.read / write
- crm.objects.products.read / write
- crm.objects.line_items.read / write
- crm.objects.goals.read / write
- crm.objects.owners.read
- crm.schemas.contacts.read / write
- crm.schemas.deals.read / write
- crm.lists.read / write
- marketing.campaigns.read / write
- automation
- automation.sequences.read
- automation.sequences.enrollments.write
- conversations.read / write
- communication_preferences.read_write
- cms.knowledge_base.articles.read / write / publish
- cms.domains.read
- files
- settings.users.read
- settings.users.teams.read
- business-intelligence
- analytics.behavioral_events.send
- sales-email-read
- tickets
