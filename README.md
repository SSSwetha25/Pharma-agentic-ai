# Agentic AI for Pharmaceutical Innovation

An Agentic AI–based decision support system that accelerates early-stage pharmaceutical research by decomposing complex strategy questions into coordinated, domain-specific analyses.

---

## 📌 Project Overview

Pharmaceutical companies aiming to move beyond low-margin generics often explore **value-added and repurposed drug opportunities**. However, identifying such opportunities requires extensive manual research across clinical trials, patents, and market data—often taking months.

This project presents an **Agentic AI–based research assistant** that demonstrates how such analysis can be **modularized, automated, and synthesized** using an agent-oriented architecture.

The system accepts a high-level research query and coordinates multiple specialized agents to generate structured insights and a consolidated research report.

---

## 🎯 Key Objectives

- Demonstrate an **Agentic AI architecture** using a Master–Worker agent model  
- Reduce time and effort required for early-stage opportunity evaluation  
- Enable interactive exploration of pharma research questions  
- Generate structured outputs suitable for decision support  
- Showcase a scalable architecture extensible to real APIs and LLMs  


## 🧱 Architecture

The project follows a **Master–Worker agentic** architecture tailored for pharma research workflows.

```text
User Query
   ↓
Master Agent (planner/orchestrator)
   ↓
+-----------------------------+
|  Clinical Evidence Agent    |
|  Patent & IP Agent          |
|  Market & Competition Agent |
+-----------------------------+
   ↓
Aggregator / Synthesizer
   ↓
Structured Research Report
```
## Getting Started

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

```bash
git clone https://github.com/SSSwetha25/Pharma-agentic-ai.git
cd Pharma-agentic-ai
pip install -r requirements.txt
```
Running the App

```bash
python app.py
```
