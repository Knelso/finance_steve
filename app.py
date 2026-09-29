import streamlit as st
import pandas as pd

# ============================================================
# KESONIA FAIR RATE AI
# Educational / indicative lending-rate analysis tool
# ============================================================

st.set_page_config(
    page_title="KESONIA Fair Rate AI",
    page_icon="🇰🇪",
    layout="centered",
)

# -----------------------------
# Constants
# -----------------------------
KESONIA_RATE = 8.7519
BANK_PROFIT_MARGIN = 2.00
OLD_BANK_RATE = 14.80

# -----------------------------
# Helper functions
# -----------------------------
def score_ability(monthly_sales, loan_amount):
    """Score ability to support the requested loan."""
    if loan_amount <= 0:
        return 0

    monthly_loan_size = loan_amount / 12

    if monthly_sales >= monthly_loan_size * 5:
        return 3
    elif monthly_sales >= monthly_loan_size * 3:
        return 2
    elif monthly_sales >= monthly_loan_size * 1.5:
        return 1
    return 0


def score_attitude(missed_payments):
    """Simple educational payment-history score."""
    if missed_payments == 0:
        return 3
    elif missed_payments <= 2:
        return 2
    elif missed_payments <= 5:
        return 1
    return 0


def score_affordability(monthly_sales, loan_amount, term_months, annual_rate):
    """Estimate affordability using an amortizing monthly payment."""
    if loan_amount <= 0 or term_months <= 0:
        return 0, 0.0

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        payment = loan_amount / term_months
    else:
        payment = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** term_months
            / ((1 + monthly_rate) ** term_months - 1)
        )

    ratio = payment / monthly_sales if monthly_sales > 0 else float("inf")

    if ratio <= 0.20:
        score = 3
    elif ratio <= 0.35:
        score = 2
    elif ratio <= 0.50:
        score = 1
    else:
        score = 0

    return score, payment


def score_label(score):
    if score == 3:
        return "Strong"
    elif score == 2:
        return "Moderate"
    elif score == 1:
        return "Weak"
    return "High Risk"


def format_kes(value):
    return f"KSh {value:,.0f}"


# -----------------------------
# Header
# -----------------------------
st.title("🇰🇪 KESONIA Fair Rate AI")
st.caption(
    "Global benchmark context: USA = SOFR | UK = SONIA | "
    f"Kenya = KESONIA {KESONIA_RATE:.2f}%"
)

