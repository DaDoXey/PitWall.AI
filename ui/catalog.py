"""ui/catalog.py — cataloghi UI (auto, piste, condizioni) per il restyle.

Liste statiche di presentazione per i selettori (Fase 7). Tenute qui per NON
importare il monolite `app_legacy.py` (che all'import esegue codice Streamlit).
Allineate alla lista storica; i range setup reali vengono comunque da
`modules.setup_params.get_params_for_car()` (override per vettura presenti nel
DB JSON, fallback ai generici per le altre).
"""

CAR_LIST = [
    "BMW M4 GT3",
    "Ferrari 296 GT3",
    "Ferrari 488 GT3 Evo",
    "Porsche 992 GT3 R",
    "Porsche 991 II GT3 R",
    "Mercedes-AMG GT3 Evo",
    "Audi R8 LMS Evo II GT3",
    "Lamborghini Huracán GT3 EVO2",
    "McLaren 720S GT3 Evo",
    "Bentley Continental GT3",
    "Honda NSX GT3 Evo",
    "Nissan GT-R Nismo GT3",
    "Lexus RC F GT3",
    "Ford Mustang GT3",
    "Aston Martin V8 Vantage GT3",
]

TRACK_LIST = [
    "Monza", "Spa-Francorchamps", "Nürburgring GP", "Silverstone",
    "Misano", "Barcelona", "Hungaroring", "Zandvoort", "Imola",
    "Kyalami", "Mount Panorama", "Suzuka", "Zolder",
    "Paul Ricard", "Brands Hatch",
]

CONDITIONS = ["Asciutto", "Umido", "Bagnato"]
