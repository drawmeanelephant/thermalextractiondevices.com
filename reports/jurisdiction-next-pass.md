# P03 jurisdiction current-law verification

Audit date: 2026-08-09
Dispatch source SHA: `a4cfbc9a801778253f0660beabbcda0b8d966690`
Scope: 74 legal jurisdiction profiles (`TJUR-0001` through `TJUR-0074`), their source ledger, and the separate Massachusetts data-landscape record (`TJUR-0075`) only as a non-jurisdiction exclusion.

This pass read the governance files, the jurisdiction coverage matrix, all 74 profile records, the existing jurisdiction-source ledger, and nearby jurisdiction records. It then checked current regulator, statute, regulation, Commonwealth Register, Federal Register, and official dataset pages where available. Existing retrieval dates were retained; only newly used evidence was added to the ledger with retrieval date `2026-08-09`. A source being official does not by itself prove that every claim in a profile is current, so this report distinguishes a verified core framework from unresolved detail.

## Severity summary

### Corrected current-law discrepancies

These were changed in the profile records during P03.

| Profile | Finding and disposition | Evidence retrieved 2026-08-09 |
| --- | --- | --- |
| `TJUR-0002` Alabama | The profile now records the first dispensary opening as June 4, 2026, rather than only describing an expected summer opening. | [AMCC dispensary status FAQ](https://amcc.alabama.gov/faq/what-is-the-status-of-medical-cannabis-dispensaries-in-alabama/) |
| `TJUR-0012` Hawaii | Removed the misleading “329-card holders” wording. DOH reports 28,849 valid in-state patients as of May 31, 2026; “329” is the statutory program/card reference. | [Hawaii DOH program statistics](https://health.hawaii.gov/medicalcannabisregistry/submenu/program-statistics/) |
| `TJUR-0031` New Jersey | Corrected home cultivation from permitted to not permitted. The CRC’s current FAQ does not authorize individuals to grow cannabis. | [NJ-CRC Commission FAQ](https://www.nj.gov/cannabis/resources/faqs/commission/) |
| `TJUR-0037` Oklahoma | Corrected the commercial-license moratorium from August 1, 2026 to August 1, 2028, subject to OMMA’s pending-review exception. The former date is superseded, not current. | [OMMA application/moratorium page](https://oklahoma.gov/omma/apply.html); [HB 3143 official bill record](https://www.oklegislature.gov/BillInfo.aspx?Bill=hb3143&Session=2600) |
| `TJUR-0047` Virginia | Corrected current possession to 2 oz; retail is still not operational, with CCA’s current schedule targeting initial licenses by May 1, 2027 and retail sales from July 1, 2027. The August 15, 2026 hemp limit remains enacted-but-not-effective on the audit date. | [CCA laws](https://cca.virginia.gov/laws); [CCA retail market schedule](https://cca.virginia.gov/retailmarijuanamarket); [Code of Virginia, Title 4.1, Chapter 11](https://law.lis.virginia.gov/vacodefull/title4.1/chapter11/); [CCA hemp information](https://cca.virginia.gov/hempinformation) |
| `TJUR-0074` U.S. federal | Corrected the Federal Register citation and scope. The effective final rule is 91 FR 22714 / document `2026-08176`; document `2026-08177` is a hearing notice for the broader NPRM, not a final marijuana-rescheduling rule. | [DEA rescheduling actions](https://www.dea.gov/marijuana-rescheduling-regulatory-actions); [91 FR 22714 final rule](https://www.federalregister.gov/documents/2026/04/28/2026-08176/schedules-of-controlled-substances-rescheduling-of-food-and-drug-administration-approved-products); [91 FR 22777 hearing notice](https://www.federalregister.gov/documents/2026/04/28/2026-08177/schedules-of-controlled-substances-rescheduling-of-marijuana) |

### Enacted but not effective on 2026-08-09

- Virginia’s hemp product limit is effective August 15, 2026; the profile now labels it future law rather than current law.
- Federal hemp changes to total THC and the final-form product cap are effective November 12, 2026. The profile keeps the current federal hemp rule separate from that future rule.
- Virginia’s retail implementation dates are future schedule points, not present commercial operation: CCA regulations by February 1, 2027, initial licenses by May 1, 2027, and retail sales from July 1, 2027.
- Georgia’s SB 220 is recorded in the existing ledger as effective July 1, 2026; the profile treats the medical expansion as current and adult use as prohibited.

### Proposed, pending, or procedurally unresolved

- The broader federal rescheduling NPRM remained a hearing/proceeding question in the evidence reviewed; no final disposition was located.
- U.S. Virgin Islands adult-use implementation material is not treated as final market operation: the accessible 2024 rules document is explicitly proposed, while the regulator site was not reliably retrievable.
- South Africa’s February 2026 Cannabis for Private Purposes Act regulations are draft regulations, not current final commercial-market law.
- Any New Jersey home-grow proposal remains a proposal; it does not override the CRC’s current no-home-grow position.
- Other profile-specific bills, rule packages, and implementation claims called out in the disposition table remain follow-up items where the source ledger is generic, secondary, or not line-level authoritative.

### Superseded or repealed material

- Oklahoma’s August 1, 2026 moratorium end date is superseded by HB 3143’s August 1, 2028 extension, subject to the OMMA exception. It was corrected in place.
- No other profile claim was affirmatively classified as repealed during this pass. Where a source was a bill, draft rule, proposed rule, or hearing notice, it was not promoted to current law.

### Unknown or not established by available evidence

The following are intentionally not guessed: American Samoa’s cannabis-specific framework; Puerto Rico’s current regulator/details beyond the general medical-program source; the U.S. Virgin Islands’ current market and home-cultivation operation; CNMI commercial operation; Portugal’s claimed 30%+ operator-status change and new 2026 reporting rule; Germany’s association-count estimates; and the current implementation/detail claims flagged for Indiana, Kansas, Louisiana, Nebraska, North Carolina, Ohio, Rhode Island, South Carolina, Tennessee, Texas, Vermont, Wyoming, Czechia, Spain, Australia subnational claims, Thailand, Mexico, and Colombia.

## Disposition of every legal profile

“Core corroborated” means the main program/prohibition statement was consistent with the identified regulator/statute source. It does not certify every numerical, subnational, data-surface, or 2026-change detail. For these rows, the exact source URL and original retrieval date remain in `metadata/jurisdiction-sources.jsonl`; dates were not bulk-refreshed.

| ID | Jurisdiction | Disposition | P03 action or remaining gap |
| --- | --- | --- | --- |
| `TJUR-0001` | California | Core corroborated | DCC source retained; current detail review remains bounded by the ledger’s 2026-08-04 retrieval. |
| `TJUR-0002` | Alabama | Corrected | AMCC first-opening date corrected to June 4, 2026; data-surface limitations remain. |
| `TJUR-0003` | Alaska | Core corroborated | AMCO and 3 AAC 306 sources retained; no verified contradiction found. |
| `TJUR-0004` | Arizona | Core corroborated | ADHS source retained; monthly PDF/data-detail claims were not reinterpreted as law. |
| `TJUR-0005` | Arkansas | Core corroborated | ADH and Medical Marijuana Commission sources retained; no verified contradiction found. |
| `TJUR-0006` | Colorado | Core corroborated | MED and Colorado open-data sources retained; no public per-batch chemistry claim remains bounded. |
| `TJUR-0007` | Connecticut | Core corroborated | DCP and data.ct.gov sources retained; product-registry/data claims remain source-bounded. |
| `TJUR-0008` | Delaware | Core corroborated | OMC source and the state’s August 1, 2025 sales announcement support current adult-use sales and prohibited home cultivation. |
| `TJUR-0009` | District of Columbia | Core corroborated | ABCA source retained; federal appropriations constraint remains a separate legal condition. |
| `TJUR-0010` | Florida | Core corroborated | OMMU source retained; adult-use status remains not enacted in the profile. |
| `TJUR-0011` | Georgia | Core corroborated | GMCC and SB 220 source retained; July 1, 2026 medical expansion is treated as effective, adult use remains prohibited. |
| `TJUR-0012` | Hawaii | Corrected | Patient-count/card wording corrected using DOH’s May 31, 2026 statistics. |
| `TJUR-0013` | Idaho | Material detail gap | Core prohibition is supported by the ODP page; any 2026 ballot/policy detail needs a direct current election or statute source. |
| `TJUR-0014` | Illinois | Core corroborated | IDFPR source retained; no verified contradiction found. |
| `TJUR-0015` | Indiana | Material source gap | The ledger relies on a secondary BillTrack50 entry for HB 1285; an official bill/statute record is required before treating its July 1, 2026 THC rules as verified. |
| `TJUR-0016` | Iowa | Core corroborated | Iowa HHS source retained; no verified contradiction found. |
| `TJUR-0017` | Kansas | Material source gap | The ledger’s generic Kansas portal is not a cannabis statute/regulator source; no stronger cannabis-specific current source was located in this pass. |
| `TJUR-0018` | Kentucky | Core corroborated | Kentucky Office of Medical Cannabis source retained; no verified contradiction found. |
| `TJUR-0019` | Louisiana | Material detail gap | LDH supports the medical program; the profile’s 2026 recriminalization/HB 373 detail needs a direct enrolled-act or official legislative source. |
| `TJUR-0020` | Maine | Core corroborated | OCP and adult-use data sources retained; no verified contradiction found. |
| `TJUR-0021` | Maryland | Core corroborated | MCA source retained; no verified contradiction found. |
| `TJUR-0022` | Massachusetts | Core corroborated | CCC and open-data sources retained; current market/data claims remain bounded by their listed retrieval dates. |
| `TJUR-0023` | Michigan | Core corroborated | CRA source retained; no verified contradiction found. |
| `TJUR-0024` | Minnesota | Core corroborated | OCM source retained; the 2026 retail ramp is treated as implementation status, not a completed market. |
| `TJUR-0025` | Mississippi | Core corroborated | MSDH source retained; no verified contradiction found. |
| `TJUR-0026` | Missouri | Core corroborated | DHSS source retained; no verified contradiction found. |
| `TJUR-0027` | Montana | Core corroborated | DOR source retained; sales/recall availability is not treated as a legal status claim. |
| `TJUR-0028` | Nebraska | Material implementation gap | MCC source supports a medical program in implementation; the July 1, 2026 permanent-regulation date needs a direct current rule/adoption record. |
| `TJUR-0029` | Nevada | Core corroborated | CCB and lab-library sources retained; public per-batch data claim remains supported by the listed dataset. |
| `TJUR-0030` | New Hampshire | Core corroborated | DHHS source retained; no verified contradiction found. |
| `TJUR-0031` | New Jersey | Corrected | Home cultivation corrected to not permitted using the CRC FAQ; adult-use sales and medical program remain current. |
| `TJUR-0032` | New Mexico | Core corroborated | RLD/CCD source retained; CROP data-surface details remain bounded by the source. |
| `TJUR-0033` | New York | Core corroborated | OCM and data.ny.gov sources retained; no verified contradiction found. |
| `TJUR-0034` | North Carolina | Material source gap | Generic NC portal is insufficient to verify the tribal-market exception and 2026 hemp detail; obtain direct statute/tribal regulator sources. |
| `TJUR-0035` | North Dakota | Core corroborated | ND HHS source retained; no verified contradiction found. |
| `TJUR-0036` | Ohio | Material detail gap | DCC supports the adult-use/medical framework; the profile’s 2026 SB 56 and hemp changes need direct enrolled-law/rule evidence. |
| `TJUR-0037` | Oklahoma | Corrected | Moratorium end date corrected to August 1, 2028 under HB 3143; July 11, 2026 rules remain current. |
| `TJUR-0038` | Oregon | Core corroborated | OLCC/OHA, license, and recall sources retained; no verified contradiction found. |
| `TJUR-0039` | Pennsylvania | Core corroborated | Pennsylvania DOH source retained; adult use remains not legal in the profile. |
| `TJUR-0040` | Rhode Island | Material detail gap | CCC supports the framework; the claimed 2026 licensing expansion needs the underlying enacted law/rule or current commission notice. |
| `TJUR-0041` | South Carolina | Material source gap | The S.423 entry is marked secondary in the ledger; no medical-program enactment should be inferred from the bill page. |
| `TJUR-0042` | South Dakota | Core corroborated | DOH source retained; no verified contradiction found. |
| `TJUR-0043` | Tennessee | Material source gap | The generic state portal does not verify the 2026 intoxicating-hemp restriction; obtain the enacted act and regulator guidance. |
| `TJUR-0044` | Texas | Material detail gap | Texas.gov supports the low-THC medical program; the 2026 consumable-hemp restriction needs a direct enacted-law/regulator source. |
| `TJUR-0045` | Utah | Core corroborated | Center for Medical Cannabis source retained; no verified contradiction found. |
| `TJUR-0046` | Vermont | Material detail gap | CCB supports the adult-use/medical framework; the 2026 Acts 176/178 detail needs direct current statutory text. |
| `TJUR-0047` | Virginia | Corrected | Current possession, sales schedule, and enacted-not-effective hemp limit corrected against CCA and Virginia Code. |
| `TJUR-0048` | Washington | Core corroborated | LCB and dated-list source retained; the RCW 42.56.070(8) commercial-use restriction remains a data-use condition. |
| `TJUR-0049` | West Virginia | Core corroborated | OMC source retained; no verified contradiction found. |
| `TJUR-0050` | Wisconsin | Material source gap | Generic Wisconsin portal is insufficient to independently verify the no-program/ordinance details. |
| `TJUR-0051` | Wyoming | Material detail gap | HB 0166 is an official bill source, but the current 2024 psychoactive-hemp criminalization detail needs enrolled-law confirmation. |
| `TJUR-0052` | Puerto Rico | Unknown detail | The general DOH source supports a medical-program starting point, but the regulator identity and current implementation details remain explicitly flagged for re-verification. |
| `TJUR-0053` | Guam | Material implementation gap | Guam CCB source supports the legal framework; 2026 permit/market-nascent claims need current permit or license evidence. |
| `TJUR-0054` | U.S. Virgin Islands | Unknown | OCR was not reliably retrievable; the accessible 2024 rules material is proposed, so current licensing, home grow, and sales operation remain unresolved. |
| `TJUR-0055` | Northern Mariana Islands | Unknown implementation status | May 15, 2025 official register notices show a lifted producer-license moratorium and adopted regulations, but no current sales/license evidence was located. |
| `TJUR-0056` | American Samoa | Unknown / needs review | Only a generic official portal was available; no authoritative cannabis-specific statute, regulator, or current program evidence was verified. |
| `TJUR-0057` | Canada | Core corroborated | Cannabis Act, Health Canada law/regulation, and licensee sources retained; provincial implementation remains a separate layer. |
| `TJUR-0058` | Germany | Core corroborated; material count gap | BMG/BfArM support CanG and medical access; association-count estimates are secondary/unverified and should not be treated as current law. |
| `TJUR-0059` | Uruguay | Core corroborated | IMPO Law 19.172 source retained; no verified contradiction found. |
| `TJUR-0060` | Netherlands | Core corroborated | Government controlled-supply experiment and medicinal-cannabis sources retained; tolerance and experiment phases remain distinct. |
| `TJUR-0061` | Malta | Material detail gap | ARUC supports the association framework; the claimed 2025 resin amendment needs direct current statutory text. |
| `TJUR-0062` | Luxembourg | Core corroborated | Ministry of Justice source retained; no verified contradiction found. |
| `TJUR-0063` | Switzerland | Core corroborated; material detail gap | BAG supports authorized pilot trials; the approximate trial count and Zurich-extension details need current official program records. |
| `TJUR-0064` | Czechia | Material source gap | SUKL is an official medical regulator source, but the profile’s 2026 personal-possession/home-cultivation law needs the official enacted legal text. |
| `TJUR-0065` | Portugal | Material claim removed/unknown | The decriminalization/medical framework remains; the unsupported “30%+” operator shakeup and new reporting-rule claim was removed from current-law prose pending INFARMED item-level evidence. |
| `TJUR-0066` | Spain | Material implementation gap | AEMPS supports the 2025 medical framework; implementation, private-use, and social-club details need direct current national/subnational sources. |
| `TJUR-0067` | Australia | Core national framework; subnational gap | TGA/ODC support medicinal cannabis; ACT/WA personal-use and 27-adverse-event details need direct state/territory evidence. |
| `TJUR-0068` | New Zealand | Core corroborated | Ministry of Health medicinal-cannabis source retained; adult-use prohibition remains separate from the scheme. |
| `TJUR-0069` | Israel | Core medical framework; policy gap | Ministry of Health source supports the medical program; committee recommendations are not treated as enacted adult-use law. |
| `TJUR-0070` | South Africa | Current/private-use plus proposed rules | The 2024 private-use statute is current in the profile; February 2026 regulations remain draft/proposed and are not current commercial-market law. |
| `TJUR-0071` | Thailand | Material volatility gap | The profile records the 2025 medical/health-use reversal, but current Thai implementation and home-cultivation licensing require a stronger current Thai-language regulatory check. |
| `TJUR-0072` | Mexico | Material source gap | COFEPRIS was not sufficient to verify the court-driven adult-use position and current commercial status in this pass. |
| `TJUR-0073` | Colombia | Material source gap | INVIMA supports the medical licensing starting point; 2026 dispensary/legalization claims remain unverified without current enacted text and regulator guidance. |
| `TJUR-0074` | United States (federal) | Corrected; broader proceeding unknown | Scoped April 28 Schedule III rule corrected; broader NPRM/hearing remains unresolved and adult use remains federally unlawful. |

`TJUR-0075` (Massachusetts Cannabis Data Landscape) is not a legal jurisdiction profile and is excluded from the 74-profile disposition count. It was not changed.

## P04 temporal-model examples and impossible states

These are concrete cases where a single timeless “current status” field cannot preserve the law’s state without losing effective dates, supersession, or scope.

1. **Virginia retail:** On 2026-08-09, sales are not operational; the CCA schedule says regulations by 2027-02-01, initial licenses by 2027-05-01, and retail sales may begin 2027-07-01. A model that stores only `sales: true/false` cannot represent both current state and enacted/implementation future.
2. **Virginia hemp:** The >2 mg total-THC/package limit is enacted but not effective until 2026-08-15. A current-law record needs `effective_from`, not a single overwrite.
3. **Federal hemp:** The current ≤0.3% delta-9 framework and the enacted total-THC/0.4 mg final-form rule effective 2026-11-12 must coexist as successive states.
4. **Oklahoma moratorium:** “Ends 2026-08-01” is a superseded date; HB 3143 moves the end to 2028-08-01 subject to an exception. A temporal model needs supersession and conditional end-state semantics.
5. **Federal scheduling scope:** The 2026-04-28 final rule covers specified FDA-approved and state-medical products, while the broader marijuana NPRM remained in a hearing process. A single `marijuana_schedule: III` value is an impossible flattening because scope and procedural status differ.
6. **South Africa:** Private-use law is current; February 2026 regulations are draft/proposed. A model must not coerce a proposed rule into the enacted rule stream.
7. **New Jersey home grow:** Current CRC guidance says no individual home cultivation, while proposed legislation can exist simultaneously. A pending proposal must not overwrite current law.
8. **Thailand:** The 2022 decriminalization regime and the 2025 medical-use restriction illustrate a policy reversal. Historical effective periods and supersession are required to explain the current state.

## Evidence and receipt

Changed profile files:

- `content/jurisdictions/alabama.md`
- `content/jurisdictions/hawaii.md`
- `content/jurisdictions/new-jersey.md`
- `content/jurisdictions/northern-mariana-islands.md`
- `content/jurisdictions/oklahoma.md`
- `content/jurisdictions/portugal.md`
- `content/jurisdictions/united-states-federal.md`
- `content/jurisdictions/virginia.md`

Changed source ledger:

- `metadata/jurisdiction-sources.jsonl`

Report:

- `reports/jurisdiction-next-pass.md`

New or corrected ledger evidence retrieved on 2026-08-09 is linked in the corrected-findings table above and includes AMCC, Hawaii DOH, NJ-CRC, OMMA, Oklahoma Legislature, Virginia CCA/Code, CNMI Commonwealth Register, DEA, and the Federal Register. Existing unchanged rows retain their original retrieval dates, including the 2026-08-08 deep dataset checks and earlier jurisdiction-specific dates.

After the P03 additions, `metadata/jurisdiction-sources.jsonl` contains 106 valid JSONL rows covering all 74 legal profile IDs.

Local checks: `git diff --check` passed; the JSONL parse and 74-profile/report-row coverage checks passed. The first complete `./bin/validate_graph.sh` run completed ID, taxonomy, COA, cannabinoid, completeness, cultivar, crosslink, Boris graph, compilation, and Markdown-link checks, then exited 1 at the repository-wide public-release audit because of 54 high blocking findings in shared history/data/PII patterns; no jurisdiction-scoped public-release finding was reported. Two immediate retries reached Boris compilation but exited 3 with `FileNotFound` while writing generated `dist/cantilever` HTML; the failure moved between output paths and did not identify a jurisdiction source or graph error.

Unresolved profiles requiring the next evidence pass: `TJUR-0013`, `TJUR-0015`, `TJUR-0017`, `TJUR-0019`, `TJUR-0028`, `TJUR-0034`, `TJUR-0036`, `TJUR-0040`, `TJUR-0041`, `TJUR-0043`, `TJUR-0044`, `TJUR-0046`, `TJUR-0051`, `TJUR-0052`, `TJUR-0053`, `TJUR-0054`, `TJUR-0055`, `TJUR-0056`, `TJUR-0058`, `TJUR-0061`, `TJUR-0063`, `TJUR-0064`, `TJUR-0065`, `TJUR-0066`, `TJUR-0067`, `TJUR-0071`, `TJUR-0072`, and `TJUR-0073`.
