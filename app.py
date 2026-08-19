"""
Planck CURVD Stumper Generator – Adaptive Edition
================================================
- Stricter filtering against strongest current models
- Hard / Adaptive mode that invents fresher traps
- Strong randomization to defeat memorization
- Techniques: hidden dependency, wrong-answer attractor, inverse problems
- Endless non-repeating problems
- In-app rating + export
"""

import streamlit as st
import random
import hashlib
import re
import math
import csv
import io
from datetime import datetime

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ============================================================
# Session state
# ============================================================
if "seen_hashes" not in st.session_state:
    st.session_state.seen_hashes = set()
if "generated_count" not in st.session_state:
    st.session_state.generated_count = 0
if "last_problem" not in st.session_state:
    st.session_state.last_problem = None
if "filter_results" not in st.session_state:
    st.session_state.filter_results = {}
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False

def problem_hash(q: str, a: str) -> str:
    return hashlib.sha256((q.strip() + "|||" + a.strip()).encode()).hexdigest()

def is_novel(q: str, a: str) -> bool:
    h = problem_hash(q, a)
    if h in st.session_state.seen_hashes:
        return False
    st.session_state.seen_hashes.add(h)
    return True

# ============================================================
# Stronger procedural generators (anti-memorization)
# ============================================================

def gen_group_order_hard():
    """Groups of order p^3 with exponent restriction – attractor is the unrestricted count 5."""
    p = random.choice([3, 5, 7, 11])
    seed = random.randrange(10**9)
    # Number of groups of order p^3 is 5. Number of exponent exactly p is 2 (for odd p).
    answer = "2"
    question = (
        f"How many groups of order ${p}^3$ have exponent exactly ${p}$? "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: There are exactly 5 groups of order p^3 up to isomorphism.\n"
        f"STEP 2: They are: Z_{{p^3}}, Z_{{p^2}}×Z_p, Z_p^3, Heis(p), and the semidirect product M.\n"
        f"STEP 3: Only the elementary abelian and the Heisenberg group mod p have exponent p.\n"
        f"STEP 4: Therefore the number is 2.\n"
        f"Wrong-answer attractor: the unrestricted total 5.\n"
        f"FINAL ANSWER: 2"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["wrong-answer attractor (total 5)", "hidden exponent restriction"],
        "seed": seed
    }


def gen_discriminant_period():
    """Discriminant of the 7th cyclotomic period cubic – forces calculation instead of recall."""
    seed = random.randrange(10**9)
    # Minimal polynomial of 2cos(2π/7) is x^3 + x^2 - 2x - 1 = 0, discriminant 49
    answer = "49"
    question = (
        f"Let $\\theta = 2\\cos(2\\pi/7)$. It is a root of the irreducible cubic "
        f"$X^3 + X^2 - 2X - 1$. What is the discriminant of this cubic? "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: For a cubic $x^3 + ax^2 + bx + c$ the discriminant is "
        f"$18abcd -4a^3d + a^2b^2 - 4b^3 - 27c^2$ (here a=1,b=-2,c=-1).\n"
        f"STEP 2: Direct evaluation yields 49.\n"
        f"STEP 3: Alternatively, known result for the 7th period polynomial.\n"
        f"Wrong-answer attractor: 7 or -49 or 1.\n"
        f"FINAL ANSWER: 49"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["forces intermediate calculation", "wrong-answer attractor (7 or -49)"],
        "seed": seed
    }


def gen_hilbert_tower():
    """[H:Q] for Q(√-47) – class number 5, but degree over Q is 10."""
    seed = random.randrange(10**9)
    answer = "10"
    question = (
        f"Let $K = \\mathbb{{Q}}(\\sqrt{{-47}})$. Let $H$ be the Hilbert class field of $K$. "
        f"What is the degree $[H : \\mathbb{{Q}}]$? Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: [H:K] = class number h_K = 5.\n"
        f"STEP 2: [K:Q] = 2.\n"
        f"STEP 3: Therefore [H:Q] = 5 × 2 = 10.\n"
        f"Wrong-answer attractor: report the class number 5 instead of the absolute degree.\n"
        f"FINAL ANSWER: 10"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["wrong-answer attractor (class number 5)", "hidden tower degree"],
        "seed": seed
    }


