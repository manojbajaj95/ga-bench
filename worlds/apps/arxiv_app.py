"""arXiv application — dummy MCP server with hardcoded research papers."""

from __future__ import annotations

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Hardcoded paper database
# ---------------------------------------------------------------------------

_PAPERS: list[dict] = [
    # LLMs / AI
    {
        "id": "2501.12345",
        "title": "Scaling Laws for Neural Language Models Revisited",
        "authors": ["Jordan Hoffman", "Sebastian Borgeaud", "Arthur Mensch", "Elena Culpepper"],
        "abstract": (
            "We revisit scaling laws for large language models, demonstrating that optimal "
            "compute allocation shifts significantly as model size increases beyond 100B parameters. "
            "Our experiments across 400 model configurations reveal a new regime where data quality "
            "dominates over raw quantity. We introduce Chinchilla-2, trained on 3T tokens, which "
            "outperforms models 4x its size on 57 evaluation benchmarks."
        ),
        "categories": ["cs.LG", "cs.CL"],
        "published": "2025-01-18",
        "url": "https://arxiv.org/abs/2501.12345",
        "citations": 312,
    },
    {
        "id": "2502.00123",
        "title": "Reasoning Chains in Large Language Models: A Survey",
        "authors": ["Xia Chen", "Yuki Tanaka", "Priya Nair"],
        "abstract": (
            "We survey 180 papers on chain-of-thought and reasoning in LLMs, categorizing "
            "approaches into in-context learning, fine-tuning, and search-augmented methods. "
            "We identify key open challenges: faithfulness of intermediate steps, computational "
            "overhead of extended reasoning, and evaluation metrics for multi-step problems. "
            "We propose a unified taxonomy and highlight the most promising research directions."
        ),
        "categories": ["cs.CL", "cs.AI"],
        "published": "2025-02-03",
        "url": "https://arxiv.org/abs/2502.00123",
        "citations": 88,
    },
    {
        "id": "2412.99876",
        "title": "Constitutional AI: Training Harmless Assistants Without Human Labels",
        "authors": ["Anthropic Research Team"],
        "abstract": (
            "We introduce Constitutional AI (CAI), a method for training AI systems to be "
            "helpful, harmless, and honest using a set of written principles rather than "
            "human-labeled preference data. The system critiques and revises its own outputs "
            "during SL-CAI, then uses RL-CAI with AI-generated feedback. Models trained with "
            "CAI show strong preference for harmless responses without significant capability loss."
        ),
        "categories": ["cs.AI", "cs.LG"],
        "published": "2024-12-10",
        "url": "https://arxiv.org/abs/2412.99876",
        "citations": 1420,
    },
    {
        "id": "2502.05501",
        "title": "Mixture of Experts at Scale: Efficiency Gains and Routing Dynamics",
        "authors": ["Marco Pellegrini", "Sara Lee", "Dmitri Volkov", "Aisha Diallo"],
        "abstract": (
            "We study Mixture-of-Experts (MoE) architectures at scales up to 1T parameters, "
            "analyzing routing dynamics, expert specialization, and failure modes. Our analysis "
            "reveals that expert collapse is the primary bottleneck at large scale, and we "
            "introduce Balanced Routing with Load-Aware Penalties (BRLAP) which improves "
            "token throughput by 2.3x while maintaining model quality."
        ),
        "categories": ["cs.LG", "cs.DC"],
        "published": "2025-02-05",
        "url": "https://arxiv.org/abs/2502.05501",
        "citations": 45,
    },
    # Robotics / RL
    {
        "id": "2501.08821",
        "title": "Learning Dexterous Manipulation from Human Video Demonstrations",
        "authors": ["Kai Zhang", "Maria Rodriguez", "Thomas Nguyen"],
        "abstract": (
            "We present VideoManip, a framework for learning dexterous robot manipulation "
            "policies directly from unlabeled human video demonstrations. By combining "
            "video diffusion models for trajectory generation with online RL fine-tuning, "
            "our system achieves 73% success on the DEXTR benchmark — a 28-point improvement "
            "over prior state-of-the-art — without any robot-collected data."
        ),
        "categories": ["cs.RO", "cs.LG"],
        "published": "2025-01-11",
        "url": "https://arxiv.org/abs/2501.08821",
        "citations": 201,
    },
    {
        "id": "2502.11034",
        "title": "RLHF Beyond Preferences: Reward Modeling with Structured Feedback",
        "authors": ["Lin Wei", "Fatima Al-Hassan", "Bjorn Eriksen"],
        "abstract": (
            "Standard RLHF relies on pairwise preference comparisons, which are noisy and "
            "inconsistent. We propose Structured Reward Learning (SRL), which uses rubric-based "
            "evaluation across 7 dimensions. SRL reward models show 34% better correlation with "
            "expert human ratings and significantly reduce reward hacking on the Anthropic "
            "Helpfulness benchmark."
        ),
        "categories": ["cs.LG", "cs.AI"],
        "published": "2025-02-11",
        "url": "https://arxiv.org/abs/2502.11034",
        "citations": 29,
    },
    # Computer Vision
    {
        "id": "2501.04400",
        "title": "Diffusion Transformers for High-Fidelity Video Generation",
        "authors": ["Yann Lecun", "Sofia Andreou", "James Park"],
        "abstract": (
            "We present DiT-Video, a diffusion transformer architecture for text-to-video "
            "generation that achieves state-of-the-art quality on EvalFID and VBench. "
            "Key innovations include 3D attention with causal masking, flow-matching training, "
            "and a multi-scale VAE encoder. DiT-Video generates 10-second 1080p clips in "
            "under 30 seconds on a single A100."
        ),
        "categories": ["cs.CV", "cs.LG"],
        "published": "2025-01-07",
        "url": "https://arxiv.org/abs/2501.04400",
        "citations": 567,
    },
    {
        "id": "2502.09900",
        "title": "Foundation Models for Medical Image Segmentation: A Comprehensive Evaluation",
        "authors": ["Amara Osei", "Rachel Kim", "Pablo Torres", "Nina Petrov"],
        "abstract": (
            "We benchmark 12 vision foundation models on 8 medical imaging datasets spanning "
            "CT, MRI, and histopathology. Contrary to prior results, we find that models "
            "pre-trained on natural images outperform domain-specific models on 6 of 8 tasks "
            "when fine-tuned. We release MedSeg-Bench, a standardized evaluation suite."
        ),
        "categories": ["cs.CV", "eess.IV"],
        "published": "2025-02-09",
        "url": "https://arxiv.org/abs/2502.09900",
        "citations": 37,
    },
    # Theory / Math
    {
        "id": "2412.77001",
        "title": "In-Context Learning as Bayesian Inference: Theory and Implications",
        "authors": ["Sham Kakade", "Percy Liang", "Tengyu Ma"],
        "abstract": (
            "We provide a theoretical characterization of in-context learning (ICL) in "
            "transformers, proving that under mild assumptions, ICL approximates Bayesian "
            "inference over the data-generating distribution. This explains empirical phenomena "
            "such as sensitivity to prompt format and the diminishing returns of additional "
            "examples. We derive sample complexity bounds for ICL."
        ),
        "categories": ["cs.LG", "stat.ML"],
        "published": "2024-12-22",
        "url": "https://arxiv.org/abs/2412.77001",
        "citations": 890,
    },
    # Systems / Efficiency
    {
        "id": "2502.03318",
        "title": "FlashAttention-4: Sub-quadratic Attention for Long Contexts",
        "authors": ["Tri Dao", "Albert Gu", "Christopher Re"],
        "abstract": (
            "FlashAttention-4 extends the IO-aware attention algorithm to support sub-quadratic "
            "complexity for sequences beyond 1M tokens. Using a hierarchical sparse attention "
            "pattern combined with exact top-k retrieval, FA4 achieves linear scaling while "
            "maintaining full accuracy on perplexity benchmarks. We demonstrate 512K-context "
            "inference at 140 tokens/sec on H100 GPUs."
        ),
        "categories": ["cs.LG", "cs.AR"],
        "published": "2025-02-03",
        "url": "https://arxiv.org/abs/2502.03318",
        "citations": 183,
    },
    # Agents / Tool Use
    {
        "id": "2501.14900",
        "title": "Agentic AI: Benchmark Design for Long-Horizon Tool-Using Agents",
        "authors": ["Mihail Popescu", "Ling Zhang", "Olusegun Okonkwo"],
        "abstract": (
            "We present AgentBench-XT, a benchmark for evaluating tool-using AI agents on "
            "long-horizon tasks requiring planning, web search, code execution, and file "
            "management. We evaluate 9 frontier models and find that performance degrades "
            "sharply beyond 10-step horizons. We identify tool selection errors as the primary "
            "failure mode (58%) and release a diagnostic toolkit for error attribution."
        ),
        "categories": ["cs.AI", "cs.CL"],
        "published": "2025-01-15",
        "url": "https://arxiv.org/abs/2501.14900",
        "citations": 256,
    },
    # Quantum / Physics
    {
        "id": "2502.07788",
        "title": "Error Correction Thresholds for Topological Quantum Codes Under Realistic Noise",
        "authors": ["John Preskill", "Alexei Kitaev", "Barbara Terhal"],
        "abstract": (
            "We derive tight error correction thresholds for the surface code and honeycomb "
            "code under realistic hardware noise models including leakage, crosstalk, and "
            "measurement errors. Our Monte Carlo simulations on 10^6 noise realizations show "
            "that the effective threshold drops from 1% (depolarizing noise) to 0.4% under "
            "realistic models, with implications for near-term quantum advantage."
        ),
        "categories": ["quant-ph", "cond-mat.str-el"],
        "published": "2025-02-07",
        "url": "https://arxiv.org/abs/2502.07788",
        "citations": 72,
    },
]


