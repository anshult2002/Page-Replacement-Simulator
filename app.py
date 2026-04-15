import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time


# Page Replacement Algorithms
def fifo(pages, frames):
    memory = []
    page_faults = 0
    memory_states = []
    decisions = []

    for page in pages:
        fault = False
        if page not in memory:
            if len(memory) < frames:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
            page_faults += 1
            fault = True
        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")
    return page_faults, memory_states, decisions


def lru(pages, frames):
    memory = []
    page_faults = 0
    memory_states = []
    decisions = []
    page_indices = {}

    for i, page in enumerate(pages):
        fault = False
        if page not in memory:
            if len(memory) < frames:
                memory.append(page)
            else:
                lru_page = min(memory, key=lambda p: page_indices.get(p, -1))
                memory.remove(lru_page)
                memory.append(page)
            page_faults += 1
            fault = True
        page_indices[page] = i
        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")
    return page_faults, memory_states, decisions


def optimal(pages, frames):
    memory = []
    page_faults = 0
    memory_states = []
    decisions = []

    for i, page in enumerate(pages):
        fault = False
        if page not in memory:
            if len(memory) < frames:
                memory.append(page)
            else:
                future_indices = []
                for mem_page in memory:
                    if mem_page in pages[i + 1:]:
                        future_indices.append(pages[i + 1:].index(mem_page))
                    else:
                        future_indices.append(float('inf'))
                replace_index = future_indices.index(max(future_indices))
                memory[replace_index] = page
            page_faults += 1
            fault = True
        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")
    return page_faults, memory_states, decisions


def second_chance(pages, frames):
    """Second Chance Algorithm"""
    memory = []
    reference_bits = []
    pointer = 0
    page_faults = 0
    memory_states = []
    decisions = []

    for page in pages:
        fault = False

        if page in memory:
            idx = memory.index(page)
            reference_bits[idx] = 1
            fault = False
        else:
            if len(memory) < frames:
                memory.append(page)
                reference_bits.append(1)
            else:
                while True:
                    if reference_bits[pointer] == 0:
                        memory[pointer] = page
                        reference_bits[pointer] = 1
                        pointer = (pointer + 1) % frames
                        break
                    else:
                        reference_bits[pointer] = 0
                        pointer = (pointer + 1) % frames

            page_faults += 1
            fault = True

        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")

    return page_faults, memory_states, decisions


def lfu(pages, frames):
    """Least Frequently Used Algorithm"""
    memory = []
    page_faults = 0
    memory_states = []
    decisions = []
    frequency = {}  # Track frequency of each page in memory
    arrival_order = {}  # Track arrival order for tie-breaking

    for i, page in enumerate(pages):
        fault = False

        if page in memory:
            # Page hit - increment frequency
            frequency[page] += 1
            fault = False
        else:
            # Page fault
            if len(memory) < frames:
                # Memory not full
                memory.append(page)
                frequency[page] = 1
                arrival_order[page] = i
            else:
                # Find page with minimum frequency (use arrival order for ties)
                min_freq = min(frequency[p] for p in memory)
                candidates = [p for p in memory if frequency[p] == min_freq]
                # Tie-break by earliest arrival (FIFO among same frequency)
                lfu_page = min(candidates, key=lambda p: arrival_order[p])

                # Remove LFU page
                idx = memory.index(lfu_page)
                del frequency[lfu_page]
                del arrival_order[lfu_page]

                # Add new page
                memory[idx] = page
                frequency[page] = 1
                arrival_order[page] = i

            page_faults += 1
            fault = True

        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")

    return page_faults, memory_states, decisions


def mfu(pages, frames):
    """Most Frequently Used Algorithm"""
    memory = []
    page_faults = 0
    memory_states = []
    decisions = []
    frequency = {}  # Track frequency of each page in memory
    arrival_order = {}  # Track arrival order for tie-breaking

    for i, page in enumerate(pages):
        fault = False

        if page in memory:
            # Page hit - increment frequency
            frequency[page] += 1
            fault = False
        else:
            # Page fault
            if len(memory) < frames:
                # Memory not full
                memory.append(page)
                frequency[page] = 1
                arrival_order[page] = i
            else:
                # Find page with maximum frequency (use arrival order for ties)
                max_freq = max(frequency[p] for p in memory)
                candidates = [p for p in memory if frequency[p] == max_freq]
                # Tie-break by earliest arrival (FIFO among same frequency)
                mfu_page = min(candidates, key=lambda p: arrival_order[p])

                # Remove MFU page
                idx = memory.index(mfu_page)
                del frequency[mfu_page]
                del arrival_order[mfu_page]

                # Add new page
                memory[idx] = page
                frequency[page] = 1
                arrival_order[page] = i

            page_faults += 1
            fault = True

        memory_states.append(memory.copy())
        decisions.append("✔️" if fault else "➖")

    return page_faults, memory_states, decisions


