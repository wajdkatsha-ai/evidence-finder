import os
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title="NSDA Evidence", layout="wide")

st.title("NSDA Evidence")
st.write("Pick a format, year, and topic window, then find evidence for each side.")

# ---------------------------------------------------------------------------
# 1. TOPICS (from speechanddebate.org/topics, checked Oct 24, 2026)
# status "Official" = final topic. "Potential" = NSDA vote still pending.
# ---------------------------------------------------------------------------
PF = "Public Forum (PF)"
LD = "Lincoln-Douglas (LD)"
CONG = "Congress"

TOPICS = {
    # ----- PUBLIC FORUM -----
    (PF, 2025, "September/October"): {
        "status": "Official",
        "options": ["Resolved: The United Kingdom should rejoin the European Union."],
    },
    (PF, 2025, "November/December"): {
        "status": "Official",
        "options": ["Resolved: The United States federal government should require technology companies to provide lawful access to encrypted communications."],
    },
    (PF, 2026, "January"): {
        "status": "Official",
        "options": ["Resolved: The People's Republic of China should substantially reduce its international extraction of natural resources."],
    },
    (PF, 2026, "February"): {
        "status": "Official",
        "options": ["Resolved: The Federal Trade Commission should establish a federal regulatory framework for sports betting."],
    },
    (PF, 2026, "March"): {
        "status": "Official",
        "options": ["Resolved: The United States federal government should ban corporate acquisition of single-family residences."],
    },
    (PF, 2026, "April"): {
        "status": "Official",
        "options": ["Resolved: The United States should eliminate the President's authority to deploy military forces abroad without Congressional approval."],
    },
    (PF, 2026, "National Tournament"): {
        "status": "Official",
        "options": ["Resolved: The United States is justified in using force to remove authoritarian leaders from power."],
    },
    (PF, 2026, "September/October"): {
        "status": "Official",
        "options": ["Resolved: The United States federal government should enact a moratorium on hyperscale data center construction."],
        "link": "https://www.speechanddebate.org/public-forum-topic-analysis-september-october-2026/",
        "link_label": "NSDA topic analysis",
    },
    (PF, 2026, "November/December"): {
        "status": "Official",
        "options": ["Resolved: European members of the North Atlantic Treaty Organization should ratify the Treaty on the Prohibition of Nuclear Weapons."],
        "link": "https://www.speechanddebate.org/public-forum-topic-analysis-2026-november-december/",
        "link_label": "NSDA topic analysis",
    },
    (PF, 2027, "January"): {
        "status": "Potential",
        "options": [
            "Resolved: The United States federal government should classify gig workers as employees.",
            "Resolved: In the United States, the benefits of big box retailers outweigh the harms.",
        ],
    },
    (PF, 2027, "February"): {
        "status": "Potential",
        "options": [
            "Resolved: The benefits of the African Continental Free Trade Area outweigh the harms.",
            "Resolved: In Africa, peacekeeping missions led by the United Nations are preferable to those led by regional organizations.",
        ],
    },
    (PF, 2027, "March"): {
        "status": "Potential",
        "options": [
            "Resolved: In the United States, Congressional district boundaries should be drawn by independent redistricting commissions.",
            "Resolved: In the United States, voting should be compulsory in federal elections.",
        ],
    },
    (PF, 2027, "April"): {
        "status": "Potential",
        "options": [
            "Resolved: The Federative Republic of Brazil should prioritize its environmental protection over its economic development.",
            "Resolved: Latin American countries should prioritize Chinese investment over American investment.",
        ],
    },
    # ----- LINCOLN-DOUGLAS -----
    (LD, 2025, "September/October"): {
        "status": "Official",
        "options": ["Resolved: In the United States criminal justice system, plea bargaining is just."],
    },
    (LD, 2025, "November/December"): {
        "status": "Official",
        "options": ["Resolved: The United States ought to rewild substantial tracts of land."],
    },
    (LD, 2026, "January/February"): {
        "status": "Official",
        "options": ["Resolved: The possession of nuclear weapons is immoral."],
    },
    (LD, 2026, "March/April"): {
        "status": "Official",
        "options": ["Resolved: The United States military ought to abide by the principle of non-intervention."],
    },
    (LD, 2026, "National Tournament"): {
        "status": "Official",
        "options": ["Resolved: Democracies ought to prioritize the protection of civil liberties over national security."],
    },
    (LD, 2026, "September/October"): {
        "status": "Official",
        "options": ["Resolved: Outer space colonization is a moral imperative."],
        "link": "https://www.speechanddebate.org/lincoln-douglas-topic-analysis-2026-september-october/",
        "link_label": "NSDA topic analysis",
    },
    (LD, 2026, "November/December"): {
        "status": "Official",
        "options": ["Resolved: De-extinction is unethical."],
        "link": "https://www.speechanddebate.org/lincoln-douglas-topic-analysis-2026-november-december/",
        "link_label": "NSDA topic analysis",
    },
    (LD, 2027, "January/February"): {
        "status": "Potential",
        "options": [
            "Resolved: The use of artificial intelligence for offensive military operations is immoral.",
            "Resolved: The United States ought to substantially increase subsidies for renewable energy.",
        ],
    },
    (LD, 2027, "March/April"): {
        "status": "Potential",
        "options": [
            "Resolved: The United States ought to provide a universal basic income.",
            "Resolved: In a democracy, a candidate for public office's right to privacy ought to be valued above the public's right to know.",
        ],
    },
    # ----- CONGRESS (NSDA posts a sample docket on the 1st of each month) -----
    (CONG, 2026, "September"): {
        "status": "Official",
        "options": ["Sample docket of bills and resolutions for September 2026."],
        "link": "https://www.speechanddebate.org/congress-legislation-2026-september/",
        "link_label": "Open the September 2026 docket on speechanddebate.org",
    },
    (CONG, 2026, "October"): {
        "status": "Official",
        "options": ["Sample docket of bills and resolutions for October 2026."],
        "link": "https://www.speechanddebate.org/congress-legislation-2026-october/",
        "link_label": "Open the October 2026 docket on speechanddebate.org",
    },
}

