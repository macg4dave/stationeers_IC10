//! Repo-wide static checks: IC10 lint, modular setup contracts, doc path references.
//! `check_all` runs them together with the catalog checks; `cargo test` runs it too.

use crate::catalog;
use crate::engine::{Level, analyse, known_logic_types, load};
use regex::Regex;
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

/// Repo root (this crate lives at the root).
pub fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

pub fn glob_sorted(base: &Path, pattern: &str) -> Vec<PathBuf> {
    let full = format!("{}/{pattern}", glob::Pattern::escape(&base.to_string_lossy()));
    let mut out: Vec<PathBuf> = glob::glob(&full).into_iter().flatten().flatten().collect();
    out.sort();
    out.dedup();
    out
}

/// Every shipped `.ic10` file (`scripts/`, `script set/` and `modular scripts/`).
pub fn scripts(root: &Path) -> Vec<PathBuf> {
    ["scripts", "script set", "modular scripts"]
        .iter()
        .flat_map(|dir| glob_sorted(&root.join(dir), "**/*.ic10"))
        .collect()
}

pub fn rel(root: &Path, path: &Path) -> String {
    path.strip_prefix(root).unwrap_or(path).to_string_lossy().replace('\\', "/")
}

/// One check's result: a summary line and the problems it found.
pub struct Outcome {
    pub name: &'static str,
    pub summary: String,
    pub errors: Vec<String>,
    pub notes: Vec<String>,
}

impl Outcome {
    pub fn passed(&self) -> bool {
        self.errors.is_empty()
    }
}

/// Lint `files`. Errors fail; warnings (and info, when asked) are notes.
pub fn lint(root: &Path, files: &[PathBuf], info: bool) -> Outcome {
    let types = known_logic_types(&root.join("catalog/devices"));
    let (mut errors, mut notes) = (vec![], vec![]);
    for path in files {
        for f in analyse(&load(path), &types) {
            let line = f.format(&rel(root, path));
            match f.level {
                Level::Error => errors.push(line),
                Level::Warning => notes.push(line),
                Level::Info if info => notes.push(line),
                Level::Info => {}
            }
        }
    }
    let summary = format!(
        "{} file(s): {} error(s), {} warning(s)",
        files.len(),
        errors.len(),
        notes.iter().filter(|n| n.contains(": warning ")).count()
    );
    Outcome { name: "ic10 lint", summary, errors, notes }
}