st.info(
    "Framework concept: Loan Rate = KESONIA + K. "
    "K is an indicative risk/margin component based on "
    "Ability + Attitude + Affordability."
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("⚙️ Loan Inputs")

monthly_sales = st.sidebar.number_input(
    "Monthly M-Pesa / business sales (KSh)",
    min_value=0.0,
    value=100000.0,
    step=5000.0,
)

business_age = st.sidebar.number_input(
    "Business age (months)",
    min_value=0,
    value=24,
    step=1,
)

missed_payments = st.sidebar.number_input(
    "Missed payments in the last 12 months",
    min_value=0,
    value=0,
    step=1,
)

loan_amount = st.sidebar.number_input(
    "Requested loan amount (KSh)",
    min_value=1000.0,
    value=300000.0,
    step=10000.0,
)

term_months = st.sidebar.number_input(
    "Loan term (months)",
    min_value=1,
    value=24,
    step=1,
)

# -----------------------------
# Triple-A scoring
# -----------------------------
ability = score_ability(monthly_sales, loan_amount)
attitude = score_attitude(missed_payments)

# Preliminary rate used for affordability assessment.
preliminary_rate = KESONIA_RATE + BANK_PROFIT_MARGIN
affordability, monthly_payment = score_affordability(
    monthly_sales,
    loan_amount,
    term_months,
    preliminary_rate,
)

triple_a_total = ability + attitude + affordability

# Business-age adjustment is deliberately modest and transparent.
if business_age >= 36:
    age_note = "Established business history"
elif business_age >= 12:
    age_note = "At least one year of operating history"
else:
    age_note = "Early-stage business"

# -----------------------------
# Indicative K / rate framework
# -----------------------------
if triple_a_total >= 8:
    risk_margin = 1.00
    decision = "Lower indicative risk margin"
elif triple_a_total >= 6:
    risk_margin = 2.00
    decision = "Moderate indicative risk margin"
elif triple_a_total >= 4:
    risk_margin = 3.50
    decision = "Higher indicative risk margin"
else:
    risk_margin = 5.00
    decision = "Very high indicative risk margin"

suggested_rate = KESONIA_RATE + risk_margin

final_affordability_score, suggested_payment = score_affordability(
    monthly_sales,
    loan_amount,
    term_months,
    suggested_rate,
)

monthly_payment = suggested_payment

if triple_a_total >= 8 and final_affordability_score >= 2:
    approval_status = "🟢 Indicatively affordable"
elif triple_a_total >= 5 and final_affordability_score >= 1:
    approval_status = "🟡 Review required"
else:
    approval_status = "🔴 High affordability risk"

# -----------------------------
# Main dashboard
# -----------------------------
st.subheader("📊 Borrower Assessment")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("KESONIA", f"{KESONIA_RATE:.2f}%")

with col2:
    st.metric("Indicative K", f"{risk_margin:.2f}%")

with col3:
    st.metric("Indicative Rate", f"{suggested_rate:.2f}%")

st.write(f"**Business profile:** {age_note}")
st.write(f"**Assessment:** {decision}")

st.divider()

# -----------------------------
# Triple-A cards
# -----------------------------
st.subheader("🔍 Triple-A Credit Assessment")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Ability", f"{ability}/3")
    st.caption(score_label(ability))

with c2:
    st.metric("Attitude", f"{attitude}/3")
    st.caption(score_label(attitude))

with c3:
    st.metric("Affordability", f"{final_affordability_score}/3")
    st.caption(score_label(final_affordability_score))

with c4:
    st.metric("Total", f"{triple_a_total}/9")
    st.caption("Indicative score")

st.success(approval_status)

# -----------------------------
# Repayment comparison
# -----------------------------
st.subheader("💰 Rate & Repayment Comparison")

old_score, old_payment = score_affordability(
    monthly_sales,
    loan_amount,
    term_months,
    OLD_BANK_RATE,
)

kesonia_plus_margin_payment = score_affordability(
    monthly_sales,
    loan_amount,
    term_months,
    preliminary_rate,
)[1]

comparison = pd.DataFrame(
    {
        "Scenario": [
            "Indicative KESONIA + K",
            "KESONIA + 2% reference",
            "Illustrative old rate",
        ],
        "Annual Rate (%)": [
            suggested_rate,
            preliminary_rate,
            OLD_BANK_RATE,
        ],
        "Monthly Payment (KSh)": [
            monthly_payment,
            kesonia_plus_margin_payment,
            old_payment,
        ],
    }
)

st.dataframe(
    comparison.style.format(
        {
            "Annual Rate (%)": "{:.2f}%",
            "Monthly Payment (KSh)": "KSh {:,.0f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.bar_chart(
    comparison.set_index("Scenario")["Monthly Payment (KSh)"]
)

# -----------------------------
# Savings / difference
# -----------------------------
difference = old_payment - monthly_payment

if difference > 0:
    st.info(
        f"At the indicative rate, the estimated monthly payment is "
        f"{format_kes(difference)} lower than the illustrative {OLD_BANK_RATE:.2f}% scenario."
    )
elif difference < 0:
    st.warning(
        f"At the indicative rate, the estimated monthly payment is "
        f"{format_kes(abs(difference))} higher than the illustrative {OLD_BANK_RATE:.2f}% scenario."
    )
else:
    st.info("The estimated monthly payments are the same in these scenarios.")

# -----------------------------
# What if banks ignore KESONIA?
# -----------------------------
st.subheader("⚠️ What if banks ignore KESONIA?")

tab1, tab2 = st.tabs(["Economy Impact", "USA 2008 Lesson"])

with tab1:
    st.markdown(
        """
        **If banks do not use transparent interest-rate benchmarks effectively:**

        1. **Borrowers:** Loan pricing may become less transparent and harder to compare.
        2. **Banks:** Poor credit assessment and high borrowing costs can increase credit risk and non-performing loans.
        3. **Economy:** Weak transmission of monetary-policy changes can reduce the effectiveness of interest-rate policy.

        **Key idea:** A transparent benchmark such as KESONIA can help make the
        reference component of lending rates easier to understand and compare.
        """
    )

with tab2:
    st.markdown(
        """
        **USA 2008 Lesson**

        The 2007–2009 financial crisis exposed major weaknesses in mortgage
        underwriting, risk management, and the pricing of credit.

        **Important distinction:** SOFR was introduced after the financial crisis
        as a transaction-based benchmark for overnight U.S. dollar funding markets.
        It was not itself the solution to the subprime crisis.

        **Lesson for Kenya:** Transparent benchmarks should work together with
        responsible lending, affordability assessment, credit-risk management,
        and effective regulation.
        """
    )

# -----------------------------
# What is KESONIA?
# -----------------------------
st.subheader("🇰🇪 What is KESONIA?")

with st.expander("Read the explanation"):
    st.markdown(
        """
        **KESONIA** is Kenya's overnight interbank average rate and is intended
        to provide a transparent reference for the cost of Kenyan-shilling
        overnight funding.

        In a lending framework, a benchmark can provide the reference component
        while the lender's additional margin reflects factors such as credit
        risk, operating costs, capital costs, and profit.

        This app uses KESONIA as an educational reference point. It does not
        determine or certify an official bank lending rate.
        """
    )

# -----------------------------
# Global benchmark context
# -----------------------------
st.subheader("🌍 Global Benchmark Context")

global_data = pd.DataFrame(
    {
        "Market": ["United States", "United Kingdom", "Kenya"],
        "Benchmark": ["SOFR", "SONIA", "KESONIA"],
        "Purpose": [
            "Overnight U.S. dollar funding benchmark",
            "Overnight sterling benchmark",
            "Overnight Kenyan-shilling interbank benchmark",
        ],
    }
)

st.dataframe(
    global_data,
    use_container_width=True,
    hide_index=True,
)

# -----------------------------
# Audit receipt
# -----------------------------
st.subheader("🧾 Indicative Audit Receipt")

receipt = f"""
KESONIA FAIR RATE AI — INDICATIVE RECEIPT
------------------------------------------
KESONIA reference:        {KESONIA_RATE:.4f}%
Indicative K:             {risk_margin:.2f}%
Indicative lending rate:  {suggested_rate:.2f}%

Monthly sales:             {format_kes(monthly_sales)}
Business age:              {business_age} months
Missed payments (12M):     {missed_payments}
Requested loan:            {format_kes(loan_amount)}
Term:                      {term_months} months

Ability score:             {ability}/3
Attitude score:            {attitude}/3
Affordability score:       {final_affordability_score}/3
Triple-A total:             {triple_a_total}/9

Estimated monthly payment: {format_kes(monthly_payment)}
Status:                    {approval_status}
"""

st.code(receipt, language="text")

# -----------------------------
# Disclaimer
# -----------------------------
st.warning(
    "Educational / indicative tool only. This app does not represent an official "
    "CBK lending-rate calculator, bank credit decision, financial advice, or "
    "certification. Actual loan pricing and approval depend on the lender's "
    "policies, current benchmark data, borrower risk, fees, collateral, and "
    "applicable regulation."
)

st.caption(
    "Framework reference: KESONIA transition framework began 1 September 2025 "
    "and the transition period ended 28 February 2026. "
    "Always verify the current official benchmark before making a financial decision."
)
