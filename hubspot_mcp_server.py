"""
HubSpot MCP Server — Phase 1
==============================
8 Universal Tools  +  5 Resources  +  7 Prompts

TOOLS (model-controlled):
  1. crm_object_action   — ALL CRM objects in one tool
  2. engagement_action   — notes, calls, emails, meetings, tasks
  3. automation_action   — workflows + sequences
  4. marketing_action    — campaigns, lists, forms, emails
  5. conversation_action — inbox threads + communication prefs
  6. analytics_action    — reports, events, GraphQL, forecasts
  7. cms_action          — knowledge base, files, domains
  8. settings_action     — users, teams, owners, pipelines, properties

RESOURCES (app-controlled, read-only context):
  hubspot://pipelines
  hubspot://ticket-pipelines
  hubspot://owners
  hubspot://contact-properties
  hubspot://deal-properties

PROMPTS (user-controlled slash commands):
  /find_contact  /deal_report  /create_contact_flow
  /contact_summary  /pipeline_overview  /log_call_flow  /ticket_triage
"""

import os, json, time, httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
mcp = FastMCP("HubSpotMCP", log_level="ERROR")
BASE = "https://api.hubapi.com"

# =============================================================================
# HTTP helpers
# =============================================================================

def _headers() -> dict:
    token = os.getenv("HUBSPOT_TOKEN", "")
    if not token:
        raise ValueError("HUBSPOT_TOKEN is missing in .env — get it from HubSpot → Settings → Integrations → Private Apps")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def _get(path: str, params: dict | None = None) -> dict:
    r = httpx.get(f"{BASE}{path}", headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def _post(path: str, body) -> dict:
    r = httpx.post(f"{BASE}{path}", headers=_headers(), json=body, timeout=15)
    r.raise_for_status()
    return r.json()

def _patch(path: str, body: dict) -> dict:
    r = httpx.patch(f"{BASE}{path}", headers=_headers(), json=body, timeout=15)
    r.raise_for_status()
    return r.json()

def _delete(path: str) -> dict:
    r = httpx.delete(f"{BASE}{path}", headers=_headers(), timeout=15)
    r.raise_for_status()
    return {"status": "deleted", "path": path}

def ok(d) -> str:
    return json.dumps(d, indent=2)

def ts() -> str:
    return str(int(time.time() * 1000))

# Association type IDs for common pairs
ASSOC_TYPES = {
    ("contacts", "deals"):     [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 4}],
    ("contacts", "companies"): [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 279}],
    ("contacts", "tickets"):   [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 16}],
    ("deals",    "companies"): [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 342}],
    ("deals",    "tickets"):   [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 28}],
    ("notes",    "contacts"):  [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}],
    ("notes",    "deals"):     [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 214}],
    ("tasks",    "contacts"):  [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 204}],
    ("calls",    "contacts"):  [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 194}],
    ("emails",   "contacts"):  [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 198}],
    ("meetings", "contacts"):  [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 200}],
    ("line_items","deals"):    [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 20}],
    ("quotes",   "deals"):     [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 64}],
}

def _associate(from_obj: str, from_id: str, to_obj: str, to_id: str):
    """Link two HubSpot records using v4 associations."""
    key = (from_obj.lower(), to_obj.lower())
    types = ASSOC_TYPES.get(key, [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}])
    try:
        _post(f"/crm/v4/objects/{from_obj}/{from_id}/associations/{to_obj}/{to_id}", types)
    except Exception:
        pass  # association is optional — don't fail the main action

# =============================================================================
# TOOL 1 — crm_object_action
# =============================================================================

# Supported CRM objects and their default read properties
CRM_OBJECT_PROPS = {
    "contacts":           "firstname,lastname,email,phone,company,hs_lead_status,createdate",
    "companies":          "name,domain,industry,city,phone,annualrevenue,numberofemployees",
    "deals":              "dealname,amount,dealstage,closedate,pipeline,hubspot_owner_id",
    "tickets":            "subject,content,hs_ticket_priority,hs_pipeline_stage,hubspot_owner_id",
    "leads":              "hs_lead_name,hs_lead_status,hubspot_owner_id",
    "quotes":             "hs_title,hs_status,hs_expiration_date,hs_quote_amount",
    "invoices":           "hs_invoice_status,hs_due_date,hs_amount_billed,hs_currency",
    "orders":             "hs_order_name,hs_order_status,hs_currency_code,createdate",
    "products":           "name,description,price,hs_sku,hs_product_type",
    "line_items":         "name,quantity,price,amount,hs_product_id",
    "subscriptions":      "hs_subscription_name,hs_billing_start_date,hs_subscription_status",
    "goals":              "hs_goal_name,hs_target_amount,hs_completion_percentage",
    "appointments":       "hs_appointment_name,hs_appointment_start,hs_appointment_status",
    "marketing_events":   "hs_event_name,hs_start_date,hs_end_date,hs_event_type",
    "feedback_submissions":"hs_submission_timestamp,hs_value",
    "services":           "name,description,price",
    "courses":            "hs_course_name,hs_course_status",
    "carts":              "hs_cart_name,hs_currency_code,hs_total_price",
    "commercepayments":   "hs_payment_status,hs_payment_amount,hs_currency_code",
}