def _matches(query: str, paper: dict) -> bool:
    q = query.lower()
    return (
        q in paper["title"].lower()
        or q in paper["abstract"].lower()
        or any(q in a.lower() for a in paper["authors"])
        or any(q in c.lower() for c in paper["categories"])
    )


def _score(query: str, paper: dict) -> int:
    q = query.lower()
    score = 0
    if q in paper["title"].lower():
        score += 3
    if q in paper["abstract"].lower():
        score += 1
    if any(q in a.lower() for a in paper["authors"]):
        score += 2
    if any(q in c.lower() for c in paper["categories"]):
        score += 1
    return score


class ArxivApp:
    """Dummy arXiv application for searching and retrieving research papers."""

    def __init__(self) -> None:
        self.name = "arxiv"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def search_papers(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> list[dict]:
        """Search arXiv for research papers by keyword, author, or category.

        Args:
            query: Search query — can include topic keywords, author names, or arXiv categories
                   like 'cs.LG', 'cs.CL', 'cs.CV', 'quant-ph'.
            max_results: Maximum number of results to return (default 5, max 10).
            sort_by: Sort order — 'relevance' (default) or 'citations' or 'date'.

        Returns:
            list[dict]: Matching papers with id, title, authors, categories, published,
                        url, citations, and truncated abstract.

        Tags:
            arxiv, search, papers, research, academic
        """
        max_results = min(max_results, 10)
        matches = [(p, _score(query, p)) for p in _PAPERS if _matches(query, p)]

        if sort_by == "citations":
            matches.sort(key=lambda x: x[0]["citations"], reverse=True)
        elif sort_by == "date":
            matches.sort(key=lambda x: x[0]["published"], reverse=True)
        else:
            matches.sort(key=lambda x: x[1], reverse=True)

        return [
            {
                "id": p["id"],
                "title": p["title"],
                "authors": p["authors"],
                "categories": p["categories"],
                "published": p["published"],
                "url": p["url"],
                "citations": p["citations"],
                "abstract": p["abstract"][:300] + "..." if len(p["abstract"]) > 300 else p["abstract"],
            }
            for p, _ in matches[:max_results]
        ]

    def get_paper(self, paper_id: str) -> dict:
        """Retrieve full details for a specific paper by its arXiv ID.

        Args:
            paper_id: The arXiv paper ID (e.g. '2501.12345').

        Returns:
            dict: Full paper details including complete abstract, or error dict if not found.

        Tags:
            arxiv, paper, detail, read, full
        """
        paper = next((p for p in _PAPERS if p["id"] == paper_id), None)
        if paper is None:
            return {"error": f"Paper '{paper_id}' not found."}
        return dict(paper)

    def list_recent(self, category: str | None = None, limit: int = 5) -> list[dict]:
        """List the most recently published papers, optionally filtered by category.

        Args:
            category: arXiv category code to filter by (e.g. 'cs.LG', 'cs.CL', 'cs.CV',
                      'cs.AI', 'cs.RO', 'quant-ph'). None returns all categories.
            limit: Maximum number of results (default 5).

        Returns:
            list[dict]: Papers sorted newest first, without full abstract.

        Tags:
            arxiv, recent, new, papers, list
        """
        papers = _PAPERS
        if category:
            papers = [p for p in papers if category in p["categories"]]
        papers = sorted(papers, key=lambda p: p["published"], reverse=True)
        return [{k: v for k, v in p.items() if k != "abstract"} for p in papers[:limit]]

    def list_categories(self) -> list[str]:
        """List all arXiv subject categories available in the database.

        Returns:
            list[str]: Sorted unique category codes.

        Tags:
            arxiv, categories, subjects, taxonomy
        """
        cats: set[str] = set()
        for p in _PAPERS:
            cats.update(p["categories"])
        return sorted(cats)

    def get_by_author(self, author_name: str) -> list[dict]:
        """Find all papers by a specific author.

        Args:
            author_name: Full or partial author name (case-insensitive).

        Returns:
            list[dict]: Matching papers sorted by citation count descending.

        Tags:
            arxiv, author, papers, search, academic
        """
        name = author_name.lower()
        matches = [p for p in _PAPERS if any(name in a.lower() for a in p["authors"])]
        matches.sort(key=lambda p: p["citations"], reverse=True)
        return [{k: v for k, v in p.items() if k != "abstract"} for p in matches]

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [
            self.search_papers,
            self.get_paper,
            self.list_recent,
            self.list_categories,
            self.get_by_author,
        ]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = ArxivApp()
    server = app.create_mcp_server()
    server.run()
