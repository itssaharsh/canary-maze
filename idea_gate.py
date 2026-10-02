#!/usr/bin/env python3
"""Checks an idea package (product or hackathon mode), renders it and keeps the session ledger.
The anti-wrapper filter (Stage 4b/6W) is enforced here: an idea whose product disappears with the
model, or that reduces to "give X to a model, get Y back", fails and must be regenerated.
usage: python3 idea_gate.py ideas.json [--ledger L.jsonl] [--prior prior.json] [--reply reply.md]
         [--render idea-package.md [--append log.md,intel.md]] [--append-ledger L.jsonl] [--mode pressure]
Exits 1 on any FAIL. Disclose the WARNs (grouped) in the reply. Entries of the current run in the ledger
are ignored when checking and replaced when appending, so re-running after a late fix is safe."""
import json, re, sys

CARD = {"product": ["idea", "problem", "user", "current_workaround", "product", "core_workflow", "ai_role",
                    "non_ai_product", "data_loop", "why_now", "business_model", "distribution", "retention",
                    "defensibility", "mvp", "expansion", "risks"],
        "hackathon": ["concept", "problem", "user", "why_it_matters", "core_workflow", "ai_role", "non_ai_product",
                      "data_loop", "hard_part", "technical_implementation", "mvp_scope", "differentiation", "risks",
                      "buildable_in_event"]}
SCAN = {"product": ["direct", "indirect", "workaround", "oss", "recent", "graveyard"],
        "hackathon": ["startup", "oss", "hackathon", "platform", "research", "workaround"]}
CHECKS = ["acuteness", "deep_well", "switching", "payer", "economics", "wrapper_test", "hand_squeeze", "miracles",
          "graveyard", "size", "first_adopters"]
DEMO = ["first_10s", "first_minute", "wow_moment", "technical_depth", "story", "unhappy_path", "judge_touches"]
KILL = {"shared": ["no_clear_user", "nonexistent_problem", "technology_first", "clone", "recycled_generic",
                   "default_match", "ledger_repeat", "chatgpt_wrapper", "generic_rag", "generic_agent",
                   "generic_dashboard", "llm_wrapper", "no_product_without_model", "prompt_moat", "textbox_ui",
                   "chatgpt_obvious"],
        "product": ["tarpit", "vitamin", "no_payer", "hand_squeeze", "cascading_miracles", "absorbed"],
        "hackathon": ["sponsor_first", "default_entry", "wrong_brief", "impossible_demo", "unrealistic_data"]}
FIX = {"product": ["channel_hope", "fake_moat", "big_behavior_change", "forced_tech", "one_off", "weekend_clone"],
       "hackathon": ["forced_blockchain", "forced_ar_vr", "forced_iot", "forced_multi_agent", "superficial_sponsor",
                     "platformmaxxing", "weekend_clone"]}
BACKGROUND_KEYS = ["resume_first", "prior_project_variation"]  # hackathon, unless general-strict
TYPES, LEVEL = {"fact", "evidence", "assumption", "hypothesis"}, {"weak": 1, "moderate": 2, "strong": 3}
FAMILIES = {"prevent", "detect", "verify", "repair", "replace", "automate", "create", "connect", "inform", "transact"}
CONTEXTS, METHODS = {"general", "general-strict", "personal"}, {"blind_subagent", "sequenced"}
DEPTHS, SPECIAL = {"core", "meaningful", "superficial"}, {"user-relayed", "assumed"}
BASIS = {"official", "pattern", "inference"}
NOTE_KEYS = {"idea", "why_you", "what_you_lack", "constraint_fit", "familiarity", "new_to_them", "build_estimate", "gated_access",
             "gaps", "location", "smaller_cut"}
LABELS = {"product": ["idea", "problem", "user", "current workaround", "evidence", "product", "core workflow", "ai role",
                      "non[- ]ai product", "data loop", "why now", "wedge", "business model",
                      "distribution", "retention", "moat", "mvp", "expansion", "validation", "risks", "competitors"],
          "hackathon": ["concept", "problem", "user", "why it matters", "core workflow", "ai role", "non[- ]ai product",
                        "data loop", "hard part", "technical implementation", "sponsor fit",
                        "(judging )?criteria alignment", "demo flow", "wow( moment)?", "mvp( scope)?", "differentiation", "risks",
                        "(what can be built|buildable)"]}
SECTIONS = {"product": ["tradeoffs", "killed", "sources"], "hackathon": ["tradeoffs", "sponsor verdicts", "killed", "sources"]}
BUZZ = re.compile(r"\b(revolutioni[sz]\w*|transformative|transform(s|ing)? (how|the way|industr\w*|businesses)|next[- ]gen"
                  r"\w*|ai[- ](powered|driven|first)|seamless\w*|cutting[- ]edge|intelligent platform|frictionless|game[- ]"
                  r"chang\w*|democrati[sz]\w*|ecosystems?|leverag\w*|unlock\w*|empower\w*|supercharg\w*|streamlin\w*"
                  r"|disrupt\w*|state[- ]of[- ]the[- ]art|synerg\w*|paradigm)\b", re.I)
RANK = re.compile(r"\b(score|rating|grade)\s*[:=]\s*\d|\boverall (score|rating)\b|\bscored\s+\d|\brank(ed|ing)?\s*(#|no\.?\s*)?"
                  r"\d|(?<!\bno )(?<!\bnot the )(?<!\bnot a )(?<!n't a )(?<!n't the )\b(best|top|strongest|number[- ]one) (idea|pick|bet|candidate)s?\b|#1 (idea|pick)|\b(overall|clear"
                  r"|obvious) winner\b|\bwinning idea\b|\bfront-?runner\b|\b(i|we)('d| would)? (recommend|suggest) (going wi"
                  r"th|picking|choosing)\b|★{2,}", re.I)
PREDICT = re.compile(
    r"\b((this|the|our|your) (idea|project|entry|build|demo)|this|it|we|you)\s+(can|could|would|will|should|might|may)\s+"
    r"(also\s+)?(win|place|take)\b[^.\n]{0,30}\b(prizes?|tracks?|awards?|hackathon|grand|first|1st|top \d+|judges?|podium"
    r"|bount(y|ies)|competition)\b|\b(likely|sure|guaranteed|poised|positioned|set) to win\b|\b(best|good|strong|high) "
    r"(chance|odds) of winning\b|\bjudges will (pick|reward|love|choose|prefer)\b|\b(real|good|strong|decent|fair) shot at\b"
    r"|\b(strong |serious |top )?contenders?\b", re.I)
def unquote(t): return re.sub(r'"[^"\n]{3,300}"|“[^”\n]{3,300}”', '""', str(t))
TRAITS = re.compile(r"\b(religio\w*|devout|faith\w*|church|mosque|temple|politic\w*|conservative|liberal|ethnic\w*|race"
                    r"|gender|married|personality)\b", re.I)
TAILOR = re.compile(r"\b(avoid|tailor\w*|pitch (it )?to|appeal to|play to|so (we|you) should|steer)\b", re.I)


JUDGE = re.compile(r"\bjudges?\b[^.\n]{0,60}\b(likes?|loves?|hates?|prefers?|dislikes?|enjoys?|favou?rs?|is a fan of"
                   r"|are fans of)\b", re.I)
SOURCED = re.compile(r"https?://|\]\(|\b(says|said|wrote|writes|states|stated|according to|guide|rules|rubric)\b", re.I)
BUILDER = re.compile(
    r"\byou('ve| have) (already )?(built|shipped|won|worked on)\b|\byour (experience|skills?|strengths?|track record|turf"
    r"|wheelhouse|(past|previous|prior) (projects?|wins?|work|entries))\b|\byour background (in|as|with)\b"
    r"|\bplays to your\b|\bsince you (already )?(know|built|won|worked on|have experience)\b"
    r"|\b(builder|candidate|founder)'?s? (experience|background|skills?|strengths?|past projects?|previous (projects?|wins?))\b",
    re.I)
SHAPED = re.compile(r"\b(agents?|agentic|chat\w*|rag|assistants?|copilots?|llm)\b", re.I)
HOPE = re.compile(r"\b(ads?|advertis\w*|press|viral\w*|seo|social media|influencers?)\b", re.I)
DIRECT = re.compile(r"\b(communit\w*|forums?|subreddits?|slack|discord|groups?|lists?|network\w*|associations?|marketplaces?"
                    r"|meetups?|conferences?|events?|trade shows?|outreach|cold (email|call)\w*|door|partners?\w*|"
                    r"integrations?|app stores?|director(y|ies)|newsletters?|referrals?|sales|dms?|emails?)\b", re.I)
