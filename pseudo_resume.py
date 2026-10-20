"""Structured data behind the /pseudo_resume page.

The prose version of all of this lives in `articles/Pseudo Resume.md`, and the
research projects and talks come from `templates/research.html`. This module
holds the same information as dated records so the page can place everything
on a timeline, filter it by category, sort it, and search it.

Nothing here is user input, so the detail strings may contain markup; the page
inserts them as HTML. Titles and summaries are plain text.

Dates
-----
Every date is a string in one of these shapes, optionally prefixed with "~" to
mark it as approximate (the page shows it as "c. ..." and fades the bar edge):

    "2024"          a whole year
    "2024-09"       a month
    "2024-fall"     a season: winter, spring, summer, fall

An entry is placed in time in one of three ways:

    "start" / "end"     a span; leave out "end" for something still going
    "dates"             one or more one-off occurrences (a conference each April)
    "label"             no dates at all, just a phrase to show instead
"""

import datetime
import html
import re

# Category order here is the order the filter chips and the grouping use. An
# entry's first category is its primary one: it sets the colour of its bar.
CATEGORIES = [
    {"id": "cyber", "label": "Cybersecurity"},
    {"id": "research", "label": "Research"},
    {"id": "leadership", "label": "Leadership"},
    {"id": "competition", "label": "Competition"},
    {"id": "work", "label": "Work"},
    {"id": "talks", "label": "Talks & events"},
    {"id": "academics", "label": "Academics"},
    {"id": "personal", "label": "Personal"},
]

# Named stretches of time offered as one-click zoom presets on the timeline.
ERAS = [
    {"label": "High school", "start": "2021-fall", "end": "2023-summer"},
    {"label": "College", "start": "2023-fall"},
]

# Headline numbers. Clicking one either opens an entry or filters to a category.
STATS = [
    {"value": "1st", "label": "of 71 teams at Cyphercon 2025", "entry": "cyphercon"},
    {"value": "Top 30", "label": "of 500+ in the NIST ARIA red team", "entry": "aria"},
    {"value": "85", "label": "machines I help administer", "entry": "hpc"},
    {"value": "$1.2M", "label": "campus IT budget I vote on", "entry": "itc"},
    {"value": "1,000+", "label": "delegates faced at ChoMUN", "entry": "model-un"},
    {"value": "{research}", "label": "research projects", "cat": "research"},
    {"value": "{martial}+", "label": "years of martial arts", "entry": "martial-arts"},
]

