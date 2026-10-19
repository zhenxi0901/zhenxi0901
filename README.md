<div align="center">

<a href="https://portfolio-emsghin2iq-as.a.run.app">
  <img width="100%" alt="Li ZhenXi: SRE, cloud and AI infrastructure" src="https://capsule-render.vercel.app/api?type=waving&height=210&color=0:0d1117,100:1a2e05&text=Li%20ZhenXi&fontColor=c2f75c&fontSize=58&fontAlignY=36&desc=SRE%20%C2%B7%20Cloud%20%C2%B7%20AI%20infrastructure&descSize=18&descAlignY=58&section=header" />
</a>

<img alt="I run Kubernetes in production on Google Cloud. I run an AI agent platform on Cloud Run. I benchmark LLM agents on A100 GPUs." src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=17&pause=1600&color=C2F75C&center=true&vCenter=true&width=640&lines=I+run+Kubernetes+in+production+on+Google+Cloud;I+run+an+AI+agent+platform+on+Cloud+Run;I+benchmark+LLM+agents+on+A100+GPUs;SLOs%2C+error+budgets+and+burn-rate+alerts" />

Computer Science at NTU, graduating June 2027 · DevOps intern · ICCV 2025 co-author<br>
**Open to 2027 roles in SRE, cloud and AI infrastructure.**

<a href="https://portfolio-emsghin2iq-as.a.run.app"><img alt="Portfolio" src="https://img.shields.io/badge/Portfolio-c2f75c?style=for-the-badge&logo=googlecloud&logoColor=0d1117" /></a>
<a href="https://www.linkedin.com/in/zhenxi-li-lzx391/"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-0d1117?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPHBhdGggZmlsbD0iI2MyZjc1YyIgZD0iTTIwLjQ1IDIwLjQ1aC0zLjU2di01LjU3YzAtMS4zMy0uMDItMy4wNC0xLjg1LTMuMDQtMS44NSAwLTIuMTQgMS40NS0yLjE0IDIuOTR2NS42N0g5LjM0VjloMy40MnYxLjU2aC4wNWMuNDgtLjkgMS42NC0xLjg1IDMuMzctMS44NSAzLjYgMCA0LjI3IDIuMzcgNC4yNyA1LjQ2djYuMjh6TTUuMzQgNy40M2EyLjA2IDIuMDYgMCAxIDEgMC00LjEzIDIuMDYgMi4wNiAwIDAgMSAwIDQuMTN6TTcuMTIgMjAuNDVIMy41NlY5aDMuNTZ2MTEuNDV6TTIyLjIyIDBIMS43N0MuNzkgMCAwIC43NyAwIDEuNzN2MjAuNTRDMCAyMy4yMy43OSAyNCAxLjc3IDI0aDIwLjQ1Yy45OCAwIDEuNzgtLjc3IDEuNzgtMS43M1YxLjczQzI0IC43NyAyMy4yIDAgMjIuMjIgMHoiLz48L3N2Zz4%3D" /></a>
<a href="mailto:zli057@e.ntu.edu.sg"><img alt="Email" src="https://img.shields.io/badge/Email-0d1117?style=for-the-badge&logo=gmail&logoColor=c2f75c" /></a>

<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml"><img alt="Commit live on my portfolio right now" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fportfolio-emsghin2iq-as.a.run.app%2Fapi%2Fstatus&query=%24.commit&label=live%20commit&style=flat-square&labelColor=0d1117&color=c2f75c&logo=googlecloud&logoColor=c2f75c" /></a>
<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/ci.yml"><img alt="Portfolio CI" src="https://github.com/zhenxi0901/portfolio/actions/workflows/ci.yml/badge.svg" /></a>
<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml"><img alt="Portfolio deploy" src="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml/badge.svg" /></a>

</div>

## What I work on