RECYCLED = {
    "AI note taker": r"\b(note[- ]?tak\w*|meeting (notes|summar\w*))\b",
    "AI recruiter": r"\b(recruit\w*|r[eé]sum[eé] (screen|build|pars|review|match)\w*|cv screen\w*|job match\w*|candidate screen\w*)\b",
    "AI tutor": r"\b(tutor\w*|study (buddy|assistant|companion)|flashcards?)\b",
    "AI coding assistant": r"\b(coding assistant|code (assistant|copilot)|pair[- ]programm\w*)\b",
    "AI travel planner": r"\b(travel (planner|itinerar\w*)|trip planner)\b",
    "document chatbot": r"\b(chat with (your |the )?(docs?|documents?|pdfs?|files?|data)|pdf (chat|bot)|rag (chat)?bot)\b",
    "generic multi-agent system": r"\bmulti[- ]agent (system|framework|platform)\b",
    "generic dashboard": r"^\W*(a |an )?(\w+ )?dashboard\b",
    "X-for-Y clone": r"\b(uber|airbnb|tinder|linkedin|netflix|spotify|duolingo) for\b",
    "wellness chatbot": r"\b(mental[- ]health|wellness|therapy) (chat)?bot\b",
    "tracker app": r"\b(habit|fitness|calorie|meal|mood|expense|carbon[- ]footprint) (tracker|tracking|planner|splitt\w*)\b",
    "friends activity app": r"\b(things to do with friends|plans? with friends)\b",
    "AI companion": r"\bai (companion|friend|girlfriend|boyfriend)\b",
    "content generator": r"\b(copywrit\w*|content generat\w*|post generat\w*|blog generat\w*)\b",
    "NFT or swap UI": r"\b(nfts?|token[- ]gated|cross[- ]chain swaps?)\b"}
STOP = set("the and for with from into that this your their our are was were has have via can will not but all any each "
           "per than then them they you its one get gets when what who how use uses who whom while".split())

# --- anti-wrapper filter (Stage 4b and 6W) ---------------------------------------------------------
# Shapes that reduce to "the user gives X to a model and gets Y back". A match isn't a kill on its own,
# but it must be declared in wrapper_test.archetype with what this does beyond the shape.
WRAPPER_SHAPES = {
    "generic AI assistant": r"\b(ai|llm|gpt|smart)[- ]?(assistant|helper|companion)\b|\bgeneral[- ]purpose (assistant|agent)\b",
    "AI chatbot": r"\b(chat ?bots?|conversational (ai|assistant|interface)|ask[- ]me[- ]anything)\b",
    "chat with your data": r"\b(chat|talk|converse) (with|to|over) (your |the |my )?(data|docs?|documents?|pdfs?|files?|"
                           r"database|codebase|notes|wiki|spreadsheets?)\b|\bask questions? (about|of|over) (your|the|my) "
                           r"(docs?|documents?|data|pdfs?|files?|notes)\b|\bnatural[- ]language (queries|interface) (to|over) "
                           r"(your|the) (data|database|docs?)\b",
    "document summarizer": r"\b(pdf|document|doc|paper|article|report|contract|book|email|thread)s?[- ]?(summari[sz]\w*|"
                           r"digest\w*|tl;?dr)\b|\bsummari[sz]es? (pdfs?|documents?|papers?|articles?|reports?|contracts?|"
                           r"emails?|threads?|videos?|transcripts?)\b",
    "meeting summarizer": r"\bmeeting (summar\w*|notes|recaps?|minutes|assistant)\b|\bnote[- ]?tak\w*\b|\btranscri\w+ "
                          r"(and )?summar\w*\b",
    "content generator": r"\b(content|copy|blog|post|caption|newsletter|ad|ads|seo|script|thumbnail)[- ]?(generat\w*|"
                         r"writ(er|ing)|creat(or|ion)|factor(y|ies))\b|\bwrites? (your )?(blogs?|posts?|captions?|ads?)\b",
    "AI email or message writer": r"\b(e-?mails?|messages?|dms?|replies|reply|outreach|cold[- ]e?mails?|linkedin)[- ]?"
                                  r"(writ(er|ing)|generat\w*|draft(er|ing)|compos\w*|personali[sz]\w*)\b|\bwrites? your "
                                  r"(e-?mails?|replies|messages?)\b",
    "generic research agent": r"\b(research|deep[- ]research|browsing|web|search)[- ]?agents?\b|\bresearch assistant\b|"
                              r"\bagent that (researches|browses|searches the web)\b",
    "generic RAG app": r"\brags?\b|\bretrieval[- ]augmented\b|\bvector (search|db|database|store)[- ]?(app|product|tool|"
                       r"startup|saas)\b|\bembeds? (your|the) (docs?|documents?|knowledge base)\b",
    "generic coding assistant": r"\b(coding|code|dev(eloper)?|programming)[- ]?(assistant|copilot|agents?|buddy)\b|"
                                r"\bpair[- ]programm\w*\b|\bwrites? (your )?code\b",
    "AI dashboard": r"\bai[- ](powered |driven |generated )?(dashboard|analytics|reporting|insights?)\b|\b(dashboard|"
                    r"analytics|reports?) (with|powered by|generated by|using) (ai|llms?|gpt)\b|\bai insights? (dashboard|"
                    r"panel|feed)\b",
    "model API wrapper": r"\b(wrapper|thin (layer|wrapper)|ui|front[- ]?end|interface) (on top of|around|over|for) "
                         r"(open ?ai|claude|anthropic|gemini|gpt|llms?|an? llm|the (model|api))\b|\bjust calls? the "
                         r"(open ?ai|claude|gemini|model) api\b|\bprompt (library|marketplace|manager|templates? (app|store))\b",
    "agentic clone of existing SaaS": r"\bagentic (version|layer|clone|crm|erp|helpdesk|saas|workflow tool)\b|\b(crm|erp|"
                                      r"helpdesk|ticketing|project management|bookkeeping|hr) (but|except) (with )?(ai|agents?|"
                                      r"an llm)\b|\b(ai|agent)[- ]native (crm|erp|helpdesk|ticketing)\b"}
# Where a model may genuinely create leverage. Generation-only leverage is the wrapper shape, so an idea
# whose only kinds are in DRAFTING has to name another kind too.
AI_LEVERAGE = {"perception", "extraction", "classification", "reasoning over messy inputs", "prediction",
               "personalization", "anomaly detection", "multimodal understanding", "ranking", "normalization",
               "matching", "planning under constraints", "judgement step in a workflow", "simulation",
               "drafting", "code generation", "speech", "translation"}
DRAFTING = {"drafting", "code generation", "translation"}
# Authenticity signals, grouped. Every surviving idea needs signals from all three groups: a real workflow,
# something that compounds with use, and substance that isn't the model.
AUTH_GROUPS = {"workflow": {"narrow_persona", "real_workflow", "existing_workaround", "integration",
                            "writes_to_system_of_record", "automation_changes_workflow", "domain_logic",
                            "takes_responsibility_for_outcome"},
               "compounding": {"usage_data", "feedback_loop", "accumulated_history", "better_with_repeat_use",
                               "network_effects", "workflow_effects"},
               "substance": {"deterministic_core", "eval_infrastructure", "hard_implementation",
                             "operational_complexity", "proprietary_data", "hardware_or_sensors",
                             "distribution_or_trust", "multi_provider"}}
AUTH_SIGNALS = {sig: grp for grp, sigs in AUTH_GROUPS.items() for sig in sigs}
AUTH_MIN = 5
MOAT_MECH = {"proprietary data", "workflow lock-in", "integrations", "accumulated history", "domain model",
             "eval infrastructure", "operational complexity", "distribution", "network effects", "switching costs",
             "regulatory or trust position", "system of record"}
ALT_TODAY = {"existing saas", "spreadsheets", "whatsapp", "email", "manual process", "scripts", "consultants",
             "employees", "agencies", "fragmented tools", "in-house tool", "paper", "phone calls", "doing nothing",
             "general assistant"}
WHYNOW_KIND = {"capability", "cost", "interface", "protocol", "regulation", "platform", "distribution", "behavior",
               "economics", "hardware", "data availability", "none"}
SMELL = ["q1_one_api_call", "q2_textbox_ui", "q3_prompt_differentiator", "q4_workflow_outside_model",
         "q5_touches_real_systems", "q6_improves_with_use", "q7_pays_after_novelty", "q8_chatgpt_would_suggest"]
SMELL_FATAL = {"q1_one_api_call": "the whole backend could be one model call",
               "q2_textbox_ui": "the interface is a textbox and a generated answer",
               "q3_prompt_differentiator": "the differentiator is the prompt",
               "q8_chatgpt_would_suggest": "100 people asking a chatbot for AI startup ideas would produce it"}
SMELL_REQUIRED = {"q4_workflow_outside_model": "there is no workflow outside the model",
                  "q5_touches_real_systems": "it touches no real system, data or ongoing process"}
