# Saint Vincent and the Grenadines — LawCodex

Legislation of Saint Vincent and the Grenadines as plain Markdown. Part of
[LawCodex](https://github.com/LawCodex).

**Status: minimal.** No official online edition of the Revised Laws of Saint Vincent and the
Grenadines (Revised Edition 2009, about 400 chapters) could be found. This repo has the
Constitution and the handful of Acts that government websites publish as text PDFs.

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | The Saint Vincent Constitution Order 1979 (S.I. 1979 No. 916), with the Constitution in Schedule 1 | 1 |
| `acts/<year>/` | Education Act 2005; Information and Communications Technology Services Investment Incentives Act 2007; Small Business Development Act 2007; Permitted Use of Cannabis for Religious Purposes Act 2018; Child Justice Act 2019; Public Order Act | 6 |

### Sources

- Government of Saint Vincent and the Grenadines portal, "Policies, Acts and Bills":
  https://www.gov.vc/images/PoliciesActsAndBills/
- House of Assembly: https://assembly.gov.vc/assembly/images/ActsBillsPolicies/
- Former government portal files (`http://www.gov.vc/govt/Files/...`), which still respond.
- **Constitution:** the only official copies found are a scanned image of S.I. 1979/916 on
  [legislation.gov.uk](https://www.legislation.gov.uk/uksi/1979/916/contents/made), with no
  text layer, and a `1979_Constitution.pdf` once linked on gov.vc, which is now 404 and was never
  archived. The text here is therefore taken from the transcription published by the
  **Organization of American States**
  (https://oas.org/ext/Portals/33/Files/Member-States/Stvinc_intro_fundtxt_eng.doc.pdf). That is a
  reputable but **non-official** mirror and contains some typing errors. It does not include
  later amendments.

Every file's `source` field gives the URL it was taken from.

## What is not covered (gaps)

- **Revised Laws of Saint Vincent and the Grenadines** (all chapters) and annual Acts. The
  House of Assembly publishes only yearly *lists* of Acts
  (e.g. https://assembly.gov.vc/assembly/images/Acts/Acts%202024.pdf). The Attorney General's
  Chambers / Legal Affairs site (https://legal.gov.vc/legal/) publishes Gazettes but not Act
  texts. The revised laws are otherwise available only through commercial services.
- These scanned PDFs have no text layer and were not OCR'd: Freedom of Information Act 2003,
  Electronic Transactions Act 2015 and Cybercrime Act 2016, all on gov.vc.
- These files were once linked on the old gov.vc portal but are now 404 and were not captured
  by the Internet Archive: Copyright Act 2003, Trade Marks Act 2003, Geographical Indications
  Act 2004, National Emergency Act, and Electronic Transactions Act 2007.
- No subsidiary legislation (S.R.O.s) is included.

## Format

One Markdown file per law with YAML front matter (`title`, `identifier`, `type`,
`jurisdiction`, `language`, `status`, `source`, `retrieved`). Text was extracted from the PDFs
with `pdftotext` (no OCR) and kept as extracted. Running page headers and page numbers were
removed. PART/CHAPTER/SCHEDULE lines and section numbers became headings.

## Licence / copyright

These are official legislative texts of Saint Vincent and the Grenadines, published by the
Government for public access. This is not an official publication.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils
python3 scripts/vc_fetch.py               # caches PDFs in ../_raw/vc/pdf, writes Markdown
```

Retrieved: 2026-10-13.
