#!/usr/bin/env python3
"""Fetch the (few) texts of Saint Vincent and the Grenadines legislation that
are published on official government websites, and convert them to Markdown.

No official online edition of the Revised Laws of Saint Vincent and the
Grenadines exists (see README). This script collects:
  * PDFs currently online at www.gov.vc ("Policies, Acts and Bills") and
    assembly.gov.vc (House of Assembly);
  * PDFs formerly published at www.gov.vc/govt/Files/ (the old portal is
    offline; the Internet Archive fallback is tried, but none were archived);
  * the Constitution Order 1979 from the Organization of American States
    (non-official mirror), because the only official copies found (the
    old gov.vc file and the legislation.gov.uk PDF of S.I. 1979/916) are
    unavailable or scanned images.
For each document the live URL is tried first, then the archived copy.
Usage: vc_fetch.py
"""
import datetime
import json
import os
import subprocess
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vc_pdf2md  # noqa: E402

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "vc"))
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TODAY = datetime.date.today().isoformat()
WB = "https://web.archive.org/web/2020id_/"

# (original official URL, output path, title, type, identifier, status)
DOCS = [
    ("https://oas.org/ext/Portals/33/Files/Member-States/Stvinc_intro_fundtxt_eng.doc.pdf", "constitution/saint-vincent-constitution-order-1979.md",
     "The Saint Vincent Constitution Order 1979", "constitution", "S.I. 1979 No. 916", "in_force"),
    ("https://www.gov.vc/images/PoliciesActsAndBills/SVG_Freedom_of_Information_Act_2003.pdf",
     "acts/2003/freedom-of-information-act-2003.md", "Freedom of Information Act, 2003", "act", "", "in_force"),
    ("http://www.gov.vc/govt/Files/Copyright%20Act%202003.pdf", "acts/2003/copyright-act-2003.md",
     "Copyright Act, 2003", "act", "", "in_force"),
    ("http://www.gov.vc/govt/files/TM%20Act%202003.pdf", "acts/2003/trade-marks-act-2003.md",
     "Trade Marks Act, 2003", "act", "", "in_force"),
    ("http://www.gov.vc/govt/files/Geographical%20Indications%20Act,%202004.pdf",
     "acts/2004/geographical-indications-act-2004.md", "Geographical Indications Act, 2004", "act", "", "in_force"),
    ("http://www.gov.vc/govt/Files/EducationAct2005.pdf", "acts/2005/education-act-2005.md",
     "Education Act, 2005", "act", "", "in_force"),
    ("http://www.gov.vc/govt/Files/4222-National%20Emergency%20Act.pdf", "acts/national-emergency-act.md",
     "National Emergency Act", "act", "", "unknown"),
    ("http://www.gov.vc/govt/Files/Electronic_Transactions_Act,_2007.pdf", "acts/2007/electronic-transactions-act-2007.md",
     "Electronic Transactions Act, 2007", "act", "", "unknown"),
    ("http://www.gov.vc/govt/Files/Infor%20and%20comm%20tech%20services%20Invest%20Incent%20Act%202007.pdf",
     "acts/2007/information-and-communications-technology-services-investment-incentives-act-2007.md",
     "Information and Communications Technology Services Investment Incentives Act, 2007", "act", "", "in_force"),
    ("http://www.gov.vc/govt/Files/Small%20Business%20Development%20Act,%202007.pdf",
     "acts/2007/small-business-development-act-2007.md", "Small Business Development Act, 2007", "act", "", "in_force"),
    ("https://www.gov.vc/images/PoliciesActsAndBills/SVG_Electronic_Transactions_Act_2015.pdf",
     "acts/2015/electronic-transactions-act-2015.md", "Electronic Transactions Act, 2015", "act", "", "in_force"),
    ("https://www.gov.vc/images/PoliciesActsAndBills/SVG_Cybercrime_Act_2016.pdf",
     "acts/2016/cybercrime-act-2016.md", "Cybercrime Act, 2016", "act", "", "in_force"),
    ("https://www.gov.vc/images/PoliciesActsAndBills/The_Permitted_Use_of_Cannabis_for_Religious_Purposes_Act_ACT_of-2018.pdf",
     "acts/2018/permitted-use-of-cannabis-for-religious-purposes-act-2018.md",
     "Permitted Use of Cannabis for Religious Purposes Act, 2018", "act", "", "in_force"),
    ("https://assembly.gov.vc/assembly/images/ActsBillsPolicies/child_justice_act_2019.pdf",
     "acts/2019/child-justice-act-2019.md", "Child Justice Act, 2019", "act", "", "in_force"),
    ("https://www.gov.vc/images/PoliciesActsAndBills/Public-Order-Act.pdf", "acts/public-order-act.md",
     "Public Order Act", "act", "", "in_force"),
]


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fetch(s, url, path):
    """Try live URL, then Wayback. Returns the URL actually used or None."""
    for u in (url, WB + url):
        for i in range(3):
            try:
                r = s.get(u, timeout=300)
                if r.status_code == 200 and r.content[:5] == b"%PDF-":
                    open(path, "wb").write(r.content)
                    if pdf_ok(path):
                        return u
                if r.status_code in (404, 410):
                    break
            except requests.RequestException as e:
                print("retry", u, e, file=sys.stderr)
            time.sleep(5 * (i + 1))
        time.sleep(2)
    return None


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    meta_p = os.path.join(RAW, "used.json")
    used = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    gaps = []
    for url, rel, title, typ, ident, status in DOCS:
        p = os.path.join(RAW, "pdf", os.path.basename(rel)[:-3] + ".pdf")
        if not pdf_ok(p):
            got = fetch(s, url, p)
            if not got:
                gaps.append((title, url, "not retrievable"))
                continue
            used[url] = got
            json.dump(used, open(meta_p, "w"), indent=1)
        pages = vc_pdf2md.pages_of(p)
        if vc_pdf2md.is_scan(pages):
            gaps.append((title, url, "scanned PDF"))
            continue
        fm = ["---", "title: " + yq(title)]
        if ident:
            fm.append("identifier: " + yq(ident))
        fm += ["type: " + typ, "jurisdiction: vc", "language: en", "status: " + status, "source: " + yq(url)]
        if used.get(url, url) != url:
            fm.append("archived_copy: " + yq(used[url].replace("2020id_", "2020")))
        if "oas.org" in url:
            fm.append('note: "Non-official transcription published by the Organization of American States; '
                      'may contain typing errors. Official print: S.I. 1979 No. 916 (scan only at '
                      'https://www.legislation.gov.uk/uksi/1979/916/contents/made)."')
        fm += ["retrieved: " + TODAY, "---"]
        out = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write("\n".join(fm) + "\n\n# " + title + "\n\n" + vc_pdf2md.convert(pages))
        print("ok", rel, len(pages))
    print("gaps:", gaps)
    json.dump(gaps, open(os.path.join(RAW, "gaps.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
