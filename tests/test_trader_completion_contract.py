from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class TraderCompletionContractSurfaceTest(unittest.TestCase):
    def test_repo_contract_and_goal_require_shipped_clean_learning(self) -> None:
        agents = (REPO / "AGENTS.md").read_text()
        goal = (REPO / "configs" / "build_lab_free_goal.txt").read_text()
        for token in ("RUN COMPLETE", "full-suite", "integrated into `main`", "Learning is promoted"):
            self.assertIn(token, agents)
        for token in ("deterministic completion gate", "durable learning", "RUN COMPLETE"):
            self.assertIn(token, goal)

    def test_all_moa_entrypoints_share_fail_closed_build_orchestrator(self) -> None:
        build = (REPO / "scripts" / "trader_build_lab_moa.sh").read_text()
        stress = (REPO / "scripts" / "trader_wake_moa.sh").read_text()
        self.assertNotIn("run_chall || true", build)
        self.assertNotIn("run_chall || true", stress)
        self.assertIn("run_finalize", build)
        self.assertIn("integrate_run", build)
        self.assertIn("exec \"$BUILD_WRAPPER\"", stress)
        self.assertIn("--finalizer-only", stress)
        self.assertIn("--resume", stress)

    def test_bootstrap_does_not_overwrite_evolved_profile_contract(self) -> None:
        bootstrap = (REPO / "scripts" / "bootstrap_trader_profile.sh").read_text()
        protected = (
            '${PROFILE_DIR}/SOUL.md',
            '${PROFILE_DIR}/skills/trading/trader-self-evolution/SKILL.md',
            '${PROFILE_DIR}/workspace/AGENTS.md',
            '${PROFILE_DIR}/memories/MEMORY.md',
            '${PROFILE_DIR}/memories/USER.md',
            '${PROFILE_DIR}/skills/trading/trading-partner/SKILL.md',
        )
        for path in protected:
            self.assertIn(f'if [[ ! -f "{path}" ]]', bootstrap)

    def test_bootstrap_preserves_existing_profile_surfaces_in_fake_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".hermes" / "profiles" / "trader"
            protected = (
                profile / "SOUL.md",
                profile / "skills" / "trading" / "trader-self-evolution" / "SKILL.md",
                profile / "skills" / "trading" / "trading-partner" / "SKILL.md",
                profile / "workspace" / "AGENTS.md",
                profile / "memories" / "MEMORY.md",
                profile / "memories" / "USER.md",
            )
            for path in protected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"EVOLVED:{path.name}\n", encoding="utf-8")
            (profile / "config.yaml").write_text(
                "platform_toolsets:\n  cli: []\n", encoding="utf-8"
            )
            fake_bin = home / "bin"
            fake_bin.mkdir()
            hermes = fake_bin / "hermes"
            hermes.write_text(
                "#!/bin/sh\n"
                "case \"$*\" in\n"
                "  \"profile list\") echo trader ;;\n"
                "  *\"skills list\"*) echo pmcc-strategy ;;\n"
                "  *) exit 0 ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            hermes.chmod(0o755)
            before = {path: path.read_bytes() for path in protected}
            env = os.environ.copy()
            env["HOME"] = str(home)
            env["PATH"] = f"{fake_bin}:{REPO / '.venv' / 'bin'}:{env['PATH']}"
            subprocess.run(
                ["bash", str(REPO / "scripts" / "bootstrap_trader_profile.sh")],
                cwd=REPO,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertEqual(before, {path: path.read_bytes() for path in protected})

    def test_stress_adapter_forwards_recovery_to_build_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy2(REPO / "scripts" / "trader_wake_moa.sh", scripts / "trader_wake_moa.sh")
            wrapper = scripts / "trader_build_lab_moa.sh"
            wrapper.write_text(
                "#!/bin/sh\nprintf '%s\n' \"$@\"\n", encoding="utf-8"
            )
            wrapper.chmod(0o755)
            proc = subprocess.run(
                [
                    "bash", str(scripts / "trader_wake_moa.sh"),
                    "--hyps", "id1,id2", "--stamp", "test-stamp", "--resume",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("manual-stress", proc.stdout)
            self.assertIn("id1,id2", proc.stdout)
            self.assertIn("test-stamp", proc.stdout)
            self.assertIn("--resume", proc.stdout)

    def test_claude_points_to_current_suite_and_contract(self) -> None:
        claude = (REPO / "CLAUDE.md").read_text()
        self.assertIn("Read `AGENTS.md` first", claude)
        self.assertIn("python -m unittest discover -s tests", claude)
        self.assertNotIn("There is **no unit-test suite**", claude)


if __name__ == "__main__":
    unittest.main()