@mcp.tool()
def crm_object_action(
    object_type: str,
    action: str,
    object_id: str = "",
    query: str = "",
    properties: dict = {},
    limit: int = 20,
    after: str = "",
    to_object_type: str = "",
    to_object_id: str = "",
    primary_id: str = "",
    secondary_id: str = "",
) -> str:
    """
    Universal tool for ALL HubSpot CRM objects — one tool replaces 30+ individual tools.

    object_type options:
      contacts, companies, deals, tickets, leads, quotes, invoices, orders,
      products, line_items, subscriptions, goals, appointments, marketing_events,
      feedback_submissions, services, courses, carts, commercepayments

    action options:
      search  — full-text search (requires: query)
      get     — get one record by ID (requires: object_id)
      list    — list all records with pagination (optional: limit, after)
      create  — create a new record (requires: properties dict)
      update  — update a record (requires: object_id + properties dict)
      delete  — archive a record (requires: object_id)
      associate — link two records (requires: object_id + to_object_type + to_object_id)
      merge   — merge duplicate records (requires: primary_id + secondary_id, contacts only)

    Examples:
      crm_object_action("contacts", "search", query="john@acme.com")
      crm_object_action("deals", "create", properties={"dealname":"Acme","pipeline":"default","dealstage":"appointmentscheduled","amount":"5000"})
      crm_object_action("contacts", "update", object_id="123", properties={"phone":"+91-9876543210"})
      crm_object_action("leads", "list", limit=10)
      crm_object_action("contacts", "associate", object_id="123", to_object_type="deals", to_object_id="456")
    """
    obj = object_type.lower().rstrip("s") + "s"  # normalize e.g. "contact" -> "contacts"
    props_str = CRM_OBJECT_PROPS.get(obj, "")

    try:
        if action == "search":
            if not query:
                return ok({"error": "query is required for search action"})
            body = {"query": query, "limit": limit}
            if props_str:
                body["properties"] = props_str.split(",")
            return ok(_post(f"/crm/v3/objects/{obj}/search", body))

        elif action == "get":
            if not object_id:
                return ok({"error": "object_id is required for get action"})
            params = {"properties": props_str} if props_str else {}
            return ok(_get(f"/crm/v3/objects/{obj}/{object_id}", params or None))

        elif action == "list":
            params: dict = {"limit": limit}
            if props_str:
                params["properties"] = props_str
            if after:
                params["after"] = after
            return ok(_get(f"/crm/v3/objects/{obj}", params))

        elif action == "create":
            if not properties:
                return ok({"error": "properties dict is required for create action"})
            return ok(_post(f"/crm/v3/objects/{obj}", {"properties": properties}))

        elif action == "update":
            if not object_id:
                return ok({"error": "object_id is required for update action"})
            if not properties:
                return ok({"error": "properties dict is required for update action"})
            return ok(_patch(f"/crm/v3/objects/{obj}/{object_id}", {"properties": properties}))

        elif action == "delete":
            if not object_id:
                return ok({"error": "object_id is required for delete action"})
            return ok(_delete(f"/crm/v3/objects/{obj}/{object_id}"))

        elif action == "associate":
            if not all([object_id, to_object_type, to_object_id]):
                return ok({"error": "object_id, to_object_type, to_object_id all required for associate"})
            to_obj = to_object_type.lower().rstrip("s") + "s"
            _associate(obj, object_id, to_obj, to_object_id)
            return ok({"status": "associated", "from": f"{obj}/{object_id}", "to": f"{to_obj}/{to_object_id}"})

        elif action == "merge":
            if not all([primary_id, secondary_id]):
                return ok({"error": "primary_id and secondary_id required for merge"})
            return ok(_post(f"/crm/v3/objects/{obj}/merge",
                           {"primaryObjectId": primary_id, "objectIdToMerge": secondary_id}))

        else:
            return ok({"error": f"Unknown action '{action}'. Use: search, get, list, create, update, delete, associate, merge"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 2 — engagement_action
# =============================================================================

@mcp.tool()
def engagement_action(
    engagement_type: str,
    action: str,
    contact_id: str = "",
    deal_id: str = "",
    body_text: str = "",
    subject: str = "",
    duration_seconds: int = 0,
    call_outcome: str = "CONNECTED",
    due_date: str = "",
    owner_id: str = "",
    start_time: str = "",
    end_time: str = "",
    task_status: str = "",
    limit: int = 20,
    email_subject: str = "",
) -> str:
    """
    Universal tool for ALL HubSpot engagement types — notes, calls, emails, meetings, tasks.

    engagement_type options: note | call | email | meeting | task

    action options:
      create       — create a new engagement
      update       — update an existing engagement (requires: contact_id as the object id)
      get_timeline — get full activity history for a contact (requires: contact_id)
      list         — list recent engagements of this type

    Note params:    body_text, contact_id (optional), deal_id (optional)
    Call params:    contact_id, body_text (notes), duration_seconds, call_outcome
                    call_outcome: CONNECTED | LEFT_VOICEMAIL | NO_ANSWER | WRONG_NUMBER
    Email params:   contact_id, email_subject, body_text
    Meeting params: subject (title), body_text (notes), start_time, end_time, contact_id
    Task params:    subject, body_text, due_date (YYYY-MM-DD), owner_id, contact_id
                    task_status for update: NOT_STARTED | IN_PROGRESS | COMPLETED | DEFERRED

    Examples:
      engagement_action("note", "create", body_text="Called about renewal", contact_id="123")
      engagement_action("call", "create", contact_id="123", body_text="Discussed pricing", duration_seconds=900, call_outcome="CONNECTED")
      engagement_action("task", "create", subject="Follow up", due_date="2025-06-01", contact_id="123")
      engagement_action("meeting", "create", subject="Demo", start_time="2025-06-01T10:00:00.000Z", contact_id="123")
      engagement_action("note", "get_timeline", contact_id="123")
    """
    etype = engagement_type.lower()

    try:
        if action == "get_timeline":
            if not contact_id:
                return ok({"error": "contact_id required for get_timeline"})
            results = {}
            for obj in ["notes", "calls", "emails", "meetings", "tasks"]:
                prop_map = {
                    "notes":    "hs_note_body,hs_timestamp",
                    "calls":    "hs_call_body,hs_call_duration,hs_call_disposition,hs_timestamp",
                    "emails":   "hs_email_subject,hs_email_text,hs_timestamp",
                    "meetings": "hs_meeting_title,hs_meeting_start_time,hs_timestamp",
                    "tasks":    "hs_task_subject,hs_task_status,hs_timestamp",
                }
                try:
                    assoc = _get(f"/crm/v3/objects/contacts/{contact_id}/associations/{obj}")
                    ids = [r["id"] for r in assoc.get("results", [])[:5]]
                    items = [_get(f"/crm/v3/objects/{obj}/{oid}", {"properties": prop_map[obj]}) for oid in ids]
                    results[obj] = items
                except Exception:
                    results[obj] = []
            return ok(results)

        elif action == "list":
            obj_map = {"note": "notes", "call": "calls", "email": "emails",
                       "meeting": "meetings", "task": "tasks"}
            obj = obj_map.get(etype, etype + "s")
            prop_map = {
                "notes": "hs_note_body,hs_timestamp",
                "calls": "hs_call_body,hs_call_disposition,hs_timestamp",
                "emails": "hs_email_subject,hs_email_status,hs_timestamp",
                "meetings": "hs_meeting_title,hs_meeting_start_time",
                "tasks": "hs_task_subject,hs_task_status,hs_timestamp,hubspot_owner_id",
            }
            return ok(_get(f"/crm/v3/objects/{obj}", {"limit": limit, "properties": prop_map.get(obj, "")}))

        elif action == "create":
            if etype == "note":
                props = {"hs_note_body": body_text, "hs_timestamp": ts()}
                result = _post("/crm/v3/objects/notes", {"properties": props})
                nid = result.get("id", "")
                if contact_id: _associate("notes", nid, "contacts", contact_id)
                if deal_id:    _associate("notes", nid, "deals", deal_id)
                return ok(result)

            elif etype == "call":
                if not contact_id:
                    return ok({"error": "contact_id required for call"})
                props = {
                    "hs_call_body":        body_text,
                    "hs_call_duration":    str(duration_seconds * 1000),
                    "hs_call_disposition": call_outcome,
                    "hs_call_status":      "COMPLETED",
                    "hs_timestamp":        ts(),
                }
                result = _post("/crm/v3/objects/calls", {"properties": props})
                _associate("calls", result.get("id",""), "contacts", contact_id)
                return ok(result)

            elif etype == "email":
                if not contact_id:
                    return ok({"error": "contact_id required for email"})
                props = {
                    "hs_email_subject":   email_subject or subject,
                    "hs_email_text":      body_text,
                    "hs_email_direction": "EMAIL",
                    "hs_email_status":    "SENT",
                    "hs_timestamp":       ts(),
                }
                result = _post("/crm/v3/objects/emails", {"properties": props})
                _associate("emails", result.get("id",""), "contacts", contact_id)
                return ok(result)

            elif etype == "meeting":
                props: dict = {
                    "hs_meeting_title": subject,
                    "hs_meeting_body":  body_text,
                    "hs_timestamp":     ts(),
                }
                if start_time: props["hs_meeting_start_time"] = start_time
                if end_time:   props["hs_meeting_end_time"]   = end_time
                result = _post("/crm/v3/objects/meetings", {"properties": props})
                if contact_id: _associate("meetings", result.get("id",""), "contacts", contact_id)
                return ok(result)

            elif etype == "task":
                props: dict = {
                    "hs_task_subject": subject,
                    "hs_task_body":    body_text,
                    "hs_task_status":  "NOT_STARTED",
                }
                if due_date:  props["hs_timestamp"]       = f"{due_date}T00:00:00.000Z"
                if owner_id:  props["hubspot_owner_id"]   = owner_id
                result = _post("/crm/v3/objects/tasks", {"properties": props})
                if contact_id: _associate("tasks", result.get("id",""), "contacts", contact_id)
                return ok(result)

            else:
                return ok({"error": f"Unknown engagement_type '{etype}'. Use: note, call, email, meeting, task"})

        elif action == "update":
            if not contact_id:
                return ok({"error": "contact_id (as object_id) required for update"})
            obj_map = {"note": "notes", "call": "calls", "email": "emails",
                       "meeting": "meetings", "task": "tasks"}
            obj = obj_map.get(etype, etype + "s")
            props: dict = {}
            if task_status: props["hs_task_status"] = task_status
            if body_text:   props["hs_task_body"] = body_text
            if subject:     props["hs_task_subject"] = subject
            return ok(_patch(f"/crm/v3/objects/{obj}/{contact_id}", {"properties": props}))

        else:
            return ok({"error": f"Unknown action '{action}'. Use: create, update, list, get_timeline"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 3 — automation_action
# =============================================================================

@mcp.tool()
def automation_action(
    type: str,
    action: str,
    contact_id: str = "",
    workflow_id: str = "",
    sequence_id: str = "",
    sender_email: str = "",
) -> str:
    """
    Universal tool for HubSpot automation — workflows AND sequences.

    type options: workflow | sequence

    action options:
      list            — list all workflows or sequences
      enroll          — enroll a contact into a workflow or sequence
      unenroll        — remove a contact from a workflow or sequence
      get_enrollments — get workflows/sequences a contact is enrolled in

    Workflow params: contact_id, workflow_id
    Sequence params: contact_id, sequence_id, sender_email (required for enroll)

    Examples:
      automation_action("workflow", "list")
      automation_action("workflow", "enroll", contact_id="123", workflow_id="456")
      automation_action("sequence", "list")
      automation_action("sequence", "enroll", contact_id="123", sequence_id="789", sender_email="rep@company.com")
    """
    try:
        if type == "workflow":
            if action == "list":
                return ok(_get("/automation/v3/workflows"))

            elif action == "enroll":
                if not all([contact_id, workflow_id]):
                    return ok({"error": "contact_id and workflow_id required for workflow enroll"})
                return ok(_post(f"/automation/v3/workflows/{workflow_id}/enrollments/contacts/{contact_id}", {}))

            elif action == "unenroll":
                if not all([contact_id, workflow_id]):
                    return ok({"error": "contact_id and workflow_id required for workflow unenroll"})
                r = httpx.delete(
                    f"{BASE}/automation/v3/workflows/{workflow_id}/enrollments/contacts/{contact_id}",
                    headers=_headers(), timeout=15
                )
                return ok({"status": "unenrolled", "code": r.status_code})

            elif action == "get_enrollments":
                if not contact_id:
                    return ok({"error": "contact_id required for get_enrollments"})
                return ok(_get(f"/automation/v3/workflows/enrollments/contacts/{contact_id}"))

        elif type == "sequence":
            if action == "list":
                return ok(_get("/crm/v3/objects/sequences", {"limit": 50, "properties": "hs_name,hs_status"}))

            elif action == "enroll":
                if not all([contact_id, sequence_id, sender_email]):
                    return ok({"error": "contact_id, sequence_id, sender_email all required for sequence enroll"})
                return ok(_post("/automation/v3/sequences/enrollments", {
                    "sequenceId": sequence_id,
                    "contactId":  contact_id,
                    "senderEmail": sender_email,
                }))

            elif action == "unenroll":
                if not all([contact_id, sequence_id]):
                    return ok({"error": "contact_id and sequence_id required for sequence unenroll"})
                return ok(_post("/automation/v3/sequences/enrollments/unenroll", {
                    "sequenceId": sequence_id,
                    "contactId":  contact_id,
                }))

        return ok({"error": f"Unknown type/action combination: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 4 — marketing_action
# =============================================================================

@mcp.tool()
def marketing_action(
    type: str,
    action: str,
    name: str = "",
    list_id: str = "",
    form_id: str = "",
    campaign_id: str = "",
    contact_ids: list = [],
    start_date: str = "",
    end_date: str = "",
    limit: int = 20,
    dynamic: bool = False,
) -> str:
    """
    Universal tool for HubSpot Marketing Hub — campaigns, lists, forms, emails.

    type options: campaign | list | form | email

    action options:
      list         — list all (campaigns / lists / forms)
      get          — get one by ID (requires: campaign_id / list_id / form_id)
      create       — create new (requires: name; list also accepts dynamic bool)
      add_contacts — add contacts to a list (requires: list_id + contact_ids)
      submissions  — get form submissions (requires: form_id)

    Examples:
      marketing_action("campaign", "list")
      marketing_action("campaign", "create", name="Q3 Outbound", start_date="2025-07-01")
      marketing_action("list", "list")
      marketing_action("list", "create", name="Web Summit Leads")
      marketing_action("list", "add_contacts", list_id="123", contact_ids=["1","2","3"])
      marketing_action("form", "list")
      marketing_action("form", "submissions", form_id="abc-123")
    """
    try:
        if type == "campaign":
            if action == "list":
                return ok(_get("/marketing/v3/campaigns", {"limit": limit}))
            elif action == "get":
                return ok(_get(f"/marketing/v3/campaigns/{campaign_id}"))
            elif action == "create":
                body: dict = {"name": name}
                if start_date: body["startDate"] = start_date
                if end_date:   body["endDate"]   = end_date
                return ok(_post("/marketing/v3/campaigns", body))

        elif type == "list":
            if action == "list":
                return ok(_get("/contacts/v1/lists", {"count": limit}))
            elif action == "get":
                return ok(_get(f"/contacts/v1/lists/{list_id}"))
            elif action == "create":
                return ok(_post("/contacts/v1/lists", {
                    "name": name, "dynamic": dynamic, "filters": []
                }))
            elif action == "add_contacts":
                if not list_id or not contact_ids:
                    return ok({"error": "list_id and contact_ids required"})
                return ok(_post(f"/contacts/v1/lists/{list_id}/add", {"vids": contact_ids}))

        elif type == "form":
            if action == "list":
                return ok(_get("/marketing/v3/forms", {"limit": limit}))
            elif action == "get":
                return ok(_get(f"/marketing/v3/forms/{form_id}"))
            elif action == "submissions":
                if not form_id:
                    return ok({"error": "form_id required for submissions"})
                return ok(_get(f"/form-integrations/v1/submissions/forms/{form_id}", {"limit": limit}))

        return ok({"error": f"Unknown type/action: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 5 — conversation_action
# =============================================================================

@mcp.tool()
def conversation_action(
    type: str,
    action: str,
    thread_id: str = "",
    contact_id: str = "",
    message_text: str = "",
    channel_id: str = "",
    subscription_type: str = "",
    status: str = "",
    limit: int = 20,
) -> str:
    """
    Universal tool for HubSpot Conversations — inbox threads and communication preferences.

    type options: thread | preferences

    action options for thread:
      list   — list all conversation threads
      get    — get a thread by ID (requires: thread_id)
      send   — send a message to a thread (requires: thread_id + message_text)
      archive — archive a thread (requires: thread_id)

    action options for preferences:
      get    — get communication preferences for a contact (requires: contact_id)
      update — update opt-in/out status (requires: contact_id + subscription_type + status)
               status: SUBSCRIBED | UNSUBSCRIBED | NOT_SPECIFIED

    Examples:
      conversation_action("thread", "list")
      conversation_action("thread", "get", thread_id="123")
      conversation_action("thread", "send", thread_id="123", message_text="Hello!")
      conversation_action("preferences", "get", contact_id="456")
      conversation_action("preferences", "update", contact_id="456", subscription_type="MARKETING", status="UNSUBSCRIBED")
    """
    try:
        if type == "thread":
            if action == "list":
                return ok(_get("/conversations/v3/conversations/threads", {"limit": limit}))
            elif action == "get":
                if not thread_id:
                    return ok({"error": "thread_id required"})
                return ok(_get(f"/conversations/v3/conversations/threads/{thread_id}"))
            elif action == "send":
                if not thread_id or not message_text:
                    return ok({"error": "thread_id and message_text required"})
                return ok(_post(f"/conversations/v3/conversations/threads/{thread_id}/messages", {
                    "type": "MESSAGE", "text": message_text,
                }))
            elif action == "archive":
                if not thread_id:
                    return ok({"error": "thread_id required"})
                return ok(_patch(f"/conversations/v3/conversations/threads/{thread_id}",
                                 {"archived": True}))

        elif type == "preferences":
            if action == "get":
                if not contact_id:
                    return ok({"error": "contact_id required"})
                return ok(_get(f"/communication-preferences/v3/status/email/{contact_id}"))
            elif action == "update":
                if not all([contact_id, subscription_type, status]):
                    return ok({"error": "contact_id, subscription_type, and status all required"})
                return ok(_post("/communication-preferences/v3/subscribe", {
                    "emailAddress":      contact_id,
                    "subscriptionId":    subscription_type,
                    "legalBasis":        "LEGITIMATE_INTEREST_OTHER",
                    "legalBasisExplanation": "Updated via CRM agent",
                }))

        return ok({"error": f"Unknown type/action: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 6 — analytics_action
# =============================================================================

@mcp.tool()
def analytics_action(
    type: str,
    action: str,
    query: str = "",
    event_name: str = "",
    event_properties: dict = {},
    contact_id: str = "",
    date_range: str = "LAST_30_DAYS",
) -> str:
    """
    Universal tool for HubSpot Analytics — reports, behavioral events, GraphQL, forecasts.

    type options: report | event | graphql | forecast

    action options:
      query       — run a GraphQL analytics query (type=graphql, requires: query)
      send_event  — send a behavioral event (type=event, requires: event_name + contact_id)
      list_defs   — list event definitions (type=event)
      get         — get forecasts or reports (type=forecast / report)

    Examples:
      analytics_action("graphql", "query", query="{ contacts { items { id email } } }")
      analytics_action("event", "send_event", event_name="product_viewed", contact_id="123", event_properties={"product":"Pro Plan"})
      analytics_action("event", "list_defs")
      analytics_action("forecast", "get")
    """
    try:
        if type == "graphql":
            if action == "query":
                if not query:
                    return ok({"error": "query required for graphql"})
                return ok(_post("/collector/graphql", {"query": query}))

        elif type == "event":
            if action == "list_defs":
                return ok(_get("/events/v3/event-definitions", {"limit": 50}))
            elif action == "send_event":
                if not event_name or not contact_id:
                    return ok({"error": "event_name and contact_id required"})
                payload: dict = {
                    "eventName": event_name,
                    "objectId":  contact_id,
                    "occurredAt": ts(),
                    "properties": event_properties,
                }
                return ok(_post("/events/v3/send", payload))

        elif type == "forecast":
            if action == "get":
                return ok(_get("/crm/v3/objects/forecasts", {"limit": 20,
                    "properties": "hs_forecast_amount,hs_forecast_category,hs_fiscal_period"}))

        elif type == "report":
            if action == "get":
                return ok(_get("/analytics/v2/reports", {"limit": 20}))

        return ok({"error": f"Unknown type/action: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 7 — cms_action
# =============================================================================

@mcp.tool()
def cms_action(
    type: str,
    action: str,
    article_id: str = "",
    title: str = "",
    content: str = "",
    category_id: str = "",
    language: str = "en",
    limit: int = 20,
) -> str:
    """
    Universal tool for HubSpot CMS — knowledge base articles, domains, files.

    type options: knowledge_base | domain | file

    action options:
      list    — list all items
      get     — get one by ID (requires: article_id)
      create  — create new article (requires: title + content + category_id)
      update  — update article (requires: article_id + optional title/content)
      publish — publish a draft article (requires: article_id)
      archive — archive an article (requires: article_id)

    Examples:
      cms_action("knowledge_base", "list")
      cms_action("knowledge_base", "create", title="How to reset password", content="Go to settings...", category_id="123")
      cms_action("knowledge_base", "publish", article_id="456")
      cms_action("domain", "list")
      cms_action("file", "list")
    """
    try:
        if type == "knowledge_base":
            if action == "list":
                return ok(_get("/cms/v3/knowledge-base/articles", {"limit": limit}))
            elif action == "get":
                return ok(_get(f"/cms/v3/knowledge-base/articles/{article_id}"))
            elif action == "create":
                if not all([title, content, category_id]):
                    return ok({"error": "title, content, and category_id required"})
                return ok(_post("/cms/v3/knowledge-base/articles", {
                    "title":      title,
                    "htmlBody":   content,
                    "categoryId": int(category_id),
                    "language":   language,
                }))
            elif action == "update":
                body: dict = {}
                if title:   body["title"]    = title
                if content: body["htmlBody"] = content
                return ok(_patch(f"/cms/v3/knowledge-base/articles/{article_id}", body))
            elif action == "publish":
                return ok(_patch(f"/cms/v3/knowledge-base/articles/{article_id}",
                                 {"currentState": "PUBLISHED"}))
            elif action == "archive":
                return ok(_patch(f"/cms/v3/knowledge-base/articles/{article_id}",
                                 {"currentState": "ARCHIVED"}))

        elif type == "domain":
            if action == "list":
                return ok(_get("/cms/v3/domains", {"limit": limit}))

        elif type == "file":
            if action == "list":
                return ok(_get("/files/v3/files", {"limit": limit}))

        return ok({"error": f"Unknown type/action: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# TOOL 8 — settings_action
# =============================================================================

@mcp.tool()
def settings_action(
    type: str,
    action: str,
    object_type: str = "contacts",
    user_id: str = "",
    team_id: str = "",
    property_name: str = "",
    property_label: str = "",
    field_type: str = "text",
    group_name: str = "contactinformation",
    pipeline_object: str = "deals",
    limit: int = 100,
) -> str:
    """
    Universal tool for HubSpot Settings — users, teams, owners, properties, pipelines.

    type options: user | team | owner | property | pipeline | currency

    action options:
      list    — list all items
      get     — get one by ID (requires relevant ID param)
      create  — create new property (type=property requires: object_type + property_name + property_label)
      update  — update a user or team

    property field_type options: text | textarea | number | date | select | checkbox | booleancheckbox
    property group_name examples: contactinformation | dealinformation | companyinformation | ticketinformation

    Examples:
      settings_action("owner", "list")
      settings_action("user", "list")
      settings_action("team", "list")
      settings_action("pipeline", "list", pipeline_object="deals")
      settings_action("pipeline", "list", pipeline_object="tickets")
      settings_action("property", "list", object_type="contacts")
      settings_action("property", "create", object_type="contacts", property_name="contract_type", property_label="Contract Type", field_type="select")
      settings_action("currency", "list")
    """
    try:
        if type == "owner":
            if action == "list":
                return ok(_get("/crm/v3/owners", {"limit": limit}))
            elif action == "get":
                return ok(_get(f"/crm/v3/owners/{user_id}"))

        elif type == "user":
            if action == "list":
                return ok(_get("/settings/v3/users", {"limit": limit}))

        elif type == "team":
            if action == "list":
                return ok(_get("/settings/v3/users/teams", {"limit": limit}))
            elif action == "get":
                return ok(_get(f"/settings/v3/users/teams/{team_id}"))

        elif type == "property":
            if action == "list":
                data = _get(f"/crm/v3/properties/{object_type}")
                simplified = [
                    {"name": p.get("name"), "label": p.get("label"),
                     "type": p.get("type"), "fieldType": p.get("fieldType")}
                    for p in data.get("results", []) if not p.get("hidden", False)
                ]
                return ok({"results": simplified, "total": len(simplified)})
            elif action == "create":
                if not all([property_name, property_label]):
                    return ok({"error": "property_name and property_label required"})
                return ok(_post(f"/crm/v3/properties/{object_type}", {
                    "name":      property_name,
                    "label":     property_label,
                    "type":      "string" if field_type in ("text","textarea","select") else field_type,
                    "fieldType": field_type,
                    "groupName": group_name,
                }))

        elif type == "pipeline":
            if action == "list":
                return ok(_get(f"/crm/v3/pipelines/{pipeline_object}"))

        elif type == "currency":
            if action == "list":
                return ok(_get("/settings/v3/currencies"))

        return ok({"error": f"Unknown type/action: {type}/{action}"})

    except httpx.HTTPStatusError as e:
        return ok({"error": f"HubSpot API error {e.response.status_code}", "detail": e.response.text})
    except Exception as e:
        return ok({"error": str(e)})


# =============================================================================
# RESOURCES — app-controlled read-only context
# =============================================================================

@mcp.resource("hubspot://pipelines")
def get_pipelines() -> str:
    """All HubSpot deal pipelines with stage names and IDs.
    Always reference this before creating or moving deals."""
    try:
        data = _get("/crm/v3/pipelines/deals")
        out = []
        for p in data.get("results", []):
            out.append({
                "pipeline_id":   p.get("id"),
                "pipeline_name": p.get("label"),
                "stages": [
                    {"stage_id": s.get("id"), "stage_name": s.get("label"),
                     "probability": s.get("metadata", {}).get("probability")}
                    for s in p.get("stages", [])
                ],
            })
        return json.dumps(out, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("hubspot://ticket-pipelines")
def get_ticket_pipelines() -> str:
    """All HubSpot ticket pipelines with stage IDs.
    Always reference this before creating or updating tickets."""
    try:
        data = _get("/crm/v3/pipelines/tickets")
        out = []
        for p in data.get("results", []):
            out.append({
                "pipeline_id":   p.get("id"),
                "pipeline_name": p.get("label"),
                "stages": [{"stage_id": s.get("id"), "stage_name": s.get("label")}
                           for s in p.get("stages", [])],
            })
        return json.dumps(out, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("hubspot://owners")
def get_owners_resource() -> str:
    """All HubSpot owners (users) with IDs, emails and names.
    Always reference this before assigning deals, tasks or tickets."""
    try:
        data = _get("/crm/v3/owners", {"limit": 100})
        out = [
            {"owner_id": o.get("id"), "email": o.get("email"),
             "name": f"{o.get('firstName','')} {o.get('lastName','')}".strip()}
            for o in data.get("results", [])
        ]
        return json.dumps(out, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("hubspot://contact-properties")
def get_contact_properties() -> str:
    """All valid HubSpot contact property names and types.
    Reference this before creating or updating contacts."""
    try:
        data = _get("/crm/v3/properties/contacts")
        out = [
            {"name": p.get("name"), "label": p.get("label"),
             "type": p.get("type"), "field_type": p.get("fieldType")}
            for p in data.get("results", []) if not p.get("hidden", False)
        ]
        return json.dumps(out, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("hubspot://deal-properties")
def get_deal_properties() -> str:
    """All valid HubSpot deal property names and types.
    Reference this before creating or updating deals."""
    try:
        data = _get("/crm/v3/properties/deals")
        out = [
            {"name": p.get("name"), "label": p.get("label"), "type": p.get("type")}
            for p in data.get("results", []) if not p.get("hidden", False)
        ]
        return json.dumps(out, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# PROMPTS — user-controlled slash commands
# =============================================================================

@mcp.prompt()
def find_contact(identifier: str) -> str:
    """/find_contact <email or name> — Search and show a full contact summary."""
    return f"""
Search HubSpot for a contact matching: "{identifier}"
Use crm_object_action(object_type="contacts", action="search", query="{identifier}")
Present the result as:
─────────────────────────────────────
👤  Name:    [firstname lastname]
📧  Email:   [email]
📞  Phone:   [phone]
🏢  Company: [company]
🆔  ID:      [id]
📊  Status:  [hs_lead_status]
─────────────────────────────────────
If not found say: "No contact found for '{identifier}' in HubSpot."
"""


@mcp.prompt()
def deal_report(stage_filter: str = "") -> str:
    """/deal_report [stage] — Show all deals, optionally filtered by stage."""
    filt = f'Filter to stage: "{stage_filter}"' if stage_filter else "Show all open deals"
    return f"""
{filt}
Use crm_object_action(object_type="deals", action="list") or action="search".
Present as a table:
──────────────────────────────────────────────────────
Deal Name          | Amount    | Stage         | Close
──────────────────────────────────────────────────────
[dealname]         | $[amount] | [stage]       | [date]
──────────────────────────────────────────────────────
At the bottom:
  Total deals: X
  Total pipeline value: $X
"""


@mcp.prompt()
def create_contact_flow(email: str) -> str:
    """/create_contact_flow <email> — Guided contact creation with duplicate check."""
    return f"""
User wants to create a HubSpot contact with email: {email}
Step 1: crm_object_action("contacts", "search", query="{email}") to check for duplicates.
Step 2: If exists — show their details and ask if user wants to update instead.
Step 3: If not — ask for first name, last name, phone, company one at a time.
Step 4: crm_object_action("contacts", "create", properties={{...}})
Step 5: Confirm: "✅ Contact created! ID: [id]"
"""


@mcp.prompt()
def contact_summary(contact_id: str) -> str:
    """/contact_summary <contact_id> — Full 360° CRM summary for a contact."""
    return f"""
Pull a full CRM summary for contact ID: {contact_id}
Step 1: crm_object_action("contacts", "get", object_id="{contact_id}")
Step 2: crm_object_action("deals", "search", query="[contact company name]")
Step 3: crm_object_action("tickets", "search", query="[contact name]")
Step 4: engagement_action("note", "get_timeline", contact_id="{contact_id}")
Present as:
═══════════════════════════════════════
  CONTACT SUMMARY — HubSpot CRM
═══════════════════════════════════════
👤 [Full Name]  📧 [email]  📞 [phone]
🏢 [company]

💰 DEALS ([count])
  • [deal name] — $[amount] — [stage]

🎫 TICKETS ([count])
  • [subject] — [priority] — [status]

📋 RECENT ACTIVITY
  [last 3 engagements from timeline]
═══════════════════════════════════════
"""


@mcp.prompt()
def pipeline_overview() -> str:
    """/pipeline_overview — Full pipeline breakdown by stage with values."""
    return """
Get a full sales pipeline overview.
Step 1: settings_action("pipeline", "list", pipeline_object="deals") — get all stages
Step 2: crm_object_action("deals", "list", limit=100) — get all deals
Step 3: Group deals by stage and sum amounts.
Present as:
═══════════════════════════════════════
  PIPELINE OVERVIEW — HubSpot CRM
═══════════════════════════════════════
Stage              | Deals | Total Value
───────────────────|───────|────────────
[stage name]       |  [n]  | $[value]
───────────────────|───────|────────────
TOTAL PIPELINE: $[grand total]
═══════════════════════════════════════
"""


@mcp.prompt()
def log_call_flow(contact_identifier: str) -> str:
    """/log_call_flow <name or email> — Guided call logging with follow-up task."""
    return f"""
User wants to log a call for: "{contact_identifier}"
Step 1: crm_object_action("contacts", "search", query="{contact_identifier}") — get contact ID
Step 2: Ask — "How long was the call? (minutes)"
Step 3: Ask — "Outcome? (Connected / Left voicemail / No answer)"
Step 4: Ask — "Any notes or action items from the call?"
Step 5: engagement_action("call", "create", contact_id="[id]", body_text="[notes]", duration_seconds=[n], call_outcome="[outcome]")
Step 6: Ask — "Want to create a follow-up task?"
Step 7: If yes → engagement_action("task", "create", subject="Follow up", due_date="...", contact_id="[id]")
Confirm: "✅ Call logged on [contact name]'s record."
"""


@mcp.prompt()
def ticket_triage(priority: str = "HIGH") -> str:
    """/ticket_triage [priority] — List and triage tickets by priority."""
    return f"""
Find all open HubSpot tickets with priority: {priority}
Use crm_object_action("tickets", "search", query="{priority}") or action="list".
Present triage list:
🎫 [subject] | Priority: [priority] | Owner: [owner] | Stage: [stage]
Then ask: "Would you like to escalate, reassign, or resolve any of these?"
If escalate → crm_object_action("tickets", "update", object_id="[id]", properties={{"hs_ticket_priority":"URGENT"}})
If reassign → crm_object_action("tickets", "update", object_id="[id]", properties={{"hubspot_owner_id":"[owner_id]"}})
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
