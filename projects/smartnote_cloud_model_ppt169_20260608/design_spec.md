# SmartNoteCloud Cloud Computing Report - Design Spec

> Human-readable design narrative for a 15-slide Vietnamese Cloud Computing report deck. Machine-readable execution contract lives in `spec_lock.md`.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | SmartNoteCloud / MindDeckNote Lite Cloud Report |
| **Canvas Format** | PPT 16:9 (1280x720) |
| **Page Count** | 15 slides |
| **Design Style** | General Consulting + cloud architecture visual report |
| **Target Audience** | Giang vien va sinh vien mon Cloud Computing |
| **Use Case** | Bao cao project cuoi ky: trinh bay kien truc, quy trinh deploy, IaaS/PaaS/SaaS va ket qua demo |
| **Created Date** | 2026-06-08 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280x720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 56px, top 42px, bottom 38px |
| **Content Area** | 1168x640 |

---

## III. Visual Theme

### Theme Style

- **Style**: General Consulting + cloud architecture visual report
- **Theme**: Light theme
- **Tone**: professional, cloud-native, technical but presentation-friendly

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#F8FAFC` | Nen chinh sach, sang, de doc |
| **Secondary bg** | `#FFFFFF` | Card, module, container |
| **Primary** | `#2563EB` | IaaS / EC2 / infrastructure |
| **Accent** | `#00A676` | SaaS / AI API / ket qua tot |
| **Secondary accent** | `#F59E0B` | PaaS / alternative / diem can chu y |
| **Body text** | `#0F172A` | Text chinh |
| **Secondary text** | `#475569` | Caption, note |
| **Tertiary text** | `#94A3B8` | Footer, page number |
| **Border/divider** | `#CBD5E1` | Border, connectors |
| **Success** | `#16A34A` | Health OK, HTTPS OK |
| **Warning** | `#DC2626` | Risk / security warning |

### AI Image Strategy

- **Image Rendering**: `3d-isometric`
- **Image Palette**: `cool-corporate`
- **Use**: AI raster images are optional hero/support assets for cover and model-intuition pages. Core architecture, arrows, labels, tables and process diagrams remain SVG-native for editability and accuracy.

---

## IV. Typography System

### Font Plan

**Typography direction**: Vietnamese technical report, PPT-safe modern sans with monospace for terminal/config snippets.

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks**:

- Title: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: `"Microsoft YaHei", Arial, sans-serif`
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

**Baseline**: Body font size = 18px

| Purpose | Ratio to body | Current Project | Weight |
| ------- | ------------- | --------------- | ------ |
| Cover title | 3.2-4.0x | 60-72px | Bold |
| Page title | 1.8-2.3x | 34-42px | Bold |
| Subtitle | 1.2-1.5x | 22-27px | SemiBold |
| **Body content** | **1x** | **18px** | Regular |
| Annotation / caption | 0.75-0.9x | 14-16px | Regular |
| Code / terminal | 0.78-0.9x | 14-16px | Regular |

Formula rendering policy: `text-only` because this deck has no mathematical formula.

---

## V. Layout Principles

### Page Structure

- **Header area**: 42-92px, title + short section label.
- **Content area**: 500-570px, diagram/table/cards.
- **Footer area**: 30px, page number and project label.

### Layout Pattern Library

- Architecture pages use left-to-right system flow with colored service-model zones.
- IaaS/PaaS/SaaS pages use three-tier comparison cards and layered stack diagrams.
- Evidence pages use terminal-style proof blocks with status chips.
- Result and conclusion pages use high-contrast takeaway panels.

### Spacing Specification

| Element | Current Project |
| ------- | --------------- |
| Safe margin from canvas edge | 56px |
| Content block gap | 24-36px |
| Icon-text gap | 10px |
| Card gap | 20-28px |
| Card padding | 22-28px |
| Card border radius | 14px |

---

## VI. Icon Usage Specification

### Source

- **Built-in icon library**: `tabler-outline`
- **Stroke width**: 2
- **Usage method**: SVG placeholder `<use data-icon="tabler-outline/icon-name" .../>`

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| Browser / user entry | `tabler-outline/browser` | P05, P06 |
| EC2 / server | `tabler-outline/server` | P05, P07, P09 |
| Docker / container | `tabler-outline/brand-docker` | P07, P08 |
| Nginx / gateway | `tabler-outline/route` | P05, P06 |
| Database | `tabler-outline/database` | P05, P13 |
| Cloud / SaaS | `tabler-outline/cloud-computing` | P10-P12 |
| API | `tabler-outline/api` | P11 |
| Security | `tabler-outline/shield-lock` | P14 |
| User | `tabler-outline/user` | P02, P03 |
| Layers | `tabler-outline/layers-linked` | P08-P12 |

---

## VII. Visualization Reference List

