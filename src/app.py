import streamlit as st

def main():
    st.set_page_config(page_title="Insurance Claims Triage", layout="wide")
    
    st.title("🩺 AI-Powered Insurance Claims Triage")
    st.markdown("---")
    
    # Main layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Submit Claim")
        st.text_input("Patient Age")
        st.selectbox("Diagnosis", ["Select...", "Surgery", "Emergency", "Routine"])
        st.date_input("Admission Date")
        st.date_input("Discharge Date")
        st.number_input("Claimed Amount ($)")
        st.button("Submit Claim")
    
    with col2:
        st.subheader("📊 Claim Status")
        st.info("Status: Not Submitted")
        
    st.markdown("---")
    st.caption("Prototype v0.1 - Frontend Wireframe")

if __name__ == "__main__":
    main()