def gen_modular_order_hard():
    primes = [11, 13, 17, 19, 23, 29, 31]
    p = random.choice(primes)
    q = random.choice([r for r in primes if r != p])
    n = p * q

    def order_mod(base, mod):
        if math.gcd(base, mod) != 1:
            return None
        o, val = 1, base % mod
        while val != 1:
            val = (val * base) % mod
            o += 1
            if o > mod:
                return None
        return o

    op = order_mod(2, p)
    oq = order_mod(2, q)
    if op is None or oq is None:
        return gen_modular_order_hard()
    ans = math.lcm(op, oq)
    seed = random.randrange(10**9)
    question = (
        f"Let $n={n}={p}\\times{q}$. "
        f"Compute the multiplicative order of 2 modulo $n$. "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: ord_{p}(2) = {op}\n"
        f"STEP 2: ord_{q}(2) = {oq}\n"
        f"STEP 3: ord_n(2) = lcm = {ans}\n"
        f"Wrong-answer attractor: φ(n)={(p-1)*(q-1)}.\n"
        f"FINAL ANSWER: {ans}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": str(ans),
        "golden": golden,
        "techniques": ["tempting φ(n) attractor", "hidden CRT"],
        "seed": seed
    }


def gen_supergravity_dof():
    data = [
        (11, "graviton", 44),
        (11, "3-form", 84),
        (10, "graviton", 35),
        (9, "graviton", 27),
        (8, "graviton", 20),
        (7, "graviton", 14),
        (6, "graviton", 9),
        (5, "graviton", 5),
    ]
    D, field, dof = random.choice(data)
    seed = random.randrange(10**9)
    question = (
        f"In $D={D}$ spacetime dimensions, how many on-shell degrees of freedom does a massless "
        f"{field} possess? Give the exact integer."
    )
    answer = str(dof)
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: On-shell graviton dof = D(D-3)/2.\n"
        f"STEP 2: For p-form use binom(D-2,p).\n"
        f"STEP 3: Result = {dof}.\n"
        f"Wrong-answer attractor: off-shell count.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Physics",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["wrong-answer attractor (off-shell)", "on-shell vs off-shell"],
        "seed": seed
    }


def gen_recoil():
    ratio = random.choice([9, 14, 18, 25, 35])
    seed = random.randrange(10**9)
    question = (
        f"A thin spherical shell of mass $M$ is at rest in free space. "
        f"A point mass $m = M/{ratio}$ is released from rest at distance $2R$ from the centre. "
        f"When the point mass reaches distance $R$, what is the displacement of the shell centre "
        f"as a simplified fraction of $R$?"
    )
    ans = f"1/{ratio+1}"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: CM fixed → M d = m (R - d).\n"
        f"STEP 2: d = m/(M+m) R = 1/{ratio+1} R.\n"
        f"Wrong-answer attractor: 0 (fixed shell).\n"
        f"FINAL ANSWER: {ans}"
    )
    return {
        "category": "Physics",
        "question": question,
        "answer": ans,
        "golden": golden,
        "techniques": ["wrong-answer attractor (fixed body)", "hidden CM"],
        "seed": seed
    }


def gen_procedural():
    gens = [
        gen_group_order_hard,
        gen_discriminant_period,
        gen_hilbert_tower,
        gen_modular_order_hard,
        gen_supergravity_dof,
        gen_recoil,
    ]
    for _ in range(30):
        prob = random.choice(gens)()
        if is_novel(prob["question"], prob["answer"]):
            return prob
    return gen_group_order_hard()


# ============================================================
# Adaptive / Hard mode – LLM invents fresher traps
# ============================================================

ADAPTIVE_PROMPT = """You are an expert at designing problems that stump frontier LLMs.

Create ONE original, self-contained PhD-level Math or Physics problem that is likely to be missed by current strong models because of pure recall or shallow pattern matching.

Mandatory requirements (CURVD):
- Exact unique short answer (integer or simple expression)
- Fully self-contained
- Solvable by careful human reasoning without a computer
- Answer solely derivable from the problem statement

Mandatory techniques (use at least three):
1. Hidden critical dependency (a parameter that looks minor but changes everything)
2. Strong wrong-answer attractor (a very natural wrong answer that most models will give)
3. Inverse formulation or non-obvious restriction
4. Fresh random parameters so the concrete numbers have never been seen together

Strict output format only:

CATEGORY: Math
QUESTION:
<problem>
ANSWER:
<exact short answer>
GOLDEN:
SEED = <random 9-digit>
STEP 1: ...
STEP 2: ...
FINAL ANSWER: <same>

Do not reuse famous textbook numbers as the final answer.
"""

