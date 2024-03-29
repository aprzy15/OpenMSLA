import os
from pubsub import pub
import numpy as np


class AbstractPage:
    def __init__(self):
        pass

    def update_screen(self):
        pass

    def enter(self):
        pass

    def up(self):
        pass

    def dn(self):
        pass


class GenericListPage:
    def __init__(self, context, page_list):
        self.lcd = context.lcd
        self.nrows = context.cfg.lcd_rows
        self.context = context
        self.wind_start_index = 0
        self.last_cur_index = 0
        self.cur_index = 0
        self.last_index = 0
        self.page_list = page_list

    def update(self, index):
        if index == self.last_index:
            return
        self.last_index = index
        if self.cur_index == self.last_cur_index:
            self.wind_start_index = max([0, index - (self.nrows - 1)])
            self.update_screen()
        else:
            self.update_cursor()

    def update_screen(self):
        pages = self.page_list[self.wind_start_index:self.wind_start_index + self.nrows]
        str_list = []
        for i, page in enumerate(pages):
            name = page['name']
            str_list.append(' ' + name)
        screen = '\r\n'.join(str_list)
        self.lcd.clear()
        self.lcd.write_string(screen)
        self.update_cursor()

    def update_cursor(self):
        self.lcd._set_cursor_pos((self.last_cur_index, 0))
        self.lcd.write_string(' ')
        self.lcd._set_cursor_pos((self.cur_index, 0))
        self.lcd.write_string('>')
        self.last_cur_index = self.cur_index

    def enter(self):
        d = self.page_list[self.last_index]
        page = d['page']
        self.context.navigate(page)

    def up(self):
        self.cur_index = max([0, self.last_cur_index - 1])
        index = max([0, self.last_index - 1])
        self.update(index)

    def dn(self):
        self.cur_index = min([self.nrows - 1, self.last_cur_index + 1])
        index = min([len(self.page_list) - 1, self.last_index + 1])
        self.update(index)


class MainPage(GenericListPage):
    def __init__(self, context):
        page_list = [
            {'name': 'Info', 'page': ZAdjustPage},
            {'name': 'Adjust Z', 'page': ZAdjustPage},
            {'name': 'Load Files', 'page': FilePage},
            {'name': 'Home Z', 'page': HomingPage},
            {'name': 'Macros', 'page': MacroPage},
        ]
        super().__init__(context, page_list)


class FilePage(GenericListPage):
    def __init__(self, context):
        context.load_files()
        files = context.files.copy()
        page_list = []
        for file in files:
            name = file
            if len(file) > context.cfg.lcd_cols:
                name = file[:context.cfg.lcd_cols - 1]
            d = {'name': name, 'file': file}
            page_list.append(d)
        page_list.append({'name': 'Back', 'file': None})
        super().__init__(context, page_list)

    def enter(self):
        d = self.page_list[self.last_index]
        file = d['file']
        if file is not None:
            self.context.fname = file
            fpath = os.path.join(self.context.cfg.build_folder, file)
            pub.sendMessage('printer.start_print', fpath=fpath)
        else:
            self.context.navigate(MainPage)


class MacroPage(GenericListPage):
    def __init__(self, context):
        context.load_files()
        macros = context.macros.copy()
        page_list = []
        for macro in macros:
            name = macro
            if len(macro) > context.cfg.lcd_cols:
                name = macro[:context.cfg.lcd_cols - 1]
            d = {'name': name, 'file': macro}
            page_list.append(d)
        page_list.append({'name': 'Back', 'file': None})
        super().__init__(context, page_list)

    def enter(self):
        d = self.page_list[self.last_index]
        file = d['file']
        self.context.fname = file
        if file is not None:
            fpath = os.path.join(self.context.cfg.build_folder, file)
            pub.sendMessage('printer.start_macro', fpath=fpath)
        else:
            self.context.navigate(MainPage)


