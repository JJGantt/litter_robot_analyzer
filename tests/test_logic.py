import numpy as np
import pandas as pd

from logic import identify_cats, identify_and_clean


def synthetic(weights, per_cat=60):
    """Visits from cats of the given weights, spread over a month, interleaved."""
    rng = np.random.default_rng(0)
    rows = []
    start = pd.Timestamp('2024-01-01')
    for i in range(per_cat):
        for w in weights:
            rows.append((start + pd.Timedelta(hours=12 * i + rng.uniform(0, 6)),
                         w + rng.normal(0, 0.1)))
    df = pd.DataFrame(rows, columns=['Date', 'Weight'])
    df['x'] = df.Date.apply(lambda d: d.timestamp())
    return df


def test_identify_cats_finds_as_many_cats_as_asked():
    for weights in ([6.0, 12.0], [5.0, 9.0, 13.0], [4.0, 7.0, 10.0, 13.0]):
        df, lines = identify_cats(synthetic(weights), len(weights))
        assert sorted(lines) == list(range(len(weights)))
        assert df['Cat'].nunique() == len(weights)
        # every visit lands with the cat whose weight it is
        for cat, w in enumerate(sorted(weights)):
            assert (df.loc[df['Cat'] == cat, 'Weight'] - w).abs().max() < 1


def test_identify_cats_does_not_carry_lines_between_calls():
    identify_cats(synthetic([6.0, 12.0]), 2)
    df = synthetic([20.0, 30.0])
    _, lines = identify_cats(df, 2)
    slope, intercept = lines[0]
    assert abs(slope * df['x'].mean() + intercept - 20) < 1


def test_identify_and_clean_two_cats():
    df, lines = identify_and_clean(synthetic([6.0, 12.0])[['Date', 'Weight']], 2)
    assert set(df['Cat']) == {0, 1}
