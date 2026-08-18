"If you fail to plan, you are planing to fail"

# 10-Week Rollout Checklist

**Goal:** Move from "Chaos" to "Controlled Operating System" without disrupting daily operations.

---

## Phase 0: Discovery & Validation (Weeks 1-2)

- [ ] **Week 1:** Print the Business Model Canvas. Schedule 45-min CEO meeting.
- [ ] **Week 1:** Conduct the CEO meeting. Get sign-off on the 9-block canvas.
- [ ] **Week 2:** Conduct technician interviews (4 techs, 60 mins each).
- [ ] **Week 2:** Transcribe interview insights. Map to plugin library.

---

## Phase 1: Historical Data Test (Week 3-4)

- [ ] **Week 3:** Pull 5-10 historical projects (mix of profitable and unprofitable).
- [ ] **Week 3:** Fill the `historical_data_template.xlsx` with extracted data.
- [ ] **Week 4:** Install Python and dependencies (pandas, matplotlib, openpyxl).
- [ ] **Week 4:** Run `costing_engine.py` and `validation_grid.py`.
- [ ] **Week 4:** Review the 2x2 grid. Identify bottom-right quadrant projects.

---

## Phase 2: Calibration & Refinement (Week 5-6)

- [ ] **Week 5:** Present findings to CEO. Adjust `base_modules.csv` and `plugins_catalog.csv` based on real data.
- [ ] **Week 5:** Calculate the correct `BURDEN_RATE` using actual payroll data.
- [ ] **Week 6:** Refine the Python scripts. Ensure margin calculations match CEO's expectation.

---

## Phase 3: Paper Pilot (Week 7-8)

- [ ] **Week 7:** Print 100 copies of the Farsi Technician Daily Log form.
- [ ] **Week 7:** Train technicians (15 mins) on how to fill the form (2-minute rule).
- [ ] **Week 8:** Collect forms weekly. Manually input data into Excel template.
- [ ] **Week 8:** Run weekly reports. Compare 5 new projects against the model.

---

## Phase 4: Digital Transition (Week 9-10)

- [ ] **Week 9:** Install PostgreSQL locally. Execute `ddl_schema.sql`.
- [ ] **Week 9:** Build the frontend PWA (follow the Application Prompt).
- [ ] **Week 10:** Deploy the app to a test server. Onboard 2 technicians to pilot.
- [ ] **Week 10:** Live pilot with 5 projects. Validate against the paper forms.

---

## Phase 5: Go-Live (Week 11+)

- [ ] **Week 11:** Train all technicians on the app.
- [ ] **Week 11:** Sunset the paper forms.
- [ ] **Week 12:** CEO reviews the first full month of digital data.
- [ ] **Week 12:** Plan Phase 2 (Financial Integration & Notifications).

---

**⚠️ CRITICAL: DO NOT SKIP PHASE 0-2.** The app is useless if the financial model is wrong.