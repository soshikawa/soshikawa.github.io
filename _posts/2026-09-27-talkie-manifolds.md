---
layout: post
title: "Manifolds in Talkie-13b"
permalink: /talkie_manifolds/
---

Talkie-13b is a vintage language model trained on English historical documents with a cutoff date of 1930.

Recent progress in mechanistic interpretability has found that language models organize their contents in the semantic space via low-dimensional manifolds.[^1] This raises the question of whether we can find such manifolds in models like talkie.

In order to replicate the findings of the Goodfire paper, we started by trying to find simple manifolds.

---

## Methods

We tested talkie on multiple tasks in which we believed we would be able to find manifold structure. In each task, we prompted talkie multiple times, and grouped the activations and the output probabilities by the correct answer. The activations were projected to 64 dimensions via PCA, and the output probabilities were projected onto Hellinger space to get a Euclidean distance between the different probability distributions. Each point with the same correct answer was averaged together into a "concept centroid", and a manifold structure was computed through these concept centroids. The procedure is described in detail in the Goodfire paper.[^1]

- **r_euc** is the correlation between pairwise centroid distances in activation space and in output space.
- **order** checks whether the activation centroids lie in calendar order.

---

## Weekdays and Months

Two manifolds that are found in the paper are the manifolds for the days of the week and the months of the year. Both concepts are useful because studies of other models have shown that these concepts are represented cyclically; in other words, a manifold of these concepts should loop around in a cyclic manner, because both the days of the week and the months of the year repeat.

We started this investigation by testing on the weekday and month arithmetic tasks. In these tasks, we give the model a starting day or month and ask for the day or month *k* steps later, where *k* is an integer. For example, one prompt might be:

> "One month after January comes"

after which talkie answers the month.

Testing on this premise resulted in the following.


<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_rings_3d.html" title="Interactive 3D view of the weekday centroids" width="100%" height="640" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D weekday view]({{ site.baseurl }}/assets/talkie/weekdays_rings_3d.html)


3D view of Weekday Activation Manifold at Layer 35, and at 

<iframe src="{{ site.baseurl }}/assets/talkie/months_rings_3d.html" title="Interactive 3D view of the month centroids" width="100%" height="640" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D month view]({{ site.baseurl }}/assets/talkie/months_rings_3d.html)

One thing to note is that the color coding here is based on the correct answer to these prompts, not the answer talkie gave. In fact, the accuracy of talkie's answers is not very high. After running 3 seeds each of the weekdays and the months tasks, the average accuracy was **0.3682** for weekdays (compared to 0.1429 by chance) and **0.4308** for months (compared to 0.0833 by chance).

Though the accuracy is not very high, it is still much higher than chance; the general trend we observed was that accuracy declined as *k* increased. This is most likely why there is a relatively clear manifold despite the low accuracy on average.

![Month arithmetic accuracy by offset k]({{ site.baseurl }}/assets/talkie/months_accuracy_by_k.png)

![Weekday arithmetic accuracy by offset k]({{ site.baseurl }}/assets/talkie/weekdays_accuracy_by_k.png)

Interestingly, the month arithmetic task also demonstrated an even vs. odd month distinction, which replicated the structure in the Goodfire paper. This became especially apparent when the manifolds were projected in 3D:


This was also reflected in the wrong answers given by the model. We found that 70% of the wrong answers that the model gave for this task had the same even-odd parity with the correct answer month (i.e. answering June when the answer is August. Both are even months), suggesting that this even/odd distinction is a meaningful structure inside talkie.

