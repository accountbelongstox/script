from pycore.dbmode.baseclass.base.dbbase import DBBase
class Ttransport(DBBase):

    def transport(self, from_db, to_db, tabname, step=10000):
        from_db = self.get_dbmodefromname(from_db)
        to_db = self.get_dbmodefromname(to_db)
        from_dbname = self.get_dbnamefrommode(from_db)
        to_dbname = self.get_dbnamefrommode(to_db)
        origin_len = from_db.count(tabname)
        if origin_len == 0:
            return False

        target_len = 0
        if to_db.exist_table(tabname) == True:
            target_len = to_db.count(tabname)

        self.com_util.print_info(f'{tabname} {origin_len},target-count{target_len} data wait copying ')
        # 每次复制数据
        limit = self.init_limit(step)
        limit_start = limit[0]
        # columns = from_db.get_columns(tabname)
        while limit_start < (origin_len - 1):
            limit = self.get_limitincrement()
            limit_step = limit[0]
            limit_start = limit[1]
            limit_end = limit_start + limit_step
            self.com_util.print_info(f'\treading {tabname}:{limit_start}-{limit_end} from {from_dbname} to {to_dbname}')
            origin_data = from_db.read(tabname, limit=limit)

            if to_db.exist_table(tabname) == False:
                fields = from_db.get_fields()
                to_db.create_table(tabname, fields)
                print(fields)
                exit()

            self.com_util.print_info(
                f'\ttranslating of {tabname}({len(origin_data)} item by data)')
            # to_db.save(tabname, origin_data)
            self.com_util.print_info(
                f'\tSuccessfully! {tabname}')
            self.com_util.print_info(
                f'------------------------------------------------------------------------------------')
