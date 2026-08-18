"""
Planck CURVD Stumper Generator App – Enhanced + Feedback
=======================================================
- More procedural templates
- Automatic multi-model filter
- Export button
- In-app rating + feedback system (stars + comment + optional email)
- Techniques to defeat pure recall
- Endless non-repeating random problems
"""

import streamlit as st
import random
import hashlib
import re
import math
import csv
import io
from datetime import datetime

# Optional imports
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
# Procedural generators
# ============================================================

def gen_group_order():
    primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    p = random.choice(primes)
    q = random.choice([r for r in primes if r != p])
    n = p * q
    if (p - 1) % q == 0 or (q - 1) % p == 0:
        answer = "2"
    else:
        answer = "1"
    seed = random.randrange(10**9)
    question = (
        f"Let $G$ be a group of order ${n} = {p}\\times{q}$. "
        f"How many distinct groups of order ${n}$ exist up to isomorphism? "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: n_p ≡ 1 mod p and divides q; n_q ≡ 1 mod q and divides p.\n"
        f"STEP 2: Divisibility check shows {'non-trivial' if answer=='2' else 'only trivial'} actions exist.\n"
        f"STEP 3: Exactly {answer} isomorphism class(es).\n"
        f"Wrong-answer attractor: always claim 1 (cyclic only).\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["wrong-answer attractor (always cyclic)", "hidden Sylow dependency"],
        "seed": seed
    }


def gen_modular_order():
    primes = [11, 13, 17, 19, 23, 29]
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
        return gen_modular_order()
    ans = math.lcm(op, oq)
    seed = random.randrange(10**9)
    question = (
        f"Let $n={n}={p}\\times{q}$. "
        f"Compute the multiplicative order of 2 modulo $n$ "
        f"(smallest positive $k$ with $2^k\\equiv 1\\pmod{{n}}$). "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: ord_{p}(2) = {op}\n"
        f"STEP 2: ord_{q}(2) = {oq}\n"
        f"STEP 3: ord_n(2) = lcm({op},{oq}) = {ans}\n"
        f"Wrong-answer attractor: φ(n)={(p-1)*(q-1)} or simply {op}/{oq}.\n"
        f"FINAL ANSWER: {ans}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": str(ans),
        "golden": golden,
        "techniques": ["tempting invalid simplification (φ(n))", "hidden CRT dependency"],
        "seed": seed
    }


def gen_class_number_degree():
    data = [
        (23, 3), (31, 3), (39, 4), (47, 5), (59, 3),
        (67, 1), (71, 7), (83, 3), (87, 6), (103, 5),
    ]
    d, h = random.choice(data)
    seed = random.randrange(10**9)
    question = (
        f"Let $K=\\mathbb{{Q}}(\\sqrt{{-{d}}})$. "
        f"Let $H$ be the Hilbert class field of $K$. "
        f"What is the degree $[H:K]$? "
        f"Give the exact integer."
    )
    answer = str(h)
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: [H:K] equals the class number h_K of K.\n"
        f"STEP 2: For the imaginary quadratic field Q(√-{d}) the class number is {h}.\n"
        f"STEP 3: Therefore [H:K] = {h}.\n"
        f"Wrong-answer attractor: claim degree 1 or 2.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["misleading formulation (degree vs class number)", "wrong-answer attractor (degree 1)"],
        "seed": seed
    }


def gen_schur_evaluation():
    partitions = [
        ([3, 1], 4, [1, 1, 2, 1], 20),
        ([2, 2], 4, [1, 1, 1, 2], 10),
        ([4, 1], 5, [1, 1, 1, 1, 2], 35),
        ([3, 2], 5, [1, 2, 1, 1, 1], 50),
        ([3, 1, 1], 5, [1, 1, 1, 2, 1], 45),
    ]
    part, n, point, val = random.choice(partitions)
    seed = random.randrange(10**9)
    part_str = ",".join(map(str, part))
    point_str = ",".join(map(str, point))
    question = (
        f"Let $s_{{\\lambda}}$ be the Schur polynomial associated to the partition $\\lambda=({part_str})$. "
        f"Evaluate $s_{{\\lambda}}$ at the point $({point_str})$ (n={n} variables). "
        f"Give the exact integer value."
    )
    answer = str(val)
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Expand via Weyl formula or monomial basis.\n"
        f"STEP 2: Substitute the given point.\n"
        f"STEP 3: Evaluation equals {val}.\n"
        f"Wrong-answer attractor: evaluate at all-ones instead.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["hidden critical dependency (evaluation point)", "wrong-answer attractor (all-ones)"],
        "seed": seed
    }


