# Version 3 validation audit

Source: `results/prefix_suffix_v3_validation.json`
Replicates per matched profile: 200

## Mechanical audit

**PASS:** output is structurally complete under the declared Version 3 validation rules.

## Voynich neutral-value diagnostics

- Page-block prefix: 1.020 [0.978, 1.064], fraction >=1: 0.770 (interval crosses neutral)
- Page-block suffix: 1.110 [1.074, 1.145], fraction >=1: 1.000 (above-neutral interval)
- Page-block minimum: 1.020 [0.978, 1.064], fraction >=1: 0.770 (interval crosses neutral)
- Line-deletion prefix (stability only): 1.013 [1.005, 1.025], fraction >=1: 0.995
- All-system small-target minimum: 1.019 [0.985, 1.060], fraction >=1: 0.850 (interval crosses neutral)

## Comparator pattern in the line-deletion sensitivity

- Comparators with minimum-side median below 1.0: 14/14.
- Comparators whose entire 95% minimum-side interval is below 1.0: 14/14.

## Exact-repeat robustness

- Observed exact adjacent repeats: 249.
- Expected exact adjacent repeats under within-unit shuffle: 244.274.
- Suffix ratio after breaking every exact adjacent repeat pair: 1.064.

## Line-deletion stability sensitivity

Target tokens: 28,447

| System | Prefix order ratio | Suffix order ratio | Minimum | Neutral status |
|---|---:|---:|---:|---|
| Arabic | 0.862 [0.741, 1.018], fraction >=1: 0.040 | 1.002 [0.900, 1.107], fraction >=1: 0.510 | 0.861 [0.741, 0.997], fraction >=1: 0.020 | below-neutral interval |
| Estonian | 0.728 [0.584, 0.850], fraction >=1: 0.000 | 1.373 [1.193, 1.508], fraction >=1: 1.000 | 0.728 [0.584, 0.850], fraction >=1: 0.000 | below-neutral interval |
| Finnish | 0.683 [0.526, 0.811], fraction >=1: 0.000 | 1.281 [1.216, 1.341], fraction >=1: 1.000 | 0.683 [0.526, 0.811], fraction >=1: 0.000 | below-neutral interval |
| Georgian | 0.911 [0.841, 0.984], fraction >=1: 0.015 | 0.971 [0.926, 1.020], fraction >=1: 0.155 | 0.910 [0.841, 0.976], fraction >=1: 0.005 | below-neutral interval |
| Hebrew | 0.572 [0.392, 0.820], fraction >=1: 0.000 | 1.609 [1.539, 1.692], fraction >=1: 1.000 | 0.572 [0.392, 0.820], fraction >=1: 0.000 | below-neutral interval |
| Hungarian | 0.610 [0.484, 0.728], fraction >=1: 0.000 | 0.602 [0.466, 0.738], fraction >=1: 0.000 | 0.566 [0.449, 0.659], fraction >=1: 0.000 | below-neutral interval |
| Italian | 0.686 [0.586, 0.794], fraction >=1: 0.000 | 0.714 [0.611, 0.805], fraction >=1: 0.000 | 0.669 [0.584, 0.746], fraction >=1: 0.000 | below-neutral interval |
| KJV English | 0.313 [0.274, 0.354], fraction >=1: 0.000 | 0.092 [0.060, 0.126], fraction >=1: 0.000 | 0.092 [0.060, 0.126], fraction >=1: 0.000 | below-neutral interval |
| Latin | 0.621 [0.515, 0.755], fraction >=1: 0.000 | 1.539 [1.477, 1.607], fraction >=1: 1.000 | 0.621 [0.515, 0.755], fraction >=1: 0.000 | below-neutral interval |
| Middle English | 0.513 [0.450, 0.580], fraction >=1: 0.000 | 0.355 [0.281, 0.440], fraction >=1: 0.000 | 0.355 [0.281, 0.440], fraction >=1: 0.000 | below-neutral interval |
| North Azerbaijani | 0.499 [0.375, 0.633], fraction >=1: 0.000 | 0.787 [0.679, 0.930], fraction >=1: 0.000 | 0.499 [0.375, 0.633], fraction >=1: 0.000 | below-neutral interval |
| Swahili | 0.964 [0.899, 1.013], fraction >=1: 0.085 | 0.884 [0.839, 0.946], fraction >=1: 0.000 | 0.884 [0.839, 0.943], fraction >=1: 0.000 | below-neutral interval |
| Tagalog | 0.534 [0.484, 0.590], fraction >=1: 0.000 | 0.901 [0.851, 0.951], fraction >=1: 0.000 | 0.534 [0.484, 0.590], fraction >=1: 0.000 | below-neutral interval |
| Turkish | 0.635 [0.541, 0.737], fraction >=1: 0.000 | 0.735 [0.605, 0.860], fraction >=1: 0.000 | 0.635 [0.541, 0.719], fraction >=1: 0.000 | below-neutral interval |
| VOYNICH | 1.013 [1.005, 1.025], fraction >=1: 0.995 | 1.108 [1.099, 1.116], fraction >=1: 1.000 | 1.013 [1.005, 1.025], fraction >=1: 0.995 | above-neutral interval |

