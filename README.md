# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Daniikhwan/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Daniikhwan/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A one-image front page summing up Thursday 26 November 2026: Taiwan holds its 15% US tariff, America marks Thanksgiving, Game 3 of the World Chess Championship in Geneva, India marks Constitution Day and 18 years since the 26/11 Mumbai attacks, Virgin Australia staff strike, and EU leaders haggle over the budget. Drawn from scratch in pure Python (standard library only) — deterministic, no network, no fonts.

## The six stories

1. **Taiwan keeps its 15% US tariff** — Taipei says it is confident of keeping the agreed 15% rate after the Trump administration's new tariff salvo on 14 trading partners (Reuters, Taipei, 26 Nov).
2. **America gives thanks** — Thanksgiving Day, Thursday 26 November; tables full, US markets shut for the holiday.
3. **Chess, Game 3 in Geneva** — defending champion Gukesh Dommaraju v challenger Javokhir Sindarov, tied 1–1 in the youngest World Championship match in history; Game 3 is played today.
4. **India remembers 26/11** — Constitution Day (Samvidhan Divas), 18 years after the Mumbai terror attacks of 26 November 2008.
5. **Virgin walks out** — airport staff strike at four Australian airports today in a pay dispute.
6. **EU leaders haggle over the budget** — talks in Brussels on the Union's next long-term budget.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024×1024). Running it twice produces byte-identical output: no randomness, no clock, no network, no external files. The image is drawn entirely in code — every letter comes from a 5×7 bitmap font defined in `main.py`, and the PNG itself is encoded by hand with `zlib` + `struct`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vnsny7za&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