def gen_supergravity_dof():
    data = [
        (11, "graviton", 44),
        (11, "3-form", 84),
        (10, "graviton", 35),
        (10, "2-form", 28),
        (9, "graviton", 27),
        (8, "graviton", 20),
        (7, "graviton", 14),
        (6, "graviton", 9),
        (5, "graviton", 5),
        (4, "graviton", 2),
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
        f"STEP 1: On-shell dof for massless graviton in D dimensions is D(D-3)/2.\n"
        f"STEP 2: For a massless p-form the count is binom(D-2, p).\n"
        f"STEP 3: Direct evaluation yields {dof}.\n"
        f"Wrong-answer attractor: report the off-shell count.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Physics",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["wrong-answer attractor (off-shell count)", "hidden on-shell vs off-shell distinction"],
        "seed": seed
    }


def gen_recoil_physics():
    ratio = random.choice([8, 12, 15, 20, 24, 30])
    seed = random.randrange(10**9)
    question = (
        f"A thin spherical shell of mass $M$ and radius $R$ is initially at rest in free space. "
        f"A point mass $m=M/{ratio}$ is released from rest at distance $2R$ from the centre of the shell. "
        f"When the point mass reaches distance $R$ from the centre, what is the displacement of the "
        f"centre of the shell relative to the original inertial frame, expressed as a simplified fraction of $R$?"
    )
    ans = f"1/{ratio + 1}"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Centre-of-mass remains fixed.\n"
        f"STEP 2: $M d = m(R-d)$.\n"
        f"STEP 3: $d=\\frac{{m}}{{M+m}}R=\\frac{{1}}{{{ratio}+1}}R$.\n"
        f"Wrong-answer attractor: treat shell as fixed → 0.\n"
        f"FINAL ANSWER: {ans}"
    )
    return {
        "category": "Physics",
        "question": question,
        "answer": ans,
        "golden": golden,
        "techniques": ["wrong-answer attractor (fixed shell)", "hidden CM dependency"],
        "seed": seed
    }


def gen_inverse_integral():
    cases = [
        (0, r"\dfrac{\pi}{2}"),
        (1, r"\dfrac{\pi}{2\sqrt{2}}"),
    ]
    a_star, target = random.choice(cases)
    seed = random.randrange(10**9)
    question = (
        f"Consider the family\n\n"
        f"$$I(a)=\\int_0^{{\\infty}}\\frac{{1}}{{1+x^2+a x^4}}\\,dx,\\qquad a\\ge 0.$$\n\n"
        f"There is a unique $a_*\\ge 0$ such that $I(a_*)={target}$. "
        f"Determine the exact value of $a_*$."
    )
    answer = str(a_star)
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Closed-form evaluation shows I(0)=π/2 and I(1)=π/(2√2).\n"
        f"STEP 2: Uniqueness follows from strict monotonicity in a.\n"
        f"STEP 3: Therefore a_*={a_star}.\n"
        f"Wrong-answer attractor: always pick a=1.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["inverse problem", "hidden critical dependency on a", "wrong-answer attractor"],
        "seed": seed
    }


def gen_cyclotomic_period():
    p = random.choice([7, 13])
    seed = random.randrange(10**9)
    if p == 7:
        answer = "-1"
        question = (
            f"Let $\\zeta=e^{{2\\pi i/7}}$. Define the period "
            f"$\\eta=\\zeta+\\zeta^{{-1}}+\\zeta^{{2}}+\\zeta^{{-2}}$. "
            f"What is the exact value of $\\eta$? Give the integer."
        )
        golden = (
            f"SEED = {seed}\n"
            f"STEP 1: Sum of all non-1 seventh roots of unity is -1.\n"
            f"STEP 2: The real periods satisfy a known cubic; direct evaluation gives η = -1.\n"
            f"FINAL ANSWER: -1"
        )
    else:
        answer = "-1"
        question = (
            f"Let $\\zeta=e^{{2\\pi i/13}}$. Let $\\eta$ be the sum of one set of quadratic-residue periods "
            f"(length 6). What is $\\eta + \\eta' $ where $\\eta'$ is the complementary period? "
            f"Give the exact integer."
        )
        golden = (
            f"SEED = {seed}\n"
            f"STEP 1: Sum of all non-trivial 13th roots of unity is -1.\n"
            f"STEP 2: The two periods of length 6 therefore sum to -1.\n"
            f"FINAL ANSWER: -1"
        )
    return {
        "category": "Math",
        "question": question,
        "answer": answer,
        "golden": golden,
        "techniques": ["misleading period definition", "wrong-answer attractor (0 or 1)"],
        "seed": seed
    }


