import pandas as pd


def resample_records(records, rule):
    """Resamples records with pandas DataFrame.resample()

    Args:
         records (django queryset): Ordinary django queryset to be resampled
            with pandas resample.
         rule (pandas resampling rule): Pandas resampling rule. 'D' for
            resampling records within days, 'T' for within minutes, and 'H' for
            within hours, for example, are possible. See pandas docs for further
            details.
    """
    # Return empty queryset itself if given records queryset is empty.
    if not records.exists():
        return records.none()

    # Otherwise return resampled queryset.
    df = pd.DataFrame.from_records(list(records.all().values()))
    df = df.set_index(pd.DatetimeIndex(df['created']))
    df = df.resample(rule, how='last')
    return records.filter(id__in=df['id'])
