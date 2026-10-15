<div align="center">

<a href="https://portfolio-emsghin2iq-as.a.run.app">
  <img width="100%" alt="Li ZhenXi: SRE, cloud and AI infrastructure" src="https://capsule-render.vercel.app/api?type=waving&height=210&color=0:0d1117,100:1a2e05&text=Li%20ZhenXi&fontColor=c2f75c&fontSize=58&fontAlignY=36&desc=SRE%20%C2%B7%20Cloud%20%C2%B7%20AI%20infrastructure&descSize=18&descAlignY=58&section=header" />
</a>

<img alt="I run Kubernetes in production on Google Cloud. I run an AI agent platform on Cloud Run. I benchmark LLM agents on A100 GPUs." src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=17&pause=1600&color=C2F75C&center=true&vCenter=true&width=640&lines=I+run+Kubernetes+in+production+on+Google+Cloud;I+run+an+AI+agent+platform+on+Cloud+Run;I+benchmark+LLM+agents+on+A100+GPUs;SLOs%2C+error+budgets+and+burn-rate+alerts" />

Computer Science at NTU, graduating June 2027 · DevOps intern · ICCV 2025 co-author<br>
**Open to 2027 roles in SRE, cloud and AI infrastructure.**

<a href="https://portfolio-emsghin2iq-as.a.run.app"><img alt="Portfolio" src="https://img.shields.io/badge/Portfolio-c2f75c?style=for-the-badge&logo=googlecloud&logoColor=0d1117" /></a>
<a href="https://portfolio-emsghin2iq-as.a.run.app/Li_ZhenXi_Resume.pdf"><img alt="Résumé" src="https://img.shields.io/badge/R%C3%A9sum%C3%A9-0d1117?style=for-the-badge&logo=readthedocs&logoColor=c2f75c" /></a>
<a href="https://www.linkedin.com/in/zhenxi-li-lzx391/"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-0d1117?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPHBhdGggZmlsbD0iI2MyZjc1YyIgZD0iTTIwLjQ1IDIwLjQ1aC0zLjU2di01LjU3YzAtMS4zMy0uMDItMy4wNC0xLjg1LTMuMDQtMS44NSAwLTIuMTQgMS40NS0yLjE0IDIuOTR2NS42N0g5LjM0VjloMy40MnYxLjU2aC4wNWMuNDgtLjkgMS42NC0xLjg1IDMuMzctMS44NSAzLjYgMCA0LjI3IDIuMzcgNC4yNyA1LjQ2djYuMjh6TTUuMzQgNy40M2EyLjA2IDIuMDYgMCAxIDEgMC00LjEzIDIuMDYgMi4wNiAwIDAgMSAwIDQuMTN6TTcuMTIgMjAuNDVIMy41NlY5aDMuNTZ2MTEuNDV6TTIyLjIyIDBIMS43N0MuNzkgMCAwIC43NyAwIDEuNzN2MjAuNTRDMCAyMy4yMy43OSAyNCAxLjc3IDI0aDIwLjQ1Yy45OCAwIDEuNzgtLjc3IDEuNzgtMS43M1YxLjczQzI0IC43NyAyMy4yIDAgMjIuMjIgMHoiLz48L3N2Zz4%3D" /></a>
<a href="mailto:zli057@e.ntu.edu.sg"><img alt="Email" src="https://img.shields.io/badge/Email-0d1117?style=for-the-badge&logo=gmail&logoColor=c2f75c" /></a>

<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml"><img alt="Commit live on my portfolio right now" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fportfolio-emsghin2iq-as.a.run.app%2Fapi%2Fstatus&query=%24.commit&label=live%20commit&style=flat-square&labelColor=0d1117&color=c2f75c&logo=googlecloud&logoColor=c2f75c" /></a>
<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/ci.yml"><img alt="Portfolio CI" src="https://github.com/zhenxi0901/portfolio/actions/workflows/ci.yml/badge.svg" /></a>
<a href="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml"><img alt="Portfolio deploy" src="https://github.com/zhenxi0901/portfolio/actions/workflows/deploy.yml/badge.svg" /></a>

</div>

## What I work on

| | What it is | My part |
|---|---|---|
| **Building IoT platform**<br><sub>Primustech</sub> | Live data from building systems (sensors, HVAC, meters), with the dashboards and alarms facility teams use. Kubernetes on GKE. | Moved it from one VM to GKE microservices with Terraform. Own its Cloud Build CI/CD (63 merged PRs). Cut cloud spend ~15%. Grafana dashboards and alerts. |
| **AI agent platform**<br><sub>Primustech</sub> | Two agents for facility teams: one answers from live building data, the other from company documents (RAG). Cloud Run and Vertex AI. | Deploy and run the agent and RAG services in dev, staging and production. Per-environment CI/CD, IAM, secrets and shared-VPC networking. Latency, token-cost and model benchmarks. |
| **ARIES agent benchmarks**<br><sub>NTU HyScale Lab, final-year project</sub> | Long-horizon LLM agent workloads on the lab's open-source agent-serving framework. | The Toolathlon adapter for ARIES. 320 agent runs benchmarked on a hosted API and on self-hosted SGLang on an A100. |

## See it running

My [portfolio](https://portfolio-emsghin2iq-as.a.run.app) is a small production service in its own right: a Go API on Cloud Run with SLO burn-rate alerts, keyless deploys by image digest, and a smoke test against the live URL after every release. Some of what is on it:

<table>
  <tr>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/#ai"><img alt="A request walking through the AI agent platform" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/ai-platform-map.webp" /></a></td>
    <td width="50%"><a href="https://portfolio-emsghin2iq-as.a.run.app/#platform"><img alt="SLOs and error budgets after a simulated incident" src="https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/slo-board.webp" /></a></td>
  </tr>
  <tr>
    <td><sub><b>Follow a request</b> through the AI agent platform, and see which parts are mine.</sub></td>
    <td><sub><b>SLOs and error budgets</b>, with multi-window burn-rate alerts and a replayable incident.</sub></td>
  </tr>
</table>

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
| [`cbf0f8e`](https://github.com/zhenxi0901/portfolio/commit/cbf0f8e72410705d6d4dd3024bcb7a76795e647b) README: screenshots and what the site covers now | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38709362112) | 2026-10-15 08:57 | 1m 26s |
| [`6dfcc52`](https://github.com/zhenxi0901/portfolio/commit/6dfcc5258cd5fc5d25175ed18b7ee3d94fd49f04) Command palette finds sections by what is in them; name its button | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38707762661) | 2026-10-15 08:43 | 1m 28s |
| [`3563c2f`](https://github.com/zhenxi0901/portfolio/commit/3563c2f16f0bbf28ba3c95d62996e3154d49a3c3) Résumé: give the AI agent platform its own section | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38704979186) | 2026-10-15 08:20 | 1m 27s |
| [`4356f2a`](https://github.com/zhenxi0901/portfolio/commit/4356f2a2c5c0bd7a3746d33c1a56e7c3aeea07ec) Two products and the FYP; SLOs and error budgets; the AI infra up close | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38703173611) | 2026-10-15 08:05 | 1m 22s |
| [`86a24f1`](https://github.com/zhenxi0901/portfolio/commit/86a24f136081e2430a092361137f4ce9760999bc) Résumé: describe the AI platform instead of naming the product | [passed](https://github.com/zhenxi0901/portfolio/actions/runs/38700633362) | 2026-10-15 07:43 | 1m 32s |
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


<sub>This README keeps itself current: a daily GitHub Action pulls my merged pull requests and my portfolio's deploys, and another redraws the contribution snake.</sub>
