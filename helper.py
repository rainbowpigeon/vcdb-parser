import itertools


def print_columns(df):
    """
    Helper function to print columns in dataframe in alphabetical order
    :param df: pandas DataFrame
    :return: None
    """
    print('\n'.join(sorted(df.columns)))


def get_column_nulls_count(df, col):
    """
    Helper function to return the number of NaN/Null values in a column of a pandas DataFrame
    :param df: pandas DataFrame
    :param col: Column in a pandas DataFrame
    :return: Integer representing number of NaN/Null values in the column
    """
    return df[col].isnull().sum()


def column_has_null(df, col):
    """
    Helper function
    :param df: pandas DataFrame
    :param col: Column in a pandas DataFrame
    :return: True if the column contains any NaN values, false otherwise.
    """
    return df[col].isnull().values.any()


def get_columns_without_any_null(df):
    """
    Helper function to return columns in dataframe with no null values in them at all
    :param df: pandas DataFrame
    :return: List of columns in the pandas DataFrame that do not contain any null values
    """
    return [col for col in df.columns if not column_has_null(df, col)]


def get_row_count(df):
    """
    Helper function to return the number of rows in the pandas DataFrame
    :param df: pandas DataFrame
    :return: Integer representing number of rows in the pandas DataFrame
    """
    return len(df.index)


def col_contains_lists(df, col):
    """
    Helper function to determine if a pandas DataFrame column contains lists as its values
    :param df: pandas DataFrame
    :param col: Column in a pandas DataFrame
    :return: True if the column contains values which are lists, False otherwise.
    """
    return (df[col].sample(10).apply(type) == list).any()


def get_unique_col_values(df, column):
    """
    Helper function to return list of unique values in column
    :param df: pandas DataFrame
    :param column: Column in a pandas DataFrame
    :return: Sorted list of unique values in the specified column of the pandas DataFrame
    """
    if col_contains_lists(df, column):
        values = set(itertools.chain.from_iterable(df[column]))
        if None in values:
            values = list(values)
            values[:] = [v for v in values if v is not None]
            values.sort()
            values.insert(0, None)
            return values
        else:
            return sorted(values)
    else:
        df = df[column].drop_duplicates()
        df = df.dropna()
        return sorted(df.to_list())
