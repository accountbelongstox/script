from pycore.base.base import Base
import re
import datetime

class Exchangerate(Base):
    __base_money = "CNY"
    __rate_list = []
    __world_money = None

    def __init__(self, args):
        pass

    def rate_to(self, from_money, to_money, from_number_money):
        self.get_rate_list_from_web()
        from_money_exchange_sell_per_base_rate = self.get_money_exchange_rate(from_money, to_money)
        exchange_money = from_number_money * from_money_exchange_sell_per_base_rate
        return exchange_money

    def get_money_exchange_rate(self, from_money, to_money):
        from_money_rate = self.get_money_exchange_rate_full(from_money, to_money)
        exchange_sell_rate = from_money_rate["exchange_sell_rate"]
        return exchange_sell_rate

    def get_money_exchange_rate_full(self, from_money, to_money):
        from_money_rate = self.get_money_rate(from_money)
        to_money_rate = self.get_money_rate(to_money)
        # 与比币的汇率
        from_money_exchange_sell_per_base_rate = from_money_rate["exchange_sell_rate"] / to_money_rate[
            "exchange_sell_rate"]
        from_money_money_sell_per_base_rate = from_money_rate["money_sell_rate"] / to_money_rate["money_sell_rate"]
        from_money_exchange_buy_per_base_rate = from_money_rate["exchange_buy_rate"] / to_money_rate[
            "exchange_buy_rate"]
        from_money_money_buy_per_base_rate = from_money_rate["money_buy_rate"] / to_money_rate["money_buy_rate"]
        return {
            "exchange_sell_rate": from_money_exchange_sell_per_base_rate,
            "money_sell_rate": from_money_money_sell_per_base_rate,
            "exchange_buy_rate": from_money_exchange_buy_per_base_rate,
            "money_buy_rate": from_money_money_buy_per_base_rate,
        }

    def get_money_rate(self, money_name):
        if self.__world_money == None:
            self.__world_money = self.get_world_money()
        for money_info in self.__world_money:
            if len(money_info) > 4:
                money_presentation = money_info[4]
            else:
                money_presentation = money_info[3]
            if money_name in money_info and money_presentation.upper().__eq__(money_name.upper()) == True:
                for m in self.__rate_list:
                    if money_info[1] == m['money_name']:
                        return m
        return None
        # print(soup.prettify())

    def get_rate_list_from_web(self):
        if len(self.__rate_list) == 0 \
                or \
                datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%S').__eq__(self.rate_list[0]["time_update"]) == True:

            web = "http://fx.cmbchina.com/Hq/"
            soup = self.com_http.open_url_beautifulsoup(web, "utf-8")

            taketime = \
                re.search(re.compile(r"\d{4}[\u4e00-\u9fa5]\d{2}[\u4e00-\u9fa5]\d{2}[\u4e00-\u9fa5]"), str(soup.html))[
                    0]
            taketime = re.sub(re.compile(r"[\u4e00-\u9fa5]"), " ", taketime)
            taketime = "-".join(taketime.strip().split(" "))

            rates = soup.find(id="realRateInfo")
            rates = rates.find_all("tr")[1:]
            for rate in rates:
                rate_tds = rate.find_all("td")
                money_name = rate_tds[0].get_text().strip()
                country = money_name
                base_rate = float(rate_tds[1].get_text())
                exchange_sell_price = float(rate_tds[3].get_text())
                money_sell_price = float(rate_tds[4].get_text())
                exchange_buy_price = float(rate_tds[5].get_text())
                money_buy_price = float(rate_tds[6].get_text())
                add_time_hsm = rate_tds[7].get_text().strip()
                if len(self.__rate_list) == 0:
                    # 添加本币
                    self.__rate_list.append(
                        {
                            "country": "中国",
                            "money_name": "人民币元",
                            "money_token": "RMB￥",
                            "money_alphas": "CNY",
                            "exchange_sell_rate": 1,
                            "money_sell_rate": 1,
                            "exchange_buy_rate": 1,
                            "money_buy_rate": 1,
                            "time_update": taketime,
                            "time": f"{taketime} {add_time_hsm}"
                        }
                    )
                self.__rate_list.append(
                    {
                        "country": country,
                        "money_name": money_name,
                        "money_token": money_name,
                        "money_alphas": money_name,
                        "exchange_sell_rate": exchange_sell_price / base_rate,
                        "money_sell_rate": money_sell_price / base_rate,
                        "exchange_buy_rate": exchange_buy_price / base_rate,
                        "money_buy_rate": money_buy_price / base_rate,
                        "time_update": taketime,
                        "time": f"{taketime} {add_time_hsm}"
                    }
                )

    def add_rate_to_list(self, country, money_name, money_token, money_alphas, exchange_sell_rate, money_sell_rate,
                         exchange_buy_rate, money_buy_rate, time_update, time):
        self.__rate_list.append(
            {
                "country": country,
                "money_name": money_name,
                "money_token": money_token,
                "money_alphas": money_alphas,
                "exchange_sell_rate": exchange_sell_rate,
                "money_sell_rate": money_sell_rate,
                "exchange_buy_rate": exchange_buy_rate,
                "money_buy_rate": money_buy_rate,
                "time_update": time_update,
                "time": time
            }
        )

    def get_world_money(self):
        world_money = [
            ("中国香港", "港币", "HongKong Dollars", "HK＄", "HKD", "1HKD=100cents（分)"),
            ("中国澳门", "澳门元", "Macao Pataca", "PAT.;P.", "MOP", "1MOP=100avos（分）"),
            ("中国", "人民币元", "Renminbi Yuan", "RMB￥", "CNY", "1CNY=10 jao（角）"),
            ("朝鲜", "圆", "Korean Won", " ", "KPW", "1KPW=100分"),
            ("越南", "越南盾", "Vietnamese Dong", "D.", "VND", "1VND=10角=100分"),
            ("日本", "日圆", "Japanese Yen", "￥;J.￥", "JPY", "1JPY=100 sen（钱）"),
            ("老挝", "基普", "Laotian Kip", "K.", "LAK", "1LAK 1LAK=100 ats（阿特)"),
            ("柬埔寨", "瑞尔", "Camboddian Riel", "CR.;J Ri.", "KHR", "1KHR=100 sen（仙）"),
            ("菲律宾", "菲律宾比索", "Philippine Peso", "Ph.Pes.; Phil.P.", "PHP", "1PHP=100 centavos（分）"),
            ("马元", "Malaysian Dollar", "M.＄;Mal.＄", "MYR", "1MYR=100 cents（分）"),
            ("新加坡", "新加坡元", "Ssingapore Dollar", "S.＄", "SGD", "1SGD=100 cents（分）"),
            ("泰国", "泰铢", "Thai Baht (Thai Tical)", "BT.;Tc.", "THP", "1THP=100 satang（萨当）"),
            ("缅甸", "缅元", "Burmese Kyat", "K.", "BUK", "1BUK=100 pyas（分）"),
            ("斯里兰卡", "斯里兰卡卢比", "Sri Lanka Rupee", "S.Re. 复数:S.Rs.", "LKR", "1LKR=100 cents（分）"),
            ("马尔代夫", "马尔代夫卢比", "Maldives Rupee", "M.R.R; MAL.Rs.", "MVR", "1MVR=100 larees（拉雷）"),
            ("印度尼西亚", "盾", "Indonesian Rupiah", "Rps.", "IDR", "1IDR=100 cents（分）"),
            ("巴基斯坦", "巴基斯坦卢比", "Pakistan Pupee", "Pak.Re.;P.Re. 复数:P.Rs.", "PRK", "1PRK=100 paisa（派萨）"),
            ("印度", "卢比", "Indian Rupee", "Re.复数:Rs.", "INR", "1INR=100paise（派士）（单数:paisa）"),
            ("尼泊尔", "尼泊尔卢比", "Nepalese Rupee", "N.Re.复数:N.Rs.", "NPR", "1NPR=100 paise（派司）"),
            ("阿富汗", "阿富汗尼", "Afghani", "Af.", "AFA", "1AFA=100 puls（普尔）"),
            ("伊朗", "伊朗里亚尔", "Iranian Rial", "RI.", "IRR", "1Irr=100 dinars（第纳尔）"),
            ("伊拉克", "伊拉克第纳尔", "Iraqi Dinar", "ID", "IQD", "1IQD=1000 fils（费尔）"),
            ("叙利亚", "叙利亚镑", "Syrian Pound", "￡.Syr.; ￡.S.", "SYP", "1SYP=100 piastres（皮阿斯特）"),
            ("黎巴嫩", "黎巴嫩镑", "Lebanese Pound", "￡L.", "LBP", "1LBP=100 piastres（皮阿斯特）"),
            ("约旦", "约旦第纳尔", "Jordanian Dinar", "J.D.; J.Dr.", "JOD", "1JOD=1,000 fils（费尔）"),
            ("沙特阿拉伯", "亚尔", "Saudi Arabian Riyal", "S.A.Rls.; S.R.", "SAR",
             "1SAR=100qurush（库尔什）1qurush=5 halals（哈拉）沙特里"),
            ("科威特", "科威特第纳尔", "Kuwaiti Dinar", "K.D.", "KWD", "1KWD=1,000 fils（费尔）"),
            ("巴林", "巴林第纳尔", "Bahrain Dinar", "BD.", "BHD", "1BHD=1,000 fils（费尔）"),
            ("卡塔尔", "卡塔尔里亚尔", "Qatar Riyal", "QR.", "QAR", "1QAR=100 dirhams（迪拉姆）"),
            ("阿曼", "阿曼里亚尔", "Oman Riyal", "RO.", "OMR", "1OMR=1,000 baiza（派沙）"),
            ("阿拉伯也门", "也门里亚尔", "Yemeni Riyal", "YRL.", "YER", "1YER=100 fils（费尔）"),
            ("民主也门", "也门第纳尔", "Yemeni Dinar", "YD.", "YDD", "1YDD=1,000 fils（费尔）"),
            ("土耳其", "土耳其镑", "Turkish Pound (Turkish Lira)", "￡T. (TL.)", "TRL",
             "1TRL=100 kurus（库鲁）"),
            ("塞浦路斯", "塞浦路斯镑", "Cyprus Pound", "￡C.", "CYP", "1CYP=1,000 mils（米尔）"),
            ("欧洲货币联盟", "欧元", "Euro", "EUR", "EUR", "1EUR=100 euro cents（生丁）"),
            ("冰岛", "冰岛克朗", "Icelandic Krona（复数：Kronur）", "I.Kr.", "ISK", "1ISK=100 aurar（奥拉）"),
            ("丹麦", "丹麦克朗", "Danish Krona（复数：Kronur）", "D.Kr.", "DKK", "1DKK=100 ore（欧尔）"),
            ("挪威", "挪威克朗", "Norwegian Krone（复数：Kronur）", "N.Kr.", "NOK", "1NOK=100 ore（欧尔）"),
            ("瑞典", "瑞典克朗", "Swedish Krona（复数：Kronor）", "S.Kr.", "SEK", "1SEK=100 ore（欧尔）"),
            ("芬兰", "芬兰马克", "Finnish Markka (or Mark)", "MK.;FM.; FK.;FMK.", "FIM",
             "1FIM=100 penni（盆尼）"),
            ("俄罗斯", "卢布", "Russian Ruble (or Rouble)", "Rbs. Rbl.", "SUR", "1SUR=100 kopee（戈比）"),
            ("波兰", "兹罗提", "Polish Zloty", "ZL.", "PLZ", "1PLZ=100 groszy（格罗希）"),
            ("捷克和斯洛伐克", "捷克克朗", "Czechish Koruna", "Kcs.; Cz.Kr.", "CSK", "100 Hellers=（赫勒）"),
            ("匈牙利", "福林", "Hungarian Forint", "FT.", "HUF", "1HUF=100 filler（菲勒）"),
            ("德国", "马克", "Deutsche Mark", "DM.", "DEM", "1DEM=100 pfennig（芬尼）"),
            ("奥地利", "奥地利先令", "Austrian Schilling", "Sch.", "ATS", "1ATS=100 Groschen（格罗申）"),
            ("瑞士", "瑞士法郎", "Swiss Franc", "SF.;SFR.", "CHF", "1CHF=100 centimes（分）"),
            ("荷兰", "荷兰盾", "Dutch Guilder(or Florin)", "Gs.;Fl.;Dfl.; Hfl.;fl.", "NLG",
             "1NLG=100 cents（分）"),
            ("比利时", "比利时法郎", "Belgian Franc", "Bi.;B.Fr.; B.Fc.", "BEF", "1BEF=100 centimes（分）*"),
            ("卢森堡", "卢森堡法郎", "Luxembourg Franc", "Lux.F.", "LUF", "1LUF=100 centimes（分）"),
            ("英国", "英镑", "Pound, Sterling", "￡;￡ Stg.", "GBP", "1GBP=100 new pence（新便士）"),
            ("爱尔兰", "爱尔兰镑", "Irish pound", "￡.Ir.", "IEP", "1IEP=100 new pence（新便士）"),
            ("法国", "法郎", "French Franc", "F.F.;Fr.Fc.; F.FR.", "FRF", "1FRF=100 centimes（分）"),
            ("西班牙", "比塞塔", "Spanish Peseta", "Pts.;Pes.", "ESP", "1ESP=100 centimos（分）"),
            ("葡萄牙", "埃斯库多", "Portuguese Escudo", "ESC.", "PTE**", "1PTE=100 centavos（分）"),
            ("意大利", "里拉", "Italian Lira", "Lit.", "ITL", "1ITL=100 centesimi（分）***"),
            ("马耳他", "马耳他镑", "Maltess Pound", "￡.M.", "MTP", "1MTP=100 cents（分）1Cent=10 mils（米尔）"),
            ("南斯拉夫", "南斯拉夫新第纳尔", "Yugoslav Dinar", "Din.Dr.", "YUD", "1YUD=100 paras（帕拉）"),
            ("罗马尼亚", "列伊", "Rumanian Leu（复数：Leva）", "L.", "ROL", "1ROL=100 bani（巴尼）"),
            ("保加利亚", "列弗", "Bulgarian Lev（复数：Lei）", "Lev.", "BGL", "1BGL=100 stotinki（斯托丁基）"),
            ("阿尔巴尼亚", "列克", "Albanian Lek", "Af.", "ALL", "1All=100 quintars（昆塔）"),
            ("希腊", "德拉马克", "Greek Drachma", "Dr.", "GRD", "1GRD=100 lepton（雷普顿）or lepta（雷普塔）"),
            ("加拿大", "加元", "Canadian Dollar", "Can.＄", "CAD", "1CAD=100 cents（分）"),
            ("美国", "美元", "U.S.Dollar", "U.S.＄", "USD", "1USD=100 cent（分）"),
            ("墨西哥", "墨西哥比索", "Mexican Peso", "Mex.＄", "MXP", "1MXP=100 centavos（分）"),
            ("危地马拉", "格查尔", "Quatemalan Quetzal", "Q", "GTQ", "1GTQ=100 centavos（分）"),
            ("萨尔瓦多", "萨尔瓦多科朗", "Salvadoran Colon", "￠", "SVC", "1SVC=100 centavos（分）"),
            ("洪都拉斯", "伦皮拉", "Honduran Lempira", "L.", "HNL", "1HNL=100 centavos（分）"),
            ("尼加拉瓜", "科多巴", "Nicaraguan Cordoba", "CS", "NIC", "1NIC=100 centavos（分）"),
            ("哥斯达黎加", "哥斯达黎加科朗", "Costa Rican Colon", "￠", "CRC", "1CRC=100 centavos（分）"),
            ("巴拿马", "巴拿马巴波亚", "Panamanian Balboa", "B.", "PAB", "1PAB=100 centesimos（分）"),
            ("古巴", "古巴比索", "Cuban Peso", "Cu.Pes.", "CUP", "1CUP=100 centavos（分）"),
            ("巴哈马联邦", "巴哈马元", "Bahaman Dollar", "B.＄", "BSD", "1BSD=100 cents（分）"),
            ("牙买加", "牙买加元", "Jamaican Dollars", "＄.J.", "JMD", "1JMD=100 cents（分）"),
            ("海地", "古德", "Haitian Gourde", "G.;Gds.", "HTG", "1HTG=100 centimes（分）"),
            ("多米尼加", "多米尼加比索", "Dominican Peso", "R.D.＄", "DOP", "1DOP=100 centavos（分）"),
            ("特立尼达和多巴哥", "特立尼达多巴哥元", "Trinidad and Tobago Dollar", "T.T.＄", "TTD",
             "1TTD=100 cents（分)"),
            ("巴巴多斯", "巴巴多斯元", "Barbados Dollar", "BDS.＄", "BBD", "1BBD=100 cents（分）"),
            ("哥伦比亚", "哥伦比亚比索", "Colombian Peso", "Col＄", "COP", "1COP=100 centavos（分）"),
            ("委内瑞拉", "博利瓦", "Venezuelan Bolivar", "B", "VEB", "1VEB=100 centimos（分）"),
            ("圭亚那", "圭亚那元", "Guyanan Dollar", "G.＄", "GYD", "1GYD=100 cents（分）"),
            ("苏里南", "苏里南盾", "Surinam Florin", "S.Fl.", "SRG", "苏1SRG=100分"),
            ("秘鲁", "新索尔", "Peruvian Sol", "S/.", "PES", "1PES=100 centavos（分）"),
            ("厄瓜多尔", "苏克雷", "Ecuadoran Sucre", "S/.", "ECS", "1ECS=100 centavos（分）"),
            ("巴西", "新克鲁赛罗", "Brazilian New Cruzeiro G", "Gr.＄", "BRC", "1BRC=100 centavos（分）"),
            ("玻利维亚", "玻利维亚比索", "Bolivian Peso", "Bol.P.", "BOP", "1BOP=100 centavos（分）"),
            ("智利", "智利比索", "Chilean Peso", "P.", "CLP", "1CLP=100 centesimos（分）"),
            ("阿根廷", "阿根廷比索", "Argentine Peso", "Arg.P.", "ARP", "1ARP=100 centavos（分）"),
            ("巴拉圭", "巴拉圭瓜拉尼", "Paraguayan Guarani", "Guars.", "PYG", "1PYG=100 centimes（分）"),
            ("乌拉圭", "乌拉圭新比索", "New Uruguayan Peso", "N.＄", "UYP", "1UYP=100 centesimos（分）"),
            ("埃及", "埃及镑", "Egyptian Pound", "￡E.;LF.", "EGP", "1EGP=100 piastres（皮阿斯特）"),
            ("利比亚", "利比亚第纳尔", "Libyan Dinar", "LD.", "LYD", "1LYD=100 piastres（皮阿斯特）"),
            ("苏丹", "苏丹镑", "Sudanese Pound", "￡S.", "SDP", "1SDP=100 piastres（皮阿斯特）"),
            ("突尼斯", "突尼斯第纳尔", "Tunisian Dinar", "TD.", "TND", "1TND=1,000 milliemes（米利姆）"),
            ("阿尔及利亚", "阿尔及利亚第纳尔", "Algerian Dinar", "AD.", "DZD", "1DZ=100 centimes（分）"),
            ("摩洛哥", "摩洛哥迪拉姆", "Moroccan Dirham", "DH.", "MAD", "1MAD=100 centimes（分）"),
            ("毛里塔尼亚", "乌吉亚", "Mauritania Ouguiya", "UM", "MRO", "1MRO=5 khoums（库姆斯）"),
            ("塞内加尔", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("上沃尔特", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("科特迪瓦", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("多哥", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("贝宁", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("尼泊尔", "非共体法郎", "African Financial Community Franc", "C.F.A.F.", "XOF",
             "1XOF=100 centimes（分）"),
            ("冈比亚", "法拉西", "Gambian Dalasi", "D.G.", "GMD", "1GMD=100 bututses（分）"),
            ("几内亚比绍", "几内亚比索", "Guine- Bissau peso", "PG."),
            ("几内亚", "几内亚西里", "Guinean Syli", "GS.", "GNS", "辅币为科里cauri,但50科里以下"),
            ("塞拉里昂", "利昂", "Sierra Leone Leone", "Le.", "SLL", "1SLL=100 cents（分）"),
            ("利比里亚", "利比里亚元", "Liberian Dollar", "L.＄￡;Lib.＄", "LRD", "1LRD=100 cents（分）"),
            ("加纳", "塞地", "Ghanaian Cedi", "￠", "GHC", "1GHC=100 pesewas（比塞瓦）"),
            ("尼日利亚", "奈拉", "Nigerian Naira", "N", "NGN", "1NGN=100 kobo（考包）"),
            ("喀麦隆", "中非金融合作法郎", "Central African Finan-Coop Franc", "CFAF", "XAF",
             "1XAF=100 centimes（分）"),
            ("乍得", "中非金融合作法郎", "Central African Finan-Coop Franc", "CFAF", "XAF",
             "1XAF=100 centimes（分）"),
            ("刚果", "中非金融合作法郎", "Central African Finan-Coop Franc", "CFAF", "XAF",
             "1XAF=100 centimes（分）"),
            ("加蓬", "中非金融合作法郎", "Central African Finan-Coop Franc", "CFAF", "XAF",
             "1XAF=100 centimes（分）"),
            ("中非", "中非金融合作法郎", "Central African Finan-Coop Franc", "CFAF", "XAF",
             "1XAF=100 centimes（分）"),
            ("赤道几内亚", "赤道几内亚埃奎勒", "Equatorial Guinea Ekuele", "EK.", "GQE",
             "1GQE=100 centimes（分）"),
            ("南非", "兰特", "South African Rand", "R.", "ZAR", "1ZAR=100 cents（分）"),
            ("吉布提", "吉布提法郎", "Djibouti Franc", "DJ.FS;DF", "DJF", "1DJF=100 centimes（分）"),
            ("索马里", "索马里先令", "Somali Shilling", "Sh.So.", "SOS", "1SOS=100 cents（分）"),
            ("肯尼亚", "肯尼亚先令", "Kenya Shilling", "K.Sh", "KES", "1KES=100 cents（分）"),
            ("乌干达", "乌干达先令", "Uganda Shilling", "U.Sh.", "UGS", "1UGS=100 cents（分）"),
            ("坦桑尼亚", "坦桑尼亚先令", "Tanzania Shilling", "T.Sh.", "TZS", "1TZS=100 cents（分）"),
            ("卢旺达", "卢旺达法郎", "Rwanda Franc", "RF.", "RWF", "1RWF=100 cents（分）"),
            ("布隆迪", "布隆迪法郎", "Burnudi Franc", "F.Bu", "BIF", "1BIF=100 cents（分）"),
            ("扎伊尔", "扎伊尔", "Zaire Rp Zaire", "Z.", "ZRZ", "1ZRZ=100 makuta（马库塔）"),
            ("赞比亚", "赞比亚克瓦查", "Zambian Kwacha", "KW.;K.", "ZMK", "1ZMK=100 nywee（恩韦）"),
            ("马达加斯加", "马达加斯加法郎", "Franc de Madagasca", "F.Mg.", "MCF", "1MCF=100 cents（分）"),
            ("塞舌尔", "塞舌尔卢比", "Seychellesx Rupee", "S.RP(S)", "SCR", "1SCR=100 cent（分）"),
            ("毛里求斯", "毛里求斯卢比", "Mauritius Rupee", "Maur. Rp.", "MUR", "1MUR=100 centimes（分）"),
            ("津巴布韦", "津巴布韦元", "Zimbabwe Dollar", "ZIM.＄", "ZWD", "1ZWD=100 cents（分）"),
            ("科摩罗", "科摩罗法郎", "Comoros Franc", "Com.F.", "KMF", "1KMF=100 tambala（坦巴拉）"),
            ("澳大利亚", "澳大利亚元", "Australian Dollar", "＄A.", "AUD", "1AUD=100 cents"),
            ("新西兰", "新西兰元", "New Zealand Dollar", "＄NZ.", "NZD", "1NZD=100 cents"),
            ("斐济", "斐济元", "Fiji Dollar", "F.＄", "FJD", "1FJD=100 cents"),
            ("所罗门群岛", "所罗门元", "Solomon Dollar.", "SL. ＄", "SBD", "1SBD=100 cents")
        ]
        return world_money