# ---------------------------------------------------------------------------
# 2. SELECTORS
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    format_choice = st.selectbox("Debate format", [PF, LD, CONG])

with col2:
    years = sorted({k[1] for k in TOPICS if k[0] == format_choice}, reverse=True)
    default_year = years.index(2026) if 2026 in years else 0
    year_choice = st.selectbox("Year", years, index=default_year)

with col3:
    periods = [k[2] for k in TOPICS if k[0] == format_choice and k[1] == year_choice]
    period_choice = st.selectbox("Topic window", periods)

info = TOPICS[(format_choice, year_choice, period_choice)]
label = "Docket" if format_choice == CONG else "Resolution"

if info["status"] == "Official":
    st.info(f"**{label} ({period_choice} {year_choice}):** {info['options'][0]}")
else:
    st.warning(
        f"**Potential topics for {period_choice} {year_choice}.** "
        "The NSDA picks the final one by vote shortly before the window starts."
    )
    for opt in info["options"]:
        st.markdown(f"- {opt}")

if info.get("link"):
    st.markdown(f"📘 [{info.get('link_label', 'Official NSDA page')}]({info['link']})")

st.caption("Topics from speechanddebate.org/topics. Always confirm there before a tournament.")


def side_label(side):
    if format_choice == LD:
        return "Affirmative" if side == "Pro" else "Negative"
    return "Pro" if side == "Pro" else "Con"


query = st.text_input(
    "Keyword or argument (e.g. deterrence, economy, environment). Leave blank to search the whole topic:"
).strip()

# ---------------------------------------------------------------------------
# 3. FIND EVIDENCE ONLINE (live web search)
# ---------------------------------------------------------------------------
TRUSTED_DOMAINS = (
    "rand.org", "brookings.edu", "cfr.org", "csis.org", "carnegieendowment.org",
    "piie.com", "nber.org", "pewresearch.org", "jstor.org", "nature.com",
    "sciencedirect.com", "reuters.com", "apnews.com", "un.org", "worldbank.org",
    "imf.org", "oecd.org", "iea.org",
)

# Each side searches from several angles so neither side gets "lost".
# "Answers the other side" finds evidence that responds to the opposing
# team's best arguments, which is often what the keyword needs.
ANGLES = {
    "Pro": [
        ("Direct support", "{kw} {topic} benefits evidence study"),
        ("Case made by supporters", "why {topic} {kw} case for supporters argue"),
        ("Answers the other side", "{kw} {topic} critics wrong flawed overstated response"),
        ("Expert analysis", "{kw} {topic} policy analysis in favor"),
    ],
    "Con": [
        ("Direct support", "{kw} {topic} risks harms evidence study"),
        ("Case made by opponents", "why not {topic} {kw} case against opponents argue"),
        ("Answers the other side", "{kw} {topic} supporters wrong flawed overstated response"),
        ("Expert analysis", "{kw} {topic} policy analysis opposed"),
    ],
}


