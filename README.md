# Li ZhenXi

SRE, cloud and AI infrastructure. DevOps intern at Primustech, Computer Science at NTU (graduating June 2027),
ICCV 2025 co-author. Open to 2027 roles in SRE, cloud and AI infrastructure.

[Portfolio](https://portfolio-emsghin2iq-as.a.run.app) · [Résumé (PDF)](https://portfolio-emsghin2iq-as.a.run.app/Li_ZhenXi_Resume.pdf) · [LinkedIn](https://www.linkedin.com/in/zhenxi-li-lzx391/) · [zli057@e.ntu.edu.sg](mailto:zli057@e.ntu.edu.sg)

[![My portfolio site: a 3D service mesh of the tools I work with](https://raw.githubusercontent.com/zhenxi0901/portfolio/main/docs/screenshots/hero.webp)](https://portfolio-emsghin2iq-as.a.run.app)

## What I work on

| | What it is | My part |
|---|---|---|
| **Building IoT platform**<br>Primustech | Live data from building systems (sensors, HVAC, meters), with the dashboards and alarms facility teams use. Kubernetes on GKE. | Moved it from one VM to GKE microservices with Terraform. Own its Cloud Build CI/CD (63 merged PRs). Cut cloud spend ~15%. Grafana dashboards and alerts. |
| **AI agent platform**<br>Primustech | Two agents for facility teams: one answers from live building data, the other from company documents (RAG). Cloud Run and Vertex AI. | Deploy and run the agent and RAG services in dev, staging and production. Per-environment CI/CD, IAM, secrets and shared-VPC networking. Latency, token-cost and model benchmarks. |
| **ARIES agent benchmarks**<br>NTU HyScale Lab, final-year project | Long-horizon LLM agent workloads on the lab's open-source agent-serving framework. | The Toolathlon adapter for ARIES. 320 agent runs benchmarked on a hosted API and on self-hosted SGLang on an A100. |

## Open source

Merged into [hyscale-lab/ARIES](https://github.com/hyscale-lab/ARIES):

- [#55](https://github.com/hyscale-lab/ARIES/pull/55) feat(benchmark): add the Toolathlon adapter
- [#61](https://github.com/hyscale-lab/ARIES/pull/61) fix: wait for a Docker exec that has not started yet, a race that dropped runs under load
- [#63](https://github.com/hyscale-lab/ARIES/pull/63) fix(hermes): run terminal commands in the sandbox workdir

## Numbers I can back up

- **~15%** lower cloud spend: 914 orphaned Kafka topics reaped, monitoring samples cut 40%, Cloud SQL and pods right-sized.
- **320** LLM agent runs benchmarked: tool calls are 2.7% of agent time, and 96% of input tokens come from the prefix cache.
- **~7x** more A100 time held by serving jobs than the agents used.
- **3.02x** throughput from four isolated agent tasks at once on one VM.

## Flagship repo

[**portfolio**](https://github.com/zhenxi0901/portfolio): the site above, built as a small production service. A Next.js and
three.js front end; a Go API with Prometheus metrics, SLO burn-rate alerts and Server-Timing; a 30 MB distroless image;
GitHub Actions with a CVE gate and keyless deploys to Cloud Run; all of it in Terraform.

## Stack

**Cloud:** Google Cloud (GKE, Cloud Run, Cloud Build, Cloud SQL, IAM) · AWS (EKS) · Kubernetes · Docker · Terraform<br>
**Reliability:** Prometheus · Grafana · PromQL · SLOs and error budgets · load testing<br>
**AI infrastructure:** SGLang · A100 GPUs · Vertex AI · RAG (Milvus) · Langfuse · LLM benchmarking<br>
**CI/CD:** GitHub Actions · Cloud Build · Jenkins<br>
**Languages:** Python · Java · Bash · Go
