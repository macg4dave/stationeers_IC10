//! The IC10 parser, simulator and analyser themselves.
mod common;
use common::*;
use std::collections::BTreeSet;

fn run(src: &str, ticks: u64) -> Chip {
    let mut chip = Chip::new(parse(src));
    chip.run(ticks);
    chip
}

#[test]
fn prefab_hashes_match_known_values() {
    // Hard-coded in the scripts and confirmed in-game.
    assert_eq!(hash("StructureActiveVent"), -1129453144);
    assert_eq!(hash("StructureDigitalValve"), -1280984102);
    assert_eq!(hash("StructureGasSensor"), -1252983604);
}

#[test]
fn absolute_vs_relative_branch() {
    let c = run("move r0 1\nbeqz 0 4\nmove r1 7\nyield\nmove r2 9\nyield", 1);
    assert_eq!((c.reg[1], c.reg[2]), (0.0, 9.0), "jumped to line 4");
    let c = run("move r0 1\nbreqz 0 2\nmove r1 7\nmove r2 9\nyield", 1);
    assert_eq!((c.reg[1], c.reg[2]), (0.0, 9.0), "skipped one line");
}

#[test]
fn relative_branch_with_label_adds_the_label_line() {
    // brlt with a label adds the label's line number as an offset: 2 + 3 = line 5.
    let c = run("yield\nyield\nbrlt 0 1 target\ntarget:\nyield", 3);
    assert!(c.halted.is_some());
}

#[test]
fn labels_and_blanks_use_the_line_budget() {
    assert_eq!(run("main:\nadd r0 r0 1\nj main", 1).reg[0], 43.0, "ceil(128 / 3)");
}

#[test]
fn sleep_one_second_is_two_ticks() {
    assert_eq!(run("main:\nadd r0 r0 1\nsleep 1\nj main", 4).reg[0], 2.0);
}

#[test]
fn alias_rebinds_at_runtime() {
    let (a, b) = (dev(&[("Setting", 1.0)]), dev(&[("Setting", 2.0)]));
    let src = "alias x d0\nl r0 x Setting\nalias x d1\nl r1 x Setting\nyield";
    let mut c = Chip::new(parse(src)).pin("d0", &a).pin("d1", &b);
    c.go(1);
    assert_eq!((c.reg[0], c.reg[1]), (1.0, 2.0));
}

#[test]
fn unset_pin_halts() {
    assert!(run("l r0 d0 On\nyield", 1).halted.is_some());
}

#[test]
fn and_is_bitwise() {
    let c = run("move r0 19\nand r1 r0 16\nand r2 r0 4\nyield", 1);
    assert_eq!((c.reg[1], c.reg[2]), (16.0, 0.0));
}

#[test]
fn batch_name_hash_is_exact() {
    let v1 = share(Device::new(&[("On", 0.0)]).prefab("StructureActiveVent").named("IN"));
    let v2 = share(Device::new(&[("On", 0.0)]).prefab("StructureActiveVent").named("IN_1"));
    let src = "sbn HASH(\"StructureActiveVent\") HASH(\"IN\") On 1\nyield";
    let mut c = Chip::new(parse(src)).net(&v1).net(&v2);
    c.go(1);
    assert_eq!((v1.get("On"), v2.get("On"), c.tick), (1.0, 0.0, 1));
}

fn codes(src: &str) -> Vec<&'static str> {
    let types: BTreeSet<String> = ["On", "Setting"].map(String::from).into();
    analyse(&parse(src), &types).iter().map(|f| f.code).collect()
}

#[test]
fn analyser_flags_each_mistake() {
    assert!(codes("x:\nbrlt r0 1 x").contains(&"E004"), "relative branch given a label");
    assert!(codes("beqz r0 2").contains(&"W005"), "absolute jump to a number");
    assert!(codes("j nowhere").contains(&"E003"));
    assert!(codes("a:\na:\nj a").contains(&"E006"));
    assert!(codes("main:\nbnez r1 main\nl r1 d0 On\nj main").contains(&"I008"));
}

#[test]
fn analyser_accepts_a_clean_program() {
    assert_eq!(codes("alias v d0\nw:\nyield\nbdns v w\nl r0 v On\nj w"), Vec::<&str>::new());
}
