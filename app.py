from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///magazyn.db'
db = SQLAlchemy(app)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operacja = db.Column(db.String(20), nullable=False)
    nazwakwota = db.Column(db.String(50), nullable=False)
    cena = db.Column(db.String(20), nullable=False)
    ilosc = db.Column(db.String(20), nullable=False)


class Mag(db.Model):
    idx = db.Column(db.String(60), primary_key=True)
    nazwa = db.Column(db.String(50), nullable=False)
    cena = db.Column(db.String(20), nullable=False)
    ilosc = db.Column(db.String(20), nullable=False)


class Saldo(db.Model):
    saldo = db.Column(db.String(15), primary_key=True, default='0')


alembic = Alembic()
alembic.init_app(app)


def odczyt(tabela, par1='', par2=''):
    with app.app_context():
        if tabela == 'Log':
            lista = {}
            if par1 != '' and par2 != '':
                x = db.session.query(Log).filter((Log.id >= par1), (Log.id <= par2)).all()
            elif par1 != '' and par2 == '':
                x = db.session.query(Log).filter((Log.id >= par1)).all()
            elif par2 != '' and par1 == '':
                x = db.session.query(Log).filter((Log.id <= par2)).all()
            elif par2 == '' and par1 == '':
                x = db.session.query(Log).all()
            for n in x:
                lista[n.id] = [n.operacja, n.nazwakwota, n.cena, n.ilosc]
        elif tabela == 'Mag':
            lista = {}
            if par1 != '' and par2 != '':
                x = db.session.query(Mag).filter((Mag.idx == par1), (Mag.nazwa == par2)).all()
            elif par1 != '' and par2 == '':
                x = db.session.query(Mag).filter((Mag.idx == par1)).all()
            elif par2 != '' and par1 == '':
                x = db.session.query(Mag).filter((Mag.nazwa == par2)).all()
            elif par2 == '' and par1 == '':
                x = db.session.query(Mag).all()
            for n in x:
                lista[n.idx] = [n.nazwa, n.cena, n.ilosc]
        elif tabela == 'Saldo':
            lista = []
            x = db.session.query(Saldo).all()
            for n in x:
                lista = n.saldo
    return lista


def modyfikacja(tabela, par1='', par2='', par3=''):
    with app.app_context():
        if tabela == 'Mag':
            if par1 != '' and par2 != '' and par3 != '':
                x = db.session.query(Mag).filter(Mag.idx == par1).first()
                y = db.session.query(Saldo).first()
                if x and y:
                    x.ilosc = par2
                    y.saldo = par3
                    db.session.add(x, y)
                    db.session.commit()
        elif tabela == 'Saldo':
            if par3 != '':
                y = db.session.query(Saldo).first()
                if y:
                    y.saldo = par3
                    db.session.add(y)
                    db.session.commit()
    return


def dodawanie(tabela, par1='', par2='', par3='', par4='', par5=''):
    with app.app_context():
        if tabela == 'Mag':
            if par1 != '' and par2 != '' and par3 != '' and par4 != '' and par5 != '':
                dodaj = Mag(idx=par1, nazwa=par2, cena=par3, ilosc=par4)
                y = db.session.query(Saldo).first()
                y.saldo = par5
                db.session.add(dodaj)
                db.session.commit()
        if tabela == 'Log':
            if par1 != '' and par2 != '' and par3 != '' and par4 != '':
                dodaj = Log(operacja=par1, nazwakwota=par2, cena=par3, ilosc=par4)
                db.session.add(dodaj)
                db.session.commit()
    return


def usuwanie(tabela, par1='', par2=''):
    print(tabela, par1, par2)
    with app.app_context():
        if tabela == 'Mag':
            if par1 != '' and par2 != '':
                db.session.query(Mag).filter(Mag.idx == par1).delete()
                y = db.session.query(Saldo).first()
                y.saldo = par2
                db.session.commit()
    return


