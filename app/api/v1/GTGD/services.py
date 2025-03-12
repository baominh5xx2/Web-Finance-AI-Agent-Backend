from vnstock import Vnstock

class GTGD:
    def __init__(self):
        self.stock = Vnstock().stock(source='VCI')
    def get_all_cp(self, symbol : str):
        all_cp = self.stock.listing.symbols_by_group(symbol)
        return all_cp
    def get_gtgd(self, symbol : str):
        price_datas = []
        for i in self.get_all_cp(symbol):
            price_data = self.stock.trading.price_board(i)
            total_value = price_data['match']['total_accumulated_value']
            price_datas.append({i: total_value})
        return price_datas
    