class PrintingPage(AbstractPage):
    def __init__(self, context, print_layers, current_layer, fname):
        super().__init__()
        self.context = context
        layer_str = f'{current_layer} / {print_layers}'
        num_bars = np.round((current_layer / print_layers) * self.context.cfg.lcd_cols).astype(int)
        percent_complete = ''.join(["\xff"] * num_bars)
        text = '\r\n'.join(['Printing', fname, layer_str, percent_complete])
        self.context.lcd.clear()
        self.context.lcd.write_string(text)

    # def update_screen(self):
    #     max_layer = self.context.max_layer
    #     layer_str = f'{self.context.current_layer} / {max_layer}'
    #     num_bars = np.round((self.context.current_layer / max_layer) * self.context.cfg.lcd_cols).astype(int)
    #     percent_complete = ''.join(["\xff"] * num_bars)
    #     text = '\r\n'.join(['Printing', self.context.fname, layer_str, percent_complete])
    #     self.lcd.clear()
    #     self.lcd.write_string(text)

    def enter(self):
        self.context.navigate(CancelPage)


class CancelPage(AbstractPage):
    def __init__(self, context):
        super().__init__()
        self.lcd = context.lcd
        self.screen = ''
        self.index = 0
        self.context = context
        self.lcd.clear()
        self.lcd.write_string('Cancel Print?\r\n Yes\r\n No')
        self.update_screen()

    def update_screen(self):
        self.lcd._set_cursor_pos((1, 0))
        self.lcd.write_string(' ')
        self.lcd._set_cursor_pos((2, 0))
        self.lcd.write_string(' ')
        self.lcd._set_cursor_pos((self.index + 1, 0))
        self.lcd.write_string('>')

    def enter(self):
        if self.index == 1:
            self.context.navigate(PrintingPage)
        else:
            pub.sendMessage('printer.cancel_print')
            self.context.navigate(MainPage)

    def up(self):
        index = self.index - 1
        self.index = max([0, index])
        self.update_screen()

    def dn(self):
        index = self.index + 1
        self.index = min([1, index])
        self.update_screen()


class ZAdjustPage(AbstractPage):
    def __init__(self, context):
        super().__init__()
        self.lcd = context.lcd
        self.context = context
        self.lcd.clear()
        self.lcd.write_string(f'Z Pos: {self.context.z_pos}')

    def enter(self):
        self.context.navigate(MainPage)

    def up(self):
        if self.context.is_homed:
            z_pos = self.context.z_pos + 1
            self.context.z_pos = min([z_pos, self.context.cfg.max_z])
            pub.sendMessage('ui.z_changed', arg1=self.context.z_pos)
            self.lcd.clear()
            self.lcd.write_string(f'Z Pos: {self.context.z_pos}')
        else:
            self.lcd.clear()
            self.lcd.write_string(f'Z Not Homed')

    def dn(self):
        if self.context.is_homed:
            z_pos = self.context.z_pos - 1
            self.context.z_pos = max([z_pos, 0])
            pub.sendMessage('ui.z_changed', arg1=self.context.z_pos)
            self.lcd.clear()
            self.lcd.write_string(f'Z Pos: {self.context.z_pos}')
        else:
            self.lcd.clear()
            self.lcd.write_string(f'Z Not Homed')


class HomingPage(AbstractPage):
    def __init__(self, context):
        super().__init__()
        self.lcd = context.lcd
        self.context = context
        self.lcd.clear()
        self.lcd.write_string('Homing ...')
        pub.sendMessage('printer.home')

    def enter(self):
        self.context.navigate(MainPage)


class HomedPage(AbstractPage):
    def __init__(self, context):
        super().__init__()
        self.lcd = context.lcd
        self.context = context
        self.lcd.clear()
        self.lcd.write_string('Homed')
        self.context.is_homed = True
        self.context.z_pos = 0

    def enter(self):
        self.context.navigate(MainPage)


class HomeFailedPage(AbstractPage):
    def __init__(self, context):
        super().__init__()
        self.lcd = context.lcd
        self.context = context
        self.lcd.clear()
        self.lcd.write_string('Homing Failed')
        self.context.is_homed = False

    def enter(self):
        self.context.navigate(MainPage)