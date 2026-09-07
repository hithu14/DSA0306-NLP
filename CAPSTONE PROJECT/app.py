import streamlit as st
import pandas as pd

from streamlit_mic_recorder import speech_to_text

from database import (
    create_table,
    add_complaint,
    get_complaints,
    update_complaint_status,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Complaint Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE
# ============================================================

create_table()


# ============================================================
# CUSTOM CSS
# NOTE:
# No raw HTML is used for the page content.
# This prevents <div>, <h1>, <p>, etc. from appearing as text.
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #eef7ff 0%,
            #f5f3ff 50%,
            #eefaf7 100%
        );
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #dbe5f0;
    }

    .hero-title {
        text-align: center;
        color: #123b67;
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
    }

    .hero-text {
        text-align: center;
        color: #58708a;
        font-size: 1.1rem;
        margin: 0.35rem 0;
    }

    .online-text {
        text-align: center;
        color: #16834b;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }

    .section-title {
        color: #123b67;
        font-weight: 700;
    }

    .footer-text {
        text-align: center;
        color: #718096;
        padding: 25px 0;
        margin-top: 35px;
        border-top: 1px solid #dbe5f0;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dce7f2;
        border-radius: 14px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DEPARTMENT CLASSIFICATION
# ============================================================

def classify_complaint(text):
    text = text.lower().strip()

    water_words = [
        "water",
        "tap",
        "pipe",
        "pipeline",
        "leakage",
        "leak",
        "drinking water",
        "water supply",
        "water tank",
        "no water",
        "water shortage",
        "bathroom water",
        "toilet water",
    ]

    electrical_words = [
        "power",
        "electricity",
        "electric",
        "current",
        "voltage",
        "wire",
        "wiring",
        "switch",
        "socket",
        "light",
        "bulb",
        "fan",
        "ac",
        "air conditioner",
        "lift",
        "elevator",
        "generator",
        "power cut",
        "power failure",
        "no electricity",
    ]

    housekeeping_words = [
        "clean",
        "cleaning",
        "dirty",
        "garbage",
        "waste",
        "dustbin",
        "dust",
        "toilet cleaning",
        "washroom cleaning",
        "room cleaning",
        "unhygienic",
    ]

    security_words = [
        "security",
        "guard",
        "theft",
        "stolen",
        "missing",
        "unauthorized",
        "stranger",
        "intruder",
        "camera",
        "cctv",
        "suspicious",
        "unsafe",
    ]

    network_words = [
        "internet",
        "wifi",
        "wi-fi",
        "network",
        "router",
        "connection",
        "connectivity",
        "online",
        "lan",
    ]

    maintenance_words = [
        "maintenance",
        "repair",
        "broken",
        "damage",
        "door",
        "window",
        "wall",
        "ceiling",
        "furniture",
        "chair",
        "table",
        "roof",
    ]

    if any(word in text for word in water_words):
        return "Water", "Water Department"

    if any(word in text for word in electrical_words):
        return "Electrical", "Electrical Department"

    if any(word in text for word in housekeeping_words):
        return "Housekeeping", "Housekeeping Department"

    if any(word in text for word in security_words):
        return "Security", "Security Department"

    if any(word in text for word in network_words):
        return "Internet / Network", "IT Department"

    if any(word in text for word in maintenance_words):
        return "Maintenance", "Maintenance Department"

    return "General", "General Administration"


# ============================================================
# PRIORITY DETECTION
# ============================================================

def calculate_priority(text):

    text = text.lower().strip()

    # HIGH PRIORITY - EMERGENCY / DANGEROUS SITUATIONS
    high_words = [
        "emergency",
        "urgent",
        "urgently",
        "immediately",
        "critical",
        "severe",
        "danger",
        "dangerous",
        "fire",
        "smoke",
        "accident",
        "shock",
        "electric shock",
        "sparking",
        "spark",
        "flood",
        "burst pipe",
        "major leakage",
        "no electricity",
        "complete power failure",
        "power failure",
        "lift stuck",
        "person trapped",
        "trapped",
        "life threatening",
        "life-threatening",
        "security threat",
        "theft happening"
    ]

    # MEDIUM PRIORITY - NORMAL PROBLEMS
    medium_words = [
        "not working",
        "stopped",
        "problem",
        "issue",
        "broken",
        "leak",
        "leakage",
        "slow",
        "damaged",
        "failure",
        "complaint",
        "unable",
        "cannot",
        "can't"
    ]

    # CHECK HIGH PRIORITY FIRST
    if any(word in text for word in high_words):
        return "High"

    # CHECK MEDIUM PRIORITY
    elif any(word in text for word in medium_words):
        return "Medium"

    # OTHERWISE LOW PRIORITY
    else:
        return "Low"


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(text, category):
    text = text.lower()

    keywords = {
        "Water": [
            "water",
            "tap",
            "pipe",
            "leakage",
            "water supply",
        ],
        "Electrical": [
            "power",
            "electricity",
            "electric",
            "lift",
            "elevator",
            "fan",
            "light",
            "current",
        ],
        "Housekeeping": [
            "clean",
            "dirty",
            "garbage",
            "waste",
            "dustbin",
            "unhygienic",
        ],
        "Security": [
            "security",
            "theft",
            "stolen",
            "guard",
            "cctv",
            "intruder",
        ],
        "Internet / Network": [
            "internet",
            "wifi",
            "network",
            "router",
        ],
        "Maintenance": [
            "repair",
            "broken",
            "damage",
            "door",
            "window",
            "furniture",
        ],
    }

    if category in keywords:
        matches = 0

        for word in keywords[category]:
            if word in text:
                matches += 1

        confidence = 70 + min(matches * 8, 25)

        return round(confidence, 1)

    return 60.0


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🤖 Navigation")
    st.divider()

    page = st.radio(
        "Select Module",
        [
            "🎤 Submit Complaint",
            "📊 Admin Dashboard",
        ],
    )

    st.divider()

    st.info(
        """
        **AI Complaint Analyzer**

        The system converts spoken complaints
        into text, classifies them, determines
        priority and automatically routes them
        to the correct department.
        """
    )

    st.divider()
    st.caption("AI Complaint Management System")


# ============================================================
# SUBMIT COMPLAINT PAGE
# ============================================================

if page == "🎤 Submit Complaint":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.container(border=True)

    st.markdown(
        '<p class="online-text">🟢 AI SYSTEM ONLINE</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">🎤 AI Voice Complaint Analyzer</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="hero-text">Transform voice complaints into intelligent, actionable service requests.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="hero-text">Speech Recognition • NLP • Classification • Smart Department Routing • Analytics</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # RECORD SECTION
    # --------------------------------------------------------

    st.subheader("🎤 Record Your Complaint")

    st.write(
        "Speak clearly and describe your complaint. "
        "The AI system will convert your speech into text "
        "and automatically route it to the appropriate department."
    )

    st.divider()

    # --------------------------------------------------------
    # ACTUAL SPEECH TO TEXT
    # --------------------------------------------------------

    st.markdown("### 🎙️ Speak Your Complaint")
    st.write("Click the microphone button and speak clearly.")

    spoken_text = speech_to_text(
        language="en",
        start_prompt="🎤 Start Speaking",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True,
        key="complaint_voice",
    )

    # --------------------------------------------------------
    # KEEP THE RECOGNIZED VOICE TEXT IN SESSION STATE
    # --------------------------------------------------------
    # IMPORTANT:
    # Streamlit reruns the whole script when the Analyze button
    # is clicked. The speech_to_text() result may be None on that
    # second run, so we must save the recognized text first.

    if "complaint_input" not in st.session_state:
        st.session_state.complaint_input = ""

    if "voice_received" not in st.session_state:
        st.session_state.voice_received = False

    if spoken_text:
        st.session_state.complaint_input = spoken_text.strip()
        st.session_state.voice_received = True

    if st.session_state.voice_received and st.session_state.complaint_input:
        st.success("✅ Voice successfully converted to text!")

    complaint_text = st.text_area(
        "📝 Recognized Complaint",
        height=130,
        key="complaint_input",
        placeholder=(
            "Your spoken complaint will appear here "
            "after you use the microphone."
        ),
    )

    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    if st.button(
        "🔍 Analyze & Route Complaint",
        type="primary",
        use_container_width=True,
    ):

        # Read the value that is currently stored in the text area.
        # This remains available even after Streamlit reruns the app.
        complaint_text = st.session_state.get("complaint_input", "")

        if not complaint_text or not complaint_text.strip():
            st.warning("⚠️ Please speak a complaint using the microphone.")

        else:
            complaint_text = complaint_text.strip()

            # Classification
            category, department = classify_complaint(complaint_text)

            # Priority
            priority = calculate_priority(complaint_text)

            # Confidence
            confidence = calculate_confidence(
                complaint_text,
                category,
            )

            # ------------------------------------------------
            # SAVE TO DATABASE
            # ------------------------------------------------

            add_complaint(
                complaint_text,
                category,
                confidence,
                priority,
                department,
            )

            # ------------------------------------------------
            # SHOW RESULT
            # ------------------------------------------------

            st.success(
                "✅ Complaint analyzed and routed successfully!"
            )

            st.subheader("🤖 AI Analysis Result")

            # Metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("📂 Category", category)

            with col2:
                st.metric("🎯 Confidence", f"{confidence}%")

            with col3:
                st.metric("🚨 Priority", priority)

            # Department
            st.info(
                f"🏢 **Assigned Department:** {department}\n\n"
                "This complaint has been automatically routed "
                "to the responsible department."
            )

            # Priority message
            if priority == "High":
                st.error(
                    "🚨 HIGH PRIORITY: This complaint requires immediate attention."
                )
            elif priority == "Medium":
                st.warning(
                    "🟡 MEDIUM PRIORITY: This complaint should be addressed soon."
                )
            else:
                st.success(
                    "🟢 LOW PRIORITY: This complaint can be handled normally."
                )

            st.markdown("### 📋 Complaint")
            st.write(complaint_text)


# ============================================================
# ADMIN DASHBOARD
# ============================================================

else:

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        '<p class="online-text">🟢 ADMIN SYSTEM ONLINE</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="hero-title">📊 Admin Dashboard</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="hero-text">Monitor, analyze and manage complaints</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="hero-text">Department-wise Routing • Priority Monitoring • Complaint Status Management</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    records = get_complaints()

    if records:

        columns = [
            "id",
            "complaint",
            "category",
            "confidence",
            "priority",
            "department",
            "status",
            "created_at",
        ]

        df = pd.DataFrame(records, columns=columns)

        # ----------------------------------------------------
        # DASHBOARD COUNTS
        # ----------------------------------------------------

        total = len(df)

        pending = len(
            df[df["status"] == "Pending"]
        )

        in_progress = len(
            df[df["status"] == "In Progress"]
        )

        resolved = len(
            df[df["status"] == "Resolved"]
        )

        high_priority = len(
            df[df["priority"] == "High"]
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric("📋 Total Complaints", total)

        with c2:
            st.metric("🟡 Pending", pending)

        with c3:
            st.metric("🔵 In Progress", in_progress)

        with c4:
            st.metric("🟢 Resolved", resolved)

        with c5:
            st.metric("🚨 High Priority", high_priority)

        st.divider()

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        st.subheader("🔎 Filter Complaints")

        f1, f2, f3 = st.columns(3)

        with f1:
            departments = [
                "All Departments"
            ] + sorted(
                df["department"].dropna().unique().tolist()
            )

            selected_department = st.selectbox(
                "🏢 Department",
                departments,
            )

        with f2:
            priorities = [
                "All Priorities",
                "High",
                "Medium",
                "Low",
            ]

            selected_priority = st.selectbox(
                "🚨 Priority",
                priorities,
            )

        with f3:
            statuses = [
                "All Statuses",
                "Pending",
                "In Progress",
                "Resolved",
            ]

            selected_status = st.selectbox(
                "📌 Status",
                statuses,
            )

        # ----------------------------------------------------
        # APPLY FILTERS
        # ----------------------------------------------------

        filtered_df = df.copy()

        if selected_department != "All Departments":
            filtered_df = filtered_df[
                filtered_df["department"] == selected_department
            ]

        if selected_priority != "All Priorities":
            filtered_df = filtered_df[
                filtered_df["priority"] == selected_priority
            ]

        if selected_status != "All Statuses":
            filtered_df = filtered_df[
                filtered_df["status"] == selected_status
            ]

        # ----------------------------------------------------
        # DEPARTMENT-WISE SEGREGATION
        # ----------------------------------------------------

        st.subheader("🏢 Department-wise Complaints")

        department_counts = (
            filtered_df["department"]
            .value_counts()
            .reset_index()
        )

        department_counts.columns = [
            "Department",
            "Number of Complaints",
        ]

        if not department_counts.empty:
            st.dataframe(
                department_counts,
                use_container_width=True,
                hide_index=True,
            )

        # ----------------------------------------------------
        # COMPLAINT MANAGEMENT
        # ----------------------------------------------------

        st.subheader("📋 Complaint Management")

        if filtered_df.empty:

            st.info(
                "No complaints match the selected filters."
            )

        else:

            # Display newest first
            for _, row in filtered_df.iterrows():

                complaint_id = int(row["id"])
                complaint = str(row["complaint"])
                category = str(row["category"])
                confidence = float(row["confidence"])
                priority = str(row["priority"])
                department = str(row["department"])
                status = str(row["status"])
                created_at = str(row["created_at"])

                priority_icon = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢",
                }.get(priority, "⚪")

                status_icon = {
                    "Pending": "🟡",
                    "In Progress": "🔵",
                    "Resolved": "🟢",
                }.get(status, "⚪")

                with st.expander(
                    f"Complaint #{complaint_id}  |  "
                    f"{priority_icon} {priority}  |  "
                    f"{status_icon} {status}"
                ):

                    st.write(f"**Complaint:** {complaint}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Category:** {category}")
                        st.write(f"**Confidence:** {confidence}%")

                    with col2:
                        st.write(f"**Department:** {department}")
                        st.write(f"**Priority:** {priority}")

                    with col3:
                        st.write(f"**Current Status:** {status}")
                        st.write(f"**Created:** {created_at}")

                    st.divider()

                    status_options = [
                        "Pending",
                        "In Progress",
                        "Resolved",
                    ]

                    current_index = (
                        status_options.index(status)
                        if status in status_options
                        else 0
                    )

                    new_status = st.selectbox(
                        "Update Complaint Status",
                        status_options,
                        index=current_index,
                        key=f"status_{complaint_id}",
                    )

                    if st.button(
                        "💾 Update Status",
                        key=f"update_{complaint_id}",
                    ):

                        update_complaint_status(
                            complaint_id,
                            new_status,
                        )

                        st.success(
                            f"Complaint #{complaint_id} "
                            f"updated to {new_status}."
                        )

                        st.rerun()

    else:

        st.info(
            "📭 No complaints have been submitted yet."
        )

        st.markdown("### 🎤 Submit your first complaint")

        st.write(
            "Go to **Submit Complaint** from the sidebar, "
            "speak your complaint using the microphone, "
            "and the AI system will automatically classify "
            "and route it."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div class="footer-text">
        🤖 AI Complaint Analyzer<br>
        Speech Recognition • NLP • Classification •
        Smart Department Routing • Analytics
    </div>
    """,
    unsafe_allow_html=True,
)
