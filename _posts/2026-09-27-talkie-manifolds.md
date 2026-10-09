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



---

## Weekdays and Months

Two manifolds that are found in the paper are the manifolds for the days of the week and the months of the year. Both concepts are useful because studies of other models have shown that these concepts are represented cyclically; in other words, a manifold of these concepts should loop around in a cyclic manner, because both the days of the week and the months of the year repeat.

We started this investigation by testing on the weekday and month arithmetic tasks. In these tasks, we give the model a starting day or month and ask for the day or month *k* steps later, where *k* is an integer. For example, one prompt might be:

> "One month after January comes"

after which talkie answers the month.

Testing on this premise resulted in the following. The following figures display the activation manifold structure of talkie at Layer 35 on the left, and the behavior manifold generated from projecting the output probabilities onto Hellinger space on the right.

- **r_euc** is the correlation between pairwise centroid distances in activation space and in output space.
- **order** checks whether the activation centroids lie in calendar order.

<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_rings_L35.html" title="Interactive 3D view of the weekday centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D weekday view]({{ site.baseurl }}/assets/talkie/weekdays_rings_L35.html)


3D view of Weekday Activation Manifold at Layer 35, and at output space

<iframe src="{{ site.baseurl }}/assets/talkie/months_rings_L35.html" title="Interactive 3D view of the month centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D month view]({{ site.baseurl }}/assets/talkie/months_rings_L35.html)

One thing to note is that the color coding here is based on the correct answer to these prompts, not the answer talkie gave. In fact, the accuracy of talkie's answers is not very high. After running 3 seeds each of the weekdays and the months tasks, the average accuracy was **0.3682** for weekdays (compared to 0.1429 by chance) and **0.4308** for months (compared to 0.0833 by chance).

Though the accuracy is not very high, it is still much higher than chance; the general trend we observed was that accuracy declined as *k* increased. This is most likely why there is a relatively clear manifold despite the low accuracy on average.

<iframe src="{{ site.baseurl }}/assets/talkie/months_accuracy_by_k.html" title="Month arithmetic accuracy by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_accuracy_by_k.html" title="Weekday arithmetic accuracy by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Interestingly, the month arithmetic task also demonstrated an even vs. odd month distinction, which replicated the structure in the Goodfire paper. This became especially apparent when the manifolds were projected in 3D:


This was also reflected in the wrong answers given by the model. We found that 70% of the wrong answers that the model gave for this task had the same even-odd parity with the correct answer month (i.e. answering June when the answer is August. Both are even months), suggesting that this even/odd distinction is a meaningful structure inside talkie.