def generate_adaptive(api_key: str):
    if not HAS_GENAI:
        return None, "google-genai not installed"
    models = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-2.0-flash"]
    last_error = None
    for m in models:
        try:
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(model=m)
            resp = chat.send_message(ADAPTIVE_PROMPT)
            text = resp.text or ""
            return parse_llm_output(text), None
        except Exception as e:
            last_error = str(e)
    return None, last_error


def parse_llm_output(text: str):
    cat = "Math"
    m = re.search(r"CATEGORY:\s*(Math|Physics)", text, re.I)
    if m:
        cat = m.group(1).capitalize()
    q_match = re.search(r"QUESTION:\s*(.*?)(?=ANSWER:|$)", text, re.S | re.I)
    a_match = re.search(r"ANSWER:\s*(.*?)(?=GOLDEN:|$)", text, re.S | re.I)
    g_match = re.search(r"GOLDEN:\s*(.*)", text, re.S | re.I)
    question = q_match.group(1).strip() if q_match else text
    answer = a_match.group(1).strip() if a_match else "UNKNOWN"
    golden = g_match.group(1).strip() if g_match else "Golden not provided."
    answer = re.sub(r"^\$+|\$+$", "", answer).strip()
    return {
        "category": cat,
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["adaptive LLM invention", "hidden dependency", "wrong-answer attractor"],
        "seed": random.randrange(10**9)
    }


# ============================================================
# Model callers with strongest models + fallbacks
# ============================================================

def ask_gemini(api_key: str, question: str):
    if not HAS_GENAI or not api_key:
        return None, "no key"
    models = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last = None
    for m in models:
        try:
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(model=m)
            resp = chat.send_message(
                "Solve rigorously. Final answer on its own line after FINAL ANSWER:\n\n" + question
            )
            return resp.text or "", None
        except Exception as e:
            last = str(e)
    return None, last


def ask_deepseek(api_key: str, question: str):
    if not HAS_OPENAI or not api_key:
        return None, "no key"
    models = [
        "deepseek/deepseek-v4-pro-0813",
        "deepseek/deepseek-v4-pro",
        "deepseek/deepseek-v4-flash",
        "deepseek/deepseek-r1",
        "deepseek/deepseek-chat",
    ]
    last = None
    for model in models:
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": question}],
                temperature=0,
                max_tokens=900
            )
            return r.choices[0].message.content, None
        except Exception as e:
            last = str(e)
    return None, last


def model_failed(reply: str, gold: str) -> bool:
    if not reply:
        return True
    clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", reply.lower())
    gold_clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", str(gold).lower())
    if gold_clean in clean:
        return False
    # numeric check
    try:
        g = float(gold)
        nums = re.findall(r"-?\d+\.?\d*", reply)
        for n in nums:
            if abs(float(n) - g) < 1e-6:
                return False
    except Exception:
        pass
    return True


# ============================================================
# UI
# ============================================================

st.set_page_config(page_title="Planck Adaptive Stumper Generator", layout="wide")
st.title("Planck Adaptive Stumper Generator")
st.caption("Stricter filtering • Hard/Adaptive mode • Anti-memorization • Strongest models")

with st.sidebar:
    st.header("Generation Mode")
    gen_mode = st.radio(
        "Mode",
        [
            "Procedural (fast, anti-mem)",
            "Hard Adaptive (LLM invents new traps)",
            "LLM-assisted classic"
        ],
        index=0
    )
    st.markdown("---")
    st.subheader("Filter Strength")
    use_filter = st.checkbox("Only keep problems that fail models", value=True)
    min_failures = st.slider("Minimum models that must fail", 1, 2, 1)
    st.markdown("---")
    st.subheader("API Keys")
    google_key = st.text_input("Google AI Studio key", type="password")
    openrouter_key = st.text_input("OpenRouter key (DeepSeek)", type="password")
    st.markdown("---")
    st.write(f"Generated: **{st.session_state.generated_count}**")
    st.write(f"Unique hashes: **{len(st.session_state.seen_hashes)}**")
    if st.button("Clear hash memory"):
        st.session_state.seen_hashes = set()
        st.success("Cleared")

    # Feedback
    st.markdown("---")
    st.subheader("Rate this app")
    with st.form("feedback_form", clear_on_submit=True):
        rating = st.feedback("stars")
        comment = st.text_area("Comment (optional)", max_chars=400, height=70)
        email = st.text_input("Email (optional)")
        if st.form_submit_button("Submit feedback"):
            if rating is None:
                st.warning("Select stars")
            else:
                st.session_state.feedbacks.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "rating": int(rating) + 1,
                    "comment": comment.strip(),
                    "email": email.strip()
                })
                st.success("Thank you!")
    if st.session_state.feedbacks:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "rating", "comment", "email"])
        writer.writeheader()
        writer.writerows(st.session_state.feedbacks)
        st.download_button("Download feedbacks CSV", output.getvalue(), "feedbacks.csv", "text/csv")

