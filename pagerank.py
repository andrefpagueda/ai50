import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    results_dict = {}
    num_websites = len(corpus)
    page_links = corpus.get(page)
    for website, links in corpus.items():
        if len(links) == 0:
            results_dict[website] = (1/num_websites)
        elif (website == page) or (website not in page_links):
            results_dict[website] = ((1-damping_factor)/num_websites)
        else:
            results_dict[website] = ((1-damping_factor)/num_websites) + (damping_factor/len(page_links))
    return results_dict

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    samples = []
    sample_PR_results = {}
    websites = list(corpus.keys())
    """Get the first sample randomly and set the current page"""
    page = random.choice(websites)
    samples.append(page)
    for x in range(1,n):
        """Get the probabilities for each page through the transition model"""
        prediction = transition_model(corpus, page, damping_factor)
        probabilities = list(prediction.values())
        """Choose randomly the next page"""
        page = list(random.choices(websites, probabilities, k = 1))
        page = page[0]
        samples.append(page)
    """Get the aggregated results from the sampling"""
    samples_count = Counter(samples)
    for website, count in samples_count.items():
        sample_PR_results[website] = count / SAMPLES
    return sample_PR_results

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    new_rank = dict()
    """Set the initial Pagerank"""
    for page in corpus:
        pagerank[page] = 1 / len(corpus)
    stop = False
    """While the PR does not converge, continue recalculating the PR"""
    while stop == False:
        stop = True
        for page in pagerank:
            total = 0
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += (pagerank[possible_page] / len(corpus[possible_page]))
                if len(corpus[possible_page]) == 0:
                    total += (pagerank[possible_page] / len(corpus))
            new_rank[page] = ((1 - damping_factor) / len(corpus)) + (damping_factor * total)
        for page in pagerank:
            if abs(pagerank[page] - new_rank[page]) > 0.001:
                stop = False
            pagerank[page] = new_rank[page]
    return pagerank

if __name__ == "__main__":
    main()