static HASH_NAME: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"HASH\("([^"]+)"\)"#).expect("constant regex"));
static CHANNEL: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(?:cmd_token|cmd_type|slot\d+|data\d+)\b").expect("constant regex")
});
static HOUSING: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?m)^\s*-\s*IC Housing:\s*`([^`]+)`").expect("constant regex"));

/// Each `modular scripts/<feature>/Setup.md` must name every housing, `HASH("...")`
/// name, shared channel and script file its chips use.
pub fn setup_contracts(root: &Path) -> Outcome {
    let mut errors = vec![];
    let features: Vec<PathBuf> = glob_sorted(&root.join("modular scripts"), "*/Setup.md")
        .into_iter()
        .filter_map(|p| p.parent().map(Path::to_path_buf))
        .filter(|d| !d.file_name().is_some_and(|n| n.to_string_lossy().starts_with('_')))
        .collect();
    for feature in &features {
        let setup_path = feature.join("Setup.md");
        let setup = std::fs::read_to_string(&setup_path).unwrap_or_default();
        let at = rel(root, &setup_path);
        let span = |t: &str| setup.contains(&format!("`{t}`"));
        for section in ["## Name contract", "## Setup steps"] {
            if !setup.contains(section) {
                errors.push(format!("{at}: missing section '{section}'"));
            }
        }
        let (mut names, mut channels, mut files) = (BTreeSet::new(), BTreeSet::new(), vec![]);
        for script in glob_sorted(feature, "*.ic10") {
            let text = std::fs::read_to_string(&script).unwrap_or_default();
            let head = text.lines().take(5).collect::<Vec<_>>().join("\n").to_lowercase();
            let stem = script.file_stem().unwrap_or_default().to_string_lossy().to_string();
            if head.contains("deprecated placeholder") || stem.contains('.') {
                continue;
            }
            files.push(script.file_name().unwrap_or_default().to_string_lossy().to_string());
            names.extend(HASH_NAME.captures_iter(&text).map(|c| c[1].to_string()));
            channels.extend(CHANNEL.find_iter(&text).map(|m| m.as_str().to_string()));
        }
        let housings: BTreeSet<&str> =
            HOUSING.captures_iter(&setup).filter_map(|c| c.get(1)).map(|m| m.as_str()).collect();
        if housings.is_empty() {
            errors.push(format!(
                "{at}: Name contract must include at least one 'IC Housing: `name`' entry"
            ));
        } else if housings.len() < files.len() {
            errors.push(format!(
                "{at}: IC Housing entries ({}) fewer than feature scripts ({}); list all chip housings",
                housings.len(),
                files.len()
            ));
        }
        errors.extend(names.iter().filter(|n| !span(n)).map(|n| {
            format!("{at}: missing name contract token `{n}` (referenced in feature IC10 HASH())")
        }));
        errors.extend(channels.iter().filter(|c| !span(c)).map(|c| {
            format!("{at}: missing shared-channel token `{c}` (referenced in feature IC10)")
        }));
        errors.extend(
            files
                .iter()
                .filter(|f| !setup.contains(f.as_str()))
                .map(|f| format!("{at}: missing script path/name reference '{f}'")),
        );
    }
    if features.is_empty() {
        errors.push("no feature folders with Setup.md under modular scripts/".into());
    }
    let summary = format!("{} feature(s), {} issue(s)", features.len(), errors.len());
    Outcome { name: "setup contracts", summary, errors, notes: vec![] }
}

const DOC_GLOBS: &[&str] = &[
    "README.md",
    "AGENTS.md",
    ".github/*.md",
    "catalog/README.md",
    "scripts/README.md",
    "scripts/*/README.md",
    "script set/README.md",
    "script set/*/README.md",
    "modular scripts/README.md",
    "modular scripts/*/*.md",
    "docs/**/*.md",
];
const ROOTED: &[&str] = &[
    ".github/",
    ".vscode/",
    "catalog/",
    "docs/",
    "modular scripts/",
    "scripts/",
    "script set/",
    "src/",
    "tests/",
    "README.md",
    "AGENTS.md",
    "Cargo.toml",
];
static BACKTICK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"`([^`]+)`").expect("constant regex"));
static RELATIVE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z0-9_.()-]+(/|\.md)$").expect("constant regex"));

/// Backticked paths in docs must exist: repo-rooted ones (`scripts/...`) from the root,
/// bare `name/` or `name.md` entries from the doc's own folder.
pub fn doc_paths(root: &Path) -> Outcome {
    let docs: BTreeSet<PathBuf> = DOC_GLOBS.iter().flat_map(|g| glob_sorted(root, g)).collect();
    let mut errors = vec![];
    for doc in &docs {
        let at = rel(root, doc);
        let dir = doc.parent().unwrap_or(root);
        let text = std::fs::read_to_string(doc).unwrap_or_default();
        for (n, line) in text.lines().enumerate() {
            for cap in BACKTICK.captures_iter(line) {
                let token = cap[1].split("::").next().unwrap_or_default(); // `file.rs::test`
                let token =
                    token.trim().trim_matches(['"', '\'']).trim_end_matches(['.', ',', ':', ';']);
                let skip = token.is_empty()
                    || ["<", ">", "*", "...", " --"].iter().any(|x| token.contains(x))
                    || token.starts_with("http")
                    || ["python ", "bash ", "pwsh ", "powershell ", "git ", "cargo "]
                        .iter()
                        .any(|c| token.to_lowercase().starts_with(c));
                if skip {
                    continue;
                }
                if ROOTED.iter().any(|p| token.starts_with(p)) {
                    if !root.join(token).exists() {
                        errors.push(format!("{at}:{}: missing path reference: {token}", n + 1));
                    }
                } else if RELATIVE.is_match(token)
                    && !matches!(token, "README.md" | "Setup.md" | "AGENTS.md")
                    && !dir.join(token).exists()
                    && !root.join(token).exists()
                {
                    errors.push(format!(
                        "{at}:{}: missing path reference: {token} (relative)",
                        n + 1
                    ));
                }
            }
        }
    }
    let summary = format!("{} doc file(s), {} missing reference(s)", docs.len(), errors.len());
    Outcome { name: "doc paths", summary, errors, notes: vec![] }
}

pub fn catalog_check(root: &Path) -> Outcome {
    let report = catalog::check(&root.join("catalog"));
    let summary = format!("{} error(s), {} warning(s)", report.errors.len(), report.warnings.len());
    Outcome { name: "catalog", summary, errors: report.errors, notes: report.warnings }
}

pub fn generated(root: &Path) -> Outcome {
    let (checked, errors) = catalog::stale(root);
    let summary = format!("{checked} generated file(s), {} stale", errors.len());
    Outcome { name: "generated files", summary, errors, notes: vec![] }
}

/// Every static check. Behaviour scenarios run under `cargo test`.
pub fn check_all(root: &Path) -> Vec<Outcome> {
    vec![
        lint(root, &scripts(root), false),
        setup_contracts(root),
        catalog_check(root),
        doc_paths(root),
        generated(root),
    ]
}
