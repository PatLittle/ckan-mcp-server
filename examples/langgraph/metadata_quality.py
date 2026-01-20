#!/usr/bin/env python3
"""
Metadata Quality Scoring for CKAN Datasets

Advanced quality scoring system based on:
- Completeness (required and recommended fields)
- Richness (descriptions, tags, temporal coverage)
- Resources quality (formats, accessibility)
- Temporal freshness

Score: 0-100 points
"""

from datetime import datetime
from typing import Any


class MetadataQualityScorer:
    """Calculate metadata quality score for CKAN datasets."""

    # Quality thresholds
    EXCELLENT = 80
    GOOD = 60
    ACCEPTABLE = 40
    POOR = 0

    @classmethod
    def score_dataset(cls, dataset: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate comprehensive quality score.

        Returns:
            {
                "score": 75,              # Total score 0-100
                "level": "good",          # excellent/good/acceptable/poor
                "breakdown": {
                    "completeness": 20,   # out of 30
                    "richness": 15,       # out of 30
                    "resources": 25,      # out of 30
                    "freshness": 8        # out of 10
                },
                "issues": ["Missing license", ...]
            }
        """
        issues = []
        breakdown = {
            "completeness": cls._score_completeness(dataset, issues),
            "richness": cls._score_richness(dataset, issues),
            "resources": cls._score_resources(dataset, issues),
            "freshness": cls._score_freshness(dataset, issues),
        }

        total_score = sum(breakdown.values())
        level = cls._get_level(total_score)

        return {
            "score": total_score,
            "level": level,
            "breakdown": breakdown,
            "issues": issues,
        }

    @classmethod
    def _score_completeness(cls, dataset: dict, issues: list) -> int:
        """Score 0-30: Required and recommended fields."""
        score = 0

        # Required fields (15 points)
        if dataset.get("title"):
            score += 5
        else:
            issues.append("Missing title")

        if dataset.get("notes"):  # Description
            score += 5
        else:
            issues.append("Missing description")

        if dataset.get("name"):  # Identifier
            score += 5
        else:
            issues.append("Missing identifier")

        # Recommended fields (15 points)
        if dataset.get("license_id"):
            score += 3
        else:
            issues.append("Missing license")

        if dataset.get("author") or dataset.get("maintainer"):
            score += 3
        else:
            issues.append("Missing author/maintainer")

        if dataset.get("author_email") or dataset.get("maintainer_email"):
            score += 3
        else:
            issues.append("Missing contact email")

        # Organization
        if dataset.get("organization"):
            score += 3
        else:
            issues.append("Not assigned to organization")

        # Geographical coverage
        if dataset.get("extras"):
            has_geo = any(
                e.get("key") in ["spatial", "geographic_coverage"]
                for e in dataset.get("extras", [])
            )
            if has_geo:
                score += 3

        return score

    @classmethod
    def _score_richness(cls, dataset: dict, issues: list) -> int:
        """Score 0-30: Richness of metadata."""
        score = 0

        # Description quality (10 points)
        notes = dataset.get("notes", "")
        if len(notes) > 200:
            score += 10
        elif len(notes) > 100:
            score += 5
        elif len(notes) > 0:
            score += 2
        else:
            issues.append("Very short or missing description")

        # Tags (10 points)
        tags = dataset.get("tags", [])
        num_tags = len(tags)
        if num_tags >= 5:
            score += 10
        elif num_tags >= 3:
            score += 6
        elif num_tags >= 1:
            score += 3
        else:
            issues.append("No tags")

        # Temporal coverage (5 points)
        extras = {e.get("key"): e.get("value") for e in dataset.get("extras", [])}
        if "temporal_start" in extras or "temporal_end" in extras:
            score += 3

        # Frequency/update schedule (5 points)
        if extras.get("frequency") or extras.get("update_frequency"):
            score += 2

        return score

    @classmethod
    def _score_resources(cls, dataset: dict, issues: list) -> int:
        """Score 0-30: Resources quality."""
        score = 0
        resources = dataset.get("resources", [])

        if not resources:
            issues.append("No resources")
            return 0

        # At least one resource (5 points)
        score += 5

        # Check formats (10 points)
        formats = {r.get("format", "").upper() for r in resources}
        open_formats = {"CSV", "JSON", "GEOJSON", "XML", "RDF", "JSONLD"}
        if formats & open_formats:
            score += 10
            if "CSV" in formats:
                score += 2  # Bonus for CSV
        else:
            issues.append("No open formats (CSV/JSON/XML)")

        # Resource descriptions (5 points)
        described = sum(1 for r in resources if r.get("description"))
        if described == len(resources):
            score += 5
        elif described > 0:
            score += 2

        # DataStore availability (5 points)
        has_datastore = any(r.get("datastore_active") for r in resources)
        if has_datastore:
            score += 5

        # URLs validity (5 points)
        valid_urls = sum(
            1 for r in resources if r.get("url") and r["url"].startswith("http")
        )
        if valid_urls == len(resources):
            score += 5
        elif valid_urls > 0:
            score += 2
        else:
            issues.append("Invalid or missing resource URLs")

        return score

    @classmethod
    def _score_freshness(cls, dataset: dict, issues: list) -> int:
        """Score 0-10: Temporal freshness."""
        score = 0

        # Check metadata_modified
        modified_str = dataset.get("metadata_modified")
        if not modified_str:
            issues.append("No last modified date")
            return 0

        try:
            modified = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
            now = datetime.now(modified.tzinfo)
            days_old = (now - modified).days

            if days_old < 90:  # < 3 months
                score = 10
            elif days_old < 180:  # < 6 months
                score = 7
            elif days_old < 365:  # < 1 year
                score = 5
            elif days_old < 730:  # < 2 years
                score = 3
            else:
                score = 1
                issues.append(f"Last updated {days_old} days ago")

        except (ValueError, AttributeError):
            issues.append("Invalid date format")

        return score

    @classmethod
    def _get_level(cls, score: int) -> str:
        """Convert score to quality level."""
        if score >= cls.EXCELLENT:
            return "excellent"
        elif score >= cls.GOOD:
            return "good"
        elif score >= cls.ACCEPTABLE:
            return "acceptable"
        else:
            return "poor"


# Example usage
if __name__ == "__main__":
    # Sample dataset
    sample_dataset = {
        "title": "Sample Dataset",
        "name": "sample-dataset",
        "notes": "This is a sample dataset with a detailed description " * 5,
        "license_id": "cc-by-4.0",
        "author": "Mario Rossi",
        "author_email": "mario@example.com",
        "organization": {"name": "comune-roma"},
        "tags": [
            {"name": "environment"},
            {"name": "air-quality"},
            {"name": "open-data"},
        ],
        "resources": [
            {
                "format": "CSV",
                "url": "https://example.com/data.csv",
                "description": "Data in CSV format",
                "datastore_active": True,
            },
            {
                "format": "JSON",
                "url": "https://example.com/data.json",
                "description": "Data in JSON format",
            },
        ],
        "metadata_modified": "2025-01-15T10:00:00Z",
    }

    scorer = MetadataQualityScorer()
    result = scorer.score_dataset(sample_dataset)

    print("Metadata Quality Assessment")
    print("=" * 50)
    print(f"Overall Score: {result['score']}/100")
    print(f"Quality Level: {result['level'].upper()}")
    print(f"\nBreakdown:")
    for category, score in result["breakdown"].items():
        print(
            f"  {category.capitalize():15} {score:2}/30"
            if category != "freshness"
            else f"  {category.capitalize():15} {score:2}/10"
        )
    if result["issues"]:
        print(f"\nIssues ({len(result['issues'])}):")
        for issue in result["issues"]:
            print(f"  - {issue}")
