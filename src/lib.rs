//! Tooling for the Stationeers IC10 scripts in this repo.
//!
//! - [`engine`]: IC10 parser, static analyser (lint) and tick simulator.
//! - [`catalog`]: `catalog/` schemas, consistency check, generated worker variants.
//! - [`repo`]: repo-wide checks (lint every script, setup contracts, doc paths).
//!
//! The shipped `.ic10` files stay standalone and paste-ready; nothing here is needed
//! in-game.

pub mod catalog;
pub mod engine;
pub mod repo;
