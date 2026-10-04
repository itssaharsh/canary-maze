# A post for X

## Who can actually be tagged

Checked against the live sites rather than guessed, because tagging a wrong
@handle on a public post misfires at a real person.

| Who | Handle | Verified where |
|---|---|---|
| **AI Digest / AI Village** (co-host) | **`@aidigest_`** | footer of theaidigest.org (`twitter.com/aidigest_`), and again on swarmchasing.com |
| **Grove Research** (co-host) | **none exists** | their site carries only `hi@groveresearch.com`, no social links at all |
| Ryan Greenblatt | `@RyanGreenblatt` | quoted on swarmchasing.com as a "Hugging Face incident investigator" — **not a host, organizer or judge** |
| `@slimer48484` | `@slimer48484` | the X post the event's name links to — **no role stated** |

So: tag **`@aidigest_`**, and name Grove Research in words since they have no
account. The other two are your call; neither organizes the event, and tagging a
researcher unprompted to look at your hackathon entry can read as spam. If you do
want one, `@slimer48484` is the better case — the event is named after their post.

---

## Option A — the finding, not the project (recommended)

The CDN result is the most interesting thing here to anyone outside the event, and
it is the one a stranger can act on.

```
I built a tool that plants a unique canary URL on every bot that visits your site.

Published one. Asked a chatbot to read it. 403 — it never reached me.

My own CDN was refusing GPTBot, ClaudeBot, PerplexityBot, CCBot and Bytespider.

5 of 10 never arrived.
```

Reply to yourself with:

```
So a zero in any crawler measurement taken from behind a CDN may be a property of your host, not the crawlers.

It biases toward the null, with no log line at the origin.

Built for the AI Swarm Dynamics hackathon, @aidigest_ x Grove Research.

github.com/itssaharsh/canary-maze
```

---

## Option B — the product, in one line

```
Canary Maze: prove a secret moved between two AI clients, and hand someone a record that verifies with your server switched off.

Edit any number the page shows, press verify again, and it names what no longer matches.

110s demo: site-nine-hazel-35.vercel.app/demo.mp4
```

---

## Option C — plainest

```
Submitted Canary Maze to the AI Swarm Dynamics hackathon, @aidigest_ x Grove Research.

It gives each automated visitor its own secret URL and records when a different one asks for it.

The evidence verifies in your browser with my server off.

github.com/itssaharsh/canary-maze
```

---

## What the post must not say

Organic sightings stand at **0**. Nothing here has caught two agents sharing a
link in the wild, and the post must not imply it. Every third-party fetcher that
reached the surface was handed its URL by us, which is why they are all reported
as paste-triggered. Say "a tool that can prove it", never "I caught them".
