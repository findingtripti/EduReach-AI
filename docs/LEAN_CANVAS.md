# Lean Canvas: EduReach AI

**Positioning:** an early-stage prototype and decision-support concept built as an academic project. It is not an officially adopted government platform. There are no customers, partners, revenue or field deployments.

| Block | Content |
|---|---|
| **1. Problem** | School access is often judged by whether a school exists or is near on a map. Villages with no recorded local school, or with a school that is hard to reach, can be missed. Planners lack a simple, transparent screening view at village level. Existing alternative: spreadsheets and school-count tables. |
| **2. Customer segments (proposed, not actual)** | Education planners and block/district administrators; researchers; education-focused NGOs. No user has adopted the tool. |
| **3. Unique value proposition** | An open, explainable village-level screening view of school accessibility: a transparent index, an honest unsupervised grouping, a map, a "why flagged" breakdown and a clearly labelled what-if simulator. |
| **4. Solution** | Streamlit dashboard: accessibility index, GMM patterns, interactive map, per-village explanation, hypothetical scenarios, built-in data checks and documented limitations. |
| **5. Channels (possible)** | Open-source code repository, demonstration to a faculty or local-administration audience, academic report. Nothing has been deployed. |
| **6. Revenue streams / sustainability** | None today. If it continued: academic or grant funding, or free open-source use by public bodies and NGOs. No revenue is claimed. |
| **7. Cost structure** | Developer time, data collection and cleaning, hosting for a web version, and field validation visits if pursued. |
| **8. Key metrics** | Share of flagged villages confirmed or rejected by field checks; match rate of villages and schools; usefulness rating from planners in pilot reviews; time saved in screening. None has been measured yet. |
| **9. Unfair advantage** | None claimed. Its only edge is that it is transparent and reproducible, with limitations stated up front. |

## Potential public benefit

A shortlist of villages for closer review can focus scarce attention where school access is least documented.

## Adoption pathway (proposed)

1. Confirm data sources and refresh the data with the owning departments.
2. Replace straight-line distance with road-network travel time.
3. Validate flagged villages in the field and report errors.
4. Pilot with one block office or NGO and collect feedback.

## Requirements for responsible real-world use

Data permissions and freshness checks, field validation before decisions, clear communication that labels are screening aids, review of the weights with domain experts, privacy safeguards if finer data are added, and a process to correct mistakes.
