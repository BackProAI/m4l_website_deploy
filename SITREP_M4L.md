# M4L Website Admin Button - Situation Report
**Date:** January 28, 2026  
**Status:** ⚠️ Planning & Requirements Gathering

---

## Executive Summary

Frazer Walker needs an **admin entry point** on the public Mortgage for Life (M4L) marketing site (https://www.mlfs.com.au) that securely routes internal staff to the existing M4L web application with login enforcement. The current public site is hosted on WordPress (likely managed hosting with limited code control), so the change must be coordinated through both **content updates** (adding the admin button) and **infrastructure updates** (DNS + A-record adjustments) to ensure the new admin experience resolves correctly to the M4L app stack.

**Objective:**
- Add an "Admin" button or call-to-action on mlfs.com.au that opens the authenticated M4L application. 
- Configure DNS so admin.mlfs.com.au (or equivalent) points to the M4L admin system.
- Keep scope open for upcoming model integrations that will augment the admin experience (details pending).

---

## Architecture Overview

### Current Landscape
```
mlfs.com.au (WordPress/Marketing) --> hosted by external provider (TBD)
M4L Admin Web App --> existing system (Next.js/Node backend) behind current DNS entries
DNS Provider --> pending confirmation (likely Cloudflare, Route53, or registrar panel)
```

### Target State (Phase 1)
```
[Visitor] -> mlfs.com.au (WordPress)
              └─> New Admin Button
                    └─> admin.mlfs.com.au (A record) -> M4L Admin App (login required)
```

### Key Components
- **WordPress Theme/Template**: Needs UI update (header + hero CTA) to surface Admin entry point without disrupting public funnels.
- **Admin Button Behavior**: 
  - Desktop: persistent header/link.
  - Mobile: accessible via menu or sticky button.
  - Launches the secure M4L login page in same tab (preferred) or new tab if technical constraints.
- **DNS Management**: Create/update `admin.mlfs.com.au` pointing to the M4L admin infrastructure IP (new A record). Optionally introduce `admin-api.mlfs.com.au` for API segregation.
- **M4L Admin Stack**: Already functional; must accept requests via the new hostname and enforce HTTPS + login.

---

## Current Configuration & Gaps

| Area | Status | Notes |
|------|--------|-------|
| WordPress Access | 🔄 Pending | Need admin credentials or contact to edit navigation/template |
| Admin Button UX | 🟥 Not implemented | No entry point exists on mlfs.com.au |
| DNS Ownership | 🔄 Pending | Need registrar/provider details to add A record |
| SSL Certificates | ⚠️ Unknown | Must ensure admin.mlfs.com.au gets valid cert (via hosting or reverse proxy) |
| M4L Admin Hostname | 🟥 Not configured | App currently served via internal URL/IP |

---

## Required Workstreams (Phase 1)

1. **Site Content Update (WordPress)**
   - Identify theme/header template or page builder section controlling top navigation.
   - Add "Admin" button styled consistently with brand (primary color, clear callout).
   - Optionally add short descriptor text in hero/footer for clarity ("Internal access for advisors").

2. **DNS & Networking**
   - Confirm DNS host (likely registrar or Cloudflare).
   - Create new A record `admin.mlfs.com.au` → public IP of M4L admin environment.
   - Validate propagation and update firewalls/load balancers to trust new host header.
   - Plan for SSL provisioning (Let’s Encrypt, ACM, etc.).

3. **M4L Admin App Readiness**
   - Configure application to recognize `admin.mlfs.com.au` as allowed origin/host.
   - Ensure login page enforces authentication and optionally MFA.
   - Validate redirect behavior after login when accessed via new hostname.

4. **Operational Runbook**
   - Document how to update the Admin button content in WordPress.
   - Capture DNS change steps, rollback instructions, and verification checklist.
   - Prepare communication for stakeholders before/after change.

---

## Dependencies & Assumptions

- WordPress hosting allows either direct theme editing or custom menu link injection.
- M4L admin infrastructure already exposes a stable IP/endpoint ready for public DNS routing.
- SSL termination can be handled where the M4L admin app is deployed (reverse proxy, CDN, or app server).
- No current SSO integration; existing login form remains intact.
- Additional model integration requirements will follow; document is intentionally open-ended to accommodate future sections.

---

## Immediate Next Actions

1. **Access & Ownership**
   - Confirm who controls mlfs.com.au DNS and WordPress admin credentials.
   - Inventory existing DNS records to avoid regressions.

2. **Design Decision**
   - Decide placement and styling of Admin button (header vs hero vs footer).
   - Create quick mock or screenshot annotation for stakeholder approval.

3. **Technical Preparation**
   - Obtain M4L admin application endpoint/IP and confirm authentication flow.
   - Validate that the app can serve correct TLS certificate once new hostname points to it.

4. **Change Plan Draft**
   - Outline maintenance window (if needed), DNS TTL adjustments, and verification tests.

---

## Testing Plan (To Be Elaborated)

| Test | Description | Status |
|------|-------------|--------|
| WordPress UI Check | Ensure Admin button renders on desktop & mobile | Pending |
| DNS Propagation | Validate admin.mlfs.com.au resolves globally | Pending |
| SSL Validation | Confirm certificate issued & browser shows secure padlock | Pending |
| Login Redirect | Ensure admin button leads to login screen and access is restricted | Pending |
| Regression | Verify public pages unaffected post-change | Pending |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incorrect DNS change | Admin access outage or misrouting | Lower TTL, stage change during low-traffic window, pre-validate IP |
| WordPress theme conflicts | UI breakage or lost customizations | Backup theme, implement via child theme/custom HTML block |
| SSL misconfiguration | Browser warnings, blocked access | Pre-issue certificate, use automated ACME where possible |
| Unauthenticated exposure | Sensitive admin features exposed publicly | Confirm login requirement before publishing link |

---

## My Money Page Chatbot Scope

**Target Surface:** https://www.mlfs.com.au/the-more4life-process/my-money/

**Experience Goals:**
- Embed a guided chatbot or decision-tree widget inside the "My Money" section so clients can upload their current managed fund portfolio (PDF, Excel, or Word) and receive a contextual analysis.
- Present a fixed sequence of drop-down questions to capture investor profile before analysis.
- Ensure model responses stay neutral and advisory-safe (no statements that a client portfolio is "bad" or fails compliance).

**Question Flow (mandatory order):**
1. What type of investor are you? (High Growth, Growth, Balanced, Conservative, Defensive)
2. What phase are you in? (Accumulation, Investment/Non-super, Pension)
3. How old are you? (Under 40, 40-60, 60-80, 80+)
4. Give me a commentary on each managed fund for the portfolio? (Yes, No)
5. Are these funds value for money? (Yes, No)
6. Would you like to discuss results with us? (Yes, No)

**Data Handling Requirements:**
- Accept portfolio attachments in PDF, XLS/XLSX, and DOC/DOCX formats; enforce size and malware scanning policies prior to LLM ingestion.
- Send uploaded documents plus structured answers to the backend analysis model; log consent for compliance.
- Responses must highlight insights, comparisons, and next steps without negative judgements about the client's holdings.

**Implementation Considerations:**
- UI should align with the existing WordPress theme; consider iframe, shortcode, or embedded React micro-app depending on hosting constraints.
- Provide fallbacks for users who decline file upload (e.g., prompt to book a consultation).
- Capture analytics events (e.g., GA4) for each question completion and file upload success/failure.
- Prepare privacy copy explaining how uploaded data is stored and processed.

**Next Steps:**
- Validate which chatbot framework (custom API, Dialogflow, Azure OpenAI, etc.) best supports document ingestion with deterministic prompts.
- Draft UX wireframes/mockups for approval before development.
- Coordinate with compliance to review scripted language and output guardrails.

---

## Open Items / Future Enhancements

- **Model Integration Placeholder:** Awaiting details on additional model to embed within the admin experience; dedicate a new section once requirements provided.
- **Monitoring & Analytics:** Decide whether to track admin button usage (Google Analytics events, server logs).
- **Access Controls:** Explore IP allow-listing or VPN requirement for admin hostname as a defense-in-depth measure.

---

## References & Contacts

- **Public Site:** https://www.mlfs.com.au
- **M4L Admin System:** Internal URL/IP (TBD) – requires login
- **Stakeholders:** Marketing (WordPress content), IT/Infra (DNS), Product (M4L app owners)

---

*Document intentionally left open-ended for upcoming model integration scope.*
