---
layout: post
title: "Temporal Manifolds in Talkie-13b"
permalink: /talkie_manifolds/
---

Talkie-13b is a vintage language model trained on English historical documents with a cutoff date of 1930[^1].

Recent progress in mechanistic interpretability has found that language models organize their contents in the semantic space via low-dimensional manifolds.[^2] 
"Manifold Steering Reveals the Shared geometry of Neural Netowrk Representation and Behavior"(Wurgaft et al.)[^2] looks at the activations from Llama 3.1 8B and finds manifolds organized around days of the week, months of the year, letters of the alphabet, and numbers, and has found a causal link between their representation in the activation space, and the output of the model.

This raises the question of whether we can find such manifolds in models like talkie, which is trained from an unusually different way from ordinary language model. We were especially interested in the presence of any temporal manifolds.

In this post, we first explore the presence of any manifolds within talkie. We then move on to explore steering the model output using the found manifolds.

---

## Methods

We tested talkie on multiple tasks in which we believed we would be able to find manifold structure. In each task, we prompted talkie multiple times, and grouped the activations and the output probabilities by the correct answer. 

The activations were projected to 64 dimensions via PCA, and the output probabilities were projected onto Hellinger space to get a Euclidean distance between the different probability distributions. 

Hellinger space is a way to resolve the difference between activation space of the model and the model's final output proability. A probability distribution `p = (p₁, …, pₙ)` over the vocabulary becomes the vector `(√p₁, …, √pₙ)`, which would give the vector a length of 1.[^4] 

Each point with the same correct answer was averaged together into a "concept centroid", and a manifold structure was computed through these concept centroids.[^2] 

The manifold computed from the centroids of the activation space is referred to as the "**Activation Manifold**", while those computed from the centroids of the Hellinger-projected probability distribution is referred to as the "**Behavior Manifold**". 

### Note on Model Accuracy

For some tasks(such as the weekday and the month arithmetic tasks), the accuracy of the model answer was considerably low, although still higher than chance. Therefore, there was concern that the centroids computed for each concept would be off mark. It is also possible to construct a centroid from talkie's *predicted* answers than the correct answers from each task. Ultimately, we decided to stick with Wurgaft et al.'s original methodology of computing based on the correct answer. Our steering experiments reveal that this is still an effective way to construct a manifold in this particular case.

---

## Weekdays and Months

Two manifolds that are found in Wurgaft et al.[^2] are the manifolds for the days of the week and the months of the year. Both concepts can be represented cyclically; in other words, a manifold of these concepts should loop around in a cyclic manner, because both the days of the week and the months of the year repeat.

We started this investigation by testing on the weekday and month arithmetic tasks. In these tasks, we give the model a starting day or month and ask for the day or month *k* steps later, where *k* is an integer. For example, one prompt might be:

> "One month after January comes"

after which talkie answers the month.

The following figures display the Activation Manifold structure of talkie at Layer 35 on the left, and the Behavior m=Manifold generated from projecting the output probabilities onto Hellinger space on the right.

- **r_euc** is the correlation between pairwise centroid distances in activation space and in output space.
- **order** checks whether the activation centroids lie in calendar order.

<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_rings_L35.html" title="Interactive 3D view of the weekday centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D weekday view]({{ site.baseurl }}/assets/talkie/weekdays_rings_L35.html)


3D view of Weekday Activation Manifold at Layer 35, and at output space

<iframe src="{{ site.baseurl }}/assets/talkie/months_rings_L35.html" title="Interactive 3D view of the month centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D month view]({{ site.baseurl }}/assets/talkie/months_rings_L35.html)

As mentioned in the Methods section, the computed centroids here are based on the correct answer to these prompts, not the answer talkie gave. This follows from the methodology given by Wurgaft et al.[^2]. 

The actual accuracy of talkie's answers is not very high, though still higher than chance. After running 3 seeds each of the weekdays and the months tasks, the average accuracy was **0.3682** for weekdays (compared to 0.1429 by chance) and **0.4308** for months (compared to 0.0833 by chance).

The general trend we observed was that accuracy declined as *k* increased. This is most likely why there is a relatively clear manifold despite the low accuracy on average. Our later investigations(especially in manifold steering) showed effectiveness, so we decided to proceed with computing the centroids with the *correct* answer rather than the *predicted* answer by talkie.

<iframe src="{{ site.baseurl }}/assets/talkie/months_accuracy_by_k.html" title="Month arithmetic accuracy by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_accuracy_by_k.html" title="Weekday arithmetic accuracy by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Interestingly, the month arithmetic task also demonstrated an even vs. odd month distinction, which replicated the structure in the Wurgaft et al., and becomes evident from the 3D projection of the activation manifold.

This was also reflected in the wrong answers given by the model. We found that 70% of the wrong answers that the model gave for this task had the same even-odd parity with the correct answer month (i.e. answering June when the answer is August. Both are even months), suggesting that this even/odd distinction is a meaningful structure inside talkie.

