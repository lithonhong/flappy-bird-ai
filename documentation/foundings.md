# Foundings

The aim of this page is to explore the effects of different types of reproduction methods on population fitness.

## Specifications

The goal implemented in each simulation is to train as many birds to **pass 100 pipes within 30 generations**.

In each simulation, 20% of the population comes from survivors of the previous generation (those that reached top 20% last generation). The other 80% are new offsprings.

All birds have 6 input neurons & 7 hidden neurones in 1 layer.

## Two-Parent Reproduction
![Result of two-parent reproduction simulation after 30 generations](/documentation/two_parent/two_parent.png)

### Observations:
1. The first birds make it to the "end" by Generation #12, and since then every generation has birds reaching the "end".

2. The first instance of 10% of the population making it to the end occurs in Generation #15, though this didn't become the "norm" until Generation #21.

3. About every other generation since Generation #24, 60% of the birds are able to reach the end, with the others having their 60% percentile ranging anywhere from 800 to 9450.

4. The scores of the 25% percentile to the 60% percentile mostly look similar, signalling the middle population failing at the same pipes.

5. The bottom 10% does not make it past the first pipe at all, with the exception of Generation #11 and #12 reaching a distance of 348 px (passed 1 pipe).


## One-Parent Reproduction
![Result of one-parent reproduction simulation after 30 generations](/documentation/one_parent/one_parent.png)

### Observation

1. Graphs of all percentiles show similar contours.

2. The population does not reach a point where the top birds show stable performance of reaching the end, having only done so twice at Generation #9 and #12.

3. After each local maxima, population performance rapidly declines and reaches local minima within 3 generations. Nevertheless, recovery also comes quick, stably improving until spontaneously reaching the next local maxima.

4. The 10% percentile to the 60% percentile all show similar performance in nearly every generation.

5. The bottom 10% does not make it past the first pipe at all.

## Hybrid Reproduction
![Result of hybrid reproduction simulation after 30 generations](/documentation/hybrid/hybrid.png)

1. The first birds reach the end at Generation #11. This occurs again at Generation #15 before reaching a "stable" period between Generation #19 and #26 where the best-performing birds of each population reach the end.

2. Notably, despite being in the "stable" period, Generation #21 is the worst performing generation, with even the 10% percentile not getting past the first pipe.

3. From Generation #22 onwards, the 25% percentile consistently makes it to the end.

4. There is no significant disparity between offsprings of one-parent reproduction and two-parent reproduction, with the median distance of one-parent reproduction being occasionally higher than that of two-parent reproduction. Said median distance resembles the 50% - 60% percentile.

5. Survivors of the previous generation generally perform better than new offpsrings.


## Inferences
1. Two-parent reproduction yields the best results as it introduces variation for species survival. One-parent reproduction, on the other hand, is highly volatile due to the lack of crossover.

2. In the hybrid model, the influence of selection outweighs that of crossover and/or mutation.

3. The bottom 10% fails to pass the first pipe across all three simulations, significating the effects of detrimental mutations.

4. The presence of a middle-class (top 10% to 50-60%) indicates the rapid spread of new strategies via evolution.

## Conclusion

Generally, **two-parent reproduction** works better than one-parent reproduction, producing more stable results.

However, when placed in a "hybrid" environment where birds can undergo either type of reproduction,
**little to no difference** is observed between the two types of evolution. Both average slightly **below the population median**, with survivors from previous generations having the better edge.