import pandas as pd
import ubelt as ub

df = pd.DataFrame([
    {'params.a': 1, 'params.b': [32, 32], 'params.c': "foo"},
    {'params.a': 1, 'params.b': [64, 64], 'params.c': "foo"},
    {'params.a': 2, 'params.b': [64, 64], 'params.c': "bar"},
    {'params.a': 2, 'params.b': [64, 64], 'params.c': "bar"},
    {'params.a': 3, 'params.b': [64, 64], 'params.c': "bar"},
    {'params.a': 3, 'params.b': [32, 32], 'params.c': "foo"},
    {'params.a': 4, 'params.b': 32, 'params.c': "foo"},
    {'params.a': 4, 'params.b': 64, 'params.c': "foo"},
    {'params.a': 5, 'params.b': 96, 'params.c': "foobar"},
])


def our_hacky_query(df, query):
    try:
        from pandas.core.computation.ops import UndefinedVariableError
    except Exception:
        from pandas.errors import UndefinedVariableError

    new_table = df

    if len(df) > 0:
        if 'df[' in query:
            # HACK for more expressive queries
            try:
                flags = eval(query)
            except Exception as ex:
                print(f'warning, eval query unsuccessful: ex={ex}')
            else:
                new_table = df[flags]
        else:
            try:
                new_table = df.query(query)
            except UndefinedVariableError as ex:
                print(f'warning, failed to query: ex={ex}')
    return new_table

result = our_hacky_query(df, ub.paragraph(
    '''
    `params.a` == 1
    '''))
print(result)

our_hacky_query(df, ub.paragraph(
    '''
    df['params.b'].apply(str).str.contains("64")
    '''))


if 0:
    # doesnt seem to be a way to call astype in eval correctly
    df.eval('`params.b`', parser='pandas', engine='python')
    df.eval('_["params.b"]', parser='python', engine='python')
    df.eval('a1.astype(str)', parser='python', engine='python')

result = df.query(ub.paragraph(
    '''
    `params.c`.str.contains("foo")
    '''))
print(result)

df['a1'] = df['params.a']
df.eval('a1', parser='python')

result = df.query(ub.paragraph(
    '''
    df['params.c'].str.contains("foo")
    '''), parser='python')
print(result)

result = df.query(ub.paragraph(
    '''
    `params.c`.astype(str).str.contains("foo")
    '''))
print(result)


result = df.query(ub.paragraph(
    '''
    `params.b`.str.contains("32")
    '''), parser='python')
print(result)