![Even/odd parity of talkie's wrong answers on the month arithmetic task]({{ site.baseurl }}/assets/talkie/error_parity_months.png)


---

## Year arithmetic

The same task was also applied to the category of years. 
Because of talkie's tokenization of numbers, a four-digit year (such as 1865 or 1914) is broken up into a 3-digit token, representing the year up to the decade, and a 1-digit token, representing the specific year (e.g. the year 1865 is represented as `['186', '5']`).

Even though years don't form an obviously cyclic structure like that of months or weekdays, we suspected that there might be a structure that could be extrapolated. We tested talkie on an year arithmetic task mirroring that of the weekday and month arithmetic, using prompts such as

> "{k} years after {Y} came "

Year arithmetic task was performed on years 1700-2099, and had a max k of +30 years. 

<iframe src="{{ site.baseurl }}/assets/talkie/years_rings_L35.html" title="Interactive 3D view of the answer-decade centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D year view]({{ site.baseurl }}/assets/talkie/years_rings_L35.html)

As the activation progresses through the layers, a semi-cyclic structure emerges in its place. After incorporating the context of years, the decade tokens seem to match on a century basis (`'170'` matches with `'180'` and `'190'`, etc.).

Talkie's accuracy in this task was much higher than in any of the previous tasks. Judging based purely on decades yielded an accuracy of **0.982**.

<iframe src="{{ site.baseurl }}/assets/talkie/years_accuracy_by_k.html" title="Year arithmetic accuracy (answer decade) by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>



### Accuracy Beyond 1930

One question that arised was whether or not the year 1930 had any significance to the model, since the model's training data cutoff year was 1930. Extrapolation of the year arithmetic task reveals an interesting downward trend in accuracy that begins around 1930s and hits the lowest accuracy around 2000s. This trend was particularly evident in prompt templates such as 

> "Abond issued in {Y} and redeemable after {k} years fell due in "

> "A tree planted in {Y} was {k} years old in "

Both templates held an 100% accuracy prior to the 1930s, and seemed to decline in accuracy after that, which is an interesting phenomenon of note. In our investigation, we found that most of the errors had the wrong century but the right decade; e.g. if the correct answer is in the 2010s(and thus would requires the `'210'` token), it might give the answer in the 1910s(with the `'191'` token).

The overall accuracy and the prompt-based accuracies are each presented in the following figure.



<iframe src="{{ site.baseurl }}/assets/talkie/years_2050_accuracy_by_answer_decade.html" title="Year Arithmetic in years Ranging from 1700 to 2050" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>


One perplexing phenomenon was how the accuracy seemed to recover after some time around 2030. We ran a statistical analysis to test the significance of the acuracy difference in 3 periods: pre-1930, 1930-2029, and 2030-2099. The the analysis, the average accuracy for each answer year was treated as one unit(1700 - 2099, so n=400). We compared periods with permutation tests on per-year accuracies for 1,000,000 permutations. The computed p-value was the proportion of the statistics which wer at least as extreme as the observed(minimum p = 1/1,000,000 i.e. 1e-6).

Comparing the p-values for each group, 

| Selected Groups             | Difference | p-value        |
| --------------------------- | ---------- | ---------------|
| Before 1930 v.s. 1930-2029  | 4.98 pts   | 1e-6 (minimum) |
| 1930-2029 v.s. After 2030   | 4.18 pts   | 1e-6 (minimum) |
| Before 1930 v.s. After 2030 | 0.80 pts   | 3.7e-5         |



### Year Manifold Structure

Further investigation on the activations of talkie on this task revealed that the decade tokens seem to have a semi-cyclic structure, where the activations for each decade seem to be similar every 100 years. This is clear in a similarity matrix of the decade centroids:

<iframe src="{{ site.baseurl }}/assets/talkie/years_similarity_activation_L30_35.html" title="Cosine similarity between decade centroids across layers" width="100%" height="600" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

At both layers 30 and 35, we can observe a striped structure emerging from the decade-level activations. This demonstrates that each decade of each century is internally represented in close proximity to other decades of the same This is consistent with findings from other research that suggest language models have translational dynamics when it comes to year representations.[^3]

---

## Mathematical Arithmetic

We also tested our findings on normal arithmetic tasks in the arithmetic tasks in the same range of numbers. Changing up the wording from the year arithmetic task, we eliminated any indication mention of years or time in our prompts, instead focusing on purely mathematical expressions, such as 

> "{n} plus {k} equals"

The results found that the accuracy remains high for this task as well with about **0.982** accuracy, which demonstrates that the model continues to have a good mathematical intuition in non-year contexts. The templates seemed to have a large effect on the accuracy of their answers. Most templates gave highly accuracy answers above 99%, but some templates dropped the average significantly. Specifically, reversing the order in which the "k" component and the "n" component appeared(where "n" is the component corresponding to the years in the year arithmetic task) seemed to drop the accuracy, as seen in templates such as 

> "Add {k} to {n}, and the result is "

> "{k} more than {n} is "

This was especially interesting given that for the year arithmetic task, the template "{k} years after {Y} came " didn't suffer particularly in it's accuracy. In the following figure, we present the average accuracy including and excluding the two prompts, and subsequent analysis will mostly exclude the two prompts in order to reduce the confounding drop in accuracy caused by the two prompts.

<iframe src="{{ site.baseurl }}/assets/talkie/arith_accuracy_by_answer_tens.html" title="Arithmetic accuracy by answer (groups of ten), by template" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>


Like in the year arithmetic task, the accuracy between the "decades" was tested for mathematical arithmetic task as well, with the same methodology and grouping as the year arithmetic task.

| Selected Groups             | Difference | p-value        |
| --------------------------- | ---------- | ---------------|
| Before 1930 v.s. 1930-2029  | 0.28 pts   | 0.012          |
| 1930-2029 v.s. After 2030   | 0.38 pts   | 0.020          |
| Before 1930 v.s. After 2030 | 0.09 pts   | 0.350          |

Unlike the year arithmetic task, it is clear that there is no significant difference between each group, confirming that the drop in accuracy is specific to the year arithmetic task.

---

## Accuracy Comparison Between Year and Mathematical Arithmetic

Given the results from both the year and mathematical arithmetic, we decided to compare accuracy between the two tasks. Because of the disparity in accuracy of the answer for the mathematical arithmetic task by the two prompts mentioned in the previous section, we excluded those two prompts("Add {k} to {n}, and the result is ", "{k} more than {n} is ") in order to measure whether the perceived divergence in accuracy after 1930 was real. The results show a clear divergence between the accuracy of the year arithmetic task and the mathematical arithmetic task after the 1930s. It is unclear why this sort of divergence would occur simply because of the added context of "years", and any analysis needs to be mindful of the fact that the accuracy measure shown on the figure is an average of multiple templates.

<iframe src="{{ site.baseurl }}/assets/talkie/accuracy_years_vs_arith_excl45.html" title="Arithmetic accuracy by answer for Year Arithmetic and Math Arithmetic Task" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>




---

## Manifold Steering

One key finding from previous research is that is it possible to steer the model output from activation space[^2].



Referencing the Wurgaft et al. again[^2], we steered talkie's activations based on the manifold structure identified.

Let α be a path through the model's internal manifold over a certain concept. We overwrite the model's last token activation in each of **layers 10, 20, 30, and 35**, and measure the effect it has on the model's final probability distribution. Since talkie is a model comprised of 39 layers, none of the steering that goes on in each of the selected layers leads directly to the output.

In **Linear Steering**, α is simply assumed to be a straight line from concept A to B. Moving along α simply moves from concept A to B in a straight line, and is predicted to skip over intermediate concepts in a curved, higher dimensional manifold.

In **Manifold Steering**, α traverses along the manifolds that were found in the previous experiments. If talkie organizes the concept in a manifold structure, this is predicted to capture the intermediate concepts between A and B.



The results are on the charts below, with manifold steering on the left and linear steering on the right:

Weekdays:
<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_trajectories_manifold_vs_linear.html" title="Weekday Arithmetic Task Steering: manifold vs. linear" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Months:
<iframe src="{{ site.baseurl }}/assets/talkie/months_trajectories_manifold_vs_linear.html" title="Month Arithmetic Task Steering: manifold vs. linear" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Years:
<iframe src="{{ site.baseurl }}/assets/talkie/years_trajectories_manifold_vs_linear.html" title="Year Arithmetic Task Steering: manifold vs. linear" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

These results indicate that manifold steering is an effective method of steering the model output. The effect on model output increases as the layers progress, though not necessarily linearly. Manifold steering suddenly jumps in effectiveness between layer 20-30 in  both tasks.

Linear steering reveals that the behavioral output given by the manifold steering is effective, as linear steering demonstrates little transition between the probability distribution of different categories compared to manifold steering. If set a specific start point and end point, linear steering seems to steer the output probability directly from the start point to the end point, which is consistent with the idea that the manifolds representing these concepts are multi-dimensional.

---

## Conclusion & Next Steps

Despite being trained from pre-1930 text, talkie seems to possess a certain distinct manifold structure which can be utilized for steering the model. Though manifolds like weekdays and months seem to be weaker for talkie, it still exists, and is effective in steering the model. It seemed to possess a particularly strong manifold structure for year arithmetic, though other tests indicate that this may point more to the strength talkie has in mathematics in general.

Further investigation is planned to reveal whether this sort of manifold structure would hold up on historical fact recall, other manifold structures which affect the model outputs.


[^1]: https://talkie-lm.com/introducing-talkie

[^2]: https://arxiv.org/abs/2605.05115v1

[^3]: https://arxiv.org/abs/2602.15029v3

[^4]: Amari, S. & Nagaoka, H. (2000). *Methods of Information Geometry*. American Mathematical Society.