ENTRIES = [
    # --- Undated: things that are true all the time -------------------------
    {
        "id": "focus",
        "label": "The through-line",
        "title": "Threat intelligence and influence warfare",
        "cats": ["cyber", "research"],
        "summary": "Learning everything you can about the people behind the attacks.",
        "details": [
            'My specific interest is cybersecurity <b>threat intelligence</b> &mdash; learning what you '
            'can about cyber threat actors. Alongside that I work on '
            '<a href="/articles/Introduction To Influence Warfare">influence warfare</a> and '
            'disinformation.',
        ],
    },
    {
        "id": "certs",
        "label": "Accumulating",
        "title": "Cybersecurity and IT certifications",
        "cats": ["cyber", "academics"],
        "summary": "Various certificates across security and general IT.",
        "details": [
            'A comprehensive list lives on '
            '<a href="https://www.credly.com/users/jack-hagen.fc2778b2">Credly</a>.',
        ],
        "links": [{"label": "Credly profile", "url": "https://www.credly.com/users/jack-hagen.fc2778b2"}],
    },
    {
        "id": "languages",
        "label": "Since middle school",
        "title": "Chinese, Arabic, and Klingon",
        "cats": ["personal", "academics"],
        "summary": "Chinese in school since middle school; Arabic and Klingon for fun.",
        "details": [
            'I have taken <b>Chinese</b> in school since middle school and earned a Chinese certificate '
            'in college. I am also learning <b>Arabic</b> and '
            '<a href="https://en.wikipedia.org/wiki/Klingon_language"><b>Klingon</b></a>.',
        ],
    },
    {
        "id": "linux",
        "label": "Daily driver",
        "title": "Linux, every day",
        "cats": ["personal", "work"],
        "summary": "On my personal machine, my work laptop, and the clusters.",
        "details": [
            'My work laptop and the clusters both run Rocky Linux, and Linux is what I use at home too.',
        ],
    },

    # --- Long-running -------------------------------------------------------
    {
        "id": "martial-arts",
        "start": "2014",
        "title": "Martial arts",
        "cats": ["personal"],
        "summary": "Four disciplines, starting with Aikido in 2014.",
        "children": [
            '<b>Wadokai Aikido</b> since 2014.',
            '<b>Shorin Ryu Karate</b> since 2023.',
            '<b>Tai Chi</b> since 2023.',
            '<b>Shotokan Karate</b> for an honors class in Spring 2025 &mdash; I have since become '
            'treasurer of the newly formed Shotokan Karate club.',
        ],
    },
    {
        "id": "degree",
        "start": "~2023-fall",
        "title": "Computer Science & Political Science, UWEC",
        "cats": ["academics"],
        "summary": "Double major, with certificates in Chinese and Transnational Asian Studies.",
        "details": [
            'Undergraduate at the <a href="https://uwec.edu">University of Wisconsin &ndash; Eau Claire</a>, '
            'double majoring in <b>Computer Science and Political Science</b> with certificates in '
            '<b>Chinese</b> and <b>Transnational Asian Studies</b>.',
        ],
        "children": [
            'Member of the <a href="https://www.uwec.edu/academics/mark-stephen-cosby-honors-college">'
            'UWEC Honors College</a>.',
        ],
    },

    # --- Work ---------------------------------------------------------------
    {
        "id": "hpc",
        "start": "2024-04",
        "title": "Student system administrator, UWEC High Performance Computing",
        "cats": ["work", "cyber"],
        "summary": "One of a small team running two supercomputing clusters, and the team's security person.",
        "details": [
            'Hired onto the small team that manages UWEC\'s two '
            '<a href="https://hpc.uwec.edu">supercomputing clusters</a> &mdash; about <b>85 machines</b> '
            'altogether. We present to, help, and teach the few hundred students and faculty researchers '
            'who use the clusters, keep all of the many moving parts working, and make sure everything '
            'stays up to date, secure, and available.',
            'I am also the team\'s <b>&ldquo;security person&rdquo;</b>, so I am generally in charge of '
            'most security-related work.',
        ],
        "links": [{"label": "hpc.uwec.edu", "url": "https://hpc.uwec.edu"}],
    },
    {
        "id": "police",
        "dates": ["2024"],
        "title": "Demoed physical attacks for campus police training",
        "cats": ["cyber", "work"],
        "summary": "Asked by UWEC's CISO to help train the campus police department.",
        "details": [
            'I helped demo physical cyber attacks during a training for our campus police department, '
            'and I work with our Chief Information Security Officer on various other projects.',
        ],
    },
    {
        "id": "tech-intern",
        "start": "~2021-fall",
        "end": "~2023-summer",
        "title": "Tech intern and summer IT intern",
        "cats": ["work", "cyber"],
        "summary": "Ran a helpdesk for staff and students; summers with the district IT department.",
        "details": [
            'Junior and senior year of high school I was a &ldquo;tech intern&rdquo;, part of the group '
            'that operated a helpdesk for staff and students. Over the summers I interned with the IT '
            'department: upgrading systems, managing the hundreds of Chromebooks and iPads the district '
            'owned, and checking the AV technology in every classroom across the 10-school district.',
        ],
    },

    # --- Leadership ---------------------------------------------------------
    {
        "id": "cyber-club",
        "start": "2024-fall",
        "title": "Founder and president, UWEC Cybersecurity Club",
        "cats": ["leadership", "cyber"],
        "summary": "Built the tools, the competitive team, and the weekly curriculum out of nothing.",
        "details": [
            'I built numerous technical tools and a competitive cybersecurity team. I teach the concept '
            'each week, lead hands-on activities, program and work on a lot of '
            '<a href="https://github.com/Blugold-Group">projects</a>, and generally push to create an '
            'engaging, educational, and accepting environment out of nothing.',
            'Worth noting: nothing I teach or use in the club came from my normal CS program. I learned '
            'all of it on my own in my free time.',
        ],
        "links": [{"label": "Blugold Group on GitHub", "url": "https://github.com/Blugold-Group"}],
    },
    {
        "id": "model-un",
        "start": "2024-fall",
        "title": "Founder and president, UWEC Model United Nations",
        "cats": ["leadership", "competition"],
        "summary": "Founded the club and led the competitive team against 1,000+ delegates.",
        "details": [
            'I planned Model UN\'s trip to the <a href="https://www.chomun.org/">ChoMUN</a> conference '
            'and led our competitive team, working in the on-the-fly secretariat\'s committee. We '
            'competed against over <b>1,000 delegates</b> from across the country, including Harvard, '
            'Johns Hopkins, Stanford, Purdue, Yale, Berkeley, and Georgetown.',
        ],
        "children": [
            'April 2025: ChoMUN in Chicago.',
            'April 2026: back at ChoMUN.',
        ],
    },
    {
        "id": "acm",
        "start": "~2024-winter",
        "title": "President, Student Association for Computing Machinery",
        "cats": ["leadership", "academics"],
        "summary": "Running our student ACM chapter's weekly activities.",
        "details": [
            'I organize our activities each week and work to create opportunities for students in the '
            'department.',
        ],
    },
    {
        "id": "itc",
        "start": "~2024-winter",
        "title": "Director, Student Senate Information Technology Commission",
        "cats": ["leadership", "academics"],
        "summary": "Voting member of student senate; annually approves the $1.2M campus IT budget.",
        "details": [
            'The <b>Information Technology Commission</b> advises the senate on IT needs, annually '
            'approves the <b>$1.2 million</b> UWEC IT budget, and works to improve campus IT based on '
            'student needs. As director I am a voting member of student senate.',
        ],
        "children": [
            'Winter 2024: joined the commission as a member.',
            'Spring 2025: voted in as director.',
        ],
    },
    {
        "id": "cssag",
        "start": "2025-spring",
        "title": "Founding the Computer Science Student Advisory Group",
        "cats": ["leadership", "academics"],
        "summary": "Getting students a formal voice with the CS faculty, by way of a lot of red tape.",
        "details": [
            'CSSAG aims to work with the CS professors to address student concerns and create more '
            'opportunities for students to be heard by the faculty. I have been fighting red tape and '
            'a bureaucracy &mdash; good thing I am studying political science and know how to get into a '
            'political fight.',
        ],
    },

    # --- Competitions -------------------------------------------------------
    {
        "id": "cyphercon",
        "dates": ["2024-04", "2025-04", "2026-04"],
        "title": "Cyphercon: led the team to first of 71",
        "cats": ["competition", "cyber", "leadership"],
        "summary": "Three years at Wisconsin's largest security conference: 3rd, then 1st, then 2nd.",
        "details": [
            '<a href="https://cyphercon.com/">Cyphercon</a> is Wisconsin\'s largest security conference. '
            'I go with the cybersecurity club\'s team to compete and to attend research talks.',
        ],
        "children": [
            '2024: on the team, placed <b>3rd overall</b>. I also won the Hungry Hungry Hackers '
            'competition, earning a VIP badge to the 2025 conference.',
            '2025: <b>led the team</b>. We competed against <b>71 teams</b>, <b>placed first</b>, and won '
            'a lifetime ticket to all future conferences.',
            '2026: placed <b>2nd overall</b>.',
        ],
    },
    {
        "id": "aria",
        "dates": ["2024-10"],
        "title": "NIST ARIA LLM red teaming, top 30 of 500+",
        "cats": ["competition", "cyber", "research"],
        "summary": "Broke production LLMs online, then flew to CAMLIS to do it again in person.",
        "details": [
            'An online LLM security competition run as part of the NIST <b>Assessing Risks and Impacts '
            'of AI</b> program, hosted by Humane Intelligence with support from the <b>National '
            'Institute for Standards in Technology</b>. They called for people across the nation to '
            'break production LLMs submitted by model creators.',
            'Humane Intelligence covered flights, hotel, and conference costs for the top 30 scoring '
            'participants out of more than <b>500</b>. I was one of the 30, and attended the '
            '<b>Conference on Applied Machine Learning in Information Security</b> to do a similar '
            'exercise in person, alongside research talks from Microsoft, Google, Amazon, Lockheed '
            'Martin and others.',
            'Technically it was in Arlington, Virginia, but you could see the Capitol building from the '
            'room we were red teaming in, so I call it Washington DC.',
        ],
    },
    {
        "id": "hackmit",
        "dates": ["2025-09"],
        "title": "First place in a sponsor challenge at HackMIT",
        "cats": ["competition", "cyber"],
        "summary": "Privacy-preserving, verifiable OAuth built on trusted execution environments.",
        "details": [
            'Accepted into <a href="https://hackmit.org/">HackMIT</a>, where my four-person team competed '
            'against about 1,000 other attendees and won first place in a sponsor challenge.',
            'We built a privacy-preserving, verifiable OAuth system on EigenCloud. It leverages '
            '<b>Trusted Execution Environments</b> to validate emails and other dynamic identity '
            'attributes, so anonymity is preserved even from the administrators of the service.',
        ],
        "links": [{"label": "diagonalize on GitHub",
                   "url": "https://github.com/ThisIsNotANamepng/diagonalize"}],
    },
    {
        "id": "mudac",
        "dates": ["~2024-spring", "~2025-spring"],
        "title": "Midwestern Undergraduate Data Analytics Competition",
        "cats": ["competition", "research"],
        "summary": "26 hours straight on a real client's datasets, then a presentation to judges.",
        "details": [
            'At <a href="https://www.mudac.org/">MUDAC</a> our UWEC team stayed up for 26 hours straight '
            'analyzing datasets from a real-life client to answer questions about crop optimization, '
            'then presented to judges. In <b>2025 I led our team</b>.',
        ],
    },
    {
        "id": "fbla",
        "dates": ["~2023-spring"],
        "title": "First at state, FBLA coding and programming",
        "cats": ["competition"],
        "summary": "Won the state Future Business Leaders of America competition and went to nationals.",
        "details": [
            'Senior year I won <b>first at state</b> in the Future Business Leaders of America coding and '
            'programming competition and went on to nationals in Atlanta.',
        ],
    },

    # --- Research (see templates/research.html) -----------------------------
    {
        "id": "bertini",
        "start": "2023-09",
        "end": "~2024-05",
        "title": "Making Bertini2 installable",
        "cats": ["research", "academics"],
        "summary": "Moved a polynomial system solver's build from Autotools to CMake.",
        "details": [
            'With a mathematics professor I worked on her '
            '<a href="https://github.com/bertiniteam/b2">tool for solving arbitrary polynomial '
            'systems</a>. Before our work you essentially needed an in-depth knowledge of computer '
            'systems to install it. We aimed to port it to Conda, which meant switching the build system '
            'from Autotools to CMake. We didn\'t make it to Conda, but you can now install it by cloning '
            'the repo and using <code>pip install</code>.',
            'I presented this at CERCA in April 2024.',
        ],
        "links": [{"label": "The commit",
                   "url": "https://github.com/bertiniteam/b2/commit/245ed7080ad524a1ee889547878edf7cc8f59628"}],
    },
    {
        "id": "network-ml",
        "start": "2023-09",
        "end": "2024",
        "title": "Machine learning on network traffic datasets",
        "cats": ["research", "cyber"],
        "summary": "Applying ML methods the original dataset authors overlooked.",
        "details": [
            'Part of a team that identified datasets with signatures from benign and malicious network '
            'traffic, then applied new machine learning algorithms that the original authors overlooked.',
        ],
    },
    {
        "id": "teaching-tools",
        "start": "2024-summer",
        "end": "2024-summer",
        "title": "Hands-on cybersecurity teaching tools",
        "cats": ["research", "cyber"],
        "summary": "Letter frequencies for cryptography, and attestation on a fleet of containers.",
        "details": [
            'Built tools to show cybersecurity concepts to a class hands-on: '
            '<a href="/articles/Specific Letter Frequencies">enhanced letter frequencies</a> for '
            'cryptography, and a basic system attestation tool running on a fleet of Linux containers.',
        ],
    },
    {
        "id": "phishing",
        "start": "2024-09",
        "title": "A dataset of AI-written phishing",
        "cats": ["research", "cyber"],
        "summary": "Generating phishing that beats current detectors, so the detectors can improve.",
        "details": [
            'Using various generative AI models to create a dataset of AI-written phishing emails that '
            'defeat current phishing detection techniques, to provide data for improving those systems.',
        ],
        "links": [{"label": "Research proposal (PDF)",
                   "url": "/static/PhishingGenerationResearchProposal.pdf"}],
    },
    {
        "id": "triangulation",
        "start": "2024-09",
        "title": "TriangulationNet: tracking people by their Bluetooth",
        "cats": ["research", "cyber"],
        "summary": "A campus grid of edge devices that follows the gadgets people carry.",
        "details": [
            'Inspired by the police training I helped run, I am building a grid of edge devices that '
            'uses Bluetooth triangulation of a target\'s personal devices to track them as they move '
            'through campus &mdash; to show the dangers of what we carry every day and to investigate '
            'mitigations.',
            'The first proof of concept tracks the campus food delivery KiwiBots.',
        ],
        "links": [{"label": "TriangulationNet on GitHub",
                   "url": "https://github.com/Blugold-Group/TriangulationNet"}],
    },
    {
        "id": "china-survey",
        "start": "2025-06",
        "end": "2025-12",
        "title": "Surveying Chinese students who study abroad",
        "cats": ["research", "academics"],
        "summary": "Their concerns, attitudes, and preparedness, with fieldwork in China.",
        "details": [
            'Using in-person and online surveys, researched the concerns, attitudes, and preparedness '
            'of Chinese students studying abroad in the US. I traveled to China in the summer of 2025 '
            'to run the in-person surveys.',
        ],
    },
    {
        "id": "menoa",
        "start": "2025-10",
        "title": "Detecting malware on Linux desktops",
        "cats": ["research", "cyber"],
        "summary": "ML process and log analysis, extended ClamAV definitions, binary attestation.",
        "details": [
            'Researching and building novel ways to detect malware running on a Linux desktop, '
            'including machine learning based process and log analysis, extended ClamAV definitions, '
            'and binary attestation.',
        ],
        "links": [{"label": "menoa.org", "url": "https://menoa.org/"}],
    },
    {
        "id": "ransomware",
        "start": "2026-02",
        "end": "2026-04",
        "title": "Interviewing ransomware operators",
        "cats": ["research", "cyber"],
        "summary": "How international politics and regulation shape cybercrime, asked of the criminals.",
        "details": [
            'Contacted and surveyed a number of ransomware gang operators on the effect of international '
            'politics and regulations on cybercrime operations.',
        ],
    },
    {
        "id": "table-tennis",
        "start": "2026-02",
        "end": "2026-04",
        "title": "Smartphones as table tennis paddles",
        "cats": ["research", "personal"],
        "summary": "Rigorously, with live matches.",
        "details": [
            'Systematically measured a series of smartphones in live table tennis matches to determine '
            'the most effective smartphone model for use as a table tennis paddle.',
        ],
    },
    {
        "id": "thesis",
        "start": "2026-08",
        "title": "Honors thesis: what provokes nation-state cyberwarfare",
        "cats": ["research", "cyber", "academics"],
        "summary": "Which stimuli make nation states respond with cyberattacks.",
        "details": [
            'Using <a href="https://gdeltproject.org/">GDELT project</a> data and a self-curated dataset '
            'of nation-state cyberattacks, measuring which stimuli cause nation states to respond with '
            'cyberwarfare.',
        ],
    },

    # --- Talks and events ---------------------------------------------------
    {
        "id": "cerca",
        "dates": ["2024-04"],
        "title": "Presented my freshman research at CERCA",
        "cats": ["talks", "research"],
        "summary": "Porting Bertini2, presented at UWEC's research day.",
        "details": [
            'Presented my freshman research on porting Bertini2, a solver for arbitrary polynomial '
            'systems, at CERCA in Eau Claire.',
        ],
    },
    {
        "id": "poetry",
        "dates": ["2024", "2025"],
        "title": "International poetry night readings",
        "cats": ["talks", "personal"],
        "summary": "Basho in Japanese, then Hamlet in Klingon.",
        "details": [
            'UWEC holds an annual international poetry reading night for poetry in languages other than '
            'English.',
        ],
        "children": [
            '2024: read a Matsuo Basho poem in <b>Japanese</b>.',
            '2025: read a <b>Chinese</b> poem with two other students, plus the '
            '<i>To Be Or Not To Be</i> soliloquy in <b>Klingon</b>.',
        ],
    },
    {
        "id": "china-talks",
        "dates": ["2026-03", "2026-04"],
        "title": "Presented the China study abroad research, twice",
        "cats": ["talks", "research"],
        "summary": "At AsiaNet in Chicago and at the National Conference on Undergraduate Research.",
        "children": [
            'March 2026: <b>AsiaNet</b>, Chicago.',
            'April 2026: <b>National Conference on Undergraduate Research</b>, Richmond, Virginia.',
        ],
    },
    {
        "id": "code-camp",
        "dates": ["2026-04"],
        "title": "Presented Stultus at Chippewa Valley Code Camp",
        "cats": ["talks"],
        "summary": "A search engine four of us built from scratch.",
        "details": [
            'Presented with three teammates on <a href="https://stultus.rip">Stultus</a>, a handmade '
            'search engine we built from scratch.',
        ],
        "links": [{"label": "stultus.rip", "url": "https://stultus.rip"}],
    },
    {
        "id": "secretcon",
        "dates": ["2026-04"],
        "title": "Hosted the threat intelligence village at Secretcon",
        "cats": ["talks", "cyber", "leadership"],
        "summary": "Ran the cyber threat intelligence village in Saint Paul.",
        "details": [
            'Attended research talks and hosted the <b>cyber threat intelligence village</b>.',
        ],
    },
    {
        "id": "black-sky",
        "dates": ["2026-06"],
        "title": "Black Sky Symposium tabletop exercise",
        "cats": ["talks", "work", "cyber"],
        "summary": "Simulated a cyberattack on the southeastern US with members of civil society.",
        "details": [
            'Attended in Titusville, Florida on behalf of my employer, Alerts Bar, and worked through an '
            'extended tabletop simulation of a cyberattack on the southeastern US with members of civil '
            'society.',
        ],
    },

    # --- High school --------------------------------------------------------
    {
        "id": "start-college-now",
        "start": "~2022-fall",
        "end": "~2023-spring",
        "title": "Start College Now",
        "cats": ["academics", "cyber"],
        "summary": "Technical college coursework on top of a full high school load.",
        "details": [
            'My high school paid for me to attend my local technical college &mdash; which happens to '
            'have one of the best cyber programs in the state &mdash; and take classes <b>in addition</b> '
            'to my high school coursework. I picked up skills there I would not have reached until my '
            'junior or senior year of college, if at all: Cisco Networking, Linux, Bash, Enterprise '
            'Clients, and Security 1.',
        ],
    },
]