def get_api_key():
    try:
        return st.secrets["TAVILY_API_KEY"]
    except Exception:
        return os.environ.get("TAVILY_API_KEY", "")


def is_trusted(url):
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host.endswith((".gov", ".edu")) or any(
        host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS
    )


@st.cache_data(ttl=3600, show_spinner=False)
def web_search(q, key, depth):
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {key}"},
        json={"query": q, "search_depth": depth, "max_results": 5},
        timeout=45,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def gather(side, kw, topic, key, depth):
    """Run every angle for one side and merge results by URL."""
    found = {}
    errors = []
    for angle, template in ANGLES[side]:
        q = " ".join(template.format(kw=kw, topic=topic).split())
        try:
            results = web_search(q, key, depth)
        except Exception as e:
            errors.append(str(e))
            continue
        for r in results:
            url = r["url"]
            if url in found:
                found[url]["hits"] += 1
                found[url]["score"] = max(found[url]["score"], r.get("score", 0))
            else:
                found[url] = {
                    "title": r.get("title", url),
                    "url": url,
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                    "angle": angle,
                    "hits": 1,
                }
    for item in found.values():
        item["final"] = (
            item["score"]
            + (0.25 if is_trusted(item["url"]) else 0)
            + 0.05 * (item["hits"] - 1)
        )
    return found, errors


def show_fallback_links(kw, topic):
    from urllib.parse import quote_plus
    trusted = "(site:gov OR site:edu OR site:rand.org OR site:brookings.edu OR site:cfr.org OR site:csis.org)"
    cols = st.columns(2)
    for col, side, words in [
        (cols[0], "Pro", "benefits advantages support"),
        (cols[1], "Con", "harms risks disadvantages criticism"),
    ]:
        q = " ".join(f"{kw} {topic} {words}".split())
        with col:
            st.markdown(f"### {side_label(side)}")
            st.markdown(f"- [Google Scholar (studies)](https://scholar.google.com/scholar?q={quote_plus(q)})")
            st.markdown(f"- [Government, university and think-tank sites](https://www.google.com/search?q={quote_plus(q + ' ' + trusted)})")
            st.markdown(f"- [Recent news](https://www.google.com/search?q={quote_plus(q)}&tbm=nws)")
st.markdown("---")
st.subheader("Find evidence online")
api_key = get_api_key()

if not api_key:
    st.info("Live search is unavailable right now. Use these search links instead.")
    show_fallback_links(
        query,
        "" if format_choice == CONG else info["options"][0].replace("Resolved:", "").strip().rstrip("."),
    )
else:
    topic_text = info["options"][0]
    if len(info["options"]) > 1:
        topic_text = st.radio("Which potential topic do you want to research?", info["options"])

    deep = st.checkbox("Deep search (better results, uses more of your Tavily allowance)")
    button_text = f'Find evidence for "{query}"' if query else "Find evidence for this topic"

    if st.button(button_text):
        topic_core = "" if format_choice == CONG else topic_text.replace("Resolved:", "").strip().rstrip(".")
        depth = "advanced" if deep else "basic"

        with st.spinner("Searching both sides..."):
            pro_found, pro_err = gather("Pro", query, topic_core, api_key, depth)
            con_found, con_err = gather("Con", query, topic_core, api_key, depth)

        # If a page matched both sides, keep it only where it scored higher.
        for url in set(pro_found) & set(con_found):
            if pro_found[url]["final"] >= con_found[url]["final"]:
                del con_found[url]
            else:
                del pro_found[url]

        cols = st.columns(2)
        for col, side, found, errs in [
            (cols[0], "Pro", pro_found, pro_err),
            (cols[1], "Con", con_found, con_err),
        ]:
            with col:
                st.markdown(f"### {side_label(side)}")
                if errs:
                    st.error(f"Some searches failed: {errs[0]}")
                top = sorted(found.values(), key=lambda r: r["final"], reverse=True)[:6]
                if not top:
                    st.warning("No results found.")
                for r in top:
                    with st.container(border=True):
                        tag = "🏛️ gov / edu / research source" if is_trusted(r["url"]) else "🌐 general web"
                        st.markdown(f"**[{r['title']}]({r['url']})**")
                        st.caption(f"{r['angle']}  |  {urlparse(r['url']).netloc}  |  {tag}")
                        st.write(r["content"])
        if (pro_err or con_err) and not (pro_found or con_found):
            st.warning("Live search failed, so here are search links instead.")
            show_fallback_links(query, topic_core)
        st.caption("Excerpts only. Open each link and verify the quote before using it as a card.")
