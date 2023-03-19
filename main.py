import argparse
import requests

#doi = "10.1093/bioinformatics/btab069"  # replace with your DOI

class DoiInfo:
    doi: str
    pmid: str = None
    pmcid: str = None

    doi_link: str = "http://dx.doi.org/"
    pm_link: str = "http://www.ncbi.nlm.nih.gov/pubmed/"
    pmc_link: str = "http://www.ncbi.nlm.nih.gov/pmc/articles/"

    def __init__(self, doi):
        self.doi = doi
        self.doi_link += f"{self.doi}"

    def has_pmid(self) -> bool:
        return self.pmid is not None

    def has_pmcid(self) -> bool:
        return self.pmcid is not None

    # Send proper requests to gather PMID and PMCID from DOI
    def analyze(self):
        # send request to Europe PMC API
        response = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=doi:{self.doi}&format=json"
        )

        # parse response to get PMID and PMCID (if available)
        if response.status_code == 200:
            if len(response.json()["resultList"]["result"]) > 0:
                data = response.json()["resultList"]["result"][0]
                if "pmid" in data:
                    self.pmid = data["pmid"]
                    self.pm_link += f"{self.pmid}"
                else:
                    print(f"PMID not found for {self.doi}")
                if "pmcid" in data:
                    self.pmcid = data["pmcid"].split("/")[-1]
                else:
                    print(f"PMCID not found for {self.doi}")
            else:
                print(f"Error: Wrong DOI - {self.doi}")
        else:
            print(f"Error: DOI not found - {self.doi}")

    def __str__(self):
        ret = ""
        if self.has_pmid():
            ret += f"[PubMed:\\href{{{self.pm_link}}}{{{self.pmid}}}]"
        if self.has_pmcid():
            ret += f"[PubMed Central:\\href{{{self.pmc_link}}}{{{self.pmid}}}]"
        ret += f"[doi:\\href{{{self.doi_link}}}{{{self.doi}}}]"
        return ret

def main():
    # Try to get args first.
    # Program can operate in 2 modes:
    # 1. PMID and PMCID from DOI
    # 2. Read BiBTeX, search for all DOI and insert PMID and PMCID into new modified file.

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--doi",
                        action='store_true',
                        help="Analyze all provided arguments as DOI that need PMID and PMCID")
    parser.add_argument("dois",
                        metavar='DOI',
                        type=str,
                        nargs='+',
                        help="DOI to be analyzed.")
    parser.add_argument("-o", "--output",
                        help="Modified BiBTex file. By default output to terminal.")
    parser.add_argument("-b", "--bibtex",
                        help="BiBTeX file.")

    args = parser.parse_args()

    if args.bibtex:
        print("TODO: Analyze bibtex")
    elif args.doi and len(args.dois) > 0:
        for doi in args.dois:
            info = DoiInfo(doi)
            info.analyze()
            print(info)
    else:
        print("--doi or --bibtex much be provided")
        sys.exit(1)

if __name__ == "__main__":
    main()
