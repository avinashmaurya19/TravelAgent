"""Travel Policy RAG retriever providing chunking, vector scoring, and grounded retrieval."""

import os
import re
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PolicyChunk:
    """Indexed chunk representing a policy subsection."""
    doc_name: str
    section_title: str
    content: str
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "section_title": self.section_title,
            "content": self.content,
            "score": round(self.score, 3),
        }


class PolicyRetriever:
    """Loads markdown policies, creates section chunks, and performs grounded retrieval."""

    def __init__(self, policies_dir: Optional[str] = None):
        if policies_dir is None:
            policies_dir = str(Path(__file__).parent / "policies")
        self.policies_dir = Path(policies_dir)
        self.chunks: List[PolicyChunk] = []
        self._idf: Dict[str, float] = {}
        self._load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and normalize text into clean words."""
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in clean.split() if len(w) > 1]

    def _load_and_index(self) -> None:
        """Read all markdown policy files and build indexed chunks."""
        self.chunks.clear()
        if not self.policies_dir.exists():
            return

        doc_freq: Dict[str, int] = {}
        total_chunks = 0

        for file_path in sorted(self.policies_dir.glob("*.md")):
            doc_name = file_path.name
            text = file_path.read_text(encoding="utf-8")
            doc_chunks = self._chunk_markdown(doc_name, text)

            for chunk in doc_chunks:
                self.chunks.append(chunk)
                total_chunks += 1
                unique_terms = set(self._tokenize(chunk.section_title + " " + chunk.content))
                for term in unique_terms:
                    doc_freq[term] = doc_freq.get(term, 0) + 1

        # Precompute smoothed IDF
        for term, df in doc_freq.items():
            self._idf[term] = math.log((total_chunks - df + 0.5) / (df + 0.5) + 1.0)

    def _chunk_markdown(self, doc_name: str, markdown_text: str) -> List[PolicyChunk]:
        """Chunk markdown document by header sections (#, ##, ###)."""
        chunks: List[PolicyChunk] = []
        lines = markdown_text.splitlines()
        current_title = doc_name.replace(".md", "").replace("_", " ").title()
        current_lines: List[str] = []

        for line in lines:
            if re.match(r"^#{1,3}\s+", line):
                # Save previous section if not empty
                body = "\n".join(current_lines).strip()
                if body:
                    chunks.append(PolicyChunk(
                        doc_name=doc_name,
                        section_title=current_title,
                        content=body,
                    ))
                current_title = re.sub(r"^#{1,3}\s+", "", line).strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Append final section
        body = "\n".join(current_lines).strip()
        if body:
            chunks.append(PolicyChunk(
                doc_name=doc_name,
                section_title=current_title,
                content=body,
            ))

        return chunks

    def search(self, query: str, top_k: int = 3) -> List[PolicyChunk]:
        """Perform similarity search across indexed policy chunks."""
        if not self.chunks:
            return []

        query_terms = self._tokenize(query)
        if not query_terms:
            return self.chunks[:top_k]

        scored_chunks: List[PolicyChunk] = []

        for chunk in self.chunks:
            chunk_text = f"{chunk.section_title} {chunk.content}"
            chunk_terms = self._tokenize(chunk_text)
            title_terms = set(self._tokenize(chunk.section_title))
            chunk_len = len(chunk_terms)

            if chunk_len == 0:
                continue

            # Compute BM25-style relevance score
            k1 = 1.5
            b = 0.75
            avg_dl = 40.0
            score = 0.0

            term_counts: Dict[str, int] = {}
            for t in chunk_terms:
                term_counts[t] = term_counts.get(t, 0) + 1

            for qt in query_terms:
                tf = term_counts.get(qt, 0)
                if tf > 0:
                    idf = self._idf.get(qt, 1.0)
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (chunk_len / avg_dl))
                    term_score = idf * (numerator / denominator)

                    # Boost terms matching the section title
                    if qt in title_terms:
                        term_score *= 2.0

                    score += term_score

            if score > 0:
                scored_chunks.append(PolicyChunk(
                    doc_name=chunk.doc_name,
                    section_title=chunk.section_title,
                    content=chunk.content,
                    score=score,
                ))

        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        return scored_chunks[:top_k]

    def format_context(self, chunks: List[PolicyChunk]) -> str:
        """Format retrieved chunks into clean cited markdown for LLM consumption."""
        if not chunks:
            return "No matching travel policy sections found."

        formatted = []
        for i, c in enumerate(chunks, 1):
            formatted.append(
                f"[Source {i}: {c.doc_name} > {c.section_title}]\n{c.content}"
            )
        return "\n\n---\n\n".join(formatted)


# Global singleton instance
policy_retriever = PolicyRetriever()
