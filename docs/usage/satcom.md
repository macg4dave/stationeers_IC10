# SatCom setup checklist

SatCom now uses name-first auto-naming and shared data-network discovery.

Primary setup guide:

- `modular scripts/SatCom/Setup.md`

Quick checks:

- all SatCom devices are on one data network
- required names are exact/case-sensitive (`discover`, `cycle`, `dish`, etc.)
- `cmd_token`, `cmd_type`, `slot0..slot2` Logic Memory devices exist
- setup guard shows `db Setting = 1` before runtime testing
