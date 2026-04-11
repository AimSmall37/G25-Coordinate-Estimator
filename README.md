# G25 Coordinate Estimator

Approximate [Global 25 (G25)](https://vahaduo.github.io/vahaduo/) PCA coordinates for an unknown sample using only its Euclidean distances to known reference samples. This single-page web tool performs geometric interpolation via weighted multilateration — no server, no dependencies, runs entirely in the browser.

## Background

In autosomal DNA and population genetics, **PCA-based coordinate systems** like K36 and Global 25 (G25) are widely used for admixture comparison and population modeling. Each sample is represented as a point in 25-dimensional space, and the Euclidean distance between two points reflects their genetic similarity.

Tools like [Vahaduo](https://vahaduo.github.io/vahaduo/) allow users to compute distances between a target sample and a set of reference populations. The **Distance tab** in Vahaduo outputs a ranked list of these distances. This project asks a reverse question: *if you know how far a sample is from many known reference points, can you reconstruct where it sits in G25 space?*

The answer is yes — and with 25 well-chosen reference samples, the tool achieves **>99.9% Pearson correlation** with the true coordinates.

## How It Works

The estimation runs in four phases:

### Phase 1 — Inverse-Distance-Weighted Centroid

An initial guess is computed by averaging the coordinates of all matched reference samples, weighted by the inverse square of their distance. Closer samples contribute far more to the initial position. This alone gets the estimate into the correct neighborhood.

### Phase 2 — Gradient Descent Multilateration

Starting from the Phase 1 estimate, iterative least-squares optimization adjusts all 25 coordinates to minimize the total squared error between the observed distances and the distances implied by the current estimate. The optimizer uses adaptive learning rates (accelerating when cost decreases, decelerating when it increases) and runs for up to 3,000 iterations. Distance-based sample weighting ensures that closer reference samples exert proportionally more influence on the gradient.

### Phase 3 — Dimension-Weighted Blending *(optional)*

When the dimension weighting slider is set above zero, a second refinement pass runs. For each of the 25 dimensions independently, a nearest-neighbor weighted average is computed from the reference samples. Early PCA dimensions (Dim 1, 2, 3, ...) use a sharper power exponent, concentrating influence on the very closest references. These per-dimension estimates are then blended with the Phase 2 result, with the blend strength proportional to the dimension's weight — Dim 1 gets maximum correction, Dim 25 gets minimal.

### Phase 4 — Constrained Polish *(optional)*

After blending, a final gradient descent pass restores overall distance fit without undoing the dimension-weighted improvements. This is achieved by using **dimension-dependent learning rates**: early dimensions receive very small updates (protecting the Phase 3 corrections), while later dimensions absorb the compensating adjustments. The result is improved accuracy on the plotting-critical first few dimensions at a controlled cost to the later ones.

## Input Format

### ① G25 Coordinates (CSV)

A standard G25 coordinate file — one sample per line, comma-separated, with the sample name as the first field followed by 25 numeric coordinates:

```
England_EarlyMedieval.AG:I14534.AG__AD_600__Cov_68.31%,0.042,0.118,0.055,...
Scotland_Viking.SG:VK207.SG__AD_1020__Cov_52.99%,0.038,0.112,0.049,...
```

This is the standard export format used by G25/Vahaduo coordinate sheets. The file can contain thousands of samples — the tool will only use those that match entries in the distance list.

### ② Distance List

A tab-separated distance file as produced by the **Distance tab** in [Vahaduo](https://vahaduo.github.io/vahaduo/). The first line is a header identifying the target sample, followed by distance–name pairs:

```
Distance to:	AimSmall_scaled
0.02417863	England_EarlyMedieval.AG:I14534.AG__AD_600__Cov_68.31%
0.02492923	England_EarlyMedieval.AG:I16510.AG__AD_626__Cov_67.24%
0.02500288	Scotland_Viking.SG:VK207.SG__AD_1020__Cov_52.99%
...
```

Sample names must match exactly between the distance file and the coordinate CSV. The tool reports how many references were successfully matched and lists any that were not found.

**Minimum requirement:** 3 matched reference samples, though accuracy improves significantly with more. 20–30 close references typically yield excellent results.

### ③ Dimension Weighting Slider

Controls how aggressively the optimizer favors early PCA dimensions over later ones.

| Setting | Behavior |
|---------|----------|
| **Equal** (0) | All 25 dimensions treated identically. Standard multilateration only. Best overall distance fit. |
| **Mid-range** (~50) | Moderate front-loading. Dims 1–5 get ~3–5× the influence of Dims 21–25. Good balance for plotting accuracy vs. overall fit. |
| **Heavy PCA1-2** (100) | Maximum front-loading. Dim 1 gets ~46× the weight of Dim 25. Best for accurate 2D PCA plot placement at the cost of later dimensions. |

The preview below the slider shows the actual weight values and the ratio between Dim 1 and Dim 25 at the current setting.

**When to use dimension weighting:** If you plan to plot the estimated sample on a PCA chart (which uses Dim 1 and Dim 2 as axes), increase the slider to improve placement accuracy on those axes. If you need the most faithful overall coordinate reconstruction, leave it at Equal.

## Output

### Estimated Coordinates

The output is a single CSV line in standard G25 format, with `_estimated` appended to the target sample name:

```
AimSmall_scaled_estimated,0.130871,0.139456,0.052713,...
```

This can be copied directly and pasted into Vahaduo or any G25-compatible tool for further analysis, modeling, or plotting.

### Fit Diagnostics

A table showing how well the estimated position reproduces the observed distances:

| Column | Meaning |
|--------|---------|
| **Reference Sample** | Name of the matched reference |
| **Observed Dist** | The input distance from the distance file |
| **Fitted Dist** | The Euclidean distance from the estimated position to this reference |
| **Error** | Absolute difference between observed and fitted distance |
| **Fit** | Relative error as a percentage, with a visual bar |

Color coding: green (<8% error) indicates a strong fit, amber (8–20%) is acceptable, red (>20%) suggests the estimate may be unreliable for that reference. A mean relative error under 10% across all references generally indicates a trustworthy estimate.

## Accuracy Comparison

After running an estimation, click **"Compare to Actual"** to paste the known true G25 coordinates for the target sample. The tool computes four accuracy metrics:

### Pearson Correlation (R)

The primary accuracy metric. Measures how closely the estimated and actual coordinate vectors co-vary across all 25 dimensions. Displayed as a percentage — values above 99% indicate an excellent estimate. This is the number that answers "how similar are these two samples?" in the same way G25 distances do, but expressed as a correlation rather than a distance.

### Cosine Similarity

Measures directional alignment between the two coordinate vectors, independent of magnitude. A value of 99.9%+ means the estimate points in almost exactly the same direction in 25-dimensional space as the actual sample.

### Euclidean Distance

The raw geometric distance between the estimated and actual positions. Directly comparable to the input distances — if this value is smaller than the closest reference distance, the estimate is closer to the true position than any individual reference sample was.

### Mean Absolute Error per Dimension

The average per-coordinate deviation across all 25 dimensions. Useful for understanding the typical magnitude of error on any given coordinate. Values under 0.002 are excellent.

### Per-Dimension Breakdown

Expandable table showing estimated vs. actual values for each dimension, with the delta and percentage error. Color coded: green (Δ < 0.004), amber (0.004–0.01), red (>0.01).

## Practical Tips

- **More references = better accuracy.** The tool works with as few as 3, but 20–30 close references typically produce correlations above 99.5%.
- **Closer references matter more.** A handful of samples at distance 0.02 contribute more than dozens at distance 0.05. Prioritize the closest matches from Vahaduo's Distance tab.
- **Sample name matching is exact.** If references aren't matching, check for trailing whitespace, encoding differences, or version mismatches between your coordinate file and distance file.
- **The tool runs entirely client-side.** No data is uploaded anywhere. All computation happens in your browser.
- **Dimension weighting is a tradeoff.** Increasing it improves Dims 1–5 at the expense of Dims 20–25. For most use cases (plotting, visual comparison), this is a favorable trade since the later dimensions carry less population-level variance.

## Example Results

Using 25 reference samples at distances of 0.024–0.029 from the target:

| Metric | Equal Weighting | Heavy PCA1-2 |
|--------|----------------|--------------|
| Pearson R | 99.64% | 99.93% |
| Cosine Similarity | 99.68% | 99.94% |
| Euclidean Distance | 0.0178 | 0.0074 |
| Mean Abs Error/Dim | 0.00303 | 0.00115 |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
