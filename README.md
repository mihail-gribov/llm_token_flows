# How Transformers Build Their Predictions

Layer-by-layer view into how transformers resolve their next token.

## What is this?

At every layer of a transformer, we project the intermediate hidden state onto the model's vocabulary through the LM head and record the top predicted token along with its probability. This is done at **three points** within each layer:

- **Before attention** — the residual stream entering the layer
- **After attention** — the residual stream after the attention sublayer is added
- **After FFN** — the residual stream after the feed-forward sublayer is added

Reading the diagrams from bottom to top, you can observe how the model's "best guess" evolves as information flows through the network.

## Two types of diagrams

Each example includes two visualizations:

**Layer-by-layer flow** (`*_flow.png`) — shows the top-1 token at each stage of each layer. Highlighted cells with ▲/▼ indicators mark where a sublayer meaningfully changed the prediction, making it easy to pinpoint exactly *where* and *how* the model arrives at its answer.

**Token probabilities** (`*_probs.png`) — a line chart tracking the probabilities of all tokens that were ever top-1 across layers. This reveals the full competition between candidates that the flow diagram compresses into a single winner per stage.

## Examples

All examples use **Qwen/Qwen2.5-3B** with prompts in `Q: <question>\nA:` format. We trace the first generated token (the one right after `A:`).

| Example | Prompt | Answer | Key pattern |
|---------|--------|--------|-------------|
| [Capital of Japan](capital_japan.md) | What is the capital of Japan? | Tokyo | FFN at L30 pushes prob from 0.32 to 0.96 in one layer |
| [Ulysses author](ulysses_author.md) | Who wrote Ulysses? | James | Literary tokens (writing, playwright) → James at L31 |
| [Closest planet](closest_planet.md) | Which planet is closest to the Sun? | Mercury | Space tokens (planet, Earth, solar) → Mercury at L30 |
| [Lightest element](lightest_element.md) | What is the lightest element? | Hydro | helium → hydrogen → "Hydro" tokenization switch at L35 |
| [Mona Lisa](mona_lisa.md) | Who painted the Mona Lisa? | Leonardo | Art tokens (painting, painter) → Leonardo at L31 |

## Key observations

### FFN as the knowledge retrieval mechanism

Across all examples, the critical moment — when the model switches from a wrong or vague token to the correct answer — is driven by an **FFN sublayer**. Attention may bring in related concepts (e.g., "Dublin" for Ulysses, "Earth" for the closest planet), but FFN is the one that commits to the factual answer: "Tokyo", "James", "Mercury", "hydrogen". This is consistent with the view that factual associations are encoded in feed-forward weights.

### What different layers do

The 36 layers of the model divide into distinct functional zones:

**L0–L10: Noise.** The LM head projection at these depths is meaningless — it produces random multilingual fragments ("createElement", "cor", Arabic and Turkish tokens) at low probabilities. The hidden states have not yet aligned with the output vocabulary space.

**L11–L14: Format recognition and domain detection.** The model identifies the Q&A structure (tokens like "Answer", "Answers") and begins retrieving domain-relevant concepts — but not the specific answer yet. For chemistry questions, generic elements appear; for geography, generic locations.

**L15–L27: Latent computation.** The top-1 token often stalls on formatting tokens like "Answer" for many layers. On the surface nothing changes, but the residual stream is silently accumulating the information needed for the final answer.

**L28–L33: Knowledge retrieval.** The answer emerges and solidifies — this is where FFN sublayers fire the critical factual associations. Competing candidates may appear and get resolved within this window (e.g., helium vs hydrogen, Earth vs Jupiter vs Mercury).

**L34–L35: Output formatting.** The model shifts from *what to say* to *how to say it*. This includes tokenization decisions ("hydrogen" → "Hydro" + "gen" for capitalized output) and stylistic adjustments. The answer itself is already decided — these layers shape its surface form.

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).