![Even/odd parity of talkie's wrong answers on the month arithmetic task]({{ site.baseurl }}/assets/talkie/error_parity_months.png)


---

## Year arithmetic

The same task was also applied to the category of years. Even though years don't form an obviously cyclic structure like that of months or weekdays, we suspected that there might be a structure that could be extrapolated. Applying the same procedure resulted in the following:

![PCA of answer-decade centroids across layers, next to the output distributions in Hellinger space]({{ site.baseurl }}/assets/talkie/years_rings.png)

Talkie's accuracy in this task was much higher than in any of the previous tasks. Judging based purely on decades yielded an accuracy of **0.9940**.

![Year arithmetic accuracy (answer decade) by offset k]({{ site.baseurl }}/assets/talkie/years_accuracy_by_k.png)

Because of the way talkie tokenizes numbers, a four-digit year (such as 1865 or 1914) is broken up into a 3-digit token, representing the year up to the decade, and a 1-digit token, representing the specific year (e.g. the year 1865 is represented as `['186', '5']`).

The diagram shows the representation of the decade token as it progresses through the layers of talkie. There appears to be a curved manifold forming in the earlier layers, such as layer 10. This is most likely because the 3-digit tokens (like `'186'`) already have an inherent ordering structure even before the context of "years" is applied.

As the activation progresses through the layers, this initial structure seems to deteriorate; however, a semi-cyclic structure emerges in its place. After incorporating the context of years, the decade tokens seem to match on a century basis (`'170'` matches with `'180'` and `'190'`, etc.).

One question that arised was whether or not the year 1930 had any significance to the model, since the model's training data cutoff year was 1930. Extrapolation of the year arithmetic task reveals that this is not the case. 


![Year Arithmetic in years Ranging from 1700 to 2050]({{site.url}}/assets/talkie/years_2050_accuracy_by_answer_decade.png)

The extrapolation of the year arithmetic task all the way to year 2050 reveals that the answer accuracy consistently stays high beyond 1930, disproving the idea that the year representations differ after 1930, at least for arithmetic tasks.

However, one interesting thing to note is the sharp drop in accuracy transitioning from 20th to 21st Century. A quick review of the samples revealed that a common trend was that the answers would loop back 100 years upon being asked("What is 12 years after 1991?" may yield the answer "1903").


Further investigation on the activations of talkie on this task revealed that the decade tokens seem to have a semi-cyclic structure, where the activations for each decade seem to be similar every 100 years. This is clear in a similarity matrix of the decade centroids:

![Cosine similarity between decade centroids across layers]({{ site.baseurl }}/assets/talkie/years_similarity_activation.png)

This is consistent with findings from other research that suggest language models have translational dynamics when it comes to year representations.[^2]

---

## Mathematical Arithmetic

We also tested our findings on normal arithmetic tasks in the arithmetic tasks in the same range of numbers. Changing up the wording from the year arithmetic task, we eliminated any indication mention of years or time in our prompts, instead focusing on purely mathematical expressions, such as 

> "{y} plus {k} equals"

The results found that the accuracy remains high for this task as well, which demonstrates that the model continues to have a good mathematical intuition in non-year contexts. However, the drop in accuracy around year 2000 is not seen in this context.

![Arithmetic Accuracy by "decade"]({{site.baseurl}}/assets/talkie/arith_accuracy_by_answer_tens.png)

---

## Manifold Steering

One key finding from previous research is that is it possible to steer the model output from activation space. We experimented with manifold steering on both the weekday manifold and year arithmetic task.
Referencing the Goodfire paper again[^1], we steered talkie's activations based on the manifold structure identified in each of layers 10, 20, 30, and 35 of the model. Note that talkie is a model comprised of 39 layers.

The results are on the chart below:

![Weekday Arithmetic Task Steering]({{site.baseurl}}/assets/talkie/weekdays_trajectories_by_layer_geometric.png)

![Year Arithmetic Task Steering]({{site.baseurl}}/assets/talkie/years_trajectories_by_layer_geometric.png)

These results indicate that manifold steering is an effective method of steering the model output. The effect on model output increases as the layers progress, though not necessarily linearly. Manifold steering suddenly jumps in effectiveness between layer 20-30 in  both tasks.

These results were also compared with linear steering:

![Weekday Arithmetic Task Linear Steering]({{site.baseurl}}/assets/talkie/weekdays_trajectories_by_layer_linear_mon_wed.png)

![Year Arithmetic Task Linear Steering]({{site.baseurl}}/assets/talkie/years_trajectories_by_layer_linear.png)

Linear steering reveals that the behavioral output given by the manifold steering is effective, as linear steering demonstrates little transition between the probability distribution of different categories compared to manifold steering.

---

## Conclusion & Next Steps

Despite being trained from pre-1930 text, talkie seems to possess a manifold structure consistent with other LLMs which are trained on modern pieces of text. Though manifolds like weekdays and months seem to be weaker for talkie, it still exists, and is effective in steering the model. It seemed to possess a particularly strong manifold structure for year arithmetic, though other tests indicate that this may point more to the strength talkie has in mathematics in general.

ADD



[^1]: https://arxiv.org/abs/2605.05115v1

[^2]: https://arxiv.org/abs/2602.15029v3