def gen_procedural():
    gens = [
        gen_group_order,
        gen_modular_order,
        gen_class_number_degree,
        gen_schur_evaluation,
        gen_supergravity_dof,
        gen_recoil_physics,
        gen_inverse_integral,
        gen_cyclotomic_period,
    ]
    for _ in range(40):
        prob = random.choice(gens)()
        if is_novel(prob["question"], prob["answer"]):
            return prob
    return gen_group_order()


# ============================================================
# LLM-assisted generation
# ============================================================

LLM_GENERATION_PROMPT = """You are a research-level problem designer for Project Planck.

Create ONE original, self-contained PhD-level mathematics or physics problem that satisfies ALL CURVD constraints:

C – Correct: answer exactly verifiable by direct calculation.
U – Unique: exactly one correct short answer.
R – Rigorous multi-step reasoning required.
V – Verifiable without external tables beyond elementary constants.
D – Difficult for models that rely on pure recall.

Mandatory techniques (use ≥3):
- Hidden critical dependency
- Tempting invalid simplification / wrong-answer attractor
- Inverse problem or non-separable coupling
- Fresh random parameters so the concrete instance is unseen

Strict output format (nothing else):

CATEGORY: Math   or   Physics
QUESTION:
<full self-contained problem in Markdown + LaTeX>
ANSWER:
<exact short answer>
GOLDEN:
SEED = <9-digit number>
STEP 1: ...
STEP 2: ...
FINAL ANSWER: <same as ANSWER>

The answer must be solely derivable from calculation inside the problem.
"""

def generate_with_llm(api_key: str, model: str = "gemini-2.5-flash"):
    if not HAS_GENAI:
        return None, "google-genai not installed"
    try:
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model=model)
        response = chat.send_message(LLM_GENERATION_PROMPT)
        text = response.text or ""
        return parse_llm_output(text), None
    except Exception as e:
        return None, str(e)

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
        "techniques": ["LLM-generated with forced CURVD + attractor + hidden dependency"],
        "seed": random.randrange(10**9)
    }


# ============================================================
# Multi-model testing helpers
# ============================================================

def ask_gemini(api_key: str, question: str, model: str = "gemini-2.5-flash"):
    if not HAS_GENAI or not api_key:
        return None, "no key / no library"
    try:
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model=model)
        resp = chat.send_message(
            "Solve rigorously. Put the final answer on its own line after FINAL ANSWER:\n\n" + question
        )
        return resp.text or "", None
    except Exception as e:
        return None, str(e)

def ask_deepseek(api_key: str, question: str):
    if not HAS_OPENAI or not api_key:
        return None, "no key / no library"
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        r = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": question}],
            temperature=0,
            max_tokens=1200
        )
        return r.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def model_failed(reply: str, gold: str) -> bool:
    if not reply:
        return True
    clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", reply.lower())
    gold_clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", str(gold).lower())
    if gold_clean in clean:
        return False
    try:
        if abs(float(gold) - float(re.search(r"-?\d+\.?\d*", reply).group())) < 1e-6:
            return False
    except Exception:
        pass
    return True


# ============================================================
# Streamlit UI
# ============================================================

st.set_page_config(page_title="Planck CURVD Stumper Generator", layout="wide")
st.title("Planck CURVD Stumper Generator")
st.caption("Algebraic combinatorics • Class numbers • Supergravity • Multi-model filter • Feedback")

with st.sidebar:
    st.header("Settings")
    gen_mode = st.radio(
        "Generation mode",
        ["Procedural (no LLM for generation)", "LLM-assisted generation"],
        index=0
    )
    st.markdown("---")
    st.subheader("Multi-model filter")
    use_filter = st.checkbox("Only keep problems that fail ≥ N models", value=True)
    min_failures = st.slider("Minimum models that must fail", 1, 3, 1)
    st.markdown("---")
    st.subheader("API Keys")
    google_key = st.text_input("Google AI Studio key", type="password")
    openrouter_key = st.text_input("OpenRouter key (DeepSeek)", type="password")
    st.markdown("---")
    st.write(f"Generated this session: **{st.session_state.generated_count}**")
    st.write(f"Unique hashes: **{len(st.session_state.seen_hashes)}**")
    if st.button("Clear seen-hash memory"):
        st.session_state.seen_hashes = set()
        st.success("Cleared")

    # ---------- FEEDBACK SECTION IN SIDEBAR ----------
    st.markdown("---")
    st.subheader("Rate this app")
    with st.form("feedback_form", clear_on_submit=True):
        rating = st.feedback("stars")  # Streamlit native star rating (1-5)
        comment = st.text_area("Comment (optional)", max_chars=500, height=80)
        email = st.text_input("Email (optional)", placeholder="you@example.com")
        submitted = st.form_submit_button("Submit feedback")

        if submitted:
            if rating is None:
                st.warning("Please select a star rating.")
            else:
                entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "rating": int(rating) + 1,  # st.feedback returns 0-4
                    "comment": comment.strip(),
                    "email": email.strip(),
                }
                st.session_state.feedbacks.append(entry)
                st.session_state.feedback_submitted = True
                st.success("Thank you for your feedback!")

    if st.session_state.feedbacks:
        st.caption(f"{len(st.session_state.feedbacks)} feedback(s) collected in this session")
        # Download all feedbacks as CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "rating", "comment", "email"])
        writer.writeheader()
        writer.writerows(st.session_state.feedbacks)
        st.download_button(
            label="Download feedbacks (CSV)",
            data=output.getvalue(),
            file_name="planck_feedbacks.csv",
            mime="text/csv"
        )