class Manager:
    def __init__(self):
        self.actions = {}
        self.dostepne_operacje = ['saldo', 'sprzedaz', 'zakup', 'konto', 'lista', 'magazyn', 'przeglad', 'koniec']
        self.int_tpl = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
        self.fl_tpl = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.')
        self.historia = {}
        self.magazyn = {}
        self.konto = 0

    def assign(self, name):
        def decorate(cb):
            self.actions[name] = cb
        return decorate

    def execute(self, name, *args, **kwargs):
        if name not in self.actions:
            print("Action not defined")
        else:
            self.actions[name](self, *args, **kwargs)


manager = Manager()


@manager.assign("pobierz_saldo")
def pobierz_saldo(manager):
    manager.konto = float(odczyt('Saldo'))


@manager.assign("nadpisz_saldo")
def nadpisz_saldo(manager, val):
    modyfikacja('Saldo', par3=str(val))


@manager.assign("wczytaj_historie")
def wczytaj_historie(manager):
    manager.historia.clear()
    manager.historia = odczyt('Log')


@manager.assign("zapisz_historie")
def zapisz_historie(manager, oper, par1, par2, par3):
    dodawanie('Log', oper, par1, par2, par3)


@manager.assign("wczytaj_magazyn")
def wczytaj_magazyn(manager, inx=''):
    manager.magazyn.clear()
    manager.magazyn = odczyt('Mag', par1=inx)


@manager.assign("szukaj_magazyn")
def szukaj_magazyn(manager, przedmiot):
    manager.magazyn.clear()
    manager.magazyn = odczyt('Mag', par2=przedmiot)


@manager.assign("magazyn_dopisz")
def magazyn_dopisz(manager, idx, nazwa, cena, ilosc, sal):
    dodawanie('Mag', idx, str(nazwa), str(cena), str(ilosc), str(sal))


@manager.assign("magazyn_usun")
def magazyn_usun(manager, inx, sal):
    usuwanie('Mag', inx, sal)


@manager.assign("nadpisz_magazyn")
def nadpisz_magazyn(manager, idx, ilosc, sal):
    modyfikacja('Mag', idx, str(ilosc), str(sal))


@app.route('/')
def str_glowna():
    return render_template('index.html', operacje=manager.dostepne_operacje)


@app.route('/historia/', methods=['GET', 'POST'])
def przeglad_historii():
    operacja = request.form.get('operacja')
    od = request.form.get('hi_od')
    do = request.form.get('hi_do')
    informacja = ''
    dane = []
    if operacja == "przeglad":
        manager.execute("wczytaj_historie")
        if len(manager.historia) < 1:
            informacja = "Brak wpisow"
        else:
            if od == '' and do == '':
                informacja = "Podano puste wartosci - wyswietlam cala historia"
                dane = manager.historia
            elif od == '' and do != '':
                noint = 0
                for y in do:
                    if y not in manager.int_tpl:
                        noint = 1
                if noint == 1 or do == '0':
                    informacja = f"Podana wartosc jest niepoprawna dopuszczalne wartosci powinny" \
                                 f" zawierac sie pomiedzy 1 i {len(manager.historia)}"
                else:
                    informacja = "Wyswietlam historie od poczatku do podanej wartosci"
                    for i in manager.historia:
                        if i <= int(do):
                            elm = (i, manager.historia[i])
                            dane.append(elm)
                    dane = dict(dane)
            elif od != '' and do == '':
                noint = 0
                for y in od:
                    if y not in manager.int_tpl:
                        noint = 1
                if noint == 1 or od == '0':
                    informacja = f"Podana wartosc jest niepoprawna dopuszczalne wartosci powinny" \
                                 f" zawierac sie pomiedzy 1 i {len(manager.historia)}"
                else:
                    informacja = "Wyswietlam historie od podanej wartosci do konca"
                    for i in manager.historia:
                        if i >= int(od):
                            elm = (i, manager.historia[i])
                            dane.append(elm)
                    dane = dict(dane)
            elif od != '' and do != '':
                noint = 0
                for y in od:
                    if y not in manager.int_tpl:
                        noint = 1
                for z in do:
                    if z not in manager.int_tpl:
                        noint = 1
                if noint == 1:
                    informacja = "Przynajmniej  jedna podana wartosc jest niepoprawna"
                elif int(od) == 0 or int(do) == 0:
                    informacja = f"Podano niedopuszczalna zerowa wartosc dopuszczalne wartosci" \
                                 f" powinny zawierac sie pomiedzy 1 i {len(manager.historia)}"
                elif int(od) > int(do):
                    informacja = f"Wartosc poczatkowa wieksza od koncowej dopuszczalne wartosci " \
                                   "powinny zawierac sie pomiedzy 1 i {len(manager.historia)}"
                else:
                    informacja = "Wyswietlam historie dla podanego zakresu wartosci"
                    for i in manager.historia:
                        if int(od) <= i <= int(do):
                            elm = (i, manager.historia[i])
                            dane.append(elm)
                    dane = dict(dane)
    return render_template('historia.html', informacja=informacja, dane=dane)