CAT_LABEL = {c["id"]: c["label"] for c in CATEGORIES}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Season -> (first month, last month), zero-based. Winter means UWEC's January
# winterim, so it sits at the start of its year rather than straddling two.
SEASONS = {"winter": (0, 0), "spring": (1, 4), "summer": (5, 7), "fall": (8, 11)}

_DATE = re.compile(r"^(~)?(\d{4})(?:-(\d{2}|winter|spring|summer|fall))?$")
_TAG = re.compile(r"<[^>]+>")


def parse_date(text):
    """Parse a date string into months since year 0.

    Returns (first, last, label, approx): the first and last month the date
    covers (equal for a single month), how to print it, and whether it is
    approximate.
    """
    m = _DATE.match(text)
    if not m:
        raise ValueError(f"bad pseudo resume date: {text!r}")
    approx, year, part = m.group(1) is not None, int(m.group(2)), m.group(3)
    base = year * 12
    if part is None:
        first, last, label = base, base + 11, str(year)
    elif part in SEASONS:
        lo, hi = SEASONS[part]
        first, last, label = base + lo, base + hi, f"{part.capitalize()} {year}"
    else:
        month = int(part) - 1
        first, last, label = base + month, base + month, f"{MONTHS[month]} {year}"
    if approx:
        label = "c. " + label
    return first, last, label, approx


