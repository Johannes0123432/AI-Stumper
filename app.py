"""
Planck CURVD Stumper Generator – PhD / Research Level
====================================================
- Harder multi-step (≈6 steps) problems
- Domains: Math, Physics, Biology
- Anti-memorization + wrong-answer attractors
- Strict filtering against strongest models
- Hard Adaptive mode
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

# Session state
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
# HARD PhD-level generators (≈6-step trajectories)
# ============================================================

def gen_math_p3_exponent():
    p = random.choice([3, 5, 7, 11])
    seed = random.randrange(10**9)
    question = (
        f"How many groups of order ${p}^3$ have exponent exactly ${p}$? "
        f"Give the exact integer."
    )
    answer = "2"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Up to isomorphism there are exactly five groups of order p³.\n"
        f"STEP 2: They are ℤ_{{p³}}, ℤ_{{p²}}×ℤ_p, ℤ_p³, the Heisenberg group Heis(p), and one additional semidirect product.\n"
        f"STEP 3: Exponent of ℤ_{{p³}} is p³; exponent of ℤ_{{p²}}×ℤ_p is p².\n"
        f"STEP 4: Exponent of the remaining non-abelian group of maximal class is p².\n"
        f"STEP 5: Only the elementary abelian group ℤ_p³ and the Heisenberg group mod p have every non-identity element of order p.\n"
        f"STEP 6: Therefore exactly two groups have exponent p.\n"
        f"Wrong-answer attractor: the unrestricted total 5.\n"
        f"FINAL ANSWER: 2"
    )
    return {"category": "Math", "question": question, "answer": answer, "golden": golden,
            "techniques": ["wrong-answer attractor (5)", "hidden exponent restriction"], "seed": seed}


def gen_math_discriminant():
    seed = random.randrange(10**9)
    question = (
        f"Let θ = 2 cos(2π/7). It satisfies the irreducible cubic X³ + X² − 2X − 1 = 0. "
        f"Compute the discriminant of this cubic. Give the exact integer."
    )
    answer = "49"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: For the monic cubic x³ + a x² + b x + c the discriminant is 18 a b c − 4 a³ c + a² b² − 4 b³ − 27 c².\n"
        f"STEP 2: Here a = 1, b = −2, c = −1.\n"
        f"STEP 3: Compute 18(1)(−2)(−1) = 36.\n"
        f"STEP 4: −4(1)³(−1) = 4; a² b² = 4; −4 b³ = −4(−8) = 32; −27 c² = −27.\n"
        f"STEP 5: Sum: 36 + 4 + 4 + 32 − 27 = 49.\n"
        f"STEP 6: The discriminant is therefore 49.\n"
        f"Wrong-answer attractor: 7 or −49.\n"
        f"FINAL ANSWER: 49"
    )
    return {"category": "Math", "question": question, "answer": answer, "golden": golden,
            "techniques": ["forces explicit calculation", "attractor 7/−49"], "seed": seed}


def gen_math_hilbert_tower():
    seed = random.randrange(10**9)
    question = (
        f"Let K = ℚ(√−47). Let H be the Hilbert class field of K. "
        f"What is the degree [H : ℚ]? Give the exact integer."
    )
    answer = "10"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: The class number of ℚ(√−47) is h_K = 5.\n"
        f"STEP 2: By definition [H : K] = h_K = 5.\n"
        f"STEP 3: The extension K/ℚ is quadratic, so [K : ℚ] = 2.\n"
        f"STEP 4: Tower formula: [H : ℚ] = [H : K] · [K : ℚ].\n"
        f"STEP 5: Therefore [H : ℚ] = 5 · 2 = 10.\n"
        f"STEP 6: The absolute degree is 10 (not the relative class number).\n"
        f"Wrong-answer attractor: report 5.\n"
        f"FINAL ANSWER: 10"
    )
    return {"category": "Math", "question": question, "answer": answer, "golden": golden,
            "techniques": ["attractor class number 5", "hidden tower"], "seed": seed}


def gen_math_order():
    primes = [11, 13, 17, 19, 23]
    p = random.choice(primes)
    q = random.choice([r for r in primes if r != p])
    n = p * q
    def ordmod(b, m):
        if math.gcd(b, m) != 1: return None
        o, v = 1, b % m
        while v != 1:
            v = (v * b) % m
            o += 1
            if o > m: return None
        return o
    op, oq = ordmod(2, p), ordmod(2, q)
    if not op or not oq: return gen_math_order()
    ans = math.lcm(op, oq)
    seed = random.randrange(10**9)
    question = (
        f"Let n = {n} = {p}×{q}. Compute the multiplicative order of 2 modulo n. "
        f"Give the exact integer."
    )
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Compute ord_{p}(2) by successive powers → {op}.\n"
        f"STEP 2: Compute ord_{q}(2) → {oq}.\n"
        f"STEP 3: By the Chinese Remainder Theorem the order modulo n is lcm of the two orders.\n"
        f"STEP 4: lcm({op},{oq}) = {ans}.\n"
        f"STEP 5: Verify that 2^{ans} ≡ 1 (mod n) and no smaller positive exponent works.\n"
        f"STEP 6: The order is therefore {ans}.\n"
        f"Wrong-answer attractor: φ(n) = {(p-1)*(q-1)}.\n"
        f"FINAL ANSWER: {ans}"
    )
    return {"category": "Math", "question": question, "answer": str(ans), "golden": golden,
            "techniques": ["φ(n) attractor", "CRT"], "seed": seed}


def gen_physics_recoil():
    ratio = random.choice([11, 16, 24, 32])
    seed = random.randrange(10**9)
    question = (
        f"A thin spherical shell of mass M is at rest in empty space. "
        f"A point mass m = M/{ratio} is released from rest at distance 2R from the centre of the shell. "
        f"When the point mass reaches distance R from the centre, what is the displacement of the "
        f"shell’s centre relative to the original inertial frame, expressed as a simplified fraction of R?"
    )
    ans = f"1/{ratio+1}"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: No external forces → centre of mass of the two-body system remains fixed.\n"
        f"STEP 2: Let the shell centre move a distance d toward the original position of m.\n"
        f"STEP 3: In the same interval the point mass moves a distance (R − d) relative to the original frame.\n"
        f"STEP 4: CM condition: M d = m (R − d).\n"
        f"STEP 5: Solve: d (M + m) = m R ⇒ d = m/(M+m) R = 1/{ratio+1} R.\n"
        f"STEP 6: The required displacement is therefore 1/{ratio+1} R.\n"
        f"Wrong-answer attractor: 0 (treating the shell as fixed).\n"
        f"FINAL ANSWER: {ans}"
    )
    return {"category": "Physics", "question": question, "answer": ans, "golden": golden,
            "techniques": ["fixed-shell attractor", "hidden CM conservation"], "seed": seed}


def gen_physics_dof():
    data = [(11, "graviton", 44), (11, "3-form", 84), (10, "graviton", 35),
            (9, "graviton", 27), (7, "graviton", 14), (5, "graviton", 5)]
    D, field, dof = random.choice(data)
    seed = random.randrange(10**9)
    question = (
        f"In D = {D} spacetime dimensions, how many on-shell degrees of freedom does a massless "
        f"{field} possess? Give the exact integer."
    )
    answer = str(dof)
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: A massless graviton in D dimensions transforms under the little group SO(D−2).\n"
        f"STEP 2: The symmetric traceless rank-2 representation of SO(D−2) has dimension D(D−3)/2.\n"
        f"STEP 3: For a massless p-form the on-shell count is binom(D−2, p).\n"
        f"STEP 4: Substitute the given D and field type.\n"
        f"STEP 5: Evaluate the formula → {dof}.\n"
        f"STEP 6: This is the on-shell count (not the off-shell gauge-field count).\n"
        f"Wrong-answer attractor: off-shell number of components.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {"category": "Physics", "question": question, "answer": answer, "golden": golden,
            "techniques": ["off-shell attractor", "little-group analysis"], "seed": seed}


def gen_physics_instanton():
    seed = random.randrange(10**9)
    question = (
        f"In pure SU(2) Yang–Mills theory the BPST instanton has topological charge 1. "
        f"What is the value of the instanton action (in units where 8π²/g² = 1)? "
        f"Give the exact integer."
    )
    answer = "1"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: The Yang–Mills action is (1/(2g²)) ∫ Tr(F ∧ *F).\n"
        f"STEP 2: For an instanton one has *F = F (self-dual).\n"
        f"STEP 3: The topological charge k = (1/(8π²)) ∫ Tr(F ∧ F).\n"
        f"STEP 4: Self-duality implies the action equals 8π²|k|/g².\n"
        f"STEP 5: For the BPST instanton k = 1, so the action is 8π²/g².\n"
        f"STEP 6: In the units where 8π²/g² = 1 the numerical value is 1.\n"
        f"Wrong-answer attractor: 8π² or 0.\n"
        f"FINAL ANSWER: 1"
    )
    return {"category": "Physics", "question": question, "answer": answer, "golden": golden,
            "techniques": ["unit convention trap", "self-duality"], "seed": seed}


def gen_bio_moran():
    """Weak-selection fixation probability expansion – classic attractor is neutral 1/N."""
    N = random.choice([20, 30, 50, 100])
    seed = random.randrange(10**9)
    # Under weak selection the fixation probability of a rare advantageous mutant is
    # ≈ (1/N) + (s/2)(1 − 1/N) + O(s²) for birth-death Moran; the leading correction coefficient is often asked.
    # We ask for the neutral fixation probability itself but force a multi-step derivation.
    question = (
        f"In the Moran process on a well-mixed population of size N = {N}, "
        f"what is the fixation probability of a single neutral mutant? "
        f"Give the exact value as a simplified fraction."
    )
    answer = f"1/{N}"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: In the neutral Moran process every individual is equally likely to be the ancestor of the whole population.\n"
        f"STEP 2: There are N individuals, each with identical reproductive rate.\n"
        f"STEP 3: By symmetry the fixation probability of any particular individual is the same.\n"
        f"STEP 4: These N probabilities sum to 1.\n"
        f"STEP 5: Therefore each equals 1/N.\n"
        f"STEP 6: The fixation probability of a single neutral mutant is 1/{N}.\n"
        f"Wrong-answer attractor: 1/2 or 0.\n"
        f"FINAL ANSWER: {answer}"
    )
    return {"category": "Biology", "question": question, "answer": answer, "golden": golden,
            "techniques": ["symmetry argument", "attractor 1/2"], "seed": seed}


def gen_bio_sir_hopf():
    seed = random.randrange(10**9)
    question = (
        f"In the delayed SIR model with constant recruitment, a Hopf bifurcation can occur when the "
        f"delay τ exceeds a critical value. For the classic parameter set in which the critical delay "
        f"satisfies ωτ = π/2 at onset, what is the leading-order period of the emerging oscillations "
        f"expressed as a multiple of the critical delay τ_c? Give the exact integer multiple."
    )
    answer = "4"
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: At a Hopf bifurcation a pair of complex conjugate eigenvalues crosses the imaginary axis at ±iω.\n"
        f"STEP 2: The period of the emerging limit cycle is T = 2π/ω.\n"
        f"STEP 3: The problem states that at onset one has ω τ_c = π/2.\n"
        f"STEP 4: Therefore ω = (π/2)/τ_c.\n"
        f"STEP 5: T = 2π / ω = 2π · (2 τ_c / π) = 4 τ_c.\n"
        f"STEP 6: The leading-order period is 4 times the critical delay.\n"
        f"Wrong-answer attractor: 2.\n"
        f"FINAL ANSWER: 4"
    )
    return {"category": "Biology", "question": question, "answer": answer, "golden": golden,
            "techniques": ["Hopf period calculation", "attractor 2"], "seed": seed}


def gen_bio_replicator():
    seed = random.randrange(10**9)
    question = (
        f"In the two-strategy replicator dynamics on the simplex, the interior equilibrium of a "
        f"generic 2×2 game is asymptotically stable if and only if the game is of which type? "
        f"Answer with the standard name (one word or short phrase)."
    )
    answer = "Hawk-Dove"
    # More precisely "anti-coordination" or "Hawk-Dove / snowdrift", but we take the classic name.
    golden = (
        f"SEED = {seed}\n"
        f"STEP 1: Write the payoff matrix [[a,b],[c,d]].\n"
        f"STEP 2: The interior equilibrium exists when (a−c) and (d−b) have opposite signs.\n"
        f"STEP 3: Linearisation of the replicator equation yields eigenvalue proportional to (a−c)(d−b).\n"
        f"STEP 4: Stability requires the eigenvalue to be negative, i.e. (a−c)(d−b) < 0.\n"
        f"STEP 5: This is precisely the condition for a Hawk-Dove (anti-coordination) game.\n"
        f"STEP 6: In Prisoner’s Dilemma or pure coordination games the interior point is unstable.\n"
        f"Wrong-answer attractor: Prisoner’s Dilemma.\n"
        f"FINAL ANSWER: Hawk-Dove"
    )
    return {"category": "Biology", "question": question, "answer": answer, "golden": golden,
            "techniques": ["stability sign condition", "PD attractor"], "seed": seed}


def gen_procedural():
    gens = [
        gen_math_p3_exponent,
        gen_math_discriminant,
        gen_math_hilbert_tower,
        gen_math_order,
        gen_physics_recoil,
        gen_physics_dof,
        gen_physics_instanton,
        gen_bio_moran,
        gen_bio_sir_hopf,
        gen_bio_replicator,
    ]
    for _ in range(40):
        prob = random.choice(gens)()
        if is_novel(prob["question"], prob["answer"]):
            return prob
    return gen_math_p3_exponent()


# ============================================================
# Adaptive LLM generation
# ============================================================

ADAPTIVE_PROMPT = """You are an expert designer of PhD-level problems that stump frontier LLMs.