## All-system small-target sensitivity

Target tokens: 14,380

| System | Prefix order ratio | Suffix order ratio | Minimum | Neutral status |
|---|---:|---:|---:|---|
| Arabic | 0.854 [0.622, 1.011], fraction >=1: 0.050 | 1.002 [0.854, 1.156], fraction >=1: 0.515 | 0.854 [0.622, 1.003], fraction >=1: 0.030 | interval crosses neutral |
| Estonian | 0.724 [0.545, 0.905], fraction >=1: 0.000 | 1.373 [1.177, 1.559], fraction >=1: 1.000 | 0.724 [0.545, 0.905], fraction >=1: 0.000 | below-neutral interval |
| Finnish | 0.682 [0.516, 0.863], fraction >=1: 0.010 | 1.281 [1.192, 1.364], fraction >=1: 1.000 | 0.682 [0.516, 0.863], fraction >=1: 0.010 | below-neutral interval |
| Georgian | 0.914 [0.807, 1.032], fraction >=1: 0.090 | 0.974 [0.900, 1.045], fraction >=1: 0.275 | 0.909 [0.807, 1.006], fraction >=1: 0.035 | interval crosses neutral |
| Hebrew | 0.552 [0.328, 0.844], fraction >=1: 0.000 | 1.617 [1.509, 1.718], fraction >=1: 1.000 | 0.552 [0.328, 0.844], fraction >=1: 0.000 | below-neutral interval |
| Hungarian | 0.592 [0.433, 0.762], fraction >=1: 0.000 | 0.612 [0.420, 0.813], fraction >=1: 0.000 | 0.551 [0.404, 0.692], fraction >=1: 0.000 | below-neutral interval |
| Italian | 0.687 [0.550, 0.847], fraction >=1: 0.000 | 0.692 [0.560, 0.831], fraction >=1: 0.000 | 0.652 [0.534, 0.749], fraction >=1: 0.000 | below-neutral interval |
| KJV English | 0.319 [0.274, 0.364], fraction >=1: 0.000 | 0.094 [0.057, 0.140], fraction >=1: 0.000 | 0.094 [0.057, 0.140], fraction >=1: 0.000 | below-neutral interval |
| Latin | 0.628 [0.465, 0.818], fraction >=1: 0.000 | 1.543 [1.444, 1.637], fraction >=1: 1.000 | 0.628 [0.465, 0.818], fraction >=1: 0.000 | below-neutral interval |
| Middle English | 0.513 [0.437, 0.599], fraction >=1: 0.000 | 0.347 [0.254, 0.454], fraction >=1: 0.000 | 0.347 [0.254, 0.453], fraction >=1: 0.000 | below-neutral interval |
| North Azerbaijani | 0.510 [0.304, 0.736], fraction >=1: 0.000 | 0.801 [0.628, 0.969], fraction >=1: 0.010 | 0.510 [0.304, 0.735], fraction >=1: 0.000 | below-neutral interval |
| Ottoman Turkish | 0.311 [0.268, 0.339], fraction >=1: 0.000 | 0.356 [0.316, 0.399], fraction >=1: 0.000 | 0.310 [0.268, 0.338], fraction >=1: 0.000 | below-neutral interval |
| Swahili | 0.957 [0.889, 1.042], fraction >=1: 0.125 | 0.885 [0.806, 0.953], fraction >=1: 0.000 | 0.883 [0.806, 0.950], fraction >=1: 0.000 | below-neutral interval |
| Tagalog | 0.533 [0.456, 0.605], fraction >=1: 0.000 | 0.896 [0.820, 0.964], fraction >=1: 0.010 | 0.533 [0.456, 0.605], fraction >=1: 0.000 | below-neutral interval |
| Turkish | 0.640 [0.475, 0.821], fraction >=1: 0.000 | 0.737 [0.574, 0.899], fraction >=1: 0.000 | 0.634 [0.475, 0.775], fraction >=1: 0.000 | below-neutral interval |
| VOYNICH | 1.019 [0.985, 1.060], fraction >=1: 0.850 | 1.108 [1.081, 1.132], fraction >=1: 1.000 | 1.019 [0.985, 1.060], fraction >=1: 0.850 | interval crosses neutral |

## Claim gate

No claim is promoted automatically. The mechanical audit can pass while the scientific interpretation remains bounded or null. Human review must consider interval overlap, comparator scope, corpus mismatch, affix discovery sensitivity, and the finite tested set.
