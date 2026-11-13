
import streamlit as st
import plotly.graph_objects as go
import random
import os

st.set_page_config(
    page_title="SpreadMap AI",
    page_icon="🧬",
    layout="wide"
)

ROOMS = {
    "Emergency": (0, 2),
    "Waiting Area": (1, 3),
    "Reception": (2, 2),
    "Ward A": (3, 3),
    "Ward B": (3, 1),
    "Nurses Station": (4, 2),
    "Laboratory": (5, 3),
    "Pharmacy": (5, 1),
    "ICU": (6, 2)
}

CONNECTIONS = [
    ("Emergency", "Waiting Area"),
    ("Emergency", "Reception"),
    ("Waiting Area", "Reception"),
    ("Reception", "Ward A"),
    ("Reception", "Ward B"),
    ("Ward A", "Nurses Station"),
    ("Ward B", "Nurses Station"),
    ("Nurses Station", "Laboratory"),
    ("Nurses Station", "Pharmacy"),
    ("Nurses Station", "ICU")
]

def simulate(start, contact, movement, steps, seed):
    rng = random.Random(seed)
    affected = {start}
    history = [set(affected)]

    probability = min(0.8, 0.06 * contact * movement)

    for _ in range(steps):
        new = set()

        for room in affected:
            for a, b in CONNECTIONS:
                neighbor = b if a == room else a if b == room else None

                if neighbor and neighbor not in affected:
                    if rng.random() < probability:
                        new.add(neighbor)

        affected.update(new)
        history.append(set(affected))

    return history

def hospital_map(affected, start):
    fig = go.Figure()

    for a, b in CONNECTIONS:
        x1, y1 = ROOMS[a]
        x2, y2 = ROOMS[b]

        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="lines",
            line=dict(color="#AAB2BD", width=3),
            showlegend=False,
            hoverinfo="skip"
        ))

    for room, (x, y) in ROOMS.items():
        color = (
            "#F4A261" if room == start
            else "#E76F51" if room in affected
            else "#55A67A"
        )

        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            text=[room],
            textposition="bottom center",
            marker=dict(
                size=34,
                color=color,
                line=dict(color="white", width=2)
            ),
            showlegend=False,
            hovertemplate=f"<b>{room}</b><extra></extra>"
        ))

    fig.update_layout(
        height=470,
        margin=dict(l=10, r=10, t=20, b=45),
        plot_bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig

# HEADER
st.title("🧬 SpreadMap AI")
st.subheader("Hospital Infection Spread Simulator")

st.write(
    "An interactive educational simulator showing "
    "how a fictional infection could spread through "
    "connected hospital areas."
)

st.info(
    "Educational simulation only. Uses invented probabilities "
    "and does not predict real hospital outbreaks."
)

# SIDEBAR
st.sidebar.header("Simulation Controls")

start = st.sidebar.selectbox(
    "Starting location",
    list(ROOMS.keys())
)

contact = st.sidebar.slider(
    "Simulated contact level", 1, 5, 3
)

movement = st.sidebar.slider(
    "Movement between areas", 1, 5, 3
)

steps = st.sidebar.slider(
    "Simulation steps", 1, 10, 5
)

seed = st.sidebar.number_input(
    "Random seed", 1, 9999, 42
)

# RUN SIMULATION
if st.button("▶ Run Simulation", type="primary"):
    st.session_state.history = simulate(
        start, contact, movement, steps, int(seed)
    )
    st.session_state.start = start
    st.session_state.settings = (
        contact, movement, steps, int(seed)
    )

# RESULTS
if "history" in st.session_state:
    history = st.session_state.history

    selected = st.slider(
        "Simulation Timeline",
        0,
        len(history) - 1,
        0
    )

    affected = history[selected]

    col1, col2, col3 = st.columns(3)

    col1.metric("Simulation Step", selected)
    col2.metric("Affected Areas", len(affected))
    col3.metric("Unaffected Areas", len(ROOMS) - len(affected))

    st.subheader("🏥 Hospital Spread Map")

    st.plotly_chart(
        hospital_map(affected, st.session_state.start),
        use_container_width=True
    )

    st.caption(
        "🟠 Starting Area | 🔴 Affected in Simulation | "
        "🟢 Not Affected in Simulation"
    )

    st.subheader("📊 Simulation Timeline")

    for i, state in enumerate(history):
        st.write(
            f"Step {i}: {len(state)} affected areas"
        )

    # SCENARIO COMPARISON
    st.divider()
    st.subheader("Compare Scenarios")

    if st.button("Compare with Lower Movement"):

        contact_value, movement_value, steps_value, seed_value = (
            st.session_state.settings
        )

        original = simulate(
            st.session_state.start,
            contact_value,
            movement_value,
            steps_value,
            seed_value
        )

        reduced = simulate(
            st.session_state.start,
            contact_value,
            max(1, movement_value - 2),
            steps_value,
            seed_value
        )

        left, right = st.columns(2)

        with left:
            st.write("Original Movement")
            st.metric("Affected Areas", len(original[-1]))

            st.plotly_chart(
                hospital_map(original[-1], st.session_state.start),
                use_container_width=True
            )

        with right:
            st.write("Reduced Movement")
            st.metric("Affected Areas", len(reduced[-1]))

            st.plotly_chart(
                hospital_map(reduced[-1], st.session_state.start),
                use_container_width=True
            )

        st.caption(
            "These are fictional scenarios using the same random seed. "
            "Results are not real-world predictions."
        )

    # AI ANALYSIS
    st.divider()
    st.subheader("🤖 AI Analysis")

    if st.button("Analyze Results with AI"):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            st.warning(
                "AI API key is not configured. "
                "The simulator still works without AI."
            )

        else:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=api_key)

                prompt = f"""
                Explain this fictional educational simulation.

                Starting area: {st.session_state.start}
                Simulation step: {selected}
                Affected areas: {sorted(affected)}
                Total affected areas: {len(affected)}

                Explain:
                1. What happened in the simulation?
                2. Why might connected areas be affected?
                3. Which areas may need closer monitoring
                   in this fictional scenario?
                4. What general prevention lesson can be learned?

                Use simple language.
                Do not claim this predicts real outbreaks.
                Do not give medical treatment instructions.
                """

                result = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt
                )

                st.write(result.output_text)

            except Exception as e:
                st.error(f"AI analysis error: {e}")

else:
    st.subheader("Welcome to SpreadMap AI!")

    st.write(
        "Choose your settings in the sidebar "
        "and click Run Simulation to begin."
    )

    st.plotly_chart(
        hospital_map(set(), ""),
        use_container_width=True
    )