Create ONE original, self-contained problem in Math, Physics or Biology that requires approximately six reasoning steps.

CURVD requirements:
- Exact unique short answer
- Fully self-contained
- Solvable by a careful human without a computer
- Answer solely from the given information

Mandatory techniques (use ≥3):
- Hidden critical dependency
- Strong wrong-answer attractor
- Inverse or restricted formulation
- Fresh parameters

Output format ONLY:

CATEGORY: Math   or   Physics   or   Biology
QUESTION:
<problem statement>
ANSWER:
<exact short answer>
GOLDEN:
SEED = <9-digit number>
STEP 1: ...
STEP 2: ...
STEP 3: ...
STEP 4: ...
STEP 5: ...
STEP 6: ...
FINAL ANSWER: <same>
"""

def generate_adaptive(api_key: str):
    if not HAS_GENAI:
        return None, "no google-genai"
    for m in ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash"]:
        try:
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(model=m)
            resp = chat.send_message(ADAPTIVE_PROMPT)
            return parse_llm_output(resp.text or ""), None
        except Exception as e:
            last = str(e)
    return None, last


def parse_llm_output(text: str):
    cat = "Math"
    m = re.search(r"CATEGORY:\s*(Math|Physics|Biology)", text, re.I)
    if m:
        cat = m.group(1).capitalize()
    q = re.search(r"QUESTION:\s*(.*?)(?=ANSWER:|$)", text, re.S | re.I)
    a = re.search(r"ANSWER:\s*(.*?)(?=GOLDEN:|$)", text, re.S | re.I)
    g = re.search(r"GOLDEN:\s*(.*)", text, re.S | re.I)
    question = q.group(1).strip() if q else text
    answer = re.sub(r"^\$+|\$+$", "", (a.group(1).strip() if a else "UNKNOWN"))
    golden = g.group(1).strip() if g else "Golden not provided."
    return {"category": cat, "question": question, "answer": answer, "golden": golden,
            "techniques": ["adaptive invention", "hidden dependency", "attractor"], "seed": random.randrange(10**9)}


# ============================================================
# Model callers
# ============================================================

def ask_gemini(api_key: str, question: str):
    if not HAS_GENAI or not api_key: return None, "no key"
    for m in ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash"]:
        try:
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(model=m)
            resp = chat.send_message("Solve rigorously. Final answer after FINAL ANSWER:\n\n" + question)
            return resp.text or "", None
        except Exception as e:
            last = str(e)
    return None, last


def ask_deepseek(api_key: str, question: str):
    if not HAS_OPENAI or not api_key: return None, "no key"
    for model in ["deepseek/deepseek-v4-pro-0813", "deepseek/deepseek-v4-pro",
                  "deepseek/deepseek-v4-flash", "deepseek/deepseek-r1", "deepseek/deepseek-chat"]:
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            r = client.chat.completions.create(model=model, messages=[{"role":"user","content":question}],
                                               temperature=0, max_tokens=1000)
            return r.choices[0].message.content, None
        except Exception as e:
            last = str(e)
    return None, last


def model_failed(reply: str, gold: str) -> bool:
    if not reply: return True
    clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", reply.lower())
    gold_clean = re.sub(r"[^a-zA-Z0-9\\/\-\.]", "", str(gold).lower())
    if gold_clean in clean: return False
    try:
        g = float(gold)
        for n in re.findall(r"-?\d+\.?\d*", reply):
            if abs(float(n) - g) < 1e-6: return False
    except: pass
    return True


# ============================================================
# UI
# ============================================================

st.set_page_config(page_title="Planck PhD Stumper Generator", layout="wide")
st.title("Planck PhD / Research-Level Stumper Generator")
st.caption("Math • Physics • Biology • ≈6-step trajectories • Anti-memorization • Adaptive mode")

with st.sidebar:
    st.header("Mode")
    gen_mode = st.radio("Generation mode", [
        "Procedural (PhD templates)",
        "Hard Adaptive (LLM invents new traps)",
    ], index=0)
    st.markdown("---")
    use_filter = st.checkbox("Only keep problems that fail models", value=True)
    min_failures = st.slider("Min models that must fail", 1, 2, 1)
    st.markdown("---")
    google_key = st.text_input("Google AI Studio key", type="password")
    openrouter_key = st.text_input("OpenRouter key", type="password")
    st.markdown("---")
    st.write(f"Generated: **{st.session_state.generated_count}**")
    if st.button("Clear hash memory"):
        st.session_state.seen_hashes = set()
        st.success("Cleared")

    st.markdown("---")
    st.subheader("Rate this app")
    with st.form("fb", clear_on_submit=True):
        rating = st.feedback("stars")
        comment = st.text_area("Comment", max_chars=300, height=60)
        email = st.text_input("Email (optional)")
        if st.form_submit_button("Submit"):
            if rating is not None:
                st.session_state.feedbacks.append({
                    "timestamp": datetime.utcnow().isoformat()+"Z",
                    "rating": int(rating)+1, "comment": comment, "email": email
                })
                st.success("Thanks!")
    if st.session_state.feedbacks:
        buf = io.StringIO()
        csv.DictWriter(buf, fieldnames=["timestamp","rating","comment","email"]).writeheader()
        csv.DictWriter(buf, fieldnames=["timestamp","rating","comment","email"]).writerows(st.session_state.feedbacks)
        st.download_button("Download feedbacks", buf.getvalue(), "feedbacks.csv", "text/csv")

if st.button("Generate new stumper", type="primary", use_container_width=True):
    with st.spinner("Generating hard 6-step problem + filtering…"):
        kept = None
        log = []
        for attempt in range(12):
            if gen_mode.startswith("Procedural"):
                cand = gen_procedural()
            else:
                if not google_key:
                    st.error("Adaptive mode needs Google key")
                    break
                cand, err = generate_adaptive(google_key)
                if err or not cand:
                    log.append(str(err))
                    continue
                if not is_novel(cand["question"], cand["answer"]):
                    continue

            failures = 0
            results = {}
            if use_filter:
                if google_key:
                    reply, err = ask_gemini(google_key, cand["question"])
                    results["gemini"] = "ERROR" if err else ("FAILED" if model_failed(reply, cand["answer"]) else "SOLVED")
                    if results["gemini"] == "FAILED": failures += 1
                if openrouter_key:
                    reply, err = ask_deepseek(openrouter_key, cand["question"])
                    results["deepseek"] = "ERROR" if err else ("FAILED" if model_failed(reply, cand["answer"]) else "SOLVED")
                    if results["deepseek"] == "FAILED": failures += 1
                if failures >= min_failures:
                    kept = cand
                    st.session_state.filter_results = results
                    break
                else:
                    log.append(f"Attempt {attempt+1}: {failures} failures")
            else:
                kept = cand
                break

        if kept:
            st.session_state.last_problem = kept
            st.session_state.generated_count += 1
            st.success(f"Kept after {attempt+1} attempts")
        else:
            st.warning("No survivor this run. Try again.")
            if log:
                with st.expander("Log"):
                    for l in log: st.text(l)

if st.session_state.last_problem:
    p = st.session_state.last_problem
    st.markdown("### Ready for Planck")
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown(f"**Category:** `{p['category']}`")
        st.markdown("**Question**")
        st.markdown(p["question"])
        st.markdown("**Answer**")
        st.code(p["answer"])
        st.info("Leave Golden Trajectory empty on the first trial.")
        with st.expander("Golden Trajectory (6 steps – fill only after PASSED)"):
            st.code(p["golden"])
    with c2:
        st.markdown("**Techniques**")
        for t in p.get("techniques", []): st.write("• "+t)
        st.write(f"Seed: `{p.get('seed')}`")
        if st.session_state.filter_results:
            st.markdown("**Filter**")
            for m,s in st.session_state.filter_results.items():
                st.write(f"{m}: **{s}**")

    export = (f"CATEGORY: {p['category']}\n\nQUESTION:\n{p['question']}\n\n"
              f"ANSWER:\n{p['answer']}\n\nGOLDEN TRAJECTORY:\n(leave empty on first trial)\n\n"
              f"--- later ---\n{p['golden']}\n")
    st.download_button("Download Planck-ready .txt", export,
                       f"planck_{p.get('seed')}.txt", "text/plain", use_container_width=True)

st.markdown("---")
st.caption("PhD-level generators in Math, Physics and Biology with explicit 6-step golden trajectories. "
           "Anti-memorization design + adaptive invention mode + strongest-model filtering.")