SURVIVES = {"substantial", "thin", "nothing"}
BOILER = re.compile(r"^\W*(a |an |the )?(nice |clean |simple |polished |modern |thin |basic )*(ui|ux|interface|frontend|"
                    r"front[- ]end|web ?app|react app|website|wrapper|api wrapper|dashboard|database|db|crud app|"
                    r"prompts?|prompt templates?|prompt library|text ?box|chat ?window|chat ?ui|form|nothing|"
                    r"not much|very little|none|n/?a)\W*$", re.I)
PROMPT_MOAT = re.compile(r"^\W*(a |an |the |our |better |good |great )*(prompts?|prompt engineering|prompt templates?|"
                         r"system prompts?|fine[- ]?tun\w+|model choice|first[- ]mover|speed|better ux|nicer ui|"
                         r"execution|branding)\W*[.!]?\W*$", re.I)
VAGUE_WHYNOW = re.compile(r"\bai is (hot|booming|everywhere|taking off|growing|the future|maturing)\b|"
                          r"\b(llms?|models?|agents?) (are |have )?(getting (better|cheaper|smarter)|improved|matured)\b|"
                          r"\beveryone is (using|adopting) ai\b|\bthe ai (market|boom|wave|hype|era)\b|"
                          r"\bnow that (ai|llms?|gpt|agents?) exists?\b|\bai adoption is (growing|rising|increasing)\b|"
                          r"\bai is now (good|cheap|capable) enough\b(?![^.]*\d)", re.I)
fails, warns = [], []


def obj(x): return x if isinstance(x, dict) else {}
def lst(x): return x if isinstance(x, list) else []
def url(u): return isinstance(u, str) and u.startswith(("http://", "https://"))
def nourl(t): return re.sub(r"\]\([^)]*\)|https?://\S+", "]", str(t))
def label(k): return k.replace("_", " ").capitalize()


