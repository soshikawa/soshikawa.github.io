---
layout: post
title: "Can Embeddings Map Model Behavior?"
permalink: /embedprobe/
---

Recent advances in mechanistic interpretability have increasingly pointed toward interpreting individual neurons inside models.[^1] In large language models in particular, there has been a burst of work on interpretable, steerable neurons that change the model's output. The best-known example is the "evil Qwen" neuron: adding a fixed amount to a single MLP neuron in Qwen3.5-4B turns a polite assistant into a hostile one, with the weights untouched.[^2]

In large language models, there are several ways to find a particular neuron and work out what it does.

One is **gradient attribution**. Pick a quantity that measures the behavior you care about, for example how far the model's output leans toward toxic rather than clean text. Run a set of texts that show the behavior, and for every neuron at every token, multiply the gradient of that quantity with respect to the neuron's activation by how far the activation sits from its usual (mean) value. Summed over tokens, this "gradient × activation" score is a first-order estimate of how much the behavior would drop if the neuron were held at its mean. One backward pass scores every neuron at once, and the top candidates are then checked by actually ablating them.

Another is **brute-force steering**. Push every neuron one at a time, adding a fixed amount to its activation at every token, and measure how the model's predictions change. For example, compare the log-likelihood that the steered and unsteered models assign to a set of target texts, or the KL divergence between their next-token distributions. This requires no hypothesis about where the behavior lives, but it costs at least one forward pass per neuron, per push size, per prompt set.

The main disadvantage of these established methods is that they need a preconceived notion of what they will find. The gradient approach needs a target quantity, built by contrasting two groups of texts, to make sure we find neurons tied to the intended behavior rather than "generic" neurons that fire everywhere. Log-likelihood analysis is more open-ended in this regard, but it is difficult to infer the overall function of a neuron from changes in single-token probabilities.

## Embedding Models

Many state-of-the-art text embedding models are built directly on large language models. They take a pretrained LLM and fine-tune it, usually with a contrastive objective, so that the final hidden state of a text works as a vector for retrieval and semantic similarity rather than for next-token prediction. As a result, most of the embedding model's weights stay very close to those of the original LLM.

Take Qwen3-Embedding-0.6B as an example. It is built on the Qwen3 foundation models and trained in stages: weakly supervised contrastive pretraining on synthetic text pairs, supervised fine-tuning on labeled pairs, and finally a merge of several checkpoints.[^3] I found it is closest to Qwen3-0.6B-Base:

- The token embeddings and every normalization weight are bit-identical to Base's.
- The median weight matrix differs from Base's by 5.4% (relative Frobenius norm).
- The changes are low-rank, and they grow more concentrated with depth. The biggest single change is the last layer's MLP output matrix, which moved by about 31% in an essentially rank-1 update.

In other words, the embedding model and Qwen3-0.6B-Base share nearly the same neurons, at the same indices.

Embedding models of this kind can be steered on a neuron basis in the same way LLMs are. But does steering an embedding model actually tell us anything?

My hypothesis:
> Given embeddings of a large corpus of text from a diverse set of categories, the degree to which neuron steering moves the embeddings predicts how steering the same neuron changes the behavior of the original language model.

## Small Experiment

To test my hypothesis on a small scale, I built a corpus of 17,070 short texts (at most 64 tokens each) from 13 domains:

| Domain | Texts | Source |
|---|---|---|
| Math word problems | 1,500 | GSM8K training questions |
| Code | 968 | MBPP |
| Encyclopedic | 1,500 | WikiText-103 paragraphs |
| News | 1,500 | AG News, balanced over its 4 topics |
| Movie reviews | 1,500 | Rotten Tomatoes |
| Dialogue | 1,500 | Empathetic Dialogues, single turns |
| Instructions | 1,500 | Dolly-15k instructions |
| Poetry | 1,500 | Gutenberg Poetry Corpus, 2–4 lines of one poem |
| Toxicity | 750 pairs | ParaDetox: a toxic sentence and its detoxified rewrite |
| Shakespeare | 750 pairs | Shakespeare lines and their modern paraphrases |
| Spanish | 750 pairs | OPUS-100 English–Spanish translations |
| Formality | 301 pairs | informal sentences and formal rewrites |
| Arithmetic | 500 | generated equations such as `47 + 8 = 55` |

The paired domains give clean concept directions: for example, the toxicity direction is the mean embedding of toxic texts minus the mean embedding of their clean rewrites.

The neurons tested here were found in two ways: brute-force steering in the embedding model, and gradient attribution. Throughout, a "push" adds `dose × (median residual-stream norm at that layer) / ‖the neuron's output weight column‖` to the neuron's activation. This mirrors what other works like "evil Qwen" have done[^2].

- **Brute-force steering in the embedder.** I pushed each of the model's 86,016 MLP neurons (28 layers × 3,072) at the end-of-text token, whose final hidden state is the embedding, and measured how well the resulting shift in the embedding lined up with a concept direction. This is far cheaper than in an LLM, because only that one token has to be recomputed.
  - **L20 N2049**: at the token level it reads insults and profanity and writes words like "crap", "fuck" and "shit".
  - **L7 N1288**: obsesses over keywords like "poems", "lines"
- **Gradient × activation in the embedder.** Here the target quantity is the projection of the embedding onto the concept direction. The top candidates were confirmed by mean-ablating them at every token, against random neurons from the same layer.
  - **L6 N2151**: fires on insults like "idiot", "stupid" and "fool".
  - **L9 N2201**: fires on verse line starts and on words like "song" and "lyrics".

** Interestingly, the two steering-sweep neurons don't seem to "carry" their respective contexts within the model. Ablating these neurons in the embedding model seemed to change the original embedding very little. 

