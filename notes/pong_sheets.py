# /// script
# dependencies = [
#   "gspread",
#   "gspread_dataframe",
#   "gspread_formatting",
#   "ubelt",
#   "pandas",
# ]
# requires-python = ">=3.11"
# ///
"""
Requires google sheets credentials to use.

Used to generate:
    https://docs.google.com/spreadsheets/d/1VGWF7X0ur-YtVrDo0I2_S7a7IQb_8ASz2FGamYXPfG8
"""


def build_pong_google_sheet():
    """
    Requirements:
        uv pip install gspread gspread_dataframe gspread_formatting
    """
    import gspread
    import gspread_dataframe
    import ubelt as ub
    import pandas as pd
    credential_fpath = ub.Path('$HOME/erotemic/safe/google_api/credentials.json').expand()
    gc = gspread.oauth(
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        credentials_filename=credential_fpath,
        # authorized_user_filename='path/to/the/authorized_user.json'
    )
    # https://docs.google.com/spreadsheets/d/1VGWF7X0ur-YtVrDo0I2_S7a7IQb_8ASz2FGamYXPfG8/edit?gid=0#gid=0
    sheet = gc.open_by_key('1VGWF7X0ur-YtVrDo0I2_S7a7IQb_8ASz2FGamYXPfG8')
    title_of_interest = 'Bouncing Ball'
    ws = [w for w in sheet.worksheets() if w.title == title_of_interest][0]

    n_row_cells = 30
    n_col_cells = 30
    new_df = pd.DataFrame([[''] * n_row_cells] * n_col_cells)

    def to_sheet_cell(rx, cx):
        col_letter = chr(ord('A') + cx)
        row_num = rx + 1
        return f'{col_letter}{row_num}'

    grid_height = 11
    grid_width = 11
    grid_start_rx = 10
    grid_start_cx = 1

    state_cells = {}
    state_cells['label_curr'] = {'iloc': (0, 1), 'value': 'Current'}
    state_cells['label_next'] = {'iloc': (0, 2), 'value': 'Next'}

    state_cells['label_x'] = {'iloc': (1, 0), 'value': 'X:'}
    state_cells['label_y'] = {'iloc': (2, 0), 'value': 'Y:'}
    state_cells['label_vx'] = {'iloc': (3, 0), 'value': 'vX:'}
    state_cells['label_vy'] = {'iloc': (4, 0), 'value': 'vY:'}

    state_cells['curr_x'] = {'iloc': (1, 1)}
    state_cells['curr_y'] = {'iloc': (2, 1)}
    state_cells['curr_vx'] = {'iloc': (3, 1)}
    state_cells['curr_vy'] = {'iloc': (4, 1)}

    state_cells['next_x'] = {'iloc': (1, 2)}
    state_cells['next_y'] = {'iloc': (2, 2)}
    state_cells['next_vx'] = {'iloc': (3, 2)}
    state_cells['next_vy'] = {'iloc': (4, 2)}
    for value in state_cells.values():
        rx, cx = value['iloc']
        value['sloc'] = to_sheet_cell(rx, cx)

    state_cells['curr_x']['value'] = '=' + state_cells['next_x']['sloc']
    state_cells['curr_y']['value'] = '=' + state_cells['next_y']['sloc']
    state_cells['curr_vx']['value'] = '=' + state_cells['next_vx']['sloc']
    state_cells['curr_vy']['value'] = '=' + state_cells['next_vy']['sloc']

    # FIXME: there is a double bounce issue, maybe due to the ordering of the cells?
    p = state_cells['curr_x']['sloc']
    v = state_cells['curr_vx']['sloc']
    state_cells['next_x']['value'] = f'=IF({p}+{v}<1, 2, IF({p}+{v}>={grid_width}, {grid_width} - 2, {p}+{v}))'

    p = state_cells['curr_y']['sloc']
    v = state_cells['curr_vy']['sloc']
    state_cells['next_y']['value'] = f'=IF({p}+{v}<1, 2, IF({p}+{v}>={grid_height}, {grid_height} - 2, {p}+{v}))'

    p = state_cells['curr_y']['sloc']
    v = state_cells['curr_vy']['sloc']
    s = state_cells['next_vx']['sloc']
    state_cells['next_vy']['value'] = f'=IF({p}+{v}<1, 1, IF({p}+{v}>={grid_height}, -1, {s}))'

    p = state_cells['curr_x']['sloc']
    v = state_cells['curr_vx']['sloc']
    s = state_cells['next_vx']['sloc']
    state_cells['next_vx']['value'] = f'=IF({p}+{v}<1, 1, IF({p}+{v}>={grid_width}, -1, {s}))'

    for cell in state_cells.values():
        rx, cx = cell['iloc']
        if cell.get('value'):
            new_df.iloc[rx, cx] = cell['value']

    curr_x_sloc = state_cells['curr_x']['sloc']
    curr_y_sloc = state_cells['curr_y']['sloc']

    for rx in range(grid_start_rx, grid_start_rx + grid_height):
        for cx in range(grid_start_cx, grid_start_cx + grid_width):
            cell_rule = f'=IF(AND(ROW() - {grid_start_rx + 1} = {curr_y_sloc}, COLUMN() - {grid_start_cx + 1} = {curr_x_sloc}), "●", "_")'
            new_df.iloc[rx, cx] = cell_rule

    gspread_dataframe.set_with_dataframe(ws, new_df, include_column_header=False)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/pong_sheets.py
    """
    build_pong_google_sheet()
