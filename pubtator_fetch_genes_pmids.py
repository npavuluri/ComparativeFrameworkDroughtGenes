#!/usr/bin/env python3

import csv, sys, time, xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional
import requests
import argparse

PUBTATOR_URL = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml"
CONCEPTS = "gene"
BATCH = 50  # lower if 502 error
SLEEP = 0.4


# ---------- helpers ----------
def read_pmids(csv_path: Path) -> List[str]:
    pmids: List[str] = []
    with csv_path.open(encoding="utf-8") as fh:
        head = fh.readline()
        fh.seek(0)
        if "pmid" in head.lower():
            for row in csv.DictReader(fh):
                p = (row.get("pmid") or "").strip()
                if p.isdigit(): pmids.append(p)
        else:
            for line in fh:
                p = line.strip().split(",")[0]
                if p.isdigit(): pmids.append(p)
    return pmids


def chunks(xs: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def fetch_pubtator_bioc(pmids: List[str]) -> Optional[str]:
    try:
        r = requests.get(
            PUBTATOR_URL,
            params={"pmids": ",".join(pmids), "concepts": CONCEPTS},
            timeout=35,
        )
        r.raise_for_status()
        return r.text
    except requests.HTTPError as e:
        sys.stderr.write(f"[warn] PubTator HTTP {r.status_code}: {e}\n{r.text[:200]}...\n")
        return None
    except Exception as e:
        sys.stderr.write(f"[warn] Error fetching data: {e}\n")
        return None


def parse_biocxml_pubtator3(bioc: str) -> List[Dict[str, Any]]:

    rows: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    try:
        root = ET.fromstring(bioc)

        for document in root.findall("document"):
            pmid_el = document.find("id")
            if pmid_el is None or not (pmid_el.text or "").strip():
                continue
            pmid = pmid_el.text.strip()

            title = ""
            journal = ""
            for passage in document.findall("passage"):

                journal_infon = passage.find("infon[@key='journal']")
                if journal_infon is not None:
                    journal = journal_infon.text.split(';')[0].strip()

                type_infon = passage.find("infon[@key='type']")
                if type_infon is not None and (type_infon.text or "").strip().lower() == "title":
                    title_text = passage.findtext("text", "").strip()
                    if title_text:
                        title = title_text
                        break

            for passage in document.findall("passage"):
                for annotation in passage.findall("annotation"):
                    type_infon = annotation.find("infon[@key='type']")
                    if type_infon is None:
                        continue
                    if (type_infon.text or "").strip() != "Gene":
                        continue
                    id_infon = annotation.find("infon[@key='identifier']")
                    if id_infon is None:
                        continue

                    id_text = (id_infon.text or "").strip()
                    if not id_text:
                        continue
                    raw_ids = [s.strip() for s in id_text.split(";")]
                    gene_ids = [gid for gid in raw_ids if gid and gid != "-"]

                    if not gene_ids:
                        continue

                    gene_text = annotation.findtext("text", "").strip()

                    for gene_id in gene_ids:
                        key = (pmid, gene_id)
                        if key in seen:
                            continue
                        seen.add(key)

                        rows.append({
                            "pmid": pmid,
                            "gene_id": gene_id,
                            "gene_text": gene_text,
                            "title": title,
                            "journal": journal,
                        })


    except Exception as e:
        sys.stderr.write(f"[warn] Error parsing BiocXML: {e}\n")

    return rows



def write_csv(rows: List[Dict[str, Any]], out_path: Path) -> None:
    cols = ["pmid", "gene_id", "gene_text", "title", "journal"]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in cols})

def main():
    parser = argparse.ArgumentParser(description="Query PubTator3 for gene annotations for a list of PMIDs")
    parser.add_argument( "--pmids_csv", required=True, help="Path to CSV with a 'pmid' column (or one PMID per line).")
    parser.add_argument( "--outfile", required=True, help="Full path to output CSV (will be created, parents auto-created).")
    parser.add_argument("--batch_size", type=int, default=BATCH, help=f"PMIDs per PubTator request (default {BATCH}).")

    args = parser.parse_args()

    pmids_path = Path(args.pmids_csv)
    out_path   = Path(args.outfile)
    batch_size = args.batch_size

    pmids = read_pmids(pmids_path)
    if not pmids:
        print(f"No PMIDs found in {pmids_path}")
        return

    print(f"PMIDs loaded: {len(pmids)}")
    all_rows: List[Dict[str, Any]] = []

    for batch in chunks(pmids, batch_size):
        bioc = fetch_pubtator_bioc(batch)
        if bioc:
            all_rows.extend(parse_biocxml_pubtator3(bioc))
        time.sleep(SLEEP)

    write_csv(all_rows, out_path)
    print(f"Wrote {len(all_rows)} rows → {out_path}")


if __name__ == "__main__":
    main()

##usage: python pubtator_fetch_genes_pmids.py --pmids_csv data/sorghum_pmids.csv --outfile data/outputs/sorghum_genes.csv
