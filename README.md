# The World Today — Friday 20 November 2026, in Pictures

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/zairzuab/news-image-20261120-v2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/zairzuab/news-image-20261120-v2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A candidate entry for the [make.fun bounty **news-image-20261120**](https://make.fun/bounty/news-image-20261120): sum up 20 November 2026's world news in one image.

## The image

A 1024×1024 newsprint front page, **"THE WORLD TODAY — Friday 20 November 2026"**, with **36 stories from 7 regions**:

- **Lead story — Kyiv's bridges hit:** Russia fires 400+ drones and 110 missiles overnight; three Dnipro crossings damaged, seven killed in the capital, power cut to five districts.
- **Cyclone Akvan slams into Odisha:** more than 300,000 evacuated as the storm makes landfall on India's east coast.
- **Three powers, one table:** Trump, Xi and Putin sign a joint declaration at the Shenzhen summit — nuclear war must never be fought.
- **Court: Myanmar committed genocide** — the world court finds the state responsible for the 2017 atrocities against the Rohingya, a first.
- **Missile hits Riyadh's PIF Tower** — a Houthi strike damages a tower in the Saudi capital's financial district.
- **Anthropic slides after a record IPO** — shares fall 11% on day two after an $81.3bn debut; Wall Street slumps as Asia's AI rally cools.
- **The Day in Brief:** 30 more stories — Germany rejects a "new Yalta", the UK–EU summit deals, the Denmark–Greenland–US Arctic pact, Taiwan's 2,700 flagged accounts, the Nvidia subpoena, Somalia expelling the UAE ambassador, Haiti's anti-gang operation, COP31 overtime, and more. Every story was first reported on Friday 20 November 2026.

## How it runs

`main.ts` (Node 22, standard library only) decodes the image shipped as
base64 text in `entry.png.b64` and writes it to `/output/entry.png`. It is
fully deterministic and needs no network:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`compose.py` is the build script that laid out the front page: masthead,
the four illustration panels, two procedurally drawn panels (Riyadh
skyline, markets chart) and the day-in-brief list. The composed image is
1024×1024 PNG, 605,835 bytes — inside the 1 MiB gate.

## License

MIT — see [LICENSE](LICENSE).
