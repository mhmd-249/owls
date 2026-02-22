import json
import os
import tempfile

from app.models.profile import CustomerProfile
from app.services.profile_builder import (
    build_all_personas,
    generate_persona_prompt,
    load_raw_profiles,
)

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "profiles")


class TestLoadRawProfiles:
    def test_loads_all_profiles(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        assert len(profiles) >= 3, f"Expected at least 3 profiles, got {len(profiles)}"

    def test_profiles_are_customer_profile_instances(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            assert isinstance(p, CustomerProfile)

    def test_profiles_have_required_fields(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            assert p.customer_id
            assert p.name
            assert p.age > 0
            assert p.gender
            assert p.location


class TestGeneratePersonaPrompt:
    def test_persona_word_count_in_range(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            prompt = generate_persona_prompt(p)
            word_count = len(prompt.split())
            assert 150 <= word_count <= 300, (
                f"Persona for {p.name} has {word_count} words, "
                f"expected 150-300"
            )

    def test_persona_contains_name(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            prompt = generate_persona_prompt(p)
            assert p.name in prompt, f"Persona missing name '{p.name}'"

    def test_persona_contains_location(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            prompt = generate_persona_prompt(p)
            assert p.location in prompt, f"Persona missing location '{p.location}'"

    def test_persona_contains_age(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            prompt = generate_persona_prompt(p)
            assert str(p.age) in prompt, f"Persona missing age {p.age}"

    def test_persona_starts_with_you_are(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            prompt = generate_persona_prompt(p)
            assert prompt.startswith("You are"), (
                f"Persona for {p.name} should start with 'You are'"
            )

    def test_persona_mentions_segments(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles:
            if p.segments:
                prompt = generate_persona_prompt(p)
                # Segments are converted from snake_case to space-separated
                for seg in p.segments[:1]:
                    readable = seg.replace("_", " ")
                    assert readable in prompt, (
                        f"Persona for {p.name} missing segment '{readable}'"
                    )

    def test_personas_are_unique(self) -> None:
        profiles = load_raw_profiles(PROFILES_DIR)
        prompts = [generate_persona_prompt(p) for p in profiles]
        assert len(set(prompts)) == len(prompts), "Some personas are duplicates"

    def test_persona_print_samples(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Print 3 sample personas for manual review."""
        profiles = load_raw_profiles(PROFILES_DIR)
        for p in profiles[:3]:
            prompt = generate_persona_prompt(p)
            word_count = len(prompt.split())
            print(f"\n{'='*60}")
            print(f"PERSONA: {p.name} ({word_count} words)")
            print(f"{'='*60}")
            print(prompt)
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestBuildAllPersonas:
    def test_creates_persona_files_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = build_all_personas(PROFILES_DIR, tmpdir)

            # Check manifest has entries
            assert len(manifest) >= 3

            # Check manifest.json file was created
            manifest_path = os.path.join(tmpdir, "manifest.json")
            assert os.path.exists(manifest_path)

            with open(manifest_path) as f:
                saved_manifest = json.load(f)
            assert len(saved_manifest) == len(manifest)

            # Check individual persona files exist
            for cid, info in manifest.items():
                persona_path = os.path.join(tmpdir, info["persona_file"])
                assert os.path.exists(persona_path), (
                    f"Missing persona file for {cid}"
                )

                # Verify file content is non-empty
                with open(persona_path) as f:
                    content = f.read()
                assert len(content) > 100, (
                    f"Persona file for {cid} seems too short"
                )

    def test_manifest_has_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = build_all_personas(PROFILES_DIR, tmpdir)

            required_keys = {
                "persona_file", "name", "age", "gender",
                "location", "segments", "loyalty_tier", "total_purchases",
            }
            for cid, info in manifest.items():
                assert required_keys.issubset(info.keys()), (
                    f"Manifest entry for {cid} missing keys: "
                    f"{required_keys - info.keys()}"
                )