def create_animation_frame(pages, memory_states, decisions, current_step, frames, algorithm):
    """Create a single frame of the animation"""
    # Dynamically scale figure size with number of pages
    height =  len(pages)
    width = len(pages)
    fig, axes = plt.subplots(2, 1, figsize=(width, height), gridspec_kw={'height_ratios': [1, 2]})

    # Top: Reference string with current position highlighted
    ax1 = axes[0]
    ax1.set_xlim(-0.5, len(pages) - 0.5)
    ax1.set_ylim(-0.5, 1.5)
    ax1.set_title(f'''Reference String - Step {current_step + 1}/{len(pages)}


    ''', fontsize=14, fontweight='bold')
    ax1.axis('off')

    for i, page in enumerate(pages):
        if i < current_step:
            color = '#95a5a6'  # Gray for past
            alpha = 0.5
        elif i == current_step:
            color = '#e74c3c' if decisions[i] == "✔️" else '#2ecc71'  # Red for fault, green for hit
            alpha = 1.0
        else:
            color = '#bdc3c7'  # Light gray for future
            alpha = 0.3

        rect = plt.Rectangle((i - 0.4, 0.1), 0.8, 0.8,
                             facecolor=color, edgecolor='black',
                             linewidth=2, alpha=alpha)
        ax1.add_patch(rect)
        ax1.text(i, 0.5, str(page), ha='center', va='center',
                 fontsize=14, fontweight='bold',
                 color='white' if i <= current_step else 'gray')

        # Add step number below
        ax1.text(i, -0.2, str(i + 1), ha='center', va='center', fontsize=8, color='gray')

    # Add arrow pointing to current page
    if current_step < len(pages):
        ax1.annotate('', xy=(current_step, 1.0), xytext=(current_step, 1.4),
                     arrowprops=dict(arrowstyle='->', color='#3498db', lw=3))
        ax1.text(current_step, 1.5, 'Current', ha='center', va='bottom',
                 fontsize=10, color='#3498db', fontweight='bold')

    # Bottom: Memory frames visualization
    ax2 = axes[1]
    ax2.set_xlim(-1, frames + 1)
    ax2.set_ylim(-1, current_step + 2)
    ax2.set_title(f"Memory Frames ({algorithm})", fontsize=14, fontweight='bold')
    ax2.axis('off')

    # Draw frame labels
    for f in range(frames):
        ax2.text(f + 0.5, current_step + 1, f"Frame {f + 1}",
                 ha='center', va='center', fontsize=10, fontweight='bold')

    # Draw memory states up to current step
    for step in range(current_step + 1):
        # Status indicator
        if decisions[step] == "✔️":
            status_color = '#e74c3c'
            status_text = "FAULT"
        else:
            status_color = '#2ecc71'
            status_text = "HIT"

        ax2.text(-0.7, current_step - step, f"S{step + 1}\n{status_text}",
                 ha='center', va='center', fontsize=8, color=status_color, fontweight='bold')

        # Draw frames
        for f in range(frames):
            if f < len(memory_states[step]):
                page_val = memory_states[step][f]

                # Highlight if this is a new page or changed
                if step == current_step:
                    if step == 0 or (f < len(memory_states[step - 1]) and
                                     memory_states[step][f] != memory_states[step - 1][f]):
                        color = '#f39c12'  # Orange for new/changed
                    elif f >= len(memory_states[step - 1]) if step > 0 else True:
                        color = '#f39c12'
                    else:
                        color = '#3498db'  # Blue for unchanged
                else:
                    color = '#95a5a6'  # Gray for past

                rect = plt.Rectangle((f + 0.1, current_step - step - 0.4), 0.8, 0.8,
                                     facecolor=color, edgecolor='black', linewidth=1.5)
                ax2.add_patch(rect)
                ax2.text(f + 0.5, current_step - step, str(page_val),
                         ha='center', va='center', fontsize=12, fontweight='bold', color='white')
            else:
                # Empty frame
                rect = plt.Rectangle((f + 0.1, current_step - step - 0.4), 0.8, 0.8,
                                     facecolor='#ecf0f1', edgecolor='#bdc3c7',
                                     linewidth=1.5, linestyle='--')
                ax2.add_patch(rect)
                ax2.text(f + 0.5, current_step - step, '-',
                         ha='center', va='center', fontsize=12, color='#bdc3c7')

    plt.tight_layout()
    return fig


