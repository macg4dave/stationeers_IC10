//! `catalog/`: typed schemas, the consistency check and the generated
//! `autolathe_restock_vending` worker variants.
//!
//! The schemas are serde structs, so a missing key or a wrong type is reported by
//! serde with the file, line and column. Cross-file rules (titles match the index,
//! no duplicates, no orphan files) are checked here.

use serde::Deserialize;
use serde::de::DeserializeOwned;
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

#[derive(Default)]
pub struct Report {
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
}

#[derive(Deserialize, Clone, Copy, PartialEq, Eq, Default)]
#[serde(rename_all = "snake_case")]
enum Kind {
    #[default]
    WikiImport,
    BestGuess,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Source {
    #[serde(default)]
    kind: Kind,
    wiki_url: String,
    wiki_title: String,
    retrieved_at: String,
    #[serde(default)]
    #[allow(dead_code)]
    notes: Option<String>,
}

#[derive(Deserialize)]
struct Index {
    devices: Vec<IndexEntry>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct IndexEntry {
    wiki_title: String,
    file: String,
}

#[derive(Deserialize)]
#[allow(dead_code)]
struct DeviceFile {
    source: Source,
    identity: Identity,
    io: Io,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Identity {
    item_name: Option<String>,
    #[allow(dead_code)]
    item_hash: Option<i64>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Io {
    parameters: Vec<IoField>,
    outputs: Vec<IoField>,
    #[serde(default)]
    mode_values: Vec<serde_json::Value>,
}

#[derive(Deserialize)]
#[allow(dead_code)]
struct IoField {
    name: String,
    #[serde(rename = "type")]
    kind: String,
    description: String,
}

#[derive(Deserialize)]
struct RecipeIndex {
    producers: Vec<ProducerEntry>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct ProducerEntry {
    wiki_title: String,
    page_title: String,
    file: String,
    recipe_count: usize,
}

#[derive(Deserialize)]
struct RecipeFile {
    source: Source,
    producer: Producer,
    recipes: Vec<Recipe>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Producer {
    wiki_title: String,
    item_name: Option<String>,
    item_hash: Option<i64>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Recipe {
    item: Item,
    tier: String,
    time: f64,
    energy: f64,
    stack_size: Option<u32>,
    inputs: Vec<Material>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Item {
    wiki_title: String,
    display_name: String,
    item_name: Option<String>,
    item_hash: Option<i64>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Material {
    wiki_title: String,
    display_name: String,
    quantity: f64,
}

#[derive(Deserialize)]
#[allow(dead_code)]
struct ProfileIndex {
    version: i64,
    producer: String,
    profiles: Vec<ProfileEntry>,
}

#[derive(Deserialize)]
struct ProfileEntry {
    id: String,
    label: String,
    file: String,
}

/// A recipe profile (`catalog/recipes/<producer>/profiles/*.json`).
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
pub struct Profile {
    version: i64,
    pub id: String,
    label: String,
    producer: String,
    base_profile: Option<String>,
    supported_scripts: Vec<String>,
    notes: Vec<String>,
    #[serde(default)]
    recipe_overrides: Vec<serde_json::Value>,
    build: Build,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Build {
    stock_worker: StockWorker,
    logistics_worker: LogisticsWorker,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct StockWorker {
    tracked_items: Vec<Tracked>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Tracked {
    wiki_title: String,
    display_name: String,
    item_hash: i64,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct LogisticsWorker {
    low_reagent: i64,
    target_reagent: i64,
    base_contents_targets: Vec<Target>,
    recipe_required_targets: Vec<Target>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
struct Target {
    reagent_define: String,
    reagent_name: String,
    reagent_hash: i64,
    ingot_define: String,
    ingot_name: String,
    ingot_hash: i64,
}

fn load<T: DeserializeOwned>(path: &Path, report: &mut Report) -> Option<T> {
    let parsed = std::fs::read_to_string(path)
        .map_err(|e| e.to_string())
        .and_then(|t| serde_json::from_str(&t).map_err(|e| e.to_string()));
    match parsed {
        Ok(v) => Some(v),
        Err(e) => {
            report.errors.push(format!("{}: {e}", path.display()));
            None
        }
    }
}

fn json_files(dir: &Path, recursive: bool) -> Vec<PathBuf> {
    let pattern = if recursive { "**/*.json" } else { "*.json" };
    let full = format!("{}/{pattern}", glob::Pattern::escape(&dir.to_string_lossy()));
    let mut out: Vec<PathBuf> = glob::glob(&full).into_iter().flatten().flatten().collect();
    out.sort();
    out
}

/// Records a referenced catalog file; returns false (and reports) when it is bad.
fn reference(
    report: &mut Report,
    seen: &mut BTreeSet<String>,
    at: &str,
    file: &str,
    prefix: &str,
) -> bool {
    let file = file.replace('\\', "/");
    let errs = [
        (file.trim().is_empty(), format!("{at}.file must be a non-empty string")),
        (!file.starts_with(prefix), format!("{at}.file must be under {prefix}: {file}")),
        (seen.contains(&file), format!("{at}.file duplicated: {file}")),
    ];
    let bad: Vec<String> = errs.into_iter().filter(|e| e.0).map(|e| e.1).collect();
    seen.insert(file);
    let ok = bad.is_empty();
    report.errors.extend(bad);
    ok
}

fn unique(report: &mut Report, seen: &mut BTreeSet<String>, at: &str, key: &str, value: &str) {
    if value.trim().is_empty() {
        report.errors.push(format!("{at}.{key} must be a non-empty string"));
    } else if !seen.insert(value.to_string()) {
        report.errors.push(format!("{at}.{key} duplicated: {value}"));
    }
}

fn check_source(report: &mut Report, path: &Path, source: &Source, title: &str, what: &str) {
    let p = path.display();
    if source.wiki_title != title {
        let msg =
            format!("{p}: source.wikiTitle '{}' != index {what} '{title}'", source.wiki_title);
        report.errors.push(msg);
    }
    if source.kind == Kind::WikiImport {
        for (key, value) in [("wikiUrl", &source.wiki_url), ("retrievedAt", &source.retrieved_at)] {
            if value.trim().is_empty() {
                report.warnings.push(format!("{p}: source.{key} is empty"));
            }
        }
    }
}

/// Check `catalog/` (index, device files, recipes, profiles, orphans).
pub fn check(catalog: &Path) -> Report {
    let mut r = Report::default();
    let index_path = catalog.join("index.json");
    let mut referenced = BTreeSet::new();
    if let Some(index) = load::<Index>(&index_path, &mut r) {
        let mut titles = BTreeSet::new();
        for (i, e) in index.devices.iter().enumerate() {
            let at = format!("{}: devices[{i}]", index_path.display());
            unique(&mut r, &mut titles, &at, "wikiTitle", &e.wiki_title);
            if !reference(&mut r, &mut referenced, &at, &e.file, "devices/") {
                continue;
            }
            let path = catalog.join(&e.file);
            if !path.exists() {
                r.errors.push(format!("{at}: missing file: {}", path.display()));
                continue;
            }
            let Some(dev) = load::<DeviceFile>(&path, &mut r) else { continue };
            check_source(&mut r, &path, &dev.source, &e.wiki_title, "wikiTitle");
            if dev.identity.item_name.as_deref().is_some_and(|n| n.trim().is_empty()) {
                let msg =
                    format!("{}: identity.itemName is empty string (prefer null)", path.display());
                r.warnings.push(msg);
            }
        }
    }
    for p in json_files(&catalog.join("devices"), false) {
        let rel = format!("devices/{}", p.file_name().unwrap_or_default().to_string_lossy());
        if !referenced.contains(&rel) {
            r.errors
                .push(format!("{}: orphan device file not indexed: {rel}", index_path.display()));
        }
    }

    let recipes = catalog.join("recipes");
    if !recipes.exists() {
        return r;
    }
    let recipe_index = recipes.join("index.json");
    let mut referenced = BTreeSet::from(["recipes/index.json".to_string()]);
    if let Some(index) = load::<RecipeIndex>(&recipe_index, &mut r) {
        let mut titles = BTreeSet::new();
        for (i, e) in index.producers.iter().enumerate() {
            let at = format!("{}: producers[{i}]", recipe_index.display());
            unique(&mut r, &mut titles, &at, "wikiTitle", &e.wiki_title);
            if !reference(&mut r, &mut referenced, &at, &e.file, "recipes/") {
                continue;
            }
            let path = catalog.join(&e.file);
            if !path.exists() {
                r.errors.push(format!("{at}: missing file: {}", path.display()));
                continue;
            }
            check_recipes(&mut r, &path, e);
            let profiles = path.parent().map(|d| d.join("profiles")).unwrap_or_default();
            if profiles.exists() {
                check_profiles(&mut r, catalog, &profiles, &e.wiki_title, &mut referenced);
            }
        }
    }
    for p in json_files(&recipes, true) {
        let rel = p.strip_prefix(catalog).unwrap_or(&p).to_string_lossy().replace('\\', "/");
        if !referenced.contains(&rel) {
            let msg = format!("{}: orphan recipe file not indexed: {rel}", recipe_index.display());
            r.errors.push(msg);
        }
    }
    r
}

fn check_recipes(r: &mut Report, path: &Path, e: &ProducerEntry) {
    let Some(file) = load::<RecipeFile>(path, r) else { return };
    let p = path.display();
    check_source(r, path, &file.source, &e.page_title, "pageTitle");
    if file.producer.wiki_title != e.wiki_title {
        let msg = format!(
            "{p}: producer.wikiTitle '{}' != index wikiTitle '{}'",
            file.producer.wiki_title, e.wiki_title
        );
        r.errors.push(msg);
    }
    let mut items = BTreeSet::new();
    for (i, recipe) in file.recipes.iter().enumerate() {
        let at = format!("{p}: recipes[{i}]");
        if !items.insert(recipe.item.wiki_title.clone()) {
            r.errors.push(format!("{at}.item.wikiTitle duplicated: {}", recipe.item.wiki_title));
        }
        if recipe.stack_size == Some(0) {
            r.errors.push(format!("{at}.stackSize must be >= 1"));
        }
        if recipe.inputs.is_empty() {
            r.warnings.push(format!("{at}.inputs is empty"));
        }
    }
    if file.recipes.len() != e.recipe_count {
        let msg = format!(
            "{p}: recipe count {} != index recipeCount {}",
            file.recipes.len(),
            e.recipe_count
        );
        r.errors.push(msg);
    }
}

fn check_profiles(
    r: &mut Report,
    catalog: &Path,
    dir: &Path,
    producer: &str,
    referenced: &mut BTreeSet<String>,
) {
    let index_path = dir.join("index.json");
    let rel_index = index_path.strip_prefix(catalog).unwrap_or(&index_path);
    referenced.insert(rel_index.to_string_lossy().replace('\\', "/"));
    let Some(index) = load::<ProfileIndex>(&index_path, r) else { return };
    let ip = index_path.display();
    if index.producer != producer {
        r.errors.push(format!("{ip}: producer '{}' != expected '{producer}'", index.producer));
    }
    let prefix = format!("recipes/{producer}/profiles/");
    let mut ids = BTreeSet::new();
    for (i, e) in index.profiles.iter().enumerate() {
        let at = format!("{ip}: profiles[{i}]");
        unique(r, &mut ids, &at, "id", &e.id);
        if e.label.trim().is_empty() {
            r.errors.push(format!("{at}.label must be a non-empty string"));
        }
        if !reference(r, referenced, &at, &e.file, &prefix) {
            continue;
        }
        let path = catalog.join(&e.file);
        if !path.exists() {
            r.errors.push(format!("{at}: missing file: {}", path.display()));
            continue;
        }
        let Some(profile) = load::<Profile>(&path, r) else { continue };
        let p = path.display();
        if profile.id != e.id {
            r.errors.push(format!("{p}: id '{}' != index id '{}'", profile.id, e.id));
        }
        if profile.producer != producer {
            r.errors.push(format!("{p}: producer '{}' != expected '{producer}'", profile.producer));
        }
        if profile.build.stock_worker.tracked_items.is_empty() {
            r.warnings.push(format!("{p}: build.stockWorker.trackedItems is empty"));
        }
    }
}

// ------------------------------------------------------------- generated workers

const MODULE: &str = "modular scripts/autolathe_restock_vending";
const PROFILES: &str = "catalog/recipes/Autolathe/profiles";

/// Every Autolathe profile, by id.
pub fn profiles(root: &Path) -> Vec<Profile> {
    let mut report = Report::default();
    let dir = root.join(PROFILES);
    let index: Option<ProfileIndex> = load(&dir.join("index.json"), &mut report);
    let entries = index.map(|i| i.profiles).unwrap_or_default();
    entries.iter().filter_map(|e| load(&root.join("catalog").join(&e.file), &mut report)).collect()
}

/// The worker variant files a profile generates: (path, text).
pub fn render(root: &Path, profile: &Profile) -> Vec<(PathBuf, String)> {
    let dir = root.join(MODULE);
    let id = &profile.id;
    vec![
        (dir.join(format!("autolathe_restock_worker_stock.{id}.ic10")), stock_worker(profile)),
        (
            dir.join(format!("autolathe_restock_worker_logistics.{id}.ic10")),
            logistics_worker(profile),
        ),
    ]
}

/// Generated files that exist in the repo but differ from their profile.
/// Returns (files checked, stale messages). Missing variants are skipped: a profile
/// only ships the variants that are committed.
pub fn stale(root: &Path) -> (usize, Vec<String>) {
    let mut checked = 0;
    let mut stale = Vec::new();
    for profile in profiles(root) {
        for (path, text) in render(root, &profile) {
            let Ok(current) = std::fs::read_to_string(&path) else { continue };
            checked += 1;
            if current.replace("\r\n", "\n") != text {
                let rel = path.strip_prefix(root).unwrap_or(&path).display().to_string();
                stale.push(format!("STALE: {rel} (re-run: cargo run -- emit {})", profile.id));
            }
        }
    }
    (checked, stale)
}

fn stock_worker(p: &Profile) -> String {
    let tracked = &p.build.stock_worker.tracked_items;
    let mut lines: Vec<String> = vec![format!("# profile: {}", p.id)];
    lines.extend(
        [
            "alias vend d0",
            "alias n1 d1",
            "alias n2 d2",
            "alias n3 d3",
            "alias n4 d4",
            "alias n5 d5",
            "alias idx r0",
            "alias slot r1",
            "alias want r2",
            "alias occ r3",
            "alias item r4",
            "alias found r5",
            "alias token r6",
            "alias cond r7",
            "alias house r9",
            "",
            "define MEMH HASH(\"StructureLogicMemory\")",
            "define CTOK HASH(\"cmd_token\")",
            "define CTYPE HASH(\"cmd_type\")",
            "define SLOT0 HASH(\"slot0\")",
            "define SLOT1 HASH(\"slot1\")",
            "define SLOT4 HASH(\"slot4\")",
            "",
            "auto:",
            "l house db PrefabHash",
            "move idx 0",
            "move slot 2",
            "move found 0",
            "s db Setting 500",
            "",
            "main:",
            "yield",
            "bdns d0 no_vend",
        ]
        .map(String::from),
    );
    lines.push(format!("move want {}", tracked.first().map_or(0, |t| t.item_hash)));
    for (i, item) in tracked.iter().enumerate().skip(1) {
        lines.push(format!("seq cond idx {i}"));
        lines.push(format!("select want cond {} want", item.item_hash));
    }
    lines.extend(
        [
            "ls occ vend slot Occupied",
            "beqz occ next_slot",
            "ls item vend slot OccupantHash",
            "sne cond item want",
            "bnez cond next_slot",
            "move found 1",
            "next_slot:",
            "add slot slot 1",
            "slt cond slot 102",
            "bnez cond publish",
            "move slot 2",
            "bnez found next_hash",
            "lbn cond MEMH SLOT4 Setting Maximum",
            "bnez cond missing",
            "lbn token MEMH CTOK Setting Maximum",
            "add token token 1",
            "sbn MEMH SLOT0 Setting want",
            "sbn MEMH SLOT1 Setting 1",
            "sbn MEMH CTYPE Setting 1",
            "sbn MEMH CTOK Setting token",
            "missing:",
            "s db Setting want",
            "j main",
            "next_hash:",
            "move found 0",
            "add idx idx 1",
        ]
        .map(String::from),
    );
    lines.push(format!("slt cond idx {}", tracked.len()));
    lines.extend(
        [
            "bnez cond publish",
            "move idx 0",
            "publish:",
            "s db Setting 500",
            "j main",
            "no_vend:",
            "s db Setting 540",
            "j main",
        ]
        .map(String::from),
    );
    lines.join("\n") + "\n"
}

fn logistics_worker(p: &Profile) -> String {
    let lw = &p.build.logistics_worker;
    let (base, required) = (&lw.base_contents_targets, &lw.recipe_required_targets);
    let all = || base.iter().chain(required.iter());
    let mut lines: Vec<String> = vec![format!("# profile: {}", p.id)];
    let push =
        |lines: &mut Vec<String>, items: &[&str]| lines.extend(items.iter().map(|s| s.to_string()));
    push(
        &mut lines,
        &[
            "alias n0 d0",
            "alias n1 d1",
            "alias mach d2",
            "alias n3 d3",
            "alias n4 d4",
            "alias n5 d5",
            "alias need r0",
            "alias tmp r1",
            "alias oldimp r2",
            "alias level r3",
            "define MEMH HASH(\"StructureLogicMemory\")",
            "define SLOT2 HASH(\"slot2\")",
            "define CLEAR_REQ -1",
        ],
    );
    lines.push(format!("define LOW_REAGENT {}", lw.low_reagent));
    lines.push(format!("define TARGET_REAGENT {}", lw.target_reagent));
    lines.extend(all().map(|t| format!("define {} {}", t.reagent_define, t.reagent_hash)));
    lines.extend(all().map(|t| format!("define {} {}", t.ingot_define, t.ingot_hash)));
    push(
        &mut lines,
        &[
            "auto:",
            "move need CLEAR_REQ",
            "move oldimp 0",
            "s db Setting 200",
            "main:",
            "yield",
            "bdns d2 no_mach",
            "check_arrive:",
            "l tmp mach ImportCount",
            "ble tmp oldimp check_need",
            "move oldimp tmp",
            "move need CLEAR_REQ",
            "check_need:",
            "bne need CLEAR_REQ track_need",
            "scan_need:",
        ],
    );
    for t in base {
        lines.push(format!("lr tmp mach Contents {}", t.reagent_define));
        push(
            &mut lines,
            &["slt tmp tmp LOW_REAGENT", "seq level need CLEAR_REQ", "and tmp tmp level"],
        );
        lines.push(format!("select need tmp {} need", t.ingot_define));
    }
    for t in required {
        lines.push(format!("lr tmp mach Required {}", t.reagent_define));
        push(&mut lines, &["sgt tmp tmp 0", "and tmp tmp level"]);
        lines.push(format!("select need tmp {} need", t.ingot_define));
    }
    push(&mut lines, &["j publish", "track_need:"]);
    for (i, t) in required.iter().enumerate() {
        lines.push(format!("seq tmp need {}", t.ingot_define));
        lines.push(format!("bnez tmp track_required_{i}"));
    }
    lines.push("j common_need".into());
    for (i, t) in required.iter().enumerate() {
        lines.push(format!("track_required_{i}:"));
        lines.push(format!("lr tmp mach Required {}", t.reagent_define));
        push(&mut lines, &["bgtz tmp publish", "move need CLEAR_REQ", "j publish"]);
    }
    lines.push("common_need:".into());
    lines.push(format!("move level {}", base.last().map_or("0", |t| t.reagent_define.as_str())));
    for t in base {
        lines.push(format!("seq tmp need {}", t.ingot_define));
        lines.push(format!("select level tmp {} level", t.reagent_define));
    }
    push(
        &mut lines,
        &[
            "lr level mach Contents level",
            "slt tmp level TARGET_REAGENT",
            "bnez tmp publish",
            "move need CLEAR_REQ",
            "j scan_need",
            "publish:",
            "bne need CLEAR_REQ active",
            "s db Setting 200",
            "sbn MEMH SLOT2 Setting 0",
            "j main",
            "active:",
            "s db Setting need",
            "sbn MEMH SLOT2 Setting need",
            "j main",
            "no_mach:",
            "s db Setting 243",
            "j main",
        ],
    );
    lines.join("\n") + "\n"
}
