import streamlit as st
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# ============================
# LOAD DATA
# ============================
df = pd.read_csv('hrkpidata.csv')


# ============================
# DATA PREPROCESSING
# ============================

# Encode categorical variables
df['Attrition'] = df['Attrition'].map({'Yes': 1, 'No': 0})
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
df['Promotion History'] = df['Promotion History'].map({'Yes': 1, 'No': 0})

df['Department'] = df['Department'].map({
    'HR': 0,
    'IT': 1,
    'Finance': 2,
    'Sales': 3,
    'Marketing': 4,
    'Operations': 5
})

# Encode manager
df['Reporting Manager'] = df['Reporting Manager'].astype('category').cat.codes


# ============================
# KPI SCORE CREATION
# ============================
df['KPI Score'] = (
    df['Performance Rating'] * 0.4 +
    df['Engagement Score'] * 0.3 +
    df['Attendance (%)'] * 0.2 +
    df['Number of Training'] * 0.1
)


# ============================
# FEATURES & TARGETS
# ============================
X = df[['Gender', 'Department', 'Engagement Score',
        'Attendance (%)', 'Number of Training',
        'Total Experience', 'Years at Company',
        'Promotion History']]

y_attrition = df['Attrition']
y_performance = df['Performance Rating']


# ============================
# TRAIN MODELS
# ============================
X_train, X_test, y_train_attr, y_test_attr = train_test_split(
    X, y_attrition, test_size=0.2, random_state=42
)

X_train2, X_test2, y_train_perf, y_test_perf = train_test_split(
    X, y_performance, test_size=0.2, random_state=42
)

attr_model = RandomForestClassifier()
perf_model = RandomForestClassifier()

attr_model.fit(X_train, y_train_attr)
perf_model.fit(X_train2, y_train_perf)


# ============================
# SIDEBAR NAVIGATION
# ============================
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['Dashboard', 'Predictor', 'About', 'Profile'])


# ============================
# DASHBOARD PAGE
# ============================
if page == 'Dashboard':
    st.title('HR KPI Dashboard')

    col1, col2, col3 = st.columns(3)

    col1.metric("Average KPI Score", round(df['KPI Score'].mean(), 2))
    col2.metric("Attrition Rate", f"{df['Attrition'].mean() * 100:.1f}%")
    col3.metric("Average Performance", round(df['Performance Rating'].mean(), 2))

    st.subheader("Dataset Preview")
    st.dataframe(df)


# ============================
# PREDICTOR PAGE
# ============================
elif page == 'Predictor':

    st.title('HR KPI Predictor')

    st.header('Enter Employee Details:')

    # Inputs
    gender = st.selectbox('Gender', ['Male', 'Female'])
    gender = 1 if gender == 'Male' else 0

    department = st.selectbox(
        'Department',
        ['HR', 'IT', 'Finance', 'Sales', 'Marketing', 'Operations']
    )
    department = {
        'HR': 0, 'IT': 1, 'Finance': 2,
        'Sales': 3, 'Marketing': 4, 'Operations': 5
    }[department]

    engagement = st.slider('Engagement Score', 50, 100, 75)
    attendance = st.slider('Attendance (%)', 80, 100, 95)
    training = st.selectbox('Number of Training', [0, 1, 2, 3, 4, 5])

    experience = st.number_input('Total Experience', 0, 15, 5)
    years_company = st.number_input('Years at Company', 0, 10, 3)

    promotion = st.selectbox('Promotion History', ['Yes', 'No'])
    promotion = 1 if promotion == 'Yes' else 0

    # Input dataframe
    input_data = pd.DataFrame({
        'Gender': [gender],
        'Department': [department],
        'Engagement Score': [engagement],
        'Attendance (%)': [attendance],
        'Number of Training': [training],
        'Total Experience': [experience],
        'Years at Company': [years_company],
        'Promotion History': [promotion]
    })

    # Prediction
    if st.button('Predict'):

        attr_pred = attr_model.predict(input_data)
        perf_pred = perf_model.predict(input_data)

        # KPI Score
        kpi_score = (
            perf_pred[0] * 0.4 +
            engagement * 0.3 +
            attendance * 0.2 +
            training * 0.1
        )

        st.subheader("Results")

        # Attrition Result
        if attr_pred[0] == 1:
            st.error("⚠️ High Attrition Risk")
        else:
            st.success("✅ Low Attrition Risk")

        # Performance
        st.info(f"⭐ Predicted Performance Rating: {perf_pred[0]}")

        # KPI Score
        st.metric("📊 KPI Score", round(kpi_score, 2))


# ============================
# ABOUT PAGE
# ============================
elif page == 'About':
    st.title('About')
    st.write('This HR KPI App predicts:')
    st.write('- Employee Attrition Risk')
    st.write('- Performance Rating')
    st.write('- KPI Score')
    st.write('It helps HR teams make data-driven decisions.')


# ============================
# PROFILE PAGE
# ============================
elif page == 'Profile':
    st.title('Profile')

    st.write('Vivian Iyaha is a Management graduate with strong interest in HR Analytics, Machine Learning, and Artificial Intelligence.')

    st.write('She is passionate about using data to improve employee performance, reduce attrition, and drive organizational success.')

    st.write('Connect on LinkedIn:')
    st.write('https://www.linkedin.com/in/vivian-i-556499126/')
