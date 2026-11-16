# 🛡️ Yemen E-Wallet Fraud Detection System

> **An advanced, real-time hybrid machine learning system designed to detect financial fraud in Yemeni E-Wallets (Jaib, Jawali, Alkuraimi, Cash, etc.).**

---

##  About The Project

This project simulates a real-world fraud detection system for the Yemeni financial sector. Since real financial data is highly sensitive and unavailable, a robust **Synthetic Data Generator** was built to simulate **500,000 transactions** across **50,000 customers**, covering various fraud typologies:

*   Account Takeover (ATO)
*   Money Laundering
*   Mule Accounts
*   Geographic Anomalies

The core intelligence is an **XGBoost Classifier** trained on time-series data with strict prevention of data leakage. To handle the limitations of synthetic data, a **Rule-Based Security Engine** (Business Rules) was integrated to ensure high-risk transactions are intercepted, mirroring the "Hybrid Approach" used by global payment processors (e.g., Visa, PayPal).

---

## System Architecture

```text
[Customer Input] ──> [Streamlit UI] ──> [Feature Engineering] ──> [XGBoost Model] 
                                                                       │
                                                                       ▼
[Final Decision] <── [Risk Score (0-100%)] <── [Rule Engine] <── [Probability]



Run the Streamlit App

streamlit run app.py