@app.route('/', methods=['GET', 'POST'])
def menu_glowne():
    operacja = request.form.get('Operacja')
    saldo_add = request.form.get('kwota')
    produkt = request.form.get('mg_nazwa')
    z_nazwa = request.form.get('za_nazwa')
    z_cena = request.form.get('za_cena')
    z_ilosc = request.form.get('za_ilosc')
    s_nazwa = request.form.get('sp_nazwa')
    s_cena = request.form.get('sp_cena')
    s_ilosc = request.form.get('sp_ilosc')
    komunikat = ''
    wartosc = []
    manager.execute("pobierz_saldo")
    if operacja == "saldo":
        if saldo_add != '':
            if manager.konto + float(saldo_add) < 0:
                komunikat = "Operacja niemozliwa do wykonania"
            else:
                manager.konto += float(saldo_add)
                manager.execute("nadpisz_saldo", manager.konto)
                manager.execute("zapisz_historie", 'saldo', manager.konto, '-', '-')
        else:
            komunikat = "Podano pustą wartosc - operacja niemozliwa do wykonania"
    elif operacja == "konto":
        manager.execute("pobierz_saldo")
        komunikat = f"Stan konta wynosi: {manager.konto}"
    elif operacja == "lista":
        manager.execute("wczytaj_magazyn")
        if not manager.magazyn:
            komunikat = "Magazyn jest pusty"
        else:
            wartosc = manager.magazyn
            komunikat = ''
    elif operacja == "magazyn":
        if produkt == '':
            komunikat = "Podano pusta nazwa - operacja niemozliwa do wykonania"
        else:
            manager.execute("szukaj_magazyn", produkt)
            komunikat = 'Magazyn jest pusty'
            kontrolna = 1
            for element in manager.magazyn:
                kontrolna = 0
                elem = element, manager.magazyn[element]
                wartosc.append(elem)
                wartosc = dict(wartosc)
            if kontrolna == 1:
                komunikat = "Brak w magazynie"
            else:
                komunikat = ''
    elif operacja == "zakup":
        if z_nazwa == '' or z_cena == '' or z_ilosc == '':
            komunikat = "Operacja niemozliwa - podano pusta wartosc"
        else:
            # sprawdzamy poprawnosc ceny i ilosci
            noint = 0
            for y in z_cena:
                if y not in manager.fl_tpl:
                    noint = 1
            for z in z_ilosc:
                if z not in manager.int_tpl:
                    noint = 1
            if noint == 1 or z_cena == '0' or z_ilosc == '0':
                komunikat = "Przynajmniej  jedna podana wartosc jest niepoprawna"
            else:
                manager.execute("pobierz_saldo")
                z_ilosc = int(z_ilosc)
                # jako identyfikatora uzyjemy sumy nazwy i ceny - bo mozemy miec te same produkty o roznych cenach
                inx = str(z_nazwa + z_cena)
                # Najpierw sprawdzamy czy mamy wystarczajace srodki na koncie
                if manager.konto < (float(z_cena) * int(z_ilosc)):
                    komunikat = "Operacja niemozliwa - brak wystarczajacych srodkow na koncie"
                else:
                    manager.execute("wczytaj_magazyn", inx)
                    if not manager.magazyn:
                        # jesli takiego produktu niema w magazynie dopisujemy do magazynu
                        manager.konto -= (float(z_cena) * int(z_ilosc))
                        manager.execute("magazyn_dopisz", inx, z_nazwa, float(z_cena), z_ilosc, str(manager.konto))
                        komunikat = "Dodano produkt do magazynu"
                        manager.execute("zapisz_historie", 'zakup', z_nazwa, float(z_cena), z_ilosc)
                    else:
                        # jesli taki produkt istnieje dodajemy tylko ilosc sztuk
                        ile = int(manager.magazyn[inx][2]) + z_ilosc
                        manager.konto -= (float(z_cena) * int(z_ilosc))
                        manager.execute("nadpisz_magazyn", inx, str(ile), str(manager.konto))
                        komunikat = "Zmodyfikowano liczbe produktow w magazynie"
                        manager.execute("zapisz_historie", 'zakup', z_nazwa, float(z_cena), z_ilosc)
    elif operacja == "sprzedaz":
        # weryfikujemy poprawnosc zlecenia
        if s_nazwa == '' or s_cena == '' or s_ilosc == '':
            komunikat = "Operacja niemozliwa - podano pusta wartosc"
        else:
            noint = 0
            for y in s_cena:
                if y not in manager.fl_tpl:
                    noint = 1
            for z in s_ilosc:
                if z not in manager.int_tpl:
                    noint = 1
            if noint == 1 or s_cena == '0' or s_ilosc == '0':
                komunikat = "Przynajmniej  jedna podana wartosc jest niepoprawna"
            else:
                s_ilosc = int(s_ilosc)
                inx = str(s_nazwa + s_cena)
                # sprawdzamy czy mamy taki produkt
                manager.execute("wczytaj_magazyn", inx)
                if not manager.magazyn:
                    komunikat = "Produktu o takiej nazwie i/lub cenie niema w magazynie"
                else:
                    # sprawdzamy czy mamy wystarczajaca ilosc sztuk
                    if int(s_ilosc) > int(manager.magazyn[inx][2]):
                        komunikat = f"Dostepna ilosc produktu jest mniejsza i wynosi:" \
                                    f" {manager.magazyn[inx][2]}"
                    else:
                        # jesli zlecenie zabiera wszystkie sztuki produktu usuwamy produkt z magazynu
                        if int(s_ilosc) == int(manager.magazyn[inx][2]):
                            manager.konto += (float(s_cena) * int(s_ilosc))
                            manager.execute("magazyn_usun", inx, str(manager.konto))
                            komunikat = f"Sprzedano caly zapas produktu: {s_nazwa} i cenie: {float(s_cena)}"
                            manager.execute("zapisz_historie", 'sprzedaz', s_nazwa, float(s_cena), s_ilosc)
                        # jesli taki produkt istnieje modyfikujemy tylko ilosc sztuk
                        else:
                            ile = int(manager.magazyn[inx][2]) - int(s_ilosc)
                            manager.konto += (float(s_cena) * int(s_ilosc))
                            manager.execute("nadpisz_magazyn", inx, str(ile), str(manager.konto))
                            komunikat = f"Zmodyfikowano ilosc produktu: {s_nazwa} i cenie: {float(s_cena)} "\
                                        f"obecny stan to {ile}"
                            manager.execute("zapisz_historie", 'sprzedaz', s_nazwa, float(s_cena), s_ilosc)
    # koniec - konczymy program
    elif operacja == "koniec":
        print("Koniec programu")
        quit()
    return render_template('index.html', operacje=manager.dostepne_operacje, komunikat=komunikat, wartosc=wartosc)


if __name__ == "__main__":
    app.run()