# Generate
if st.button("Generate new stumper", type="primary", use_container_width=True):
    with st.spinner("Generating + strict filtering against strongest models…"):
        max_attempts = 10
        kept = None
        log = []

        for attempt in range(max_attempts):
            if gen_mode.startswith("Procedural"):
                candidate = gen_procedural()
            elif gen_mode.startswith("Hard Adaptive"):
                if not google_key:
                    st.error("Hard Adaptive mode needs a Google key")
                    break
                candidate, err = generate_adaptive(google_key)
                if err or not candidate:
                    log.append(f"Adaptive error: {err}")
                    continue
                if not is_novel(candidate["question"], candidate["answer"]):
                    continue
            else:
                if not google_key:
                    st.error("Needs Google key")
                    break
                candidate, err = generate_adaptive(google_key)  # reuse for classic too
                if err or not candidate:
                    log.append(str(err))
                    continue
                if not is_novel(candidate["question"], candidate["answer"]):
                    continue

            # Strict filter
            failures = 0
            results = {}
            if use_filter:
                if google_key:
                    reply, err = ask_gemini(google_key, candidate["question"])
                    if err:
                        results["gemini"] = f"ERROR"
                    else:
                        failed = model_failed(reply, candidate["answer"])
                        results["gemini"] = "FAILED" if failed else "SOLVED"
                        if failed:
                            failures += 1
                if openrouter_key:
                    reply, err = ask_deepseek(openrouter_key, candidate["question"])
                    if err:
                        results["deepseek"] = "ERROR"
                    else:
                        failed = model_failed(reply, candidate["answer"])
                        results["deepseek"] = "FAILED" if failed else "SOLVED"
                        if failed:
                            failures += 1

                if failures >= min_failures:
                    kept = candidate
                    st.session_state.filter_results = results
                    break
                else:
                    log.append(f"Attempt {attempt+1}: only {failures} failures → discarded")
            else:
                kept = candidate
                st.session_state.filter_results = {}
                break

        if kept:
            st.session_state.last_problem = kept
            st.session_state.generated_count += 1
            st.success(f"Kept after {attempt+1} attempt(s)")
            if st.session_state.generated_count >= 2 and not st.session_state.feedback_submitted:
                st.info("Finding these useful? Leave a star rating in the sidebar.")
        else:
            st.warning("No problem survived the filter this run. Try again or lower the threshold.")
            if log:
                with st.expander("Log"):
                    for line in log:
                        st.text(line)

# Display
if st.session_state.last_problem:
    p = st.session_state.last_problem
    st.markdown("### Ready for Planck")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"**Category:** `{p['category']}`")
        st.markdown("**Question**")
        st.markdown(p["question"])
        st.markdown("**Answer**")
        st.code(p["answer"])
        st.info("Leave Golden Trajectory **empty** on the first Planck trial.")
        with st.expander("Golden Trajectory (after ==PASSED==)"):
            st.code(p["golden"])
    with c2:
        st.markdown("**Techniques**")
        for t in p.get("techniques", []):
            st.write("• " + t)
        st.write(f"Seed: `{p.get('seed')}`")
        if st.session_state.filter_results:
            st.markdown("**Filter**")
            for m, s in st.session_state.filter_results.items():
                st.write(f"{m}: **{s}**")

    export = (
        f"CATEGORY: {p['category']}\n\n"
        f"QUESTION:\n{p['question']}\n\n"
        f"ANSWER:\n{p['answer']}\n\n"
        f"GOLDEN TRAJECTORY:\n(leave empty on first trial)\n\n"
        f"--- later ---\n{p['golden']}\n"
    )
    st.download_button(
        "Download Planck-ready .txt",
        export,
        f"planck_{p.get('seed')}.txt",
        "text/plain",
        use_container_width=True
    )

st.markdown("---")
st.caption(
    "Adaptive Edition: stronger anti-memorization templates + Hard mode that invents new traps + "
    "strict filtering against DeepSeek V4 Pro and current Gemini. "
    "Problems are forced novel via hash memory."
)
