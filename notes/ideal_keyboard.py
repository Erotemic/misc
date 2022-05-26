import kwplot
import numpy as np
import kwimage
kwplot.autompl()

f = 8
blank_key = np.zeros((64 * f, 54 * f, 3))
blank_key[:, :, :] = np.array(kwimage.Color('darkgray').as255())[None, None, :]
blank_key[0:f * 2, :] = (3, 3, 3)
blank_key[-f * 2:, :] = (3, 3, 3)
blank_key[:, 0:f * 2] = (3, 3, 3)
blank_key[:, -f * 2:] = (3, 3, 3)

key = kwimage.draw_text_on_image(blank_key.copy(), text='!\n1', halign='center', valign='center', color='white')

kwplot.imshow(key)

tab_symbol = '->'


left_rows = []

alt_text0 = [None, None, None, None, None, None, None, None]
row_text0 = ['esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'caps']
left_rows += [(alt_text0, row_text0)]

alt_text1 = [None, '~', '!', '@', '#', '$', '%', None]
row_text1 = ['tab', '`', '1', '2', '3', '4', '5', 'win']
left_rows += [(alt_text1, row_text1)]

alt_text2 = ['|', '?',  None, None, None, None, None, None]
row_text2 = ['\\', '/', 'q', 'w', 'e', 'r', 't', 'del']
left_rows += [(alt_text2, row_text2)]

alt_text3 = [None, None, None, None, None, None, None, None]
row_text3 = ['shift', 'shift', 'a', 's', 'd', 'f', 'g', 'tab']
left_rows += [(alt_text3, row_text3)]

alt_text3 = [None, None, None, None, None, None, None, None]
row_text3 = ['ctrl', 'ctrl', 'z', 'x', 'c', 'v', 'b', 'bksp']
left_rows += [(alt_text3, row_text3)]

alt_text4 = [None, None, None, None, None, None, None, None]
row_text4 = ['alt', 'home', 'pup', 'end', 'pdwn', 'end', 'space', 'enter']
left_rows += [(alt_text4, row_text4)]

row_stack = []

for alt_text, row_text in left_rows:
    row_keys = []
    for t, a in zip(row_text, alt_text):

        if len(t) == 1:
            fontScale = 4
            thickness = 6
        else:
            fontScale = 1
            thickness = 4

        if a is None:
            text = t
        else:
            text = a + '\n\n' + t

        key = kwimage.draw_text_on_image(blank_key.copy(), text=text, halign='center', valign='center', color='white', fontScale=4, thickness=thickness)
        row_keys.append(key)
    row = kwimage.stack_images(row_keys, axis=1, pad=1)
    row_stack.append(row)

left_side = kwimage.stack_images(row_stack, axis=0, pad=1)


right_rows = []

alt_text0 = [None, None, None, None, None, None, None, None]
row_text0 = ['Prt\nScn', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'DEL']
right_rows += [(alt_text0, row_text0)]

alt_text1 = [None, '^', '&', '*', '(', ')', '_', '+']
row_text1 = ['win', '6', '7', '8', '9', '0', '-', '=']
right_rows += [(alt_text1, row_text1)]

alt_text2 = [None, None, None, None, None, None, '{', '}']
row_text2 = ['del', 'y', 'u', 'i', 'o', 'p', '[', ']']
right_rows += [(alt_text2, row_text2)]

alt_text3 = [None, None, None, None, None, ':', None, None]
row_text3 = ['tab', 'h', 'j', 'k', 'l', ';', 'shift', 'shift']
right_rows += [(alt_text3, row_text3)]

alt_text3 = [None, None, None, '<', '>', '"', None, None]
row_text3 = ['bksp', 'n', 'm', ',', '.', '\'', 'ctrl', 'ctrl']
right_rows += [(alt_text3, row_text3)]

alt_text4 = [None, None, None, None, None, None, None, None]
row_text4 = ['enter', 'space', '<', '^', 'V', '>', 'alt', 'alt']
right_rows += [(alt_text4, row_text4)]

row_stack = []

for alt_text, row_text in right_rows:
    row_keys = []
    for t, a in zip(row_text, alt_text):

        if len(t) == 1:
            fontScale = 4
            thickness = 6
        else:
            fontScale = 1
            thickness = 4

        if a is None:
            text = t
        else:
            text = a + '\n\n' + t

        key = kwimage.draw_text_on_image(blank_key.copy(), text=text, halign='center', valign='center', color='white', fontScale=4, thickness=thickness)
        row_keys.append(key)
    row = kwimage.stack_images(row_keys, axis=1, pad=1)
    row_stack.append(row)

right_side = kwimage.stack_images(row_stack, axis=0, pad=1)

image = kwimage.stack_images([left_side, right_side], axis=1, pad=300)

kwplot.imshow(image)
