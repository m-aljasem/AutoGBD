"""
AI Assistant for active learning in code mapping.

This module uses transformer models to suggest GBD cause mappings
for unmapped codes, with human-in-the-loop feedback.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

try:
    from sentence_transformers import SentenceTransformer
    import torch
    HAS_AI_DEPS = True
except ImportError:
    HAS_AI_DEPS = False

from autogbd.core.provenance import ProvenanceTracker


class AIAssistant:
    """
    AI assistant for suggesting GBD cause mappings.

    Uses pre-trained transformer models to suggest the most likely
    GBD causes for unmapped codes, with confidence scoring.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        gbd_cause_list_path: Optional[str] = None,
        provenance: Optional[ProvenanceTracker] = None,
    ):
        """
        Initialize the AI assistant.

        Parameters
        ----------
        model_name : str
            Name of the sentence transformer model to use.
        gbd_cause_list_path : str, optional
            Path to file containing GBD cause list.
        provenance : ProvenanceTracker, optional
            Provenance tracker for logging actions.
        """
        self.provenance = provenance

        if not HAS_AI_DEPS:
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="ai_initialization_failed",
                    details={
                        "error": "AI dependencies (sentence-transformers, torch) not installed"
                    },
                )
            self.model = None
            self.gbd_causes = []
            return

        try:
            self.model = SentenceTransformer(model_name)
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="ai_model_loaded",
                    details={"model_name": model_name},
                )
        except Exception as e:
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="ai_model_error",
                    details={"error": str(e)},
                )
            self.model = None

        # Load GBD cause list
        self.gbd_causes = self._load_gbd_causes(gbd_cause_list_path)

        # Cache for embeddings
        self._cause_embeddings = None

    def _load_gbd_causes(self, path: Optional[str] = None) -> List[str]:
        """
        Load GBD cause list from file.

        Parameters
        ----------
        path : str, optional
            Path to GBD cause list file.

        Returns
        -------
        list of str
            List of GBD cause names.
        """
        if path and Path(path).exists():
            df = pd.read_csv(path)
            # Try common column names
            cause_col = None
            for col in ["gbd_cause", "cause_name", "name", "cause"]:
                if col in df.columns:
                    cause_col = col
                    break

            if cause_col:
                return df[cause_col].dropna().unique().tolist()

        # Default minimal GBD cause list (should be replaced with actual list)
        return [
            "Cardiovascular diseases",
            "Neoplasms",
            "Infectious diseases",
            "Respiratory diseases",
            "Digestive diseases",
            "Neurological disorders",
            "Injuries",
            "Maternal and neonatal conditions",
        ]

    def suggest_mappings(self, source_code: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest GBD cause mappings for a source code.

        Parameters
        ----------
        source_code : str
            Source code to map.
        top_k : int
            Number of top suggestions to return.

        Returns
        -------
        list of dict
            List of suggestions, each containing:
            - gbd_cause: str, suggested GBD cause
            - confidence: float, confidence score (0-1)
        """
        if not self.model or not self.gbd_causes:
            return []

        try:
            # Compute embeddings if not cached
            if self._cause_embeddings is None:
                self._cause_embeddings = self.model.encode(
                    self.gbd_causes, convert_to_tensor=True
                )

            # Encode source code
            source_embedding = self.model.encode([source_code], convert_to_tensor=True)

            # Compute cosine similarity
            from torch.nn.functional import cosine_similarity

            similarities = cosine_similarity(source_embedding, self._cause_embeddings)[0]

            # Get top-k matches
            top_indices = similarities.topk(min(top_k, len(self.gbd_causes))).indices
            top_scores = similarities[top_indices].cpu().tolist()

            # Normalize scores to 0-1 range (cosine similarity is -1 to 1)
            normalized_scores = [(score + 1) / 2 for score in top_scores]

            suggestions = []
            for idx, score in zip(top_indices, normalized_scores):
                suggestions.append(
                    {
                        "gbd_cause": self.gbd_causes[idx],
                        "confidence": float(score),
                    }
                )

            return suggestions

        except Exception as e:
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="ai_suggestion_error",
                    details={"error": str(e), "source_code": source_code},
                )
            return []

    def update_from_review(
        self, review_file_path: str, retrain: bool = False
    ) -> None:
        """
        Update model based on human review feedback.

        Parameters
        ----------
        review_file_path : str
            Path to the corrected review file with human mappings.
        retrain : bool
            Whether to fine-tune the model (future feature).
        """
        review_file = Path(review_file_path)
        if not review_file.exists():
            return

        df = pd.read_csv(review_file)

        # Filter rows where human_mapping is filled
        corrected = df[df["human_mapping"].notna() & (df["human_mapping"] != "")]

        if len(corrected) == 0:
            return

        # Store corrections for future model fine-tuning
        # For now, we just log the feedback
        if self.provenance:
            self.provenance.log(
                step="mapping",
                action="ai_feedback_received",
                details={
                    "review_file": str(review_file),
                    "corrections_count": len(corrected),
                    "retrain": retrain,
                },
            )

        # Future: Implement fine-tuning logic here
        # This would involve:
        # 1. Creating training pairs (source_code, correct_gbd_cause)
        # 2. Fine-tuning the sentence transformer model
        # 3. Saving the updated model

