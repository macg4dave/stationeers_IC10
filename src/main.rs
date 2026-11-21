//! `ic10` command line: `cargo run -- <command>`.

use clap::{Parser, Subcommand};
use ic10_tools::{catalog, engine, repo};
use std::path::PathBuf;
use std::process::ExitCode;

#[derive(Parser)]
#[command(name = "ic10", about = "Lint, check and generate this repo's IC10 scripts")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Run every static check (lint, setup contracts, catalog, doc paths, generated files).
    /// Behaviour scenarios run with `cargo test`.
    Check,
    /// Lint IC10 files (default: every shipped script).
    Lint {
        paths: Vec<PathBuf>,
        /// Also show info findings (unguarded pins, reads before writes).
        #[arg(long)]
        info: bool,
    },
    /// Print the game hash (signed CRC-32) of a name, e.g. StructureActiveVent.
    Hash { name: String },
    /// Write the autolathe_restock_vending worker variants for the given profile ids
    /// (e.g. free_ingots). With no ids, refresh the variant files already committed.
    Emit { ids: Vec<String> },
}

fn print(outcomes: &[repo::Outcome]) -> ExitCode {
    for o in outcomes {
        println!("[{}] {}: {}", if o.passed() { "PASS" } else { "FAIL" }, o.name, o.summary);
        o.errors.iter().chain(&o.notes).for_each(|line| println!("       {line}"));
    }
    let failed: Vec<&str> = outcomes.iter().filter(|o| !o.passed()).map(|o| o.name).collect();
    match failed.is_empty() {
        true => ExitCode::SUCCESS,
        false => {
            println!("\nFailed: {}", failed.join(", "));
            ExitCode::FAILURE
        }
    }
}

fn main() -> ExitCode {
    let root = repo::root();
    match Cli::parse().command {
        Command::Check => print(&repo::check_all(&root)),
        Command::Lint { paths, info } => {
            let files = match paths.is_empty() {
                true => repo::scripts(&root),
                false => paths
                    .iter()
                    .flat_map(|p| match p.is_dir() {
                        true => repo::glob_sorted(p, "**/*.ic10"),
                        false => vec![p.clone()],
                    })
                    .collect(),
            };
            print(&[repo::lint(&root, &files, info)])
        }
        Command::Hash { name } => {
            println!("{}", engine::hash(&name));
            ExitCode::SUCCESS
        }
        Command::Emit { ids } => {
            let mut failed = false;
            let profiles = catalog::profiles(&root);
            let unknown: Vec<&String> =
                ids.iter().filter(|id| !profiles.iter().any(|p| &p.id == *id)).collect();
            if !unknown.is_empty() {
                let known: Vec<&str> = profiles.iter().map(|p| p.id.as_str()).collect();
                println!("ERROR: unknown profile {unknown:?} (known: {})", known.join(", "));
                return ExitCode::FAILURE;
            }
            for profile in &profiles {
                let wanted = ids.contains(&profile.id);
                for (path, text) in catalog::render(&root, profile) {
                    if !wanted && !(ids.is_empty() && path.exists()) {
                        continue;
                    }
                    match std::fs::write(&path, text) {
                        Ok(()) => println!("Wrote {}", repo::rel(&root, &path)),
                        Err(e) => {
                            println!("ERROR: {}: {e}", path.display());
                            failed = true;
                        }
                    }
                }
            }
            if failed { ExitCode::FAILURE } else { ExitCode::SUCCESS }
        }
    }
}