# UI Configuration
st.set_page_config(layout="wide", page_title="Page Replacement Simulator")
st.title("Page Replacement Algorithm Simulator")

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")
    algorithm = st.selectbox(
        "Select Algorithm",
        ["FIFO", "LRU", "Optimal", "Second Chance", "LFU", "MFU"]
    )
    frames = st.number_input(
        "Number of frames",
        value=3, min_value = 1
    )
    ref_string = st.text_input(
        "Reference string (space-separated)",
        "6 7 8 9 6 7 1 6 7 8 9 1"
    )

    st.markdown("---")
    animation_speed = 1
    show_animation = st.checkbox("Enable Animation", value=True)

    generate = st.button("Run Simulation", type="primary")

if generate:
    try:
        pages = list(map(int, ref_string.strip().split()))
    except:
        st.error("Invalid input! Please enter space-separated integers only.")
        st.stop()

    # Display Configuration
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Algorithm", algorithm)
    with col2:
        st.metric("Frames", frames)
    with col3:
        st.metric("Reference Length", len(pages))
    with col4:
        st.metric("Reference String", " ".join(map(str, pages)))

    # Run selected algorithm
    if algorithm == "FIFO":
        page_faults, memory_states, decisions = fifo(pages, frames)
    elif algorithm == "LRU":
        page_faults, memory_states, decisions = lru(pages, frames)
    elif algorithm == "Optimal":
        page_faults, memory_states, decisions = optimal(pages, frames)
    elif algorithm == "Second Chance":
        page_faults, memory_states, decisions = second_chance(pages, frames)
    elif algorithm == "LFU":
        page_faults, memory_states, decisions = lfu(pages, frames)
    else:  # MFU
        page_faults, memory_states, decisions = mfu(pages, frames)

    # Animation Section
    if show_animation:
        st.markdown("---")
        st.subheader("Page Replacement Animation")

        animation_placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Control buttons
        col1, col2, col3 = st.columns([1, 1, 3])

        # Run animation
        for step in range(len(pages)):
            with animation_placeholder.container():
                fig = create_animation_frame(pages, memory_states, decisions, step, frames, algorithm)
                st.pyplot(fig)
                plt.close(fig)

            progress_bar.progress((step + 1) / len(pages))

            if decisions[step] == "✔️":
                status_text.error(f"⚠️ Step {step + 1}: Page {pages[step]} caused a PAGE FAULT!")
            else:
                status_text.success(f"✅ Step {step + 1}: Page {pages[step]} was a HIT!")

            time.sleep(animation_speed*0.01)

        status_text.info("Animation Complete!")

    # Results Section
    st.markdown("---")
    st.subheader("Results Summary")

    hit_count = len(pages) - page_faults
    miss_rate = (page_faults / len(pages)) * 100
    hit_rate = (hit_count / len(pages)) * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Page Faults", page_faults)
    with col2:
        st.metric("Hits", hit_count)
    with col3:
        st.metric("Total References", len(pages))

    # Hit/Miss Ratio Bar
    st.subheader("Hit/Miss Ratio")
    st.markdown(
        f"""
        <div style="width: 100%; height: 35px; background-color: #eee; border-radius: 8px; display: flex; overflow: hidden; margin: 10px 0;">
            <div style="width: {miss_rate}%; background-color: #e74c3c; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {miss_rate:.1f}% Miss
            </div>
            <div style="width: {hit_rate}%; background-color: #2ecc71; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {hit_rate:.1f}% Hit
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Memory State Table
    st.markdown("---")
    st.subheader("Memory State Changes")

    # Prepare table data
    table_data = []
    for i in range(len(pages)):
        row = {"Step": i + 1, "Page Requested": pages[i]}
        for f in range(frames):
            if f < len(memory_states[i]):
                row[f"Frame {f + 1}"] = memory_states[i][f]
            else:
                row[f"Frame {f + 1}"] = "-"
        row["Page Fault"] = decisions[i]
        table_data.append(row)

    df = pd.DataFrame(table_data)
    df = df.astype(str)
    st.dataframe(
        df.style.set_properties(**{'text-align': 'center'}).set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]}
        ]),
        width='stretch',
        hide_index=True
    )

    # Detailed step-by-step view
    st.subheader(" Step-by-Step Simulation")

    for i in range(len(pages)):
        with st.expander(f"Step {i + 1}: Request Page {pages[i]}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Memory State:**")
                memory_display = {}
                for f in range(frames):
                    if f < len(memory_states[i]):
                        memory_display[f"Frame {f + 1}"] = memory_states[i][f]
                    else:
                        memory_display[f"Frame {f + 1}"] = "-"
                st.json(memory_display)

            with col2:
                st.write("**Status:**")
                if decisions[i] == "✔️":
                    st.error("⚠️ Page Fault Occurred")
                    st.write(f"**Action:** Page {pages[i]} was loaded into memory")
                else:
                    st.success("✅ Page Hit")
                    st.write(f"**Action:** Page {pages[i]} was already in memory")

            if i > 0 and memory_states[i] != memory_states[i - 1]:
                st.info("🔄 Memory state changed!")
                st.write("**Previous Memory:**")
                prev_memory = {}
                for f in range(frames):
                    if f < len(memory_states[i - 1]):
                        prev_memory[f"Frame {f + 1}"] = memory_states[i - 1][f]
                    else:
                        prev_memory[f"Frame {f + 1}"] = "-"
                st.json(prev_memory)

    # Algorithm Comparison Chart
    st.markdown("---")
    st.subheader(f'''Algorithm Comparison''')

    # Calculate faults for all algorithms
    fifo_faults = fifo(pages, frames)[0]
    lru_faults = lru(pages, frames)[0]
    optimal_faults = optimal(pages, frames)[0]
    second_chance_faults = second_chance(pages, frames)[0]
    lfu_faults = lfu(pages, frames)[0]
    mfu_faults = mfu(pages, frames)[0]

    fig, ax = plt.subplots(figsize=(12, 6))
    algos = ["FIFO", "LRU", "Optimal", "Second Chance", "LFU", "MFU"]
    faults = [fifo_faults, lru_faults, optimal_faults, second_chance_faults, lfu_faults, mfu_faults]
    colors = ["#4C72B0", "#55A868", "#C44E52", "#FFA15A", "#8E44AD", "#1ABC9C"]

    bars = ax.bar(algos, faults, color=colors, edgecolor='black', linewidth=1.2)
    ax.set_ylabel("Number of Page Faults", fontsize=12)
    ax.set_title("Page Fault Comparison Across Algorithms", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    plt.xticks(rotation=15)
    st.pyplot(fig)

    # Performance metrics table
    st.subheader("Performance Comparison Table")
    comparison_data = {
        "Algorithm": ["FIFO", "LRU", "Optimal", "Second Chance", "LFU", "MFU"],
        "Page Faults": [fifo_faults, lru_faults, optimal_faults, second_chance_faults, lfu_faults, mfu_faults],
        "Hits": [len(pages) - fifo_faults, len(pages) - lru_faults,
                 len(pages) - optimal_faults, len(pages) - second_chance_faults,
                 len(pages) - lfu_faults, len(pages) - mfu_faults],
        "Hit Rate (%)": [round((len(pages) - fifo_faults) / len(pages) * 100, 2),
                         round((len(pages) - lru_faults) / len(pages) * 100, 2),
                         round((len(pages) - optimal_faults) / len(pages) * 100, 2),
                         round((len(pages) - second_chance_faults) / len(pages) * 100, 2),
                         round((len(pages) - lfu_faults) / len(pages) * 100, 2),
                         round((len(pages) - mfu_faults) / len(pages) * 100, 2)]
    }
    comp_df = pd.DataFrame(comparison_data)
    # Highlight best and worst
    def highlight_best_worst(s):
        if s.name == 'Page Faults':
            is_best = s == s.min()
            is_worst = s == s.max()
            return ['background-color: #25b315' if v else 'background-color: #f70707' if w else ''
                    for v, w in zip(is_best, is_worst)]
        elif s.name == 'Hit Rate (%)':
            is_best = s == s.max()
            is_worst = s == s.min()
            return ['background-color: #25b315' if v else 'background-color: #f70707' if w else ''
                    for v, w in zip(is_best, is_worst)]
        return ['' for _ in s]


    styled_df = comp_df.style.apply(highlight_best_worst)
    st.dataframe(styled_df, width='stretch', hide_index=True)

    st.caption("🟢 Green = Best Performance | 🔴 Red = Worst Performance")

# Footer
st.markdown("---")
st.caption("Made by Anshul Thakur and Ankit Yadav | Page Replacement Algorithm Simulator")