# Generate button
if st.button("Generate new stumper", type="primary", use_container_width=True):
    with st.spinner("Generating + filtering…"):
        max_attempts = 12
        kept = None
        filter_log = []

        for attempt in range(max_attempts):
            if gen_mode.startswith("Procedural"):
                candidate = gen_procedural()
            else:
                if not google_key:
                    st.error("LLM mode needs a Google key")
                    break
                candidate, err = generate_with_llm(google_key)
                if err or candidate is None:
                    filter_log.append(f"LLM error: {err}")
                    continue
                if not is_novel(candidate["question"], candidate["answer"]):
                    continue

            failures = 0
            results = {}
            if use_filter and (google_key or openrouter_key):
                if google_key:
                    reply, err = ask_gemini(google_key, candidate["question"])
                    if err:
                        results["gemini"] = f"ERROR: {err}"
                    else:
                        failed = model_failed(reply, candidate["answer"])
                        results["gemini"] = "FAILED" if failed else "SOLVED"
                        if failed:
                            failures += 1
                if openrouter_key:
                    reply, err = ask_deepseek(openrouter_key, candidate["question"])
                    if err:
                        results["deepseek"] = f"ERROR: {err}"
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
                    filter_log.append(f"Attempt {attempt+1}: only {failures} failures → discarded")
            else:
                kept = candidate
                st.session_state.filter_results = {}
                break

        if kept:
            st.session_state.last_problem = kept
            st.session_state.generated_count += 1
            st.success(f"Novel problem kept after {attempt+1} attempt(s)")
            # Gentle prompt for feedback after successful generation
            if not st.session_state.feedback_submitted and st.session_state.generated_count >= 2:
                st.info("Enjoying the app? Please leave a quick star rating in the sidebar →")
        else:
            st.warning("No problem passed the filter in this run. Try again or lower the minimum failures.")
            if filter_log:
                with st.expander("Filter log"):
                    for line in filter_log:
                        st.text(line)

# Display last problem
if st.session_state.last_problem:
    p = st.session_state.last_problem
    st.markdown("### Ready for Planck")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Category:** `{p['category']}`")
        st.markdown("**Question**")
        st.markdown(p["question"])
        st.markdown("**Answer**")
        st.code(p["answer"])
        st.info("Leave Golden Trajectory **empty** on the first Planck trial.")
        with st.expander("Golden Trajectory (fill only after ==PASSED==)"):
            st.code(p["golden"])

    with col2:
        st.markdown("**Techniques**")
        for t in p.get("techniques", []):
            st.write(f"• {t}")
        st.write(f"Seed: `{p.get('seed')}`")
        if st.session_state.filter_results:
            st.markdown("**Filter results**")
            for model, status in st.session_state.filter_results.items():
                st.write(f"{model}: **{status}**")

    st.markdown("---")
    export_text = (
        f"CATEGORY: {p['category']}\n\n"
        f"QUESTION:\n{p['question']}\n\n"
        f"ANSWER:\n{p['answer']}\n\n"
        f"GOLDEN TRAJECTORY:\n(leave empty on first trial)\n\n"
        f"--- later ---\n{p['golden']}\n"
    )
    st.download_button(
        label="Download Planck-ready .txt",
        data=export_text,
        file_name=f"planck_stumper_{p.get('seed', 'export')}.txt",
        mime="text/plain",
        use_container_width=True
    )

st.markdown("---")
st.caption(
    "Procedural templates: groups of order pq, modular orders, class numbers, Schur evaluations, "
    "supergravity d.o.f., recoil, inverse integrals, cyclotomic periods. "
    "In-app rating system included. All problems forced novel via hash memory."
)
