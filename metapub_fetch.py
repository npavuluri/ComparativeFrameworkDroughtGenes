##usage: python metapub_fetch.py --common rice --scientific Oryza_sativa

import argparse

from pathlib import Path
import os, csv
from dotenv import load_dotenv


#if os.getenv("NCBI_API_KEY"):
#    os.environ["NCBI_API_KEY"] = os.getenv("NCBI_API_KEY")

from metapub import PubMedFetcher

fetch = PubMedFetcher()

EXCLUDED_JOURNALS = ["Int J Mol Sci", "Antioxidants (Basel).", "Biomolecules", "Curr Issues Mol Biol", "Exp Appl Acarol.", "Genes (Basel)", "Molecules.", "PeerJ.", "Plants (Basel)", "Biochem Biophys Res Commun.", "Biology (Basel)", "For Res (Fayettev)", "Life (Basel)"]

def species_query(species_common: str, species_scientific: str) -> str:
    stress = '(drought[Title/Abstract] OR "water stress"[Title/Abstract] OR "water deficit"[Title/Abstract]) OR "dehydration[Title/Abstract]"'
    tolres = '(toleran*[Title/Abstract] OR resist*[Title/Abstract])'
    gene = '(gene[Title/Abstract] OR "transcription factor*"[Title/Abstract] OR "candidate gene*"[Title/Abstract])'
    sp = f'({species_common}[Title/Abstract] OR "{species_scientific}"[Title/Abstract])'
    exclude_review = 'review[Publication Type]'
    exclude_journal = ''
    for journal in EXCLUDED_JOURNALS:
        exclude_journal = exclude_journal + "NOT " + '"' + journal + '"' + "[Journal] "
    return f'{stress} AND {tolres} AND {gene} AND {sp} NOT {exclude_review} {exclude_journal}'

def main():
    parser = argparse.ArgumentParser(description="Fetch PMIDs for drought-related papers for a given species.")
    parser.add_argument("--common", required=True, help="Common species name (replace spaces with '_'), e.g. 'rice' or 'bread_wheat'")
    parser.add_argument("--scientific", required=True, help="Scientific name (replace spaces with '_'), e.g. 'Oryza_sativa'")
    parser.add_argument("--outfile", default=None, help="Optional output CSV path; default: data/<common>_pmids.csv")
    args = parser.parse_args()

    q = species_query(f'{args.common}'.replace('_', ' '), f'{args.scientific}'.replace('_', ' '))
    print(q)

    pmids = fetch.pmids_for_query(q, retmax=1000)

    default_name = f"{args.common}_pmids.csv"
    out = Path(args.outfile) if args.outfile else Path("/home/students/n.pavuluri") / "data" / default_name
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid"])
        for p in pmids:
            w.writerow([p])

    print(f"{args.common.title()} PMIDs: {len(pmids)} -> {out}")

if __name__ == "__main__":
    main()