def site(u):
    parts = re.sub(r"^www\.", "", u.split("/")[2].lower().split(":")[0]).split(".")
    if len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in ("co", "com", "org", "gov", "ac", "net", "edu", "nic"):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def keys(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from keys(v)
    elif isinstance(x, list):
        for v in x:
            yield from keys(v)


def stem(w):
    for suf in ("ies", "ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)] + ("y" if suf == "ies" else "")
    return w


def words(s): return {stem(w) for w in re.findall(r"[a-z0-9]+", str(s).lower()) if len(w) > 2 and w not in STOP}


def sim(a, b):  # overlap coefficient: short phrases that share most words count as the same
    a, b = words(a), words(b)
    return len(a & b) / min(len(a), len(b)) if a and b else 0.0


def mech(fp):
    m = str(obj(fp).get("mechanism", ""))
    return "" if m.lower().startswith("not designed") else m


def dup(a, b, hi=0.6):
    u, j = (sim(obj(a).get(k, ""), obj(b).get(k, "")) for k in ("user", "job"))
    m = sim(mech(a), mech(b))
    return "same user and job" if u >= hi and j >= hi else "same job and mechanism" if j >= hi and m >= hi else None


def near(a, b):
    return sim(obj(a).get("domain", ""), obj(b).get("domain", "")) >= 0.5 and sim(obj(a).get("job", ""), obj(b).get("job", "")) >= 0.5


def year_of(d):
    m = re.match(r"\s*(\d{4})(?:-(\d{1,2}))?", str(d))
    return (int(m.group(1)), int(m.group(2) or 6)) if m else None


def check_claims(n, i, mode, now, researched):
    F, W = fails.append, warns.append
    cl = [obj(c) for c in lst(i.get("claims"))]
    for c in cl:
        t, txt = str(c.get("type", "")).lower(), str(c.get("text", ""))[:45]
        if t not in TYPES:
            F(f"{n}: claim '{txt}' needs type fact, evidence, assumption or hypothesis")
        elif t in ("fact", "evidence") and c.get("how") != "user" and not (url(c.get("source")) and c.get("how") == "opened"):
            F(f"{n}: {t} '{txt}' needs a URL you opened (how: opened); otherwise relabel it assumption or hypothesis")
        if t == "evidence" and str(c.get("strength", "")).lower() not in LEVEL:
            F(f"{n}: evidence '{txt}' needs strength strong, moderate or weak")
        if t in ("fact", "evidence") and c.get("how") == "user":
            W(f"{n}: '{txt}' rests on the user's word; label it that way in the reply")
    ev = [c for c in cl if str(c.get("type", "")).lower() == "evidence" and c.get("how") == "opened" and url(c.get("source"))]
    stale = sum(1 for c in ev if year_of(c.get("date")) and (now[0] - year_of(c["date"])[0]) * 12 + now[1] - year_of(c["date"])[1] > 24)
    undated = sum(1 for c in ev if not year_of(c.get("date")))
    if stale:
        W(f"{n}: {stale} evidence item(s) older than 24 months; look for a recent echo")
    if undated > len(ev) / 2:
        W(f"{n}: most evidence is undated; date every item")
    for need in (("assumption", "hypothesis") if mode == "product" else ("assumption",)):
        if not any(str(c.get("type", "")).lower() == need for c in cl):
            F(f"{n}: list at least one {need}")
    for c in ev:
        if c.get("segment") and str(c["segment"]).lower() not in ("same", "neighboring"):
            F(f"{n}: evidence '{str(c.get('text', ''))[:45]}' segment must be same or neighboring")
    good = [c for c in ev if LEVEL.get(str(c.get("strength", "")).lower(), 0) >= 2]
    unattributed = [c for c in good if not (c.get("speaker") and c.get("about"))]
    offseg = [c for c in good if str(c.get("segment", "")).lower() != "same"]
    good = [c for c in good if c.get("speaker") and c.get("about") and str(c.get("segment", "")).lower() == "same"]
    orgs = {str(c.get("org") or site(c["source"])).strip().lower() for c in good}
    best = max([LEVEL.get(str(c.get("strength", "")).lower(), 0) for c in ev] or [0])
    summ = str(obj(i.get("evidence_summary")).get("strength", "")).lower()
    status = i.get("problem_status", i.get("status"))
    if summ not in LEVEL:
        F(f"{n}: evidence_summary.strength must be strong, moderate or weak")
    elif LEVEL[summ] > best:
        F(f"{n}: overall evidence called '{summ}' but no opened evidence item is that strong")
    if status not in ("validated", "hypothesis"):
        F(f"{n}: problem_status must be validated or hypothesis")
    elif status == "validated":
        if not researched:
            F(f"{n}: research was unavailable, so it can only be a hypothesis")
        elif len(orgs) < 2:
            F(f"{n}: 'validated' needs >=2 opened, attributed (speaker, about), same-segment evidence items at moderate or "
              f"better from independent organizations; else problem_status hypothesis"
              + (f" ({len(unattributed)} item(s) lack speaker/about)" if unattributed else "")
              + (f" ({len(offseg)} item(s) not marked segment: same)" if offseg else ""))
        elif summ == "weak":
            F(f"{n}: weak overall evidence can't be 'validated'")
    else:
        W(f"{n}: problem shown as a hypothesis; lead its card with the validation test")


def wcount(t): return len(re.findall(r"[A-Za-z0-9][\w'’-]*", str(t)))


def check_wrapper(n, i, mode):
    """Stage 4b / 6W: product first, AI second. Runs in both modes, before an idea can be shown."""
    F, W = fails.append, warns.append
    w, card, fp = obj(i.get("wrapper_test")), obj(i.get("card")), obj(i.get("fingerprint"))
    probe = " ".join(str(x) for x in [i.get("name"), w.get("product_is"), card.get("product"), card.get("concept"),
                                      card.get("core_workflow"), card.get("ai_role"), fp.get("mechanism"), fp.get("job")])
    if wcount(w.get("product_is")) < 8 or BOILER.match(str(w.get("product_is", "")).strip()):
        F(f"{n}: wrapper_test.product_is must say what the product is, as a product, before the model is mentioned")
    hits = sorted(k for k, rx in WRAPPER_SHAPES.items() if re.search(rx, probe, re.I))
    arch = obj(w.get("archetype"))
    declared = str(arch.get("matches", "")).strip().lower() not in ("", "none")
    if hits and not declared:
        F(f"{n}: reads as the wrapper shape {hits}; kill it, or declare wrapper_test.archetype.matches and say in "
          f"archetype.differs what this does that the shape does not")
    if declared and wcount(arch.get("differs")) < 8:
        F(f"{n}: wrapper_test.archetype declares '{arch.get('matches')}' without archetype.differs")
    # --- the three ordered questions -----------------------------------------------------------
    ai = w.get("ai_in_loop")
    if not isinstance(ai, bool):
        F(f"{n}: wrapper_test.ai_in_loop must be true or false (is a model in the core loop?)")
    lev = obj(w.get("ai_leverage"))
    kinds = [str(k).strip().lower() for k in lst(lev.get("kinds"))]
    if ai is True:
        red = obj(w.get("reduction"))
        if wcount(red.get("sentence")) < 6:
            F(f"{n}: wrapper_test.reduction.sentence must state the idea in the form 'the user gives X to a model and "
              f"gets Y back', so the fair/unfair call can be made")
        if not isinstance(red.get("fair"), bool):
            F(f"{n}: wrapper_test.reduction.fair must be true or false")
        elif red["fair"]:
            F(f"{n}: the reduction sentence is a fair summary of the product, so this is an LLM wrapper; kill it and "
              f"regenerate a mechanism that owns more of the workflow")
        if not kinds:
            F(f"{n}: wrapper_test.ai_leverage.kinds must name where the model creates leverage, from {sorted(AI_LEVERAGE)}")
        bad = [k for k in kinds if k not in AI_LEVERAGE]
        if bad:
            F(f"{n}: ai_leverage.kinds {bad} not in {sorted(AI_LEVERAGE)}")
        elif kinds and set(kinds) <= DRAFTING:
            F(f"{n}: the model's only leverage is {kinds}; generating text is the wrapper shape, so name another kind "
              f"of leverage and the deterministic step that checks the output, or kill it")
        if wcount(lev.get("why_not_deterministic")) < 8:
            F(f"{n}: ai_leverage.why_not_deterministic must say why plain code, rules or search can't do this step")
        wo = obj(w.get("without_model"))
        surv = str(wo.get("survives", "")).strip().lower()
        if wcount(wo.get("what")) < 8 or BOILER.match(str(wo.get("what", "")).strip()):
            F(f"{n}: without_model.what must list what still exists if the model disappears (the workflow, the "
              f"integrations, the records, the rules), not a UI")
        if surv not in SURVIVES:
            F(f"{n}: without_model.survives must be substantial, thin or nothing")
        elif surv == "nothing":
            F(f"{n}: nothing survives without the model, so there is no product; kill it and regenerate")
        elif surv == "thin":
            if mode == "product":
                F(f"{n}: only a thin product survives without the model; own more of the workflow or kill it")
            else:
                W(f"{n}: only a thin product survives without the model; hard_part must carry the technical depth")
        sm = obj(w.get("smell"))
        for q in SMELL:
            if not isinstance(sm.get(q), bool):
                F(f"{n}: wrapper_test.smell.{q} must be answered true or false")
        for q, why in SMELL_FATAL.items():
            if sm.get(q) is True:
                F(f"{n}: smell.{q} is true ({why}); kill it and regenerate")
        for q, why in SMELL_REQUIRED.items():
            if sm.get(q) is False:
                F(f"{n}: smell.{q} is false ({why}); kill it and regenerate")
        if sm.get("q6_improves_with_use") is False:
            W(f"{n}: repeated use doesn't make it better; say what would change that or expect it to be copied")
        if sm.get("q7_pays_after_novelty") is False:
            W(f"{n}: no reason to keep paying once AI stops being novel; check the payer and retention answers")
    elif ai is False:
        if not re.match(r"\s*(n/?a|no model|none)\b", str(card.get("ai_role", "")), re.I):
            F(f"{n}: ai_in_loop is false, so card.ai_role must start 'n/a' and say the product has no model in its loop")
        if SHAPED.search(str(fp.get("mechanism", ""))) or kinds:
            F(f"{n}: ai_in_loop is false but the mechanism or ai_leverage describes a model; settle which it is")
    # --- authenticity signals -------------------------------------------------------------------
    named, groups, evidenced = set(), set(), 0
    for a in map(obj, lst(i.get("authenticity"))):
        sig = str(a.get("signal", "")).strip().lower()
        if sig not in AUTH_SIGNALS:
            F(f"{n}: authenticity signal '{sig}' isn't one of {sorted(AUTH_SIGNALS)}")
            continue
        if wcount(a.get("how")) < 8:
            F(f"{n}: authenticity '{sig}' needs 'how' in this product's own terms, not the label restated")
            continue
        if str(a.get("basis", "")).strip().lower() not in ("evidence", "commitment"):
            F(f"{n}: authenticity '{sig}' needs basis evidence or commitment")
            continue
        named.add(sig)
        groups.add(AUTH_SIGNALS[sig])
        evidenced += str(a.get("basis", "")).strip().lower() == "evidence"
    if len(named) < AUTH_MIN:
        F(f"{n}: only {len(named)} authenticity signal(s) hold up; {AUTH_MIN}+ are needed, and a wrapper can't produce them")
    for g in sorted(AUTH_GROUPS):
        if g not in groups:
            F(f"{n}: no authenticity signal in the '{g}' group {sorted(AUTH_GROUPS[g])}; without one the model is the product")
    if not evidenced and named:
        (F if mode == "product" else W)(f"{n}: every authenticity signal is a design commitment with nothing evidenced; "
                                        f"evidence one of them or name the test that settles it")
    sm = obj(w.get("smell"))
    if sm.get("q5_touches_real_systems") is False and (named & AUTH_GROUPS["workflow"]):
        F(f"{n}: smell.q5 says it touches no real system, but the authenticity signals claim a workflow; fix the contradiction")
    if sm.get("q6_improves_with_use") is False and (named & AUTH_GROUPS["compounding"]):
        F(f"{n}: smell.q6 says repeated use changes nothing, but a compounding signal is claimed; fix the contradiction")
    if obj(obj(i.get("anti_patterns")).get("weekend_clone")).get("hit") is True and mode == "product" \
            and not (named & AUTH_GROUPS["substance"]):
        F(f"{n}: an LLM API plus a frontend reproduces this in a weekend and nothing in the substance group says otherwise")
    # --- moat, alternatives today, why now ------------------------------------------------------
    m = obj(i.get("moat"))
    mechs = [str(x).strip().lower() for x in (lst(m.get("mechanism")) or ([m["mechanism"]] if m.get("mechanism") else []))]
    if not mechs:
        F(f"{n}: moat.mechanism must name at least one of {sorted(MOAT_MECH)}")
    else:
        bad = [x for x in mechs if x not in MOAT_MECH]
        if bad:
            F(f"{n}: moat.mechanism {bad} not in {sorted(MOAT_MECH)}")
    if wcount(m.get("why_not_copyable")) < 8 or PROMPT_MOAT.match(str(m.get("why_not_copyable", "")).strip()):
        F(f"{n}: moat.why_not_copyable must answer why someone can't copy this by calling a model API; prompts, speed "
          f"and UX aren't answers")
    alts = [obj(a) for a in lst(i.get("alternatives"))]
    kindset = {str(a.get("alternative", "")).strip().lower() for a in alts}
    if not alts:
        F(f"{n}: alternatives is empty; name what this user does today, from {sorted(ALT_TODAY)}")
    unknown = sorted(k for k in kindset if k and k not in ALT_TODAY)
    if unknown:
        F(f"{n}: alternatives {unknown} not in {sorted(ALT_TODAY)}")
    for a in alts:
        if not str(a.get("today", "")).strip() or wcount(a.get("better")) < 5:
            F(f"{n}: alternative '{a.get('alternative')}' needs 'today' (what they actually do) and 'better' (what "
              f"changes for them)")
    if kindset and kindset <= {"doing nothing"}:
        W(f"{n}: the only alternative is doing nothing; check the vitamin and acuteness answers before showing it")
    wn = obj(i.get("why_now"))
    kind = str(wn.get("kind", "")).strip().lower()
    if kind not in WHYNOW_KIND:
        F(f"{n}: why_now.kind must be one of {sorted(WHYNOW_KIND)}")
    elif kind == "none":
        if wcount(wn.get("opening")) < 8:
            F(f"{n}: why_now.kind is 'none', so why_now.opening must name the opening (a neglected segment, a group "
              f"priced out, a channel others lack)")
    else:
        for k in ("change", "threshold", "who_couldnt_before"):
            if not str(wn.get(k, "")).strip():
                F(f"{n}: why_now.{k} missing; a why-now names the dated change, the threshold it crossed and who "
                  f"couldn't do this before")
        if not re.search(r"\b(19|20)\d\d\b", " ".join([str(wn.get("date", "")), str(wn.get("change", ""))])):
            F(f"{n}: why_now needs the date of the change itself, not of the page describing it")
        if kind in ("capability", "cost") and not re.search(r"\d", str(wn.get("threshold", ""))):
            W(f"{n}: why_now.threshold for a {kind} change should carry the number it crossed")
    vague = VAGUE_WHYNOW.search(" ".join(str(wn.get(k, "")) for k in ("change", "threshold", "who_couldnt_before",
                                                                      "sentence", "opening")) + " " + str(card.get("why_now", "")))
    if vague:
        F(f"{n}: '{vague.group(0)}' isn't a why-now; name the dated change and the threshold it crossed")


def check_idea(i, mode, ctx, pressure, crit_names, verdict, researched, now, build_on=()):
    F, W = fails.append, warns.append
    n = i.get("name", "?")
    if i.get("origin") not in (("problem", "user") if pressure else ("problem",)):
        F(f"{n}: origin is '{i.get('origin')}'; ideas must start from a validated problem")
    card = obj(i.get("card"))
    for k in CARD[mode]:
        if not card.get(k):
            F(f"{n}: card.{k} missing")
    fp = obj(i.get("fingerprint"))
    for k in ("domain", "user", "job", "mechanism", "mechanism_family"):
        if not fp.get(k):
            F(f"{n}: fingerprint.{k} missing")
    if fp.get("mechanism_family") and str(fp["mechanism_family"]).lower() not in FAMILIES:
        F(f"{n}: mechanism_family must be one of {sorted(FAMILIES)}")
    check_claims(n, i, mode, now, researched)
    check_wrapper(n, i, mode)
    scan = obj(i.get("competition_scan"))
    missing = [c for c in SCAN[mode] if not str(scan.get(c, "")).strip()]
    if missing:
        F(f"{n}: competition_scan lacks {missing} (write what turned up, or 'not checked: reason')")
    comps = [obj(c) for c in lst(i.get("competitors"))]
    for c in comps:
        if c.get("kind") not in SCAN[mode] or not c.get("difference") or (c.get("kind") != "workaround" and not url(c.get("url"))):
            F(f"{n}: competitor '{c.get('name')}' needs a kind from {SCAN[mode]}, a URL (except workarounds) and the difference")
    if not comps:
        W(f"{n}: no named competitors or alternatives; 'nobody does this' is rarely true")
    wedge = str(i.get("wedge", ""))
    if not wedge.strip():
        F(f"{n}: wedge missing")
    elif len(wedge.split()) < 8 or BUZZ.search(wedge) or re.fullmatch(r"\W*(ai|agents?|better ux|cheaper|faster|simpler)\W*", wedge, re.I):
        W(f"{n}: wedge looks vague; name the concrete difference versus the closest alternative")
    rec = obj(i.get("recycled"))
    probe = " ".join([str(n), str(card.get("idea") or card.get("concept") or ""), str(fp.get("mechanism", "")), str(fp.get("job", ""))])
    cat = str(rec.get("category", "none")).strip().lower()
    for name, rx in RECYCLED.items():
        if re.search(rx, probe, re.I) and cat in ("", "none"):
            W(f"{n}: looks like the recycled category '{name}'; declare recycled.category with its wedge, or drop it")
    if cat not in ("", "none") and not rec.get("wedge"):
        F(f"{n}: recycled category '{cat}' declared without the research-backed wedge")
    dm = obj(i.get("default_match"))
    if not str(dm.get("matches", "none")).lower().startswith("none") and str(dm.get("matches", "")).strip() \
            and not dm.get("why_different"):
        F(f"{n}: matches default '{dm.get('matches')}' but default_match.why_different is empty")
    ap = obj(i.get("anti_patterns"))
    need = KILL["shared"] + KILL[mode] + FIX[mode] + (BACKGROUND_KEYS if mode == "hackathon" and ctx != "general-strict" else [])
    for k in need:
        v = obj(ap.get(k))
        if v.get("hit") == "unknown" and v.get("why"):
            W(f"{n}: '{k}' unknown; the test named in its reason must settle it")
        elif not isinstance(v.get("hit"), bool) or not v.get("why"):
            F(f"{n}: anti-pattern '{k}' not assessed (needs hit true, false or 'unknown', and why)")
        elif v["hit"] and k in BACKGROUND_KEYS and ctx == "personal" and (
                k == "resume_first" or any(b in str(v.get("why", "")).lower() for b in build_on)):
            W(f"{n}: '{k}' hit, allowed in PERSONAL mode; disclose it")
        elif v["hit"] and (k in KILL["shared"] + KILL[mode] + BACKGROUND_KEYS):
            F(f"{n}: kill-level anti-pattern '{k}'; kill it or replace it from the discovery pool")
        elif v["hit"] and k == "weekend_clone":
            W(f"{n}: 'weekend_clone'; an LLM API and a frontend reproduce the core, so name the part that isn't "
              f"reproducible (moat and the substance signals carry it)")
        elif v["hit"] and k == "one_off":
            W(f"{n}: 'one_off'; fine for a service, but kill it if the user asked for SaaS or recurring revenue")
        elif v["hit"]:
            W(f"{n}: '{k}'; remove the forced part, and kill the idea if it collapses without it")
    if mode == "product":
        ch = obj(i.get("checks"))
        for k in CHECKS:
            if not ch.get(k):
                F(f"{n}: checks.{k} missing (answer it, or write 'unknown: what would settle it')")
        vals = [obj(v) for v in lst(i.get("validation"))]
        if not vals:
            F(f"{n}: no validation path")
        for v in vals:
            miss = [k for k in ("assumption", "hypothesis", "test", "pass_if", "kill_if", "cost", "time") if not v.get(k)]
            if miss:
                F(f"{n}: validation step lacks {miss}")
        dist = str(card.get("distribution", ""))
        if HOPE.search(dist) and not DIRECT.search(dist):
            W(f"{n}: distribution relies on ads, press or virality; name where the first users are and the manual action there")
        wn = str(card.get("why_now", ""))
        if re.search(r"\bai is (hot|booming|everywhere|taking off)\b", wn, re.I):
            F(f"{n}: 'AI is hot' is not a why-now; name a dated change")
        elif not re.search(r"\b(19|20)\d\d\b", wn) and not re.search(r"no recent change|the opening is", wn, re.I):
            W(f"{n}: why_now has no dated change; date it or say 'no recent change' and name the opening")
    else:
        rows = [obj(s) for s in lst(i.get("sponsors"))]
        for s in rows:
            miss = [k for k in ("capability", "why_needed", "without_it", "component", "depth", "sponsor_goal") if not s.get(k)]
            if miss:
                F(f"{n}: sponsor '{s.get('sponsor')}' missing {miss}")
            depth, sv = str(s.get("depth", "")).lower(), verdict.get(str(s.get("sponsor", "")).lower(), "")
            if depth not in DEPTHS:
                F(f"{n}: sponsor '{s.get('sponsor')}' depth must be core, meaningful or superficial")
            elif depth == "superficial" and obj(ap.get("superficial_sponsor")).get("hit") is not True:
                F(f"{n}: '{s.get('sponsor')}' is superficial, so superficial_sponsor must be a hit")
            elif depth != "superficial" and re.search(r"does ?n[o']t (meaningfully )?fit|no fit|not fit", sv) \
                    and not re.search(r"\b(core|meaningful)\b", sv):
                F(f"{n}: '{s.get('sponsor')}' is {depth} here but its verdict says it doesn't fit")
        al = [obj(a) for a in lst(i.get("criteria_alignment"))]
        got = {str(a.get("criterion", "")).lower() for a in al}
        for c in crit_names:
            if c not in got:
                F(f"{n}: no criteria_alignment entry for official criterion '{c}'")
        for a in al:
            basis = str(a.get("basis", "")).lower()
            if not a.get("how") or basis not in BASIS:
                F(f"{n}: alignment '{a.get('criterion')}' needs how and basis official/pattern/inference (not a grade)")
            elif basis != "inference" and not (url(a.get("source")) or a.get("source") in SPECIAL):
                F(f"{n}: alignment '{a.get('criterion')}' has basis {basis} but no source")
            if crit_names and str(a.get("criterion", "")).lower() not in crit_names:
                F(f"{n}: alignment criterion '{a.get('criterion')}' isn't an official criterion")
        demo = obj(i.get("demo"))
        for k in DEMO:
            if not demo.get(k):
                F(f"{n}: demo.{k} missing")
        moments = {str(obj(m).get("criterion", "")).lower() for m in lst(demo.get("moments")) if obj(m).get("moment")}
        for c in crit_names - moments:
            W(f"{n}: no demo moment for criterion '{c}'")
        cpw = obj(i.get("closest_past_winner"))
        if not ((cpw.get("name") and url(cpw.get("url")) and cpw.get("difference"))
                or (str(cpw.get("name", "")).lower().startswith("none") and lst(cpw.get("searches")))):
            F(f"{n}: closest_past_winner needs name, URL and difference, or 'none found' with the searches")
        if not i.get("outsider"):
            W(f"{n}: no outsider-test script")


def check(pkg, ledger, prior, pressure, reply):
    F, W = fails.append, warns.append
    if not isinstance(pkg, dict):
        F("ideas.json must be a JSON object")
        return
    run, pers = obj(pkg.get("run")), obj(pkg.get("personal"))
    mode, ctx, depth = run.get("mode"), run.get("context"), run.get("depth", "full")
    if mode not in CARD:
        F("run.mode must be product or hackathon")
        return
    now = year_of(run.get("date")) or (2026, 9)
    if ctx not in CONTEXTS:
        F("run.context must be general, general-strict or personal")
    if ctx == "personal" and not pers.get("explicit_request"):
        F("context personal needs personal.explicit_request (the user's own words)")
    if ctx != "personal" and lst(pers.get("facts_used")):
        F("personal facts were used in a general run")
    if ctx == "personal" and not lst(pers.get("facts_used")):
        W("context personal but facts_used is empty; say which facts shaped which ideas")
    layer = lst(pkg.get("personal_layer"))
    if layer and (ctx == "general-strict" or (ctx == "general" and mode == "product")):
        F(f"a personal layer isn't allowed in {mode} mode with context {ctx}")
    shown = {str(obj(x).get("name")) for x in lst(pkg.get("ideas"))}
    for note in map(obj, layer):
        extra = sorted(set(note) - NOTE_KEYS)
        if extra:
            F(f"personal_layer may only annotate with {sorted(NOTE_KEYS)}; found {extra}")
        if str(note.get("idea")) not in shown:
            F(f"personal_layer note for '{note.get('idea')}' matches no surviving idea; the layer can't add ideas")
    if run.get("discovery_method") not in METHODS:
        F(f"run.discovery_method must be one of {sorted(METHODS)}")
    elif run["discovery_method"] != "blind_subagent":
        W(f"discovery was '{run['discovery_method']}'; say how isolation was done")
    if run.get("context_seen") and run.get("discovery_method") == "blind_subagent":
        W("the discovery subagent found requester information in its context and ignored it; disclose it")
    lo_p, lo_g, lo_d = (10, 4, 10) if depth == "full" else (6, 3, 5)
    if not isinstance(run.get("problems_considered"), int) or run["problems_considered"] < lo_p:
        W(f"fewer than {lo_p} problems were considered")
    if len({str(g).lower() for g in lst(run.get("user_groups"))}) < lo_g:
        W(f"fewer than {lo_g} user groups were explored")
    defaults = [str(d) for d in lst(pkg.get("defaults"))]
    if len(defaults) < lo_d:
        W(f"only {len(defaults)} pre-registered defaults (want {lo_d}+)")
    researched = not run.get("research_unavailable")
    seeds = obj(run.get("seeds"))
    if not (lst(seeds.get("lenses")) and lst(seeds.get("source_types"))):
        F("run.seeds needs the lenses and source types this run used (later runs rotate away from them)")
    names = {str(obj(x).get("name")) for x in lst(pkg.get("ideas")) + lst(pkg.get("killed"))} | {"(seeds)"}
    if any(e.get("run") == run.get("slug") and str(e.get("name")) not in names for e in ledger):
        F(f"slug '{run.get('slug')}' was used by an earlier run; give this run a new slug")
    if pressure and not (obj(pkg.get("stated")).get("idea") and obj(pkg.get("stated")).get("verdict")):
        F("pressure mode needs 'stated' with the user's idea and the verdict")
    if lst(pkg.get("research_gaps")):
        W(f"{len(lst(pkg['research_gaps']))} research gap(s); list them under Gaps in the reply")
    req, note = run.get("ideas_requested"), str(pkg.get("shortfall_note", "")).strip()
    ideas_n = len(lst(pkg.get("ideas")))
    if isinstance(req, int) and req > 0:
        if ideas_n < req and not note:
            F(f"{ideas_n} of the {req} ideas asked for survived: write shortfall_note (what the filter killed and why) "
              f"and say it in the reply. Never pad the list to reach the number")
        if ideas_n > req:
            W(f"{ideas_n} ideas for a request of {req}; show the strongest and log the rest")
    elif ideas_n < 2 and not note:
        W("fewer than two survivors and no shortfall_note; say plainly why, and don't pad")
    wrapper_kills = [k for k in map(obj, lst(pkg.get("killed"))) if str(k.get("stage", "")).lower() == "wrapper"]
    if any(obj(obj(i).get("wrapper_test")).get("ai_in_loop") is True for i in lst(pkg.get("ideas"))) and not wrapper_kills:
        W("no idea was killed at the wrapper filter (stage 'wrapper'); check it actually ran on the whole pool")
    crit_names, verdict = set(), {}
    if mode == "hackathon":
        ev = obj(pkg.get("event"))
        crits = [obj(c) for c in lst(ev.get("criteria"))]
        if not crits:
            F("event.criteria is empty; record them (user-relayed or assumed when unpublished)")
        for c in crits:
            name, src = str(c.get("criterion", "")).strip(), c.get("source")
            crit_names.add(name.lower())
            if not name or not (url(src) or src in SPECIAL) or not c.get("implication"):
                F(f"criterion '{name}' needs a source (URL, user-relayed or assumed) and an implication")
            elif url(src) and not c.get("quote"):
                F(f"criterion '{name}' needs its quoted wording")
            elif src in SPECIAL:
                W(f"criterion '{name}' is {src}, not checked on an official page")
        verdict = {str(v.get("sponsor", "")).lower(): str(v.get("verdict", "")).lower()
                   for v in map(obj, lst(pkg.get("sponsor_verdicts"))) if v.get("why")}
        for s in lst(ev.get("sponsors")):
            if str(s).lower() not in verdict:
                F(f"no fit verdict with a reason for sponsor '{s}'")
    ideas, killed = [obj(i) for i in lst(pkg.get("ideas"))], lst(pkg.get("killed"))
    if not ideas:
        W("no idea survived; say so plainly and show the kill log")
        if not killed:
            F("no ideas and no kill log")
    elif not killed:
        W("the kill log is empty; every run kills something, so record it")
    build_on = [str(b).lower() for b in lst(pers.get("build_on")) if str(b).strip()]
    for i in ideas:
        check_idea(i, mode, ctx, pressure, crit_names, verdict, researched, now, build_on)
    fps = [obj(i.get("fingerprint")) for i in ideas]
    for a in range(len(ideas)):
        for b in range(a + 1, len(ideas)):
            why = dup(fps[a], fps[b])
            if why:
                F(f"'{ideas[a].get('name')}' and '{ideas[b].get('name')}' share the {why[5:]}; keep one")
    if len(ideas) >= 2:
        if len({str(f.get("mechanism_family", "")).lower() for f in fps}) == 1:
            W("every idea uses the same mechanism family; fine if the others died on evidence, but say so")
        if len({str(f.get("domain", "")).lower() for f in fps}) == 1 and ctx != "personal" \
                and str(run.get("scope", "open")).lower() in ("", "open"):
            W("every idea is in the same domain; check the brief really is that narrow")
        if sum(bool(SHAPED.search(str(f.get("mechanism", "")))) for f in fps) > max(1, len(fps) // 2):
            W("most ideas are agent/chat/assistant-shaped; check discovery wasn't technology-led")
    for i, fp in zip(ideas, fps):
        blob = " ".join([str(i.get("name")), str(obj(i.get("card")).get("idea") or obj(i.get("card")).get("concept") or ""),
                         str(fp.get("job", "")), str(fp.get("mechanism", ""))])
        if str(obj(i.get("default_match")).get("matches", "none")).strip().lower() in ("", "none"):
            for d in defaults:
                dw, bw = words(d), words(blob)
                if dw and bw and len(dw & bw) / min(len(dw), len(bw)) >= 0.5:
                    W(f"{i.get('name')}: resembles default '{d[:60]}'; declare default_match with why_different "
                      "(or matches 'none: <why>' if only words overlap), or drop it")
        for e in ledger:
            if e.get("run") == run.get("slug") or e.get("status") in ("seeds", "lead"):
                continue
            efp = obj(e.get("fingerprint"))
            why = dup(fp, efp)
            strict = run.get("request_type") == "more" or str(e.get("date")) == str(run.get("date"))
            if why and not i.get("revisit"):
                (F if strict else W)(f"{i.get('name')}: repeats '{e.get('name')}' from run {e.get('run')} ({why}); "
                                     + ("differ in user, job or mechanism" if strict else "say it was shown before"))
            elif not why and near(fp, efp) and not i.get("revisit"):
                W(f"{i.get('name')}: close to '{e.get('name')}' from run {e.get('run')} (same domain and job); say how it differs")
    for k in keys(pkg):
        if re.fullmatch(r"(scores?|rank(ing)?s?|ratings?|points|weighted(_total)?|overall_score)", str(k), re.I):
            F(f"key '{k}' looks like a score or ranking; describe tradeoffs instead")
    if len(ideas) >= 2 and not lst(pkg.get("tradeoffs")):
        W("no tradeoffs table; lay out the tradeoffs in words so the user can decide")
    scored_text = [nourl(t) for t in strings([[i.get("card"), i.get("wedge"), i.get("demo")] for i in ideas]
                                             + [pkg.get("tradeoffs")])]
    for t in scored_text:
        m = RANK.search(t)
        if m:
            F(f"ranking or scoring language '{m.group(0)}'; explain tradeoffs, don't rank")
        m = PREDICT.search(t) if mode == "hackathon" else None
        if m:
            F(f"outcome prediction '{m.group(0)}'; describe criterion fit instead")
    buzz = sorted({m.group(0).lower() for t in scored_text for m in BUZZ.finditer(t)})
    if buzz:
        W(f"buzzwords in the ideas: {', '.join(buzz)}; say what the product does instead")
    for t in strings([pkg.get("ideas"), pkg.get("tradeoffs"), pkg.get("sponsor_verdicts")]):
        judge_scan(t, "")
    if prior and mode == "hackathon" and ctx != "general-strict":
        for i in ideas:
            iw = words(" ".join([str(i.get("name")), json.dumps(obj(i.get("fingerprint")), ensure_ascii=False),
                                 str(obj(i.get("card")).get("concept") or "")]))
            for pp in map(obj, lst(obj(prior).get("projects"))):
                pw = words(str(pp.get("summary", "")) + " " + " ".join(map(str, lst(pp.get("keywords")))))
                ov = len(iw & pw) / max(1, min(len(iw), len(pw)))
                if len(iw & pw) >= 2 and ov >= 0.3:
                    W(f"{i.get('name')}: overlaps past project '{pp.get('name')}' ({', '.join(sorted(iw & pw)[:6])}); "
                      "confirm prior_project_variation")
    if ctx in ("general", "general-strict"):
        scrub = [{k: v for k, v in i.items() if k != "anti_patterns"} for i in ideas]
        m = BUILDER.search(json.dumps(scrub, ensure_ascii=False))
        if m:
            F(f"background-based reasoning in a general run: '{m.group(0)}'")
        blind = json.dumps([scrub, pkg.get("tradeoffs"), pkg.get("sponsor_verdicts")], ensure_ascii=False).lower()
        for x in lst(obj(prior).get("identifiers")):
            x = str(x).lower()
            if x and re.search(r"\b" + re.escape(x) + r"\b", blind):
                F(f"requester identifier '{x}' appears in the ideas of a general run")
    if reply:
        raw = reply
        judge_scan(raw, "reply: ")
        if ideas:
            for lab in LABELS[mode]:
                c = labels_in(raw, lab)
                if not c:
                    F(f"reply: no '{lab}' heading; each idea needs the mode's full card")
                elif c < len(ideas):
                    W(f"reply: '{lab}' appears {c} time(s) for {len(ideas)} ideas")
        for lab in SECTIONS[mode]:
            if not labels_in(raw, lab):
                (F if lab == "tradeoffs" and ideas else W)(f"reply: no '{lab}' section")
        if isinstance(run.get("ideas_requested"), int) and len(ideas) < run["ideas_requested"] \
                and not re.search(r"surviv|held up|passed the filter|of the \d+", raw[:1200], re.I):
            W(f"reply: {len(ideas)} of {run['ideas_requested']} asked-for ideas survived; say so in the opening line")
        reply = nourl(reply)
        body = re.split(r"(?im)^[ \t]*(?:#{1,6}[ \t]*(?:\d+[.)][ \t]*)?|\d+[.)][ \t]*\*\*|\*\*)sources\b", reply)[0]
        nw = len(re.findall(r"[A-Za-z0-9][\w'’-]*", body))
        if nw > 700 * max(1, len(ideas)) + 900:
            W(f"reply is long ({nw} words before Sources); keep each idea to its template and move detail into the package")
        head = notes_cut(reply)
        if ctx in ("general", "general-strict"):
            m = BUILDER.search(head)
            if m:
                F(f"reply: background-based reasoning outside the notes section: '{m.group(0)}'")
            for x in lst(obj(prior).get("identifiers")):
                if str(x).strip() and re.search(r"\b" + re.escape(str(x).lower()) + r"\b", head.lower()):
                    F(f"reply: requester identifier '{x}' appears outside the notes section")
        for m in list(RANK.finditer(reply)) + (list(PREDICT.finditer(reply)) if mode == "hackathon" else []):
            F(f"reply: '{m.group(0)}'; no rankings, scores, winners or predictions")
        rb = sorted({m.group(0).lower() for m in BUZZ.finditer(reply)})
        if rb:
            W(f"reply buzzwords: {', '.join(rb)}")


def judge_scan(text, where):
    for s_ in re.split(r"(?<=[.!?])\s+|\n", str(text)):
        if JUDGE.search(unquote(s_)):
            (warns if SOURCED.search(s_) else fails).append(f"{where}judge statement '{s_.strip()[:80]}'; cite what they said or wrote, or drop it")
        if re.search(r"\bjudges?\b", s_, re.I) and TRAITS.search(s_) and TAILOR.search(s_):
            fails.append(f"{where}tailoring to a judge's personal characteristics: '{s_.strip()[:80]}'")


def labels_in(text, lab):
    return (len(re.findall(r"(?im)\*\*[ \t]*(?:" + lab + r")\b", text))
            + len(re.findall(r"(?im)^[ \t]*#{1,6}[ \t]*(?:\d+[.)][ \t]*)?(?:" + lab + r")\b", text)))


def notes_cut(reply):  # the reply minus its "Notes for you" section, which may name the builder's projects
    lines = reply.split("\n")
    start = next((k for k, ln in enumerate(lines) if re.search(r"notes for you", ln, re.I)
                  and re.match(r"\s*(#{1,6}\s|\*\*|\d+[.)]\s*\*\*)", ln)), None)
    if start is None:
        return reply
    hm = re.match(r"\s*(#{1,6})\s", lines[start])
    end = len(lines)
    for k in range(start + 1, len(lines)):
        h = re.match(r"\s*(#{1,6})\s", lines[k])
        if (h and (not hm or len(h.group(1)) <= len(hm.group(1)))) or (not hm and re.match(r"\s*\d+[.)]\s*\*\*", lines[k])):
            end = k
            break
    return "\n".join(lines[:start] + lines[end:])


def check_intel(paths):
    for x in paths:
        if "judging" not in x.split("/")[-1].lower():
            continue
        try:
            text = open(x, encoding="utf-8").read()
        except OSError:
            continue
        judge_scan(text, f"{x}: ")
        m = PREDICT.search(text)
        if m:
            fails.append(f"{x}: outcome prediction '{m.group(0)}'")


def cell(x):
    x = "; ".join(map(str, x)) if isinstance(x, list) else json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else str(x if x is not None else "")
    return x.replace("|", "\\|").replace("\n", " ")


def table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]


def render(pkg, path, extra=()):
    run = obj(pkg.get("run"))
    mode = run.get("mode")
    L = [f"# Idea package: {run.get('slug', '')}", "",
         f"Mode {mode} \u00b7 context {run.get('context')} \u00b7 depth {run.get('depth', 'full')} \u00b7 discovery {run.get('discovery_method')} \u00b7 "
         f"{run.get('problems_considered')} problems across {len(lst(run.get('user_groups')))} user groups \u00b7 {run.get('date', '')}", "",
         f"Request: {run.get('request', '')}", "", "Ideas are listed in the order they were found. The order is not a ranking.", ""]
    st = obj(pkg.get("stated"))
    if st:
        L += ["## The idea as stated", "", f"**Idea:** {cell(st.get('idea'))}", "", f"**Verdict:** {cell(st.get('verdict'))}", "",
              f"**Checks that fired:** {cell(st.get('fired'))}", "",
              "**Competitors:** " + "; ".join(f"{obj(c).get('name')} ({obj(c).get('url')})" for c in lst(st.get("competitors"))), ""]
    if mode == "hackathon":
        ev = obj(pkg.get("event"))
        L += ["## Event", "", f"{ev.get('name', '')} \u00b7 {ev.get('platform', '')} \u00b7 window {ev.get('window', ev.get('hours', ''))} \u00b7 "
              f"{ev.get('judging_format', '')} \u00b7 {ev.get('url', '')}", ""]
        L += table(["Criterion", "Weight", "Quote", "Source", "Implication"],
                   [[obj(c).get(k) for k in ("criterion", "weight", "quote", "source", "implication")] for c in lst(ev.get("criteria"))])
    for i in map(obj, lst(pkg.get("ideas"))):
        card, es = obj(i.get("card")), obj(i.get("evidence_summary"))
        L += ["", f"## {i.get('name', '')}", "", f"Problem: {i.get('problem_status', i.get('status', ''))} ({es.get('strength', '')}) \u00b7 "
              f"Wedge: {i.get('wedge_status', 'untested')}", ""]
        L += [f"**{label(k)}:** {cell(card.get(k))}\n" for k in CARD[mode]]
        L += [f"**Wedge:** {cell(i.get('wedge'))}", "",
              "Fingerprint: " + "; ".join(f"{k}: {v}" for k, v in obj(i.get("fingerprint")).items()), ""]
        w, wn = obj(i.get("wrapper_test")), obj(i.get("why_now"))
        red, lev, wo, arch = (obj(w.get(k)) for k in ("reduction", "ai_leverage", "without_model", "archetype"))
        L += ["### Wrapper filter (Stage 4b/6W)", "",
              "**What the product is:** " + cell(w.get("product_is")), "",
              "**Model in the core loop:** " + cell(w.get("ai_in_loop")), "",
              "**Reduces to:** " + cell(red.get("sentence")) + " \u2014 fair summary: " + cell(red.get("fair")), "",
              "**AI leverage:** " + cell(lev.get("kinds")) + " \u2014 why plain code isn't enough: "
              + cell(lev.get("why_not_deterministic")), "",
              "**Without the model:** " + cell(wo.get("what")) + " (survives: " + cell(wo.get("survives")) + ")", "",
              "**Wrapper shape declared:** " + cell(arch.get("matches")) + " \u2014 differs: " + cell(arch.get("differs")), ""]
        L += table(["Wrapper-smell question", "Answer"], [[q, obj(w.get("smell")).get(q)] for q in SMELL])
        L += ["", "### Authenticity signals", ""] + table(
            ["Signal", "Group", "How it holds in this product", "Basis"],
            [[obj(a).get("signal"), AUTH_SIGNALS.get(str(obj(a).get("signal", "")).strip().lower(), "?"),
              obj(a).get("how"), obj(a).get("basis")] for a in lst(i.get("authenticity"))])
        mo = obj(i.get("moat"))
        L += ["", "**Moat:** " + cell(mo.get("mechanism")) + " \u2014 " + cell(mo.get("why_not_copyable")), "",
              "### What they do today", ""]
        L += table(["Alternative", "What they actually do", "What changes with this"],
                   [[obj(a).get(k) for k in ("alternative", "today", "better")] for a in lst(i.get("alternatives"))])
        L += ["", "**Why now:** " + " \u00b7 ".join(cell(x) for x in [wn.get("kind"), wn.get("date"), wn.get("change"),
              "threshold: " + cell(wn.get("threshold")), "couldn't before: " + cell(wn.get("who_couldnt_before")),
              wn.get("opening") or ""] if cell(x).strip()), "",
              "### Evidence", "", f"Overall {es.get('strength', '')}: {cell(es.get('why'))} Counter-evidence: {cell(es.get('counter'))} "
              f"Missing voices: {cell(es.get('missing_voices'))}", ""]
        L += table(["Type", "Claim", "Strength", "Speaker", "About", "Source", "Date"],
                   [[obj(c).get(k, "") for k in ("type", "text", "strength", "speaker", "about", "source", "date")]
                    for c in lst(i.get("claims"))])
        L += ["", "### Competitors and alternatives", ""] + table(
            ["Class", "What the scan found"], [[c, obj(i.get("competition_scan")).get(c)] for c in SCAN[mode]])
        L += [""] + table(["Name", "Kind", "URL", "How this differs"],
                          [[obj(c).get(k, "") for k in ("name", "kind", "url", "difference")] for c in lst(i.get("competitors"))])
        if mode == "product":
            ch = obj(i.get("checks"))
            L += ["", "### Checks", ""] + table(["Check", "Answer"], [[label(k), ch.get(k)] for k in CHECKS + ["constraint_fit"]
                                                                      if k in CHECKS or ch.get(k)])
            L += ["", "### Validation path", ""] + table(
                ["Assumption", "Hypothesis", "Test", "Pass if", "Kill if", "Cost", "Time"],
                [[obj(v).get(k) for k in ("assumption", "hypothesis", "test", "pass_if", "kill_if", "cost", "time")] for v in lst(i.get("validation"))])
        else:
            L += ["", "### Sponsors", ""] + table(
                ["Sponsor", "Product", "Capability", "Why needed", "Without it", "Component", "Depth", "Sponsor goal"],
                [[obj(s).get(k, "") for k in ("sponsor", "product", "capability", "why_needed", "without_it", "component", "depth",
                                              "sponsor_goal")] for s in lst(i.get("sponsors"))])
            L += ["", "### Judging criteria alignment", ""] + table(
                ["Criterion", "How it's earned", "Basis", "Source", "Gap"],
                [[obj(a).get(k, "") for k in ("criterion", "how", "basis", "source", "gap")] for a in lst(i.get("criteria_alignment"))])
            d = obj(i.get("demo"))
            L += ["", "### Demo", ""] + [f"- **{label(k)}:** {cell(d.get(k))}" for k in DEMO] + [""]
            L += table(["Criterion", "Moment that earns it"], [[obj(m).get("criterion"), obj(m).get("moment")] for m in lst(d.get("moments"))])
            L += ["", f"**Closest past winner:** {cell(i.get('closest_past_winner'))}", "", f"**Outsider test:** {cell(i.get('outsider'))}"]
            if i.get("afterlife"):
                L += ["", f"**Afterlife (product checks, on request):** {cell(i.get('afterlife'))}"]
        L += ["", "### Anti-pattern checks", ""] + table(
            ["Check", "Hit", "Why"], [[k, obj(v).get("hit"), obj(v).get("why")] for k, v in obj(i.get("anti_patterns")).items()])
    if pkg.get("tradeoffs"):
        names = [str(obj(i).get("name")) for i in lst(pkg.get("ideas"))]
        names += [k for t in lst(pkg["tradeoffs"]) for k in obj(obj(t).get("by_idea")) if k not in names]
        names = list(dict.fromkeys(names))
        L += ["", "## Tradeoffs (no scores; the user decides)", ""] + table(
            ["Dimension"] + names, [[obj(t).get("dimension")] + [obj(obj(t).get("by_idea")).get(nm, "") for nm in names] for t in lst(pkg["tradeoffs"])])
    if mode == "hackathon":
        L += ["", "## Sponsor verdicts", ""] + table(["Sponsor", "Verdict", "Why"],
                                                     [[obj(v).get(k) for k in ("sponsor", "verdict", "why")] for v in lst(pkg.get("sponsor_verdicts"))])
    if pkg.get("shortfall_note"):
        L += ["", "## Why there aren't more ideas", "", cell(pkg.get("shortfall_note"))]
    L += ["", "## Kill log", ""] + table(["Name", "Stage", "Reason"], [[obj(k).get(x) for x in ("name", "stage", "reason")] for k in lst(pkg.get("killed"))])
    L += ["", "## Pre-registered defaults (filtered out unless a wedge was proven)", ""] + [f"- {d}" for d in lst(pkg.get("defaults"))]
    if pkg.get("research_gaps"):
        L += ["", "## Research gaps", ""] + [f"- {g}" for g in lst(pkg["research_gaps"])]
    if pkg.get("personal_layer"):
        L += ["", "## Personal layer (annotations only)", ""] + [f"- {cell(p)}" for p in lst(pkg["personal_layer"])]
    for x in extra:
        try:
            L += ["", open(x, encoding="utf-8").read()]
        except OSError:
            warns.append(f"--append: couldn't read {x}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def load_ledger(path):
    out = []
    try:
        for line in open(path, encoding="utf-8"):
            if line.strip():
                out.append(obj(json.loads(line)))
    except FileNotFoundError:
        pass
    return out


def append_ledger(pkg, path):
    run = obj(pkg.get("run"))
    keep = [e for e in load_ledger(path) if e.get("run") != run.get("slug")]
    base = {"run": run.get("slug"), "date": run.get("date"), "mode": run.get("mode"), "context": run.get("context")}
    new = [dict(base, name=i.get("name"), status="shown", fingerprint=obj(i.get("fingerprint")))
           for i in map(obj, lst(pkg.get("ideas")))]
    new += [dict(base, name=k.get("name"), status="lead" if k.get("stage") == "not-deepened" else "killed",
                 fingerprint=obj(k.get("fingerprint"))) for k in map(obj, lst(pkg.get("killed"))) if k.get("fingerprint")]
    new.append(dict(base, name="(seeds)", status="seeds", seeds=dict(obj(run.get("seeds")), user_groups=lst(run.get("user_groups")))))
    with open(path, "w", encoding="utf-8") as f:
        for e in keep + new:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    opt = lambda flag: args[args.index(flag) + 1] if flag in args else None
    pkg = json.load(open(args[0], encoding="utf-8"))
    if opt("--append-ledger"):
        append_ledger(pkg, opt("--append-ledger"))
        print(f"appended to {opt('--append-ledger')}")
        sys.exit(0)
    prior = json.load(open(opt("--prior"), encoding="utf-8")) if opt("--prior") else None
    reply = open(opt("--reply"), encoding="utf-8").read() if opt("--reply") else None
    check(pkg, load_ledger(opt("--ledger")) if opt("--ledger") else [], prior, opt("--mode") == "pressure", reply)
    check_intel([x for x in (opt("--append") or "").split(",") if x])
    if opt("--render"):
        render(pkg, opt("--render"), [x for x in (opt("--append") or "").split(",") if x])
    for msg in fails:
        print("FAIL", msg)
    for msg in warns:
        print("WARN", msg)
    print(f"{len(fails)} FAIL, {len(warns)} WARN" + (f"; rendered {opt('--render')}" if opt("--render") else ""))
    sys.exit(1 if fails else 0)
