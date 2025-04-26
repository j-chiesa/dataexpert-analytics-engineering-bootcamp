# 🧠 Conceptual Data Modeling — Day 1

> A table schema is **not** where data modeling begins!  
> Conceptual modeling starts *before* thinking about tables or columns, focusing on understanding business needs and capturing the big picture.

---

## 🏗️ Conceptual Data Modeling Layers

### 1. **Conceptual**

- Think of this as a *brainstorm* phase.
- There are two project types:
    - **Greenfield Project**: Built *from scratch*, no constraints, maximum flexibility for design and technology choices.
    - **Brownfield Project**: Built on *top of existing systems*—requires integrating or modifying legacy infrastructure, so careful adaptation is needed to avoid disruptions.

### 2. **Logical**

- Focus on *relationships*.
- Define what data you need to track and *how things are related*.
- Tools: Entity-Relationship Diagrams (ERD), primary keys, foreign keys, relationship mapping.

### 3. **Physical**

- Now, think about *tables and columns*.
- Actual database structure and implementation.

---

## 🧑‍🤝‍ Stakeholder Feedback in Pipeline Brainstorming

- Always gather feedback from all **relevant stakeholders**—including people from other departments or teams!
    - **First-line stakeholders** (*easiest* to get feedback from): Analysts, Engineers, Scientists, Product Managers.
    - **Second-line stakeholders** (*harder* to reach): Customers, Executives.

> Missing a stakeholder = missing a *critical* requirement.  
> Including an irrelevant stakeholder = potentially wasting time and resources.

- Take your time in this phase—**avoids costly rebuilds later!**
- *Question costly requirements* to avoid overengineering.

---

> The essence of good design is not what you add, it’s what you intentionally leave out.

- Identify **false requirements** or **overly-ambitious requirements** early.
- Constraints are powerful—they help you focus and deliver value.

> Just because you *can* process tons of data, doesn’t mean you *should*.

- **Value, Velocity, Volume, Variety** — Typically, you only need to focus on one or two. Trying to optimize for all leads to *complicated* and hard-to-maintain systems.

---

### 🚨 The Brainstorm Isn’t Always Right!

- Brainstorms can be *overly ambitious* (see: Netflix example).
- Or, ideas might be *too vague* or *impossible* to source data for.
- That’s okay—just *communicate* these issues to stakeholders, so expectations are clear.

---

## 🔁 Work Backwards from Metrics

- Start brainstorming by asking: *“Ideally, what do we want to measure?”*
- Allow blue-sky thinking (*“If we had unlimited capacity, what would we want?”*) to discover the *true north star* metrics.
- Your job as a Data/Analytics Engineer is to then introduce constraints and focus the project (but *not* during the brainstorming!).
    - **Metrics → Data Sets → Master Data (physical) → OLAP Cubes → Metrics**

---

## 👥 Who Should Brainstorm with You?

- **Value and usage** should determine the *weight* of stakeholder input.
    - If Bob the analyst only runs one query a year, don’t re-architect for him—*unless* that one query supports a $100M business decision!
- Focus on *power users*—but don’t ignore others, as sometimes even power users don’t know what they need.
- As technical users, you must gather *business user input*.

---

## 📋 Requirements Matrix

|                           | Requirement is *necessary* | Requirement is *unnecessary*         |
|---------------------------|---------------------------|--------------------------------------|
| **Truly necessary**       | 😊 Happiness!             | 😢 Pain: backfills, pipeline rework, incomplete data |
| **Not truly necessary**   | 🐌 Slow pipelines, overly-complex models, delays | 😊 Happiness!         |

- **Always ask for context** on every column—question *why* it’s needed.
- Get stakeholders to *rank* their priorities.

---
