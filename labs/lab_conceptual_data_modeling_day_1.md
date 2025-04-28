# 🧠 Conceptual Data Modeling — Day 1

> This lab focuses on the foundational phase of **conceptual data modeling**, emphasizing the importance of business context, metric brainstorming, metric classification (leading/lagging), data source identification, and estimation of data collection effort.  
> The output is a structured conceptual data model, setting up the path for logical and physical modeling in subsequent steps.

---

## 🏷️ 1️⃣ Title: *Project Goal Statement*

Set a clear, business-oriented title for your conceptual data model that frames the purpose and outcome of the analytics initiative.

**Example:**
> “Living Your Best Life Data Model”  
> *(The goal is to measure and improve quality of life using quantifiable data.)*

*→ Define your own title based on the specific business question or outcome you want to enable.*

---

## 🧮 2️⃣ Brainstorm Metrics

Identify all possible metrics (quantitative and qualitative) that relate to your chosen title or business problem.  
Aim for a broad, creative list—include direct outcomes, inputs, behaviors, and supporting context.

**Example Metrics:**
- Sleep per night
- Income
- Net worth
- Healthy food eaten
- Time spent in nature
- Remote working
- Weight
- Calories in vs. calories burnt
- ... *(etc.)*

---

## 🗂️ 3️⃣ Group Metrics by Categories

Cluster your metrics into coherent groups or business domains (e.g., Physical Health, Mental Health, Financial Health, Social Health, Productivity, Quality of Life).  
This helps with stakeholder conversations and aligns your data model with real-world processes.

**Example Categories:**
1. Physical Health
2. Mental Health
3. Financial Health
4. Social Health
5. Productivity
6. Quality of Life

List which metrics belong to each category.

---

## ⏩ 4️⃣ Classify Metrics: Leading vs. Lagging

For each metric, determine if it’s a **Leading** or **Lagging** indicator:
- **Leading Metrics:** Change frequently, predictive, actionable in the short term.
- **Lagging Metrics:** Reflect outcomes, change more slowly, result from leading metrics.

**Example Classification:**
- **Physical Health**
    - Calories in vs calories burnt *(Leading)*
    - Cardiovascular health *(Lagging)*
    - Weight *(Lagging)*
    - Hours exercising *(Leading)*
    - etc.

*Note*: Maintaining a balance between leading and lagging metrics is crucial for actionable analytics.

---

## 🛠️ 5️⃣ Data Availability & Sources

Assess the **ease** of accessing data for each metric/category, and identify potential data sources:
- *Easy*: Direct system exports, apps, trackers.
- *Medium*: External sources, manual aggregation.
- *Hard*: Surveys, infrequent data, third-party required.

**Example:**
- Fitness tracker *(Easy)*
- Smart scale *(Easy)*
- Tax returns *(Medium)*
- Talking with your spouse *(Difficult)*

---

## ⏳ 6️⃣ Data Collection Time Estimate

Estimate how long it would take to collect/process the data for each category, based on the sources and complexity.  
Discuss with stakeholders to align data engineering effort, parallelization possibilities, and project value.

**Example:**
- Physical Health *(1 month)*
- Financial Health *(1 month)*
- Social Health *(1 month)*
- Mental Health, Quality of Life *(Out of scope for this iteration)*

---

## 🔜 Next Step

Move from **conceptual** to **logical and physical modeling** based on the structured metric map above.

---

### **Summary Table Example** (for your project):

| Category         | Metric                          | Type      | Data Source         | Ease   | Time Estimate |
|------------------|--------------------------------|-----------|---------------------|--------|--------------|
| Physical Health  | Sleep per night                | Leading   | Fitness tracker     | Easy   | 1 month      |
| Financial Health | Income                         | Leading   | Tax return, payroll | Medium | 1 month      |
| Productivity     | Productive days                | Lagging   | Work calendar       | Easy   | 1 month      |
| ...              | ...                            | ...       | ...                 | ...    | ...          |

---

> **This conceptual data model ensures you start your analytics initiative with clear business value, measurable outcomes, and actionable engineering steps.**