No external chart template is required. All charts/diagrams are free-designed SVG-native:

- P05: end-to-end architecture map.
- P06: request flow pipeline.
- P07: deployment flow.
- P08: Docker container network.
- P09-P12: IaaS/PaaS/SaaS model mapping.
- P13: entity relationship/data flow diagram.

Runners-up considered:

- `timeline_horizontal` rejected for P07 because deployment is better shown as infrastructure pipeline plus service responsibilities.
- `pyramid` rejected for P12 because the service model comparison needs equal-width columns, not hierarchy.
- `flowchart` template rejected for P06 because custom SVG flow needs mixed technical labels and security markers.

---

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference | text_policy | page_role |
| -------- | ---------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- | ----------- | --------- |
| cover_cloud_architecture.png | 1672x941 | 1.78 | Cover hero cloud architecture atmosphere | Background | #1 full-bleed background with floating title | ai | Generated | 3D isometric cloud architecture with browser, domain, EC2, Docker, Nginx, PostgreSQL and AI API cloud; no text; cool corporate palette | none | hero_page |
| iaas_paas_saas_layers.png | 1672x941 | 1.78 | Intuitive layered service model illustration | Diagram | #44 background image + native architecture diagram | ai | Generated | 3D isometric layered stack: IaaS foundation, PaaS managed platform middle, SaaS/API service top; no labels or text | none | hero_page |
| secure_request_flow.png | 1672x941 | 1.78 | Security/request mechanism support visual | Diagram | #44 background image + native network/architecture diagram | ai | Generated | Isometric secure request path with browser, HTTPS gateway, backend shield, private database, external AI cloud; no text | none | local |

> Note: AI prompts are saved in `images/image_prompts.json` and rendered to `images/image_prompts.md`. The three generated PNGs are used as visual support, while core labels/arrows remain SVG-native for clarity and editability.

---

## IX. Content Outline

| Page | Title | Rhythm | Key Message | Visual Plan |
| ---- | ----- | ------ | ----------- | ----------- |
| P01 | SmartNoteCloud / MindDeckNote Lite | anchor | Project cloud-native cho ghi chu AI va flashcard | Cover with AI-style isometric/SVG architecture motif |
| P02 | Van de & dong luc | dense | Hoc Cloud can ung dung co deploy that, co AI va du lieu | Problem-solution split |
| P03 | Tong quan san pham | dense | Notes, AI summary, flashcards, review, dashboard | Feature map |
| P04 | Chuc nang chinh | dense | Workflow nguoi dung tu note den on tap | Four capability cards |
| P05 | Kien truc tong the | dense | Browser -> Nginx -> React/FastAPI -> PostgreSQL/Mimo | End-to-end architecture |
| P06 | Luong request | dense | Frontend request va API request di khac duong | Request pipeline |
| P07 | Quy trinh deploy tren AWS | dense | DNS/HTTPS vao EC2, Docker Compose chay service | Deployment pipeline |
| P08 | Containerization Design | dense | Moi thanh phan la container rieng trong Docker network | Container network map |
| P09 | IaaS: AWS EC2 | dense | EC2 cung cap may ao; team tu quan ly OS/Docker/runtime | IaaS responsibility card |
| P10 | PaaS: huong nang cap | dense | Elastic Beanstalk/App Runner co the quan ly platform nhieu hon | Current vs PaaS comparison |
| P11 | SaaS/API: Mimo AI API | dense | App dung AI API san co, khong quan ly model/GPU | External API interaction |
| P12 | Mapping IaaS/PaaS/SaaS | anchor | Ba mo hinh cloud duoc phan biet bang muc do quan ly | 3-column service model summary |
| P13 | Database & data flow | dense | User -> workspace -> pages/blocks/decks/cards/reviews | ER/data flow diagram |
| P14 | Security & operations | dense | HTTPS, JWT, bcrypt, private DB, SSH tunnel, env secrets | Security proof board |
| P15 | Ket qua & huong phat trien | anchor | Domain HTTPS hoat dong; co the nang cap RDS/LB/CI/CD | Result + roadmap |

---

## X. Speaker Notes Strategy

Each slide has concise Vietnamese speaker notes: 2-4 sentences, suitable for oral report. Notes emphasize:

- What is deployed and how requests flow.
- Which components map to IaaS/PaaS/SaaS.
- Why PostgreSQL is private and why Nginx is the public entrypoint.
- What evidence proves the deployment works.

---

## XI. Technical Constraints

- SVG canvas must be `1280x720`.
- Avoid `rgba()`, `<style>`, `class`, `<foreignObject>`, `<script>`, animation tags.
- Use raw Unicode arrows only when needed; escape XML-reserved characters.
- Keep all core labels in SVG, not raster images.
- Use only colors/fonts/icons listed in `spec_lock.md`.