| | What it is | My part |
|---|---|---|
| **Building IoT platform**<br><sub>Primustech</sub> | Live data from building systems (sensors, HVAC, meters), with the dashboards and alarms facility teams use. Kubernetes on GKE. | Moved it from one VM to GKE microservices with Terraform. Own its Cloud Build CI/CD (63 merged PRs). Cut cloud spend ~15%. Grafana dashboards and alerts.<br><sub>Case studies: [GKE migration](https://portfolio-emsghin2iq-as.a.run.app/work/gke) · [delivery pipeline](https://portfolio-emsghin2iq-as.a.run.app/work/pipeline) · [cost cut](https://portfolio-emsghin2iq-as.a.run.app/work/reaper) · [alerting](https://portfolio-emsghin2iq-as.a.run.app/work/observability)</sub> |
| **AI agent platform**<br><sub>Primustech</sub> | Two agents for facility teams: one answers from live building data, the other from company documents (RAG). Cloud Run and Vertex AI. | Deploy and run the agent and RAG services in dev, staging and production. Per-environment CI/CD, IAM, secrets and shared-VPC networking. Latency, token-cost and model benchmarks.<br><sub>[Case study](https://portfolio-emsghin2iq-as.a.run.app/work/ai-platform) · [the platform up close](https://portfolio-emsghin2iq-as.a.run.app/#ai)</sub> |
| **ARIES agent benchmarks**<br><sub>NTU HyScale Lab, final-year project</sub> | Long-horizon LLM agent workloads on the lab's open-source agent-serving framework. | The Toolathlon adapter for ARIES. 320 agent runs benchmarked on a hosted API and on self-hosted SGLang on an A100.<br><sub>[Findings](https://portfolio-emsghin2iq-as.a.run.app/#research) · [ARIES](https://github.com/hyscale-lab/ARIES)</sub> |

## See it running

My [portfolio](https://portfolio-emsghin2iq-as.a.run.app) is a small production service in its own right: a Go API on Cloud Run with its own 99.9% SLO, measured from outside by uptime checks and shown live on the page, keyless deploys by image digest, and a smoke test against the live URL after every release. Some of what is on it:

<table>
  <tr>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/#ai"><img alt="A request walking through the AI agent platform" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/ai-platform-map.webp" /></a></td>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/#platform"><img alt="SLOs and error budgets after a simulated incident" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/slo-board.webp" /></a></td>
  </tr>
  <tr>
    <td><sub><b>Follow a request</b> through the AI agent platform, and see which parts are mine.</sub></td>
    <td><sub><b>SLOs and error budgets</b>, with multi-window burn-rate alerts and a replayable incident.</sub></td>
  </tr>
  <tr>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/work/reaper"><img alt="A case study page: the numbers, then a working model of the system" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/case-page.webp" /></a></td>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/postmortems/contact-form"><img alt="A postmortem page: impact in numbers, then the write-up" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/postmortem.webp" /></a></td>
  </tr>
  <tr>
    <td><sub><b>A page per case study</b>: the numbers, a working model to press, and the full write-up.</sub></td>
    <td><sub><b>Postmortems</b> from running the site itself, sourced from commits and Cloud Run's logs.</sub></td>
  </tr>
</table>

## Postmortems

Blameless write-ups of what went wrong while I built and ran my portfolio: timeline, root cause, detection and action items linked to the commits that fixed them.

| Postmortem | What happened | The lesson |
|---|---|---|
| [“Message sent” for messages nobody would read](https://portfolio-emsghin2iq-as.a.run.app/postmortems/contact-form)<br><sub>Near miss · 0 messages lost</sub> | For 3 h 36 min the contact form said "sent" while keeping messages on a disk Cloud Run throws away. | Only say "done" after the durable handoff. |
| [The health check that only worked from inside](https://portfolio-emsghin2iq-as.a.run.app/postmortems/healthz)<br><sub>Near miss · caught before launch</sub> | Cloud Run's front end answers some paths ending in "z" itself, so `/healthz` was a 404 from outside while the app was healthy. | Test through the same front door your users use. |
| [A failing check on a healthy site](https://portfolio-emsghin2iq-as.a.run.app/postmortems/smoke-test)<br><sub>False alarm</sub> | The smoke test reported `/metrics` as broken while every request in the logs returned 200. | A flaky check is a broken check. |

## Writing

- [What 320 agent runs taught me about serving LLM agents](https://portfolio-emsghin2iq-as.a.run.app/writing/serving-llm-agents): tool calls were 2.7% of agent time, 96% of input tokens came from the prefix cache, and the GPU sat idle most of the time it was held.
- [Finding a metrics bill in 914 orphaned Kafka topics](https://portfolio-emsghin2iq-as.a.run.app/writing/metrics-bill-kafka-topics): attribution first, a reaper that has to be a CronJob because the topics grow back, and dropping metrics only after checking who reads them.

## Merged pull requests

<!-- merged-prs:start -->
- **[hyscale-lab/ARIES](https://github.com/hyscale-lab/ARIES)**: 3 merged
  - [#55](https://github.com/hyscale-lab/ARIES/pull/55) feat(benchmark): add the Toolathlon adapter <sub>merged 2026-10-12</sub>
  - [#61](https://github.com/hyscale-lab/ARIES/pull/61) fix: wait for a Docker exec that has not started yet <sub>merged 2026-10-01</sub>
  - [#63](https://github.com/hyscale-lab/ARIES/pull/63) fix(hermes): run terminal commands in the sandbox workdir <sub>merged 2026-09-30</sub>
- **[whupdido/mdp](https://github.com/whupdido/mdp)**: 21 merged
  - [#44](https://github.com/whupdido/mdp/pull/44) Task 2: keep board telemetry out of Status; say when the board will look again <sub>merged 2026-10-13</sub>
  - [#43](https://github.com/whupdido/mdp/pull/43) Use the firmware's 07-Oct turn radii in the Android README and animation <sub>merged 2026-10-11</sub>
- **[maeganliew/LTU_VIE](https://github.com/maeganliew/LTU_VIE)**: 14 merged
  - [#17](https://github.com/maeganliew/LTU_VIE/pull/17) docs: update README with setup guide and project explanation <sub>merged 2026-05-22</sub>
  - [#16](https://github.com/maeganliew/LTU_VIE/pull/16) feat: add config-driven maps and themes <sub>merged 2026-05-21</sub>
<!-- merged-prs:end -->

## My portfolio's latest deploys

Every push to `main` runs lint, tests, a CVE gate and a container smoke test, then ships the exact image digest to Cloud Run and smoke-tests the live site.

<!-- deploys:start -->
| Commit | Result | Started (UTC) | Took |
|---|---|---|---|
| [`f39546e`](https://github.com/zhenxi0901/portfolio/commit/f39546e91003accffe20f50b7d62adf359031ee0) Take the résumé off the site and out of the repo | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/39207362206) | 2026-10-19 05:59 | 1m 20s |
| [`e3f87ee`](https://github.com/zhenxi0901/portfolio/commit/e3f87eeae032c1b982cf2ecff0eb314d27da0928) README: screenshots of a case study page and a postmortem | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38850493043) | 2026-10-16 04:24 | 1m 19s |
| [`201e71e`](https://github.com/zhenxi0901/portfolio/commit/201e71ef886057e9c64dfe55efa49f62ed531505) Caption contrast on the tinted result and lesson boxes | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38849491071) | 2026-10-16 04:13 | 1m 16s |
| [`9b3547a`](https://github.com/zhenxi0901/portfolio/commit/9b3547aff1a07eb457385339d5afd2926897b7ea) A page for each case study; deep links into the interactive tabs | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38845849909) | 2026-10-16 03:30 | 1m 25s |
| [`79c1661`](https://github.com/zhenxi0901/portfolio/commit/79c1661d313ce450374aff5b2d77f1ecb305a581) Postmortems from running this site; contact form fails closed | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38845246477) | 2026-10-16 03:23 | 1m 32s |
<!-- deploys:end -->

## Numbers I can back up

- **~15%** lower cloud spend: 914 orphaned Kafka topics reaped, monitoring samples cut 40%, Cloud SQL and pods right-sized.
- **320** LLM agent runs benchmarked: tool calls are 2.7% of agent time, and 96% of input tokens come from the prefix cache.
- **~7x** more A100 time held by serving jobs than the agents used.
- **3.02x** throughput from four isolated agent tasks at once on one VM.

## Stack

<table>
  <tr><td><b>Cloud and infra</b></td><td><img alt="Google Cloud, AWS, Kubernetes, Docker, Terraform, Linux" src="https://skillicons.dev/icons?i=gcp,aws,kubernetes,docker,terraform,linux&theme=dark" /></td></tr>
  <tr><td><b>Delivery and reliability</b></td><td><img alt="GitHub Actions, Git, Prometheus, Grafana" src="https://skillicons.dev/icons?i=githubactions,git,prometheus,grafana&theme=dark" /></td></tr>
  <tr><td><b>Languages</b></td><td><img alt="Python, Java, Bash, Go" src="https://skillicons.dev/icons?i=python,java,bash,golang&theme=dark" /></td></tr>
  <tr><td><b>Data and messaging</b></td><td><img alt="Kafka, Redis, PostgreSQL" src="https://skillicons.dev/icons?i=kafka,redis,postgresql&theme=dark" /></td></tr>
  <tr><td><b>AI infrastructure</b></td><td>
    <img alt="PyTorch" src="https://skillicons.dev/icons?i=pytorch&theme=dark" />
    <img alt="SGLang" src="https://img.shields.io/badge/SGLang-0d1117?style=for-the-badge&labelColor=0d1117&color=0d1117" />
    <img alt="NVIDIA A100" src="https://img.shields.io/badge/A100-0d1117?style=for-the-badge&logo=nvidia&logoColor=76B900" />
    <img alt="Vertex AI" src="https://img.shields.io/badge/Vertex%20AI-0d1117?style=for-the-badge&logo=googlecloud&logoColor=4285F4" />
    <img alt="Milvus" src="https://img.shields.io/badge/Milvus-0d1117?style=for-the-badge&logo=milvus&logoColor=00A1EA" />
    <img alt="Langfuse" src="https://img.shields.io/badge/Langfuse-0d1117?style=for-the-badge" />
  </td></tr>
</table>

## Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/zhenxi0901/zhenxi0901/output/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/zhenxi0901/zhenxi0901/output/snake-light.svg" />
  <img alt="My contribution graph, eaten by a snake" src="https://raw.githubusercontent.com/zhenxi0901/zhenxi0901/output/snake-dark.svg" />
</picture>

<p align="center">
  <img alt="Contribution streak" src="https://streak-stats.demolab.com?user=zhenxi0901&theme=dark&hide_border=true&background=0D1117&ring=C2F75C&fire=C2F75C&currStreakLabel=C2F75C" />
</p>


<sub>This README keeps itself current: a daily GitHub Action pulls my merged pull requests and my portfolio's deploys, and another redraws the contribution snake.</sub>
