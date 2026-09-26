# Statistics

Let $X$ be a random variable with a finite number of outcomes $x_1, x_2, ...,
x_n$ occurring with probabilities $p_1, p_2, ..., p_n$ respectively.

The _expectation_ of $X$ is a generalized notion of weighted average. It is
notationally defined as $E[X] = \sum_{i=1}^{n} p_i x_i$.

If all outcomes are equally probable, i.e. $p_1 = p_2 = ... = p_n$, then the
_expectation_ equals the arithmetic _mean_.

The _variance_ of $X$ is the expectation of the squared deviation of $X$ from
its expectation. It is notationally defined as

$$\sigma^2 = E[(X - E[X])^2]$$

The standard deviation of $X$ is defined as $\sigma = \sqrt{\sigma^2}$.

When only a dataset of outcomes of $X$ is available, the underlying metrics are
called population metrics, and the inferred metrics are called sample metrics.

The _sample mean_ of an $X$ dataset is defined as

$$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i.$$

The _sample variance_ of an $X$ dataset is defined as

$$ s^2 = \frac{1}{n - 1} \sum\_{i=1}^{n} (x_i - \bar{x})^2 $$
