import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go


# 1. Page settings


st.set_page_config(
    page_title="نظام الأمان المالي اليمني",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; background-color: #f4f7f6; }
h1, h2, h3 { color: #1E3A8A; font-weight: 700; }
.stButton>button { background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); color: white; border-radius: 12px; height: 55px; font-weight: 700; font-size: 18px; border: none; box-shadow: 0 4px 15px rgba(30, 58, 138, 0.3); }
[data-testid="stSidebar"] { background-color: #ffffff; border-left: 1px solid #e0e0e0; }
div[data-testid="stMetric"] { background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-right: 5px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ نظام كشف الاحتيال المالي اليمني</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>منصة ذكية متقدمة لحماية المحافظ الإلكترونية والمعاملات المالية</p>", unsafe_allow_html=True)
st.markdown("---")

# 2. Load the model

@st.cache_resource
def load_model():
    try:
        # The file name here has been corrected to match what was saved in Jupyter
        art = joblib.load('yemen_fraud_model_production.pkl')
        return art['model'], art['optimal_threshold'], art['features']
    except Exception as e:
        st.error(f"❌ فشل تحميل النموذج: {e}")
        st.info("تأكد من تشغيل الخلايا 7 و 8 في Jupyter Notebook لحفظ النموذج.")
        return None, None, None

model, threshold, features = load_model()
if model is None:
    st.stop()


# 3. Unified lists


GOVERNORATES = ['Sanaa','Aden','Taiz','Hodeidah','Hadramout','Ibb','Dhamar','Amran',
                'Saada','Marib','Hajjah','AlBayda','AlJawf','Lahj','Abyan','AlMahrah',
                'AlMahwit','Raymah','Socotra','Shabwah','AdhDhale','AlHudaydah']
HIGH_RISK = {'Sanaa','Aden','Taiz','Hodeidah','Hadramout'}
WALLETS = ['Jawali','Jaib','Cash','Alkuraimi','Flosak','SabaCash','BiCash','YemenCash','Mahfathati','M-Floos']


# 4. Reset values function


def reset_values():
    st.session_state["amount_yer"] = 10000
    st.session_state["velocity_24h"] = 1
    st.session_state["unique_receivers_7d"] = 1
    st.session_state["sender_risk_score"] = 10
    st.session_state["account_age_days"] = 800
    st.session_state["kyc_code"] = 2
    st.session_state["daily_limit_yer"] = 1000000
    st.session_state["avg_txn_amount_yer"] = 20000
    st.session_state["is_new_receiver"] = False


# 5. Sidebar


st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📝 بيانات المعاملة</h2>", unsafe_allow_html=True)

with st.sidebar.expander("💰 تفاصيل المعاملة", expanded=True):
    amount_yer = st.number_input("المبلغ (ريال يمني)", min_value=100, max_value=10_000_000, value=10_000, step=1000, key="amount_yer")
    txn_type = st.selectbox("نوع المعاملة", ['transfer','bill_payment','merchant_payment','cash_withdrawal','salary','topup'],
                            format_func=lambda x: {'transfer':'تحويل','bill_payment':'دفع فواتير',
                                                   'merchant_payment':'شراء','cash_withdrawal':'سحب نقدي',
                                                   'salary':'راتب','topup':'تعبئة رصيد'}[x])
    hour = st.slider("ساعة اليوم", 0, 23, 14)
    day_of_week = st.selectbox("يوم الأسبوع", [0,1,2,3,4,5,6],
                               format_func=lambda x: ['الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد'][x])
    is_ramadan = st.checkbox("خلال رمضان", value=False)
    is_eid = st.checkbox("خلال عيد", value=False)

with st.sidebar.expander("👤 المرسل", expanded=True):
    sender_wallet = st.selectbox("محفظة المرسل", WALLETS)
    sender_gov = st.selectbox("محافظة المرسل", GOVERNORATES)
    account_age_days = st.number_input("عمر الحساب (أيام)", min_value=1, max_value=3000, value=800, key="account_age_days")
    kyc_code = st.selectbox("مستوى التوثيق (KYC)", [0,1,2],
                            format_func=lambda x: {0:'أساسي',1:'متوسط',2:'موثق'}[x], index=2, key="kyc_code")
    sender_risk_score = st.slider("درجة خطورة العميل", 0, 100, 10, key="sender_risk_score")
    daily_limit_yer = st.number_input("الحد اليومي (ر.ي)", min_value=200_000, max_value=5_000_000, value=1_000_000, step=100_000, key="daily_limit_yer")
    avg_txn_amount_yer = st.number_input("متوسط مبلغ العميل (ر.ي)", min_value=5000, max_value=500_000, value=20_000, step=5000, key="avg_txn_amount_yer")

with st.sidebar.expander("👥 المستقبل", expanded=True):
    receiver_wallet = st.selectbox("محفظة المستقبل", WALLETS)
    receiver_gov = st.selectbox("محافظة المستقبل", GOVERNORATES)
    is_new_receiver = st.checkbox("المستقبل جديد على المرسل", value=False, key="is_new_receiver")

with st.sidebar.expander("📈 سلوك المرسل (آخر 24 ساعة / 7 أيام)", expanded=True):
    velocity_24h = st.slider("عدد معاملات المرسل في آخر 24 ساعة", 0, 50, 1, key="velocity_24h")
    unique_receivers_7d = st.slider("عدد المستقبلين الفريدين في آخر 7 أيام", 0, 100, 1, key="unique_receivers_7d")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Control buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    check_button = st.button("🔍 فحص", type="primary", use_container_width=True)
with col2:
    st.button("🔄 مسح", on_click=reset_values, use_container_width=True)


# 6. Prediction and display


if check_button:
    is_night = int(hour in [22,23,0,1,2,3,4,5])
    is_weekend = int(day_of_week in [4,5])
    is_cross_gov = int(sender_gov != receiver_gov)
    is_same_wallet = int(sender_wallet == receiver_wallet)

    input_data = pd.DataFrame([{
        'sender_account_age_days': account_age_days,
        'sender_kyc_code': kyc_code,
        'sender_avg_amount': avg_txn_amount_yer,
        'sender_daily_limit': daily_limit_yer,
        'sender_risk_score': sender_risk_score,
        'amount_yer': amount_yer,
        'amount_log': np.log1p(amount_yer),
        'hour': hour,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'is_night': is_night,
        'is_ramadan': int(is_ramadan),
        'is_eid': int(is_eid),
        'is_cross_governorate': is_cross_gov,
        'is_high_risk_gov': int(sender_gov in HIGH_RISK),
        'receiver_high_risk_gov': int(receiver_gov in HIGH_RISK),
        'is_same_wallet': is_same_wallet,
        'is_kyc_basic': int(kyc_code == 0),
        'is_kyc_verified': int(kyc_code == 2),
        'is_new_account': int(account_age_days < 30),
        'is_transfer': int(txn_type == 'transfer'),
        'is_cash_withdraw': int(txn_type == 'cash_withdrawal'),
        'velocity_24h': velocity_24h,
        'unique_receivers_7d': unique_receivers_7d,
        'is_new_receiver': int(is_new_receiver),
    }])[features]

    # 1. Get the raw probability from the model
    proba = float(model.predict_proba(input_data)[0, 1])
    


    # 2. Security business rules


    
    # Rule 1: Perfect citizen (reduce the probability by 50%)
    if kyc_code == 2 and account_age_days > 365 and sender_risk_score < 30:
        proba = proba * 0.5
        
    # Rule 2: Nighttime takeover with a huge amount (force the probability up)
    if amount_yer > 2_000_000 and hour in [1, 2, 3, 4, 5]:
        proba = max(proba, 0.99)
        
    # Recompute the decision based on the new probability
    is_fraud = proba >= threshold


    # 3. Display
    
    
    col_res1, col_res2 = st.columns([1, 2])
    with col_res1:
        st.markdown("<h3 style='text-align: center;'>مستوى الخطورة</h3>", unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            title={'text': "نسبة الاحتيال (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#ef4444" if is_fraud else "#10b981"},
                'steps': [
                    {'range': [0, threshold*100], 'color': '#d1fae5'},
                    {'range': [threshold*100, 100], 'color': '#fee2e2'},
                ],
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"حد القرار (Threshold): {threshold*100:.1f}%")

    with col_res2:
        if is_fraud:
            st.error(f"🚨 **تحذير: احتيال مشتبه به!** (الاحتمالية: {proba*100:.2f}%)")
        else:
            st.success(f"✅ **معاملة آمنة** (الاحتمالية: {proba*100:.2f}%)")

        st.markdown("---")
        st.markdown("<h4>🔍 العوامل المؤثرة في القرار</h4>", unsafe_allow_html=True)

        reasons = []
        if is_new_receiver: reasons.append("🔴 المستقبل جديد على المرسل.")
        if is_night: reasons.append("🟡 المعاملة في وقت متأخر (ليل).")
        if velocity_24h >= 10: reasons.append(f"🔴 سرعة عالية: {velocity_24h} معاملة/24 ساعة.")
        if unique_receivers_7d >= 15: reasons.append(f"🔴 تعدد مستقبلين: {unique_receivers_7d} في 7 أيام.")
        if amount_yer > avg_txn_amount_yer * 4: reasons.append("🔴 المبلغ أكبر من 4× متوسط العميل.")
        if amount_yer > daily_limit_yer * 0.8: reasons.append("🔴 المبلغ يقترب من الحد اليومي.")
        if account_age_days < 30: reasons.append("🔴 الحساب جديد جداً (< 30 يوم).")
        if kyc_code == 0: reasons.append("🟡 حساب بمستوى توثيق أساسي فقط.")
        if is_cross_gov: reasons.append("🟡 تحويل بين محافظات مختلفة.")
        if is_same_wallet: reasons.append("🟢 التحويل داخل نفس المحفظة.")

        if not reasons:
            reasons.append("🟢 جميع المؤشرات طبيعية.")

        for r in reasons:
            st.markdown(r)

        with st.expander("📋 عرض الميزات المُدخلة للنموذج (للتأكد من سلامة الإدخال)"):
            st.dataframe(input_data.T.rename(columns={0: 'القيمة'}), use_container_width=True)
else:
    st.info("👈 أدخل البيانات من القائمة الجانبية واضغط 'فحص'.")