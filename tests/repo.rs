//! Repo-wide checks: every shipped script, every static check, the Rust house rules.
mod common;
use common::*;
use ic10_tools::repo;

#[test]
fn inventory_is_not_empty() {
    assert!(repo::scripts(&repo::root()).len() > 40);
}

#[test]
fn every_static_check_passes() {
    let failures: Vec<String> = repo::check_all(&repo::root())
        .into_iter()
        .flat_map(|o| o.errors.into_iter().map(move |e| format!("{}: {e}", o.name)))
        .collect();
    assert_eq!(failures, Vec::<String>::new());
}

#[test]
fn every_script_runs_300_ticks_without_halting() {
    // Stub devices accept any field, so this catches jumps out of the program,
    // stack misuse and bad aliases, not behaviour.
    let root = repo::root();
    let mut halted = vec![];
    for path in repo::scripts(&root) {
        let mut chip = Chip::new(load(&path)).pin("db", &share(Device::stub()));
        for i in 0..6 {
            chip = chip.pin(&format!("d{i}"), &share(Device::stub()));
        }
        chip.run(300);
        if let Some(why) = chip.halted {
            halted.push(format!("{}: tick {}: {why}", repo::rel(&root, &path), chip.tick));
        }
    }
    assert_eq!(halted, Vec::<String>::new());
}

#[test]
fn rust_code_follows_the_house_rules() {
    // AGENTS.md "Rust tooling": no placeholders, no swallowed panics, no skipped
    // tests. The words are split so this file does not match itself.
    let banned: Vec<regex::Regex> = [
        [r"\bto", r"do!"],
        [r"\bunimple", r"mented!"],
        [r"\bTO", r"DO\b"],
        [r"\bFIX", r"ME\b"],
        [r"\bXX", r"X\b"],
        [r"\bcatch_", r"unwind\b"],
        [r"#\[ig", r"nore"],
        [r"\btr", r"y\s*\{"],
        [r"\btr", r"y!"],
    ]
    .iter()
    .filter_map(|p| regex::Regex::new(&p.concat()).ok())
    .collect();
    let root = repo::root();
    let mut found = vec![];
    for dir in ["src", "tests"] {
        for path in repo::glob_sorted(&root.join(dir), "**/*.rs") {
            let text = std::fs::read_to_string(&path).unwrap_or_default();
            for (n, line) in text.lines().enumerate() {
                for rule in banned.iter().filter(|r| r.is_match(line)) {
                    found.push(format!("{}:{}: {rule}", repo::rel(&root, &path), n + 1));
                }
            }
        }
    }
    assert_eq!(found, Vec::<String>::new());
}
