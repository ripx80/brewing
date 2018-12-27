
def check_mmum_recipe(recipe):
    """
    check relevant fields in array.
    at the moment you can only use brews with Infusion.
    check all field from https://www.maischemalzundmehr.de/rezept.json.txt
    Rastzeit, Hopfen, Malz 1-7
    WeitereZutat_Wuerze_<1-5>_Name
    Hopfen_VWH_<1-3>_Sorte    
    WeitereZutat_Gaerung_<1-3>_Name
    Stopfhopfen_<1-3>_Sorte
    This is because this json array is soo stupid -.-
    """

    if recipe["Maischform"] != "infusion":
        print("[W] Only infusion is supported...")
        return False

    single = ["Infusion_Hauptguss", "Infusion_Einmaischtemperatur","Abmaischtemperatur","Kochzeit_Wuerze","Nachguss","Hefe","Gaertemperatur"]
    for k in single:
        try:
            _=recipe[k]
        except KeyError:
            print(f"[E] invalid recipe. This field missed: {k}")
            return False

    """ This is because this json array is soo stupid -.- """
    cnt={
        'malz':0,
        'rast':0,
        'hopfen_vwh':0,
        'hopfen':0,
        'extra_ingredient':0,
        'hopfen_stopf':0,
        'extra_gaerung':0,
    }
    for k in recipe:
        key = k.split('_') 
        if k[:-1] == "Malz":
            cnt['malz'] += 1
        elif k[:17] == "Infusion_Rastzeit":
            cnt['rast'] += 1                    
        elif k[:6] == "Hopfen":                       
            if len(key) == 3:
                if key[2] == "Sorte":
                    cnt['hopfen'] += 1
            elif len(key) == 4:
                if key[3] == "Sorte":
                    cnt['hopfen_vwh'] += 1
        elif k[:19] == "WeitereZutat_Wuerze": 
            if k.split('_')[3] == "Name":
                cnt['extra_ingredient'] += 1
        elif key[0] == "Stopfhopfen":
            if key[2] == "Sorte":
                cnt['hopfen_stopf'] += 1
        elif key[0] == "WeitereZutat":
            if key[3] == "Name":
                cnt['extra_gaerung'] += 1
    
    if not cnt['hopfen'] or not cnt['malz'] or not cnt['rast']:
        print(f"[E] invalid recipe, no counter of cnt: {cnt}")
        return False

    return cnt

# change this to __repr__ class meth
def print_recipe(recipe):
    return f"""brew this recipe:
    
        Name: {recipe['Name']}
        Sorte: {recipe['Sorte']}
        Original: {recipe['Klonbier_Original']}    

    """