def _occurrences_label(parsed):
    labels = [p[2] for p in parsed]
    if len(labels) == 1:
        return labels[0]
    # "Apr 2024, 2025, 2026" reads better than repeating the month each time.
    heads = {l.rsplit(" ", 1)[0] for l in labels if " " in l}
    if len(heads) == 1 and all(" " in l for l in labels):
        head = heads.pop()
        return head + " " + ", ".join(l.rsplit(" ", 1)[1] for l in labels)
    return ", ".join(labels)


def plain(fragment):
    """Strip markup and entities from a detail string."""
    return " ".join(html.unescape(_TAG.sub(" ", fragment)).split())


def _client_entry(e):
    """One entry, reshaped for the page script."""
    out = {
        "id": e["id"],
        "title": e["title"],
        "cats": e["cats"],
        "summary": e.get("summary", ""),
        "details": e.get("details", []),
        "children": e.get("children", []),
        "links": e.get("links", []),
        "start": None,
        "end": None,
        "ongoing": False,
        "points": None,
        "approxStart": False,
        "approxEnd": False,
    }

    if "dates" in e:
        parsed = [parse_date(d) for d in e["dates"]]
        out["points"] = [[p[0], p[1]] for p in parsed]
        out["start"], out["end"] = parsed[0][0], parsed[-1][1]
        out["approxStart"] = out["approxEnd"] = any(p[3] for p in parsed)
        out["period"] = _occurrences_label(parsed)
    elif "start" in e:
        first, _, start_label, approx = parse_date(e["start"])
        out["start"], out["approxStart"] = first, approx
        if "end" in e:
            _, last, end_label, approx_end = parse_date(e["end"])
            out["end"], out["approxEnd"] = last, approx_end
            out["period"] = start_label if start_label == end_label else f"{start_label} – {end_label}"
        else:
            out["ongoing"] = True
            out["period"] = f"{start_label} – present"
    else:
        out["period"] = e["label"]

    body = [out["summary"]] + [plain(d) for d in out["details"] + out["children"]]
    out["body"] = " ".join(b for b in body if b)
    out["text"] = " ".join(
        [e["title"], out["period"], out["body"]] + [CAT_LABEL[c] for c in e["cats"]]
    ).lower()
    return out


def _stats():
    research = sum(1 for e in ENTRIES if e["cats"][0] == "research")
    martial = datetime.date.today().year - 2014
    out = []
    for s in STATS:
        s = dict(s)
        s["value"] = s["value"].format(research=research, martial=martial)
        out.append(s)
    return out


def page_data():
    """Everything the /pseudo_resume template needs."""
    entries = [_client_entry(e) for e in ENTRIES]
    eras = []
    for era in ERAS:
        eras.append({
            "label": era["label"],
            "start": parse_date(era["start"])[0],
            "end": parse_date(era["end"])[1] if "end" in era else None,
        })
    # Newest first for the no-script fallback list.
    fallback = sorted(entries, key=lambda e: (e["start"] is None, -(e["end"] or 10**6)))
    return {
        "categories": CATEGORIES,
        "cat_label": CAT_LABEL,
        "stats": _stats(),
        "fallback": fallback,
        "client": {
            "categories": CATEGORIES,
            "eras": eras,
            "entries": entries,
        },
    }