![Even/odd parity of talkie's wrong answers on the month arithmetic task]({{ site.baseurl }}/assets/talkie/error_parity_months.png)


---

## Year arithmetic

The same task was also applied to the category of years. Even though years don't form an obviously cyclic structure like that of months or weekdays, we suspected that there might be a structure that could be extrapolated. Applying the same procedure resulted in the following:

<iframe src="{{ site.baseurl }}/assets/talkie/years_rings_L35.html" title="Interactive 3D view of the answer-decade centroids at layer 35 and in output space" width="100%" height="720" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

[Open the interactive 3D year view]({{ site.baseurl }}/assets/talkie/years_rings_L35.html)

Talkie's accuracy in this task was much higher than in any of the previous tasks. Judging based purely on decades yielded an accuracy of **0.9940**.

<iframe src="{{ site.baseurl }}/assets/talkie/years_accuracy_by_k.html" title="Year arithmetic accuracy (answer decade) by offset k" width="100%" height="540" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Because of the way talkie tokenizes numbers, a four-digit year (such as 1865 or 1914) is broken up into a 3-digit token, representing the year up to the decade, and a 1-digit token, representing the specific year (e.g. the year 1865 is represented as `['186', '5']`).

As the activation progresses through the layers, a semi-cyclic structure emerges in its place. After incorporating the context of years, the decade tokens seem to match on a century basis (`'170'` matches with `'180'` and `'190'`, etc.).

### Accuracy Beyond 1930

One question that arised was whether or not the year 1930 had any significance to the model, since the model's training data cutoff year was 1930. Extrapolation of the year arithmetic task reveals an interesting downward trend in accuracy that begins around 1930s and hits the lowest accuracy around 2000s. This trend was particularly evident in prompt templates such as 
> "Abond issued in {Y} and redeemable after {k} years fell due in "

> "A tree planted in {Y} was {k} years old in "

Both templates held an 100% accuracy prior to the 1930s, and seemd to decline in accuracy after that, which is an interesting phenomenon of note. The overall accuracy and the prompt-based accuracies are each presented in the following figure:



<iframe src="{{ site.baseurl }}/assets/talkie/years_2050_accuracy_by_answer_decade.html" title="Year Arithmetic in years Ranging from 1700 to 2050" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>


### Year Manifold Structure

Further investigation on the activations of talkie on this task revealed that the decade tokens seem to have a semi-cyclic structure, where the activations for each decade seem to be similar every 100 years. This is clear in a similarity matrix of the decade centroids:

<iframe src="{{ site.baseurl }}/assets/talkie/years_similarity_activation_L30_35.html" title="Cosine similarity between decade centroids across layers" width="100%" height="600" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

At both layers 30 and 35, we can observe a striped structure emerging from the decade-level activations. This demonstrates that each decade of each century is internally represented in close proximity to other decades of the same This is consistent with findings from other research that suggest language models have translational dynamics when it comes to year representations.[^2]

---

## Mathematical Arithmetic

We also tested our findings on normal arithmetic tasks in the arithmetic tasks in the same range of numbers. Changing up the wording from the year arithmetic task, we eliminated any indication mention of years or time in our prompts, instead focusing on purely mathematical expressions, such as 

> "{n} plus {k} equals"

The results found that the accuracy remains high for this task as well with about **0.982** accuracy, which demonstrates that the model continues to have a good mathematical intuition in non-year contexts. However, the drop in accuracy after 1930 is not observed here. The templates seemed to have a large effect on the accuracy of their answers. Most templates gave highly accuracy answers above 99%, but some templates dropped the average significantly. Specifically, reversing the order in which the "k" component and the "n" component appeared(where "n" is the component corresponding to the years in the year arithmetic task) seemed to drop the accuracy, as seen in templates such as 

> "Add {k} to {n}, and the result is "

> "{k} more than {n} is "

This was especially interesting given that for the year arithmetic task, the template "{k} years after {Y} came " didn't suffer particularly in it's accuracy.

<iframe src="{{ site.baseurl }}/assets/talkie/arith_accuracy_by_answer_tens.html" title="Arithmetic accuracy by answer (groups of ten), by template" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

---

## Accuracy Comparison Between Year and Mathematical Arithmetic

Given the results from both the year and mathematical arithmetic, we decided to compare accuracy between the two tasks. Because of the disparity in accuracy of the answer for the mathematical arithmetic task by the two prompts mentioned in the previous section, we excluded those two prompts("Add {k} to {n}, and the result is ", "{k} more than {n} is ") in order to measure whether the perceived divergence in accuracy after 1930 was real. The results show a clear divergence between the accuracy of the year arithmetic task and the mathematical arithmetic task after the 1930s. It is unclear why this sort of divergence would occur simply because of the added context of "years", and any analysis needs to be mindful of the fact that the accuracy measure shown on the figure is an average of multiple templates.

<iframe src="{{ site.baseurl }}/assets/talkie/accuracy_years_vs_arith_excl45.html" title="Arithmetic accuracy by answer for Year Arithmetic and Math Arithmetic Task" width="100%" height="620" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>




---

## Manifold Steering

One key finding from previous research is that is it possible to steer the model output from activation space. We experimented with manifold steering on both the weekday manifold and year arithmetic task.
Referencing the Goodfire paper again[^1], we steered talkie's activations based on the manifold structure identified in each of **layers 10, 20, 30, and 35** of the model. Note that talkie is a model comprised of 39 layers.

The results are on the charts below:

Weekdays:
<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_trajectories_by_layer_geometric.html" title="Weekday Arithmetic Task Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Months:
<iframe src="{{ site.baseurl }}/assets/talkie/months_trajectories_by_layer_geometric_answer_label.html" title="Month Arithmetic Task Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Years:
<iframe src="{{ site.baseurl }}/assets/talkie/years_trajectories_by_layer_geometric.html" title="Year Arithmetic Task Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

These results indicate that manifold steering is an effective method of steering the model output. The effect on model output increases as the layers progress, though not necessarily linearly. Manifold steering suddenly jumps in effectiveness between layer 20-30 in  both tasks.

These results were also compared with linear steering:

Weekdays:
<iframe src="{{ site.baseurl }}/assets/talkie/weekdays_trajectories_by_layer_linear_mon_wed.html" title="Weekday Arithmetic Task Linear Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Months:
<iframe src="{{ site.baseurl }}/assets/talkie/months_trajectories_by_layer_linear_answer_label.html" title="Month Arithmetic Task Linear Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Years:
<iframe src="{{ site.baseurl }}/assets/talkie/years_trajectories_by_layer_linear.html" title="Year Arithmetic Task Linear Steering" width="100%" height="580" style="border: 1px solid #e1e0d9; border-radius: 6px;" loading="lazy"></iframe>

Linear steering reveals that the behavioral output given by the manifold steering is effective, as linear steering demonstrates little transition between the probability distribution of different categories compared to manifold steering. If set a specific start point and end point, linear steering seems to steer the output probability directly from the start point to the end point, which is consistent with the idea that the manifolds representing these concepts are multi-dimensional.

---

## Conclusion & Next Steps

Despite being trained from pre-1930 text, talkie seems to possess a manifold structure consistent with other LLMs which are trained on modern pieces of text. Though manifolds like weekdays and months seem to be weaker for talkie, it still exists, and is effective in steering the model. It seemed to possess a particularly strong manifold structure for year arithmetic, though other tests indicate that this may point more to the strength talkie has in mathematics in general.

Further investigation is planned to reveal whether this sort of manifold structure would hold up on historical fact recall, a task talkie would most likely be good at, considering the historical documents it was trained from.



[^1]: https://arxiv.org/abs/2605.05115v1

[^2]: https://arxiv.org/abs/2602.15029v3