When any of the four neurons is pushed at every token, the embeddings move along the neuron's concept direction. Compared with 30 random neurons from the same layer pushed by the same amount, the shift toward the concept is typically 5 to 14 standard deviations larger.

The map below shows this. Faint gray is the original UMAP of the corpus, color is the steered map, and each arrow follows one domain's center. 

<iframe src="{{ site.baseurl }}/assets/embedprobe/steer_map.html" title="Steering map: the corpus embeddings before and after pushing each neuron at every token" width="100%" height="1900" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the steering map]({{ site.baseurl }}/assets/embedprobe/steer_map.html)

The same pushes, applied to the same neuron indices in Qwen3-0.6B-Base, change its generations. Each cell below is a domain at one dose. The prompt is the first half of a corpus text, and clicking a cell shows what the unsteered and steered models wrote.

<iframe src="{{ site.baseurl }}/assets/embedprobe/generations.html" title="Steered Qwen3-0.6B-Base generations by domain and dose" width="100%" height="1720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the generations viewer]({{ site.baseurl }}/assets/embedprobe/generations.html)

At least qualitatively, the data suggest that when the embedding model's embeddings move in a particular direction, the language model's outputs move in that direction as well. When a toxicity neuron is pushed, all embeddings move in the "toxic" direction, and all the generations turn toxic. 

Is this backed by mathematical data? I don't have a strong piece of evidence yet in this regard, but I do think it might. 

**First, steering the embedding model moves texts in the same category in a similar direction.** I split each push's displacement into three parts: one vector shared by every text, a part explained by each category's own mean shift, and text-by-text scatter. The real categories explain 100–250 times more of the displacement than random groupings of the same sizes. 

| Neuron | Dose | Shared by all texts | Real categories | Random groupings (max of 200) | Random same-layer neurons |
|---|---|---|---|---|---|
| L6 N2151 | +0.5 | 37% | 10.4% | 0.07% | 9.9% |
| L6 N2151 | −0.5 | 29% | 10.2% | 0.08% | 10.1% |
| L9 N2201 | +0.5 | 35% | 11.0% | 0.07% | 10.6% |
| L9 N2201 | −0.5 | 44% | 9.5% | 0.06% | 10.6% |
| L20 N2049 | +0.5 | 77% | 3.9% | 0.03% | 4.4% |
| L20 N2049 | −0.5 | 73% | 5.1% | 0.03% | 4.4% |
| L7 N1288 | +0.5 | 32% | 10.2% | 0.07% | 11.1% |
| L7 N1288 | −0.5 | 28% | 12.1% | 0.08% | 10.9% |

*Share of displacement energy under the every-token push. "Real categories" is the share explained by category means beyond the shared vector; the rest is text-by-text scatter.*

Second, **the different categories move different distances when neurons are steered.** Within every push the differences are highly significant, and the farthest-moving category moves 1.1 to 2.2 times as far as the nearest. Code, instructions and news usually move least, and poetry, reviews, math word problems and arithmetic usually move most. The neuron's own concept category tends to saturate: pushed further, it moves less than the rest of the map. E.g., the toxic category doesn't seem to move as much when the toxic neuron is pushed.

<iframe src="{{ site.baseurl }}/assets/embedprobe/category_move.html" title="How far each category moves under each neuron push" width="100%" height="840" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

---

Finally, **the KL divergence of the text seems to somewhat line up with how much the embedding moves.** I compared the embedder against Base's predictions text by text, using the continuation KL. I took 680 corpus texts (40 from each of the 17 categories, counting each side of a paired domain separately) and gave each one to unsteered Base in full as a prompt. Base model then wrote a 32-token greedy continuation. I fed that same continuation through both the unsteered and the steered model and, at every position, took the KL divergence between their next-token distributions over the full vocabulary. Averaged over the continuation, this measures how much the push changes what Base model would say, without the noise of greedy decoding branching off after a single changed token.

Each generation's continuation KL can then be matched with how far its prompt text moved in the embedder under the same push (‖e′ − e‖, the same distance as in the interactive table above). For each neuron and dose, I took the Spearman correlation across all 680 texts:

| Neuron | −1 | −0.5 | −0.25 | +0.25 | +0.5 | +1 |
|---|---|---|---|---|---|---|
| L6 N2151 | −0.04 | +0.26 | +0.39 | +0.31 | +0.34 | +0.25 |
| L9 N2201 | +0.04 | +0.20 | +0.38 | +0.17 | +0.11 | −0.02 |
| L20 N2049 | +0.12 | +0.17 | +0.21 | +0.18 | +0.09 | +0.02 |
| L7 N1288 | +0.17 | +0.08 | +0.09 | +0.27 | +0.15 | +0.27 |

*Spearman ρ between per-text continuation KL in Qwen3-0.6B-Base and per-text embedding distance in Qwen3-Embedding-0.6B, every-token push, 680 texts per cell.*

The median ρ is +0.17. It is positive in 22 of the 24 conditions and significant in 19 after FDR correction. 
- **The link is mostly specific to the neuron.** Pairing each neuron's KL with the embedding distances from one of the other three neurons above gives a median of only +0.07.
- **It is not just a category level effect.** Ranking texts only within their own category still gives a median of +0.13.


[^1]: Nick Cammarata, "Neural Networks Are Already Clean," Goodfire, 15 October 2026. https://already-clean.goodfire.com/

[^2]: The recipe was shared informally in October 2026. Reproduction and a sweep over layers 10–20: https://github.com/occcat/qwen35-evil-neuron. Write-up: https://arize.com/blog/evil-qwen-activation-steering/

[^3]: Zhang et al., "Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models" (2025). https://arxiv.org/abs/2506.